"""Kontrola wydania kursowego w przeglądarce (gałąź cwiczenia i jej gałęzie pomocnicze).

Narzędzie uruchamiamy z katalogu roboczego gałęzi ćwiczeń przez uv, który
dostarcza Playwright, a build wykonuje interpreter środowiska książki
(--python):

    uv run --no-project --with playwright==1.63.0 python kurs/tools/sprawdz_wydanie.py
        --python D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe
        [--katalog-roboczy] [--zrzuty KATALOG]

--python           interpreter z zależnościami książki (mkdocs-material), którym
                   budujemy wydanie i odczytujemy definicje aktywności i nav.
--katalog-roboczy  buduje kopię katalogu roboczego razem z niezatwierdzonymi
                   i nieśledzonymi plikami zamiast commitu HEAD (pętla robocza).
--zrzuty KATALOG   zapisuje zrzuty ekranu sprawdzanych stron.

Narzędzie buduje wydanie kursowe (mkdocs.kurs.yml) z opcją --strict z czystego
eksportu commitu HEAD, serwuje je statycznie na pierwszym wolnym porcie
z zakresu 8050–8069 i sprawdza w Microsoft Edge (Playwright, kanał msedge),
w nowym kontekście przeglądarki, w trybie jasnym i ciemnym, przy szerokości
okna 1280 i 375 px:
  - konsola i sieć: brak błędów konsoli i błędów strony, nieudanych żądań
    i odpowiedzi HTTP o kodzie co najmniej 400 (niepowodzenia żądań do innych
    serwerów, np. czcionek, i ostrzeżenia spoza warstwy ćwiczeń są uwagami);
  - menu części w belce nagłówka: każda część z nav (sekcja najwyższego
    poziomu) jest widoczna w całości, nieprzycięta i niezasłonięta,
    a oznaczona jest dokładnie część bieżącej strony;
  - brak poziomego przewijania strony;
  - strony z ćwiczeniami: dokładnie jeden slot strony, oczekiwana liczba
    wyrenderowanych aktywności, atrybut data-activity-section przy każdym
    powiązanym nagłówku i przy żadnym innym elemencie, wskaźniki postępu
    stron w nawigacji i sekcji w spisie treści (w wąskim oknie widoczne
    w szufladzie nawigacji);
  - wybrane strony bez ćwiczeń (strona główna, strony wejściowe części
    i rozdziałów ze stronami z ćwiczeniami): brak slotu, oznaczonych
    nagłówków i własnych wskaźników postępu;
  - skok do kotwicy każdej powiązanej sekcji kończy się pod przypiętą belką;
  - rozwiązanie jednego pytania single_choice na każdej stronie z ćwiczeniami
    (poprawna odpowiedź z definicji YAML) oznacza je jako wykonane, wskaźniki
    postępu pokazują nowy stan, a stan przetrwa przeładowanie strony;
  - nawigacja natychmiastowa (navigation.instant) z jednej strony
    z ćwiczeniami na drugą zachowuje działający slot i wskaźniki, a dalsze
    przejście na stronę bez ćwiczeń usuwa slot i wskaźniki sekcji.

Build ustawia site_url na adres serwera, tak jak mkdocs serve w podglądzie na
porcie 8002: bez site_url mapa witryny jest pusta i Material nie przechwytuje
odnośników nawigacją natychmiastową. Definicje aktywności i nav odczytuje
interpreter --python, więc narzędzie wymaga wyłącznie biblioteki standardowej
i Playwright. Moduł playwright importuje dopiero przy uruchomieniu kontroli,
dzięki czemu testy jednostkowe działają w środowisku książki bez Playwright.

Kod wyjścia:
  0  wszystkie kontrole przeszły;
  1  co najmniej jedna kontrola nie przeszła (także build --strict);
  2  kontroli nie można było przeprowadzić: brak Playwright albo Microsoft
     Edge, interpretera --python z pakietami książki, repozytorium git lub
     wolnego portu w zakresie 8050–8069, albo błąd samego narzędzia.
"""

from __future__ import annotations

import argparse
import functools
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from dataclasses import dataclass, field
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlsplit

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402  (polecenia git i eksport commitu, wspólne z bramką)

PORTS = range(8050, 8070)
PLAYWRIGHT = "playwright==1.63.0"
CHECK_CONFIG = "mkdocs.sprawdz-wydanie.yml"
COMMAND = (
    f"uv run --no-project --with {PLAYWRIGHT} python kurs/tools/sprawdz_wydanie.py "
    "--python D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe"
)
NAVIGATION_TIMEOUT = 30_000  # ms na wczytanie strony
LAYER_TIMEOUT = 20_000  # ms na zakończenie pracy warstwy ćwiczeń po wczytaniu
ACTION_TIMEOUT = 10_000  # ms na pojedynczą akcję (kliknięcie, ukończenie)
BUILD_TIMEOUT = 900  # s na build wydania
WIDE = 1220  # px: od 76.25em Material pokazuje oba panele boczne
LAYER_SCRIPTS = "/javascripts/interactive/"

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_ENVIRONMENT = 2


@dataclass(frozen=True)
class Variant:
    """Tryb kolorów i rozmiar okna jednego przebiegu kontroli."""

    scheme: str
    width: int
    height: int

    @property
    def label(self) -> str:
        return f"{'jasny' if self.scheme == 'light' else 'ciemny'} {self.width}"

    @property
    def wide(self) -> bool:
        return self.width >= WIDE


VARIANTS = (
    Variant("light", 1280, 900),
    Variant("dark", 1280, 900),
    Variant("light", 375, 812),
    Variant("dark", 375, 812),
)

# Wiersze tabeli podsumowania: (klucz, opis).
CHECKS = (
    ("konsola", "konsola i sieć"),
    ("menu", "menu części w belce"),
    ("przewijanie", "brak przewijania poziomego"),
    ("aktywnosci", "slot i aktywności"),
    ("naglowki", "oznaczone nagłówki"),
    ("wskazniki", "wskaźniki postępu"),
    ("bez-cwiczen", "strony bez ćwiczeń"),
    ("kotwice", "skok do kotwicy sekcji"),
    ("rozwiazanie", "rozwiązanie i przeładowanie"),
    ("natychmiastowa", "nawigacja natychmiastowa"),
)


# ---------------------------------------------------------------- plan kontroli


def page_url(src: str, use_directory_urls: bool = True) -> str:
    """Adres strony docs/<src> względem katalogu głównego serwisu (jak w MkDocs)."""
    path = PurePosixPath(src)
    parent = path.parent.as_posix()
    if path.stem in ("index", "README"):
        if use_directory_urls:
            url = "" if parent == "." else f"{parent}/"
        else:
            url = "index.html" if parent == "." else f"{parent}/index.html"
    else:
        base = path.with_suffix("").as_posix()
        url = f"{base}/" if use_directory_urls else f"{base}.html"
    return quote(url)


def is_document(value: object) -> bool:
    return isinstance(value, str) and value.endswith(".md") and "://" not in value


@dataclass
class NavItem:
    """Pozycja nav: strona (page) albo sekcja z pozycjami podrzędnymi."""

    title: str | None
    page: str | None = None
    children: list[NavItem] = field(default_factory=list)

    @property
    def section(self) -> bool:
        return self.page is None


def parse_nav(entries) -> list[NavItem]:
    """Zamienia nav z konfiguracji MkDocs na drzewo pozycji."""
    items: list[NavItem] = []
    for entry in entries or []:
        if isinstance(entry, str):
            items.append(NavItem(None, entry))
        elif isinstance(entry, dict) and len(entry) == 1:
            ((title, value),) = entry.items()
            if isinstance(value, list):
                items.append(NavItem(str(title), None, parse_nav(value)))
            elif isinstance(value, str):
                items.append(NavItem(str(title), value))
    return items


def documents(items: list[NavItem]) -> list[str]:
    """Strony dokumentacji w kolejności nav (w głąb drzewa)."""
    found: list[str] = []
    for item in items:
        if item.section:
            found.extend(documents(item.children))
        elif is_document(item.page):
            found.append(item.page)
    return found


def landing(item: NavItem) -> str | None:
    """Strona, do której prowadzi pozycja menu części (jak partials/czesci.html)."""
    while item.section:
        if not item.children:
            return None
        item = item.children[0]
    return item.page if is_document(item.page) else None


def parts(items: list[NavItem]) -> list[tuple[str, str | None]]:
    """Części podręcznika: sekcje najwyższego poziomu nav i ich strony wejściowe."""
    return [(item.title or "", landing(item)) for item in items if item.section]


def part_of(items: list[NavItem]) -> dict[str, str]:
    """Część, do której należy każda strona nav."""
    owners: dict[str, str] = {}
    for item in items:
        if item.section:
            for src in documents(item.children):
                owners.setdefault(src, item.title or "")
    return owners


def chapter_index(items: list[NavItem], src: str) -> str | None:
    """Pierwsza strona najbliższej sekcji nav, która zawiera stronę src."""

    def trail_to(entries: list[NavItem], trail: list[NavItem]) -> list[NavItem] | None:
        for item in entries:
            if item.section:
                found = trail_to(item.children, [*trail, item])
                if found is not None:
                    return found
            elif item.page == src:
                return trail
        return None

    trail = trail_to(items, [])
    if not trail:
        return None
    pages = documents(trail[-1].children)
    return pages[0] if pages else None


@dataclass(frozen=True)
class Activity:
    activity_id: str
    type: str
    section_id: str | None
    correct_option_id: str | None = None
    option_ids: tuple[str, ...] = ()


@dataclass
class ExercisePage:
    src: str
    url: str
    slot_id: str
    activities: list[Activity]

    @property
    def sections(self) -> list[str]:
        """Powiązane nagłówki strony (bez wiązań z całą stroną), bez powtórzeń."""
        return list(
            dict.fromkeys(
                activity.section_id for activity in self.activities
                if activity.section_id is not None
            )
        )

    @property
    def quiz(self) -> Activity | None:
        """Pierwsze pytanie single_choice, którego poprawna odpowiedź jest wśród wariantów."""
        return next(
            (
                activity for activity in self.activities
                if activity.type == "single_choice"
                and activity.correct_option_id in activity.option_ids
            ),
            None,
        )

    def section_total(self, section_id: str | None) -> int:
        return sum(1 for activity in self.activities if activity.section_id == section_id)


@dataclass
class Plan:
    exercise_pages: list[ExercisePage]
    plain_pages: list[str]
    parts: list[tuple[str, str | None]]
    owners: dict[str, str]
    urls: dict[str, str]
    pill_menu: bool
    route: tuple[str, str, str | None] | None


def build_plan(data: dict) -> Plan:
    """Plan kontroli z nav, ustawień motywu i definicji aktywności.

    data to wynik odczytu konfiguracji wydania (READER) z kluczami nav,
    use_directory_urls, features i definitions.
    """
    items = parse_nav(data.get("nav"))
    directory_urls = bool(data.get("use_directory_urls", True))
    order = documents(items)
    position = {src: index for index, src in enumerate(order)}
    exercise: list[ExercisePage] = []
    for definition in data.get("definitions") or []:
        src = definition.get("page")
        if not is_document(src):
            continue
        activities = [
            Activity(
                activity_id=str(raw.get("activity_id")),
                type=str(raw.get("type")),
                section_id=raw.get("section_id"),
                correct_option_id=raw.get("correct_option_id"),
                option_ids=tuple(str(option) for option in raw.get("option_ids") or ()),
            )
            for raw in definition.get("activities") or []
            if isinstance(raw, dict)
        ]
        exercise.append(
            ExercisePage(src, page_url(src, directory_urls), str(definition.get("slot_id")),
                         activities)
        )
    exercise.sort(key=lambda page: position.get(page.src, len(order)))
    exercise_srcs = [page.src for page in exercise]

    candidates: list[str] = []
    home = next(
        (item.page for item in items if not item.section and is_document(item.page)), None
    )
    if home:
        candidates.append(home)
    for src in exercise_srcs:
        index = chapter_index(items, src)
        if index:
            candidates.append(index)
    candidates += [entry for _, entry in parts(items) if entry]
    plain = [src for src in dict.fromkeys(candidates) if src not in exercise_srcs]

    features = set(data.get("features") or [])
    route = None
    if "navigation.instant" in features and exercise:
        if len(exercise) >= 2:
            start, target = exercise[0].src, exercise[1].src
        else:
            start, target = chapter_index(items, exercise[0].src) or home, exercise[0].src
        leave = chapter_index(items, target)
        if leave in exercise_srcs:
            leave = None
        if start and start != target:
            route = (start, target, leave)

    urls = {src: page_url(src, directory_urls) for src in [*order, *exercise_srcs, *plain]}
    return Plan(
        exercise_pages=exercise,
        plain_pages=plain,
        parts=parts(items),
        owners=part_of(items),
        urls=urls,
        pill_menu={"navigation.tabs", "navigation.tabs.sticky"} <= features,
        route=route,
    )


def rail_state(completed: int, total: int) -> str:
    """Stan wskaźnika postępu (jak deriveCompletionProgress w progress-rail.js)."""
    if completed == 0:
        return "none_completed"
    return "completed" if completed == total else "partial"


# ---------------------------------------------------------------- ocena stanu strony
# Funkcje poniżej oceniają słowniki zwracane przez skrypty JS z sekcji
# „przeglądarka”, więc testy jednostkowe sprawdzają je bez przeglądarki.


def check_parts(state: dict, expected: list[str], active: str | None) -> list[str]:
    """Menu części w belce: pozycje z nav, bieżąca część i widoczność pozycji."""
    problems: list[str] = []
    pills = state.get("parts") or []
    texts = [pill["text"] for pill in pills]
    if texts != expected:
        problems.append(f"menu części zawiera {texts}, oczekiwano {expected}")
    marked = [pill["text"] for pill in pills if pill.get("active")]
    wanted = [active] if active else []
    if marked != wanted:
        problems.append(
            f"oznaczona część: {marked or 'żadna'}, oczekiwano: {wanted or 'żadna'}"
        )
    header = state.get("header")
    viewport = state.get("viewport") or 0
    for pill in pills:
        name = f"pozycja menu części „{pill['text']}”"
        box = pill.get("box") or {}
        if not pill.get("shown"):
            problems.append(f"{name} jest niewidoczna")
            continue
        found = []
        if box.get("left", 0) < -0.5 or box.get("right", 0) > viewport + 0.5:
            found.append(
                f"{name} wychodzi poza okno (od {box.get('left', 0):.0f} do "
                f"{box.get('right', 0):.0f} px przy szerokości {viewport} px)"
            )
        if header and (
            box.get("top", 0) < header["top"] - 0.5
            or box.get("bottom", 0) > header["bottom"] + 0.5
        ):
            found.append(f"{name} wystaje poza belkę nagłówka")
        if pill.get("clipped"):
            found.append(f"{name} jest przycięta przez element nadrzędny")
        if pill.get("covered") and not found:  # środek pozycji poza jej polem widzenia
            found.append(f"{name} jest zasłonięta przez inny element")
        if pill.get("truncated"):
            found.append(f"{name}: etykieta nie mieści się w pigułce")
        problems.extend(found)
    return problems


def check_overflow(state: dict) -> list[str]:
    overflow = state.get("overflow") or 0
    return [f"strona przewija się poziomo o {overflow:.0f} px"] if overflow > 0 else []


def nav_rail_problems(state: dict, exercise_keys: set[str], page_key: str) -> list[str]:
    """Wskaźniki stron w nawigacji: przy każdej stronie z ćwiczeniami i przy żadnej innej."""
    problems: list[str] = []
    links = state.get("navLinks") or []
    missing = sorted({
        link["key"] for link in links if link["key"] in exercise_keys and not link.get("rail")
    })
    stray = sorted({
        link["key"] for link in links if link["key"] not in exercise_keys and link.get("rail")
    })
    if missing:
        problems.append("brak wskaźnika postępu przy odnośnikach do stron: " + ", ".join(missing))
    if stray:
        problems.append(
            "wskaźnik postępu przy odnośnikach do stron bez ćwiczeń: " + ", ".join(stray)
        )
    if page_key in exercise_keys and not any(
        link["key"] == page_key and link.get("rail") for link in links
    ):
        problems.append("brak wskaźnika postępu bieżącej strony w nawigacji")
    return problems


def check_exercise_page(
    state: dict, page: ExercisePage, page_key: str, exercise_keys: set[str], wide: bool
) -> dict[str, list[str]]:
    """Strona z ćwiczeniami: slot, aktywności, oznaczone nagłówki i wskaźniki."""
    found: dict[str, list[str]] = {"aktywnosci": [], "naglowki": [], "wskazniki": []}
    slots = state.get("slots") or []
    if slots != [page.slot_id]:
        found["aktywnosci"].append(f"oczekiwano jednego slotu {page.slot_id!r}, jest {slots}")
    rendered = [activity["id"] for activity in state.get("activities") or []]
    expected = [activity.activity_id for activity in page.activities]
    if sorted(rendered) != sorted(expected):
        missing = [item for item in expected if item not in rendered]
        extra = [item for item in rendered if item not in expected]
        found["aktywnosci"].append(
            f"wyrenderowano {len(rendered)} z {len(expected)} aktywności"
            + (f"; brak: {', '.join(missing)}" if missing else "")
            + (f"; nadmiarowe: {', '.join(extra)}" if extra else "")
        )

    marked = state.get("marked") or []
    marked_ids = [element["id"] for element in marked]
    for section_id in page.sections:
        if section_id not in marked_ids:
            found["naglowki"].append(
                f"nagłówek #{section_id} nie ma atrybutu data-activity-section"
            )
    for element in marked:
        if element["id"] not in page.sections:
            found["naglowki"].append(
                f"atrybut data-activity-section ma element #{element['id']}, z którym nie "
                "wiąże się żadna aktywność"
            )
        elif element.get("tag") not in ("h2", "h3", "h4", "h5", "h6"):
            found["naglowki"].append(
                f"atrybut data-activity-section ma element {element.get('tag')} "
                f"#{element['id']}, a nie nagłówek h2–h6"
            )
        elif element.get("value") != "true":
            found["naglowki"].append(
                f"#{element['id']}: data-activity-section ma wartość {element.get('value')!r}"
            )

    rails = found["wskazniki"]
    rails.extend(nav_rail_problems(state, exercise_keys, page_key))
    toc = state.get("tocLinks") or []
    for section_id in page.sections:
        if not any(link["section"] == section_id and link.get("rail") for link in toc):
            rails.append(f"brak wskaźnika postępu sekcji #{section_id} w spisie treści")
    stray = sorted({
        link["section"] for link in toc
        if link.get("rail") and link["section"] not in page.sections
    })
    if stray:
        rails.append(
            "wskaźnik postępu przy sekcjach bez ćwiczeń: "
            + ", ".join(f"#{section_id}" for section_id in stray)
        )
    if wide:
        if not any(
            link["key"] == page_key and link.get("railShown")
            for link in state.get("navLinks") or []
        ):
            rails.append("wskaźnik postępu bieżącej strony w nawigacji jest niewidoczny")
        for section_id in page.sections:
            if not any(
                link["section"] == section_id and link.get("secondary") and link.get("railShown")
                for link in toc
            ):
                rails.append(
                    f"wskaźnik postępu sekcji #{section_id} w spisie treści jest niewidoczny"
                )
    return found


def check_plain_page(state: dict, page_key: str, exercise_keys: set[str]) -> dict[str, list[str]]:
    """Strona bez ćwiczeń: brak slotu, oznaczeń i własnych wskaźników postępu."""
    found: dict[str, list[str]] = {"bez-cwiczen": [], "wskazniki": []}
    plain = found["bez-cwiczen"]
    if state.get("slots"):
        plain.append(f"strona ma slot aktywności {state['slots']}")
    if state.get("activities"):
        plain.append(f"strona ma wyrenderowane aktywności ({len(state['activities'])})")
    if state.get("marked"):
        plain.append(
            "strona ma elementy z atrybutem data-activity-section: "
            + ", ".join(f"#{element['id']}" for element in state["marked"])
        )
    if state.get("sectionRails"):
        plain.append(f"strona ma wskaźniki postępu sekcji ({state['sectionRails']})")
    if any(link["key"] == page_key and link.get("rail") for link in state.get("navLinks") or []):
        plain.append("odnośnik do tej strony w nawigacji ma wskaźnik postępu")
    found["wskazniki"].extend(nav_rail_problems(state, exercise_keys, page_key))
    return found


def check_anchor(position: dict | None, section_id: str) -> str | None:
    """Skok do kotwicy: nagłówek pod przypiętą belką nagłówka i w obrębie okna."""
    if position is None:
        return f"na stronie nie ma elementu #{section_id}"
    if position["top"] < position["header"] - 1:
        return (
            f"po skoku do kotwicy #{section_id} nagłówek jest zasłonięty belką "
            f"(górna krawędź {position['top']:.0f} px, belka do {position['header']:.0f} px)"
        )
    if position["top"] >= position["viewport"]:
        return f"po skoku do kotwicy #{section_id} nagłówek jest poza oknem"
    return None


def classify(kind: str, text: str, url: str | None, origin: str) -> str | None:
    """Ocena zdarzenia konsoli albo sieci: 'błąd', 'uwaga' albo None (pomijamy).

    Błędem jest każdy błąd strony i błąd konsoli oraz nieudane żądanie do
    sprawdzanego serwera; ostrzeżenie konsoli tylko wtedy, gdy pochodzi ze
    skryptów warstwy ćwiczeń, które w ten sposób zgłaszają swoje awarie.
    Żądania do innych serwerów (np. czcionek) zależą od sieci, więc ich
    niepowodzenie jest uwagą. Przerwane żądanie (net::ERR_ABORTED) towarzyszy
    zwykłej zmianie strony i go nie zgłaszamy.
    """
    local = bool(url) and url.startswith(origin)
    if kind == "pageerror":
        return "błąd"
    if kind == "requestfailed":
        if "ERR_ABORTED" in text:
            return None
        return "błąd" if local else "uwaga"
    if kind == "http":
        return "błąd" if local else "uwaga"
    if kind in ("error", "assert"):
        if url and not local and text.startswith("Failed to load resource"):
            return "uwaga"
        return "błąd"
    if kind == "warning":
        return "błąd" if local and LAYER_SCRIPTS in urlsplit(url).path else "uwaga"
    return None


# ---------------------------------------------------------------- wynik


class Report:
    """Zgłoszenia kontroli w podziale na wiersze tabeli i warianty okna."""

    def __init__(self) -> None:
        self.problems: dict[tuple[str, str], list[str]] = {}
        self.ran: set[tuple[str, str]] = set()
        self.notes: list[str] = []
        self.build = "nie uruchomiono"
        self.build_failed = False

    def mark(self, check: str, variant: Variant) -> None:
        self.ran.add((check, variant.label))

    def problem(self, check: str, variant: Variant, where: str, message: str) -> None:
        self.mark(check, variant)
        self.problems.setdefault((check, variant.label), []).append(f"{where}: {message}")
        print(f"  BŁĄD   [{variant.label}] {where}: {message}", flush=True)

    def extend(self, found: dict[str, list[str]], variant: Variant, where: str) -> None:
        for check, messages in found.items():
            self.mark(check, variant)
            for message in messages:
                self.problem(check, variant, where, message)

    def note(self, message: str) -> None:
        if message not in self.notes:
            self.notes.append(message)
            print(f"  uwaga  {message}", flush=True)

    def cell(self, check: str, label: str) -> str:
        if (check, label) not in self.ran:
            return "—"
        count = len(self.problems.get((check, label), []))
        return "OK" if count == 0 else f"BŁĄD ({count})"

    def failed(self, variants=VARIANTS) -> list[str]:
        names = [
            title for check, title in CHECKS
            if any((check, variant.label) in self.problems for variant in variants)
        ]
        return (["build --strict"] if self.build_failed else []) + names


def summary_lines(report: Report, variants=VARIANTS) -> list[str]:
    """Tabela podsumowania: kontrole w wierszach, warianty okna w kolumnach."""
    width = max(len(title) for _, title in CHECKS)
    labels = [variant.label for variant in variants]
    sizes = [max(len(label), len("BŁĄD (00)")) for label in labels]

    def row(first: str, cells: list[str]) -> str:
        return (
            f"{first:<{width}}  "
            + "  ".join(f"{cell:<{size}}" for cell, size in zip(cells, sizes))
        ).rstrip()

    lines = [row("Kontrola", labels)]
    for check, title in CHECKS:
        lines.append(row(title, [report.cell(check, label) for label in labels]))
    return lines


def verdict(report: Report, head: str, working_tree: bool) -> tuple[int, str]:
    failed = report.failed()
    if failed:
        return EXIT_FAILED, f"Wynik: kontrola wydania nie przeszła ({', '.join(failed)})."
    state = "katalogu roboczego (wynik roboczy)" if working_tree else f"commitu {head[:7]}"
    return EXIT_OK, f"Wynik: kontrola wydania przeszła dla {state}."


# ---------------------------------------------------------------- serwer i build


class StaticServer(ThreadingHTTPServer):
    """Serwer plików statycznych, który nie dzieli portu z innym procesem."""

    allow_reuse_address = False
    daemon_threads = True
    # Moduły ES warstwy przeglądarka pobiera równolegle; przy domyślnej
    # kolejce 5 połączeń Windows odrzuca część z nich (ERR_CONNECTION_REFUSED).
    request_queue_size = 128

    def server_bind(self) -> None:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):  # Windows: bez współdzielenia portu
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


class QuietHandler(SimpleHTTPRequestHandler):
    """Serwuje zbudowany serwis bez dziennika żądań, z jawnymi typami MIME."""

    # Na Windows typy MIME z rejestru bywają błędne (np. text/plain dla .js),
    # a moduły ES wymagają typu JavaScript.
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".css": "text/css",
        ".js": "text/javascript",
        ".json": "application/json",
        ".mjs": "text/javascript",
        ".svg": "image/svg+xml",
        ".wasm": "application/wasm",
        ".woff2": "font/woff2",
    }

    def log_message(self, format: str, *args) -> None:  # noqa: A002 (sygnatura bazowa)
        pass


def bind_first_free(ports, factory):
    """Wiąże serwer z pierwszym wolnym portem; zwraca (port, serwer) albo None."""
    for port in ports:
        try:
            return port, factory(port)
        except OSError:
            continue
    return None


def make_server(site: Path, port: int) -> StaticServer:
    return StaticServer(
        ("127.0.0.1", port), functools.partial(QuietHandler, directory=str(site))
    )


def run_python(python: Path, *args: str, cwd: Path, timeout: float | None = None):
    return subprocess.run(
        [str(python), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=gate.child_env(),
        stdin=subprocess.DEVNULL,
        timeout=timeout,
        check=False,
    )


def copy_working_tree(target: Path) -> None:
    """Kopiuje pliki śledzone i nieśledzone (bez ignorowanych) katalogu roboczego."""
    names = gate.git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    for name in dict.fromkeys(names.split("\0")):
        if not name or not Path(name).is_file():
            continue  # pusty wpis albo usunięty plik śledzony
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(name, destination)


# Odczyt konfiguracji wydania i definicji aktywności interpreterem --python
# (MkDocs i PyYAML). Wynik trafia do pliku JSON, a nie na standardowe wyjście,
# na które mogą pisać wtyczki.
READER = r'''
import json
import sys
from pathlib import Path

import yaml
from mkdocs.utils.yaml import yaml_load

tree, config_name, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
with open(tree / config_name, "rb") as stream:
    config = yaml_load(stream) or {}
definitions = []
for source in sorted((tree / "activities").rglob("*.yaml")):
    document = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        continue
    activities = []
    for activity in document.get("activities") or []:
        if isinstance(activity, dict):
            activities.append({
                "activity_id": activity.get("activity_id"),
                "type": activity.get("type"),
                "section_id": activity.get("section_id"),
                "correct_option_id": activity.get("correct_option_id"),
                "option_ids": [
                    option.get("option_id") for option in activity.get("options") or []
                    if isinstance(option, dict)
                ],
            })
    definitions.append({
        "source": source.relative_to(tree).as_posix(),
        "page": document.get("page"),
        "slot_id": document.get("slot_id"),
        "activities": activities,
    })
theme = config.get("theme") if isinstance(config.get("theme"), dict) else {}
out.write_text(json.dumps({
    "nav": config.get("nav"),
    "use_directory_urls": config.get("use_directory_urls", True),
    "features": list(theme.get("features") or []),
    "definitions": definitions,
}, ensure_ascii=False), encoding="utf-8")
'''


def read_plan(python: Path, tree: Path, workdir: Path) -> Plan:
    reader = workdir / "odczyt.py"
    reader.write_text(READER, encoding="utf-8")
    out = workdir / "plan.json"
    result = run_python(python, str(reader), str(tree), gate.COURSE_CONFIG, str(out), cwd=tree)
    if result.returncode != 0 or not out.is_file():
        last = (result.stderr.strip().splitlines() or ["brak komunikatu"])[-1]
        raise RuntimeError(f"odczyt nav i definicji aktywności nie powiódł się: {last}")
    return build_plan(json.loads(out.read_text(encoding="utf-8")))


# ---------------------------------------------------------------- przeglądarka

# Klucz strony (origin + ścieżka, bez kotwicy), jak pageUrlKey w page-progress.js.
KEY_JS = r"""
const keyOf = (href) => {
  try {
    const url = new URL(href, document.baseURI);
    return url.hash ? null : url.origin + url.pathname;
  } catch (error) {
    return null;
  }
};
const navEntries = (pageKey) => {
  const primary = document.querySelector(".md-sidebar--primary");
  if (!primary) return [];
  const entries = [];
  for (const element of primary.querySelectorAll(
    'a.md-nav__link[href], label.md-nav__link[for="__toc"]')) {
    if (element.tagName === "A"
        && element.closest('[data-md-component="toc"], .md-nav--secondary')) continue;
    const key = element.tagName === "A" ? keyOf(element.getAttribute("href")) : pageKey;
    if (key) entries.push({element, key});
  }
  return entries;
};
const sectionOf = (link) => {
  try {
    const url = new URL(link.getAttribute("href"), document.baseURI);
    return url.hash ? decodeURIComponent(url.hash.slice(1)) : null;
  } catch (error) {
    return null;
  }
};
"""

PAGE_STATE_JS = "({pageKey}) => {" + KEY_JS + r"""
  const box = (element) => {
    const r = element.getBoundingClientRect();
    return {left: r.left, right: r.right, top: r.top, bottom: r.bottom,
            width: r.width, height: r.height};
  };
  const shown = (element) => {
    if (!element) return false;
    const style = getComputedStyle(element);
    const r = element.getBoundingClientRect();
    return style.visibility !== "hidden" && style.display !== "none"
      && r.width > 0 && r.height > 0;
  };
  const rail = (element, attribute) => {
    const marker = element.querySelector("[" + attribute + "]");
    if (!marker) return {rail: false, state: null, railShown: false};
    const visual = marker.querySelector(".interactive-progress-rail__visual") || marker;
    return {rail: true, state: marker.getAttribute("data-state"), railShown: shown(visual)};
  };
  const header = document.querySelector("header.md-header");
  const parts = [...document.querySelectorAll("nav.pn-czesci a.pn-czesci__link")].map((link) => {
    const label = link.querySelector(".pn-czesci__etykieta") || link;
    const r = box(label);
    let clipped = false;
    for (let parent = label.parentElement; parent && parent !== document.documentElement;
         parent = parent.parentElement) {
      const style = getComputedStyle(parent);
      if (style.overflowX === "visible" && style.overflowY === "visible") continue;
      const p = box(parent);
      if (r.left < p.left - 0.5 || r.right > p.right + 0.5
          || r.top < p.top - 0.5 || r.bottom > p.bottom + 0.5) {
        clipped = true;
        break;
      }
    }
    const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    return {
      text: link.textContent.trim(),
      active: link.classList.contains("pn-czesci__link--aktywny"),
      box: r,
      shown: shown(label),
      clipped,
      covered: !(hit && link.contains(hit)),
      truncated: label.clientWidth > 0 && label.scrollWidth > label.clientWidth + 1,
    };
  });
  const navLinks = navEntries(pageKey).map(({element, key}) => ({
    tag: element.tagName.toLowerCase(), key,
    ...rail(element, "data-interactive-page-progress"),
  }));
  const tocLinks = [];
  for (const toc of document.querySelectorAll('[data-md-component="toc"]')) {
    for (const link of toc.querySelectorAll("a[href]")) {
      const section = sectionOf(link);
      if (section) {
        tocLinks.push({section, secondary: !!link.closest(".md-sidebar--secondary"),
                       ...rail(link, "data-interactive-section-progress")});
      }
    }
  }
  const de = document.documentElement;
  return {
    url: location.href,
    overflow: Math.max(de.scrollWidth - de.clientWidth,
                       document.body.scrollWidth - document.body.clientWidth),
    header: header ? box(header) : null,
    viewport: innerWidth,
    parts,
    slots: [...document.querySelectorAll("[data-activity-slot]")]
      .map((slot) => slot.getAttribute("data-activity-slot")),
    activities: [...document.querySelectorAll("section.interactive-activity")]
      .map((section) => ({id: section.dataset.activityId, state: section.dataset.progressState})),
    marked: [...document.querySelectorAll("[data-activity-section]")]
      .map((element) => ({tag: element.tagName.toLowerCase(), id: element.id,
                          value: element.getAttribute("data-activity-section")})),
    navLinks,
    tocLinks,
    sectionRails: document.querySelectorAll("[data-interactive-section-progress]").length,
  };
}
"""

# Warstwa skończyła pracę: slot strony ma oczekiwaną liczbę aktywności, slot
# poprzedniej strony zniknął (nawigacja natychmiastowa), a każdy odnośnik do
# strony z ćwiczeniami w nawigacji ma wskaźnik postępu. Porównania „!= null”
# są celowe: wait_for_function przekazuje None z Pythona jako undefined,
# a evaluate jako null (Playwright 1.63).
READY_JS = "({slot, activities, goneSlot, pageKeys}) => {" + KEY_JS + r"""
  const slotted = (id) => document.querySelector(
    '[data-activity-slot="' + CSS.escape(id) + '"]');
  if (goneSlot != null && slotted(goneSlot)) return false;
  if (slot != null) {
    const host = slotted(slot);
    if (!host || host.querySelectorAll("section.interactive-activity").length < activities) {
      return false;
    }
  }
  return navEntries(null).every(({element, key}) => element.tagName !== "A"
    || !pageKeys.includes(key)
    || element.querySelector("[data-interactive-page-progress]") !== null);
}
"""

POSITION_JS = r"""
(id) => {
  const heading = document.getElementById(id);
  const header = document.querySelector("header.md-header");
  if (!heading) return null;
  return {
    top: heading.getBoundingClientRect().top,
    header: header ? header.getBoundingClientRect().bottom : 0,
    viewport: innerHeight,
  };
}
"""

ANCHOR_JS = r"""
async (id) => {
  const frame = () => new Promise((resolve) => requestAnimationFrame(() => resolve()));
  location.hash = "";
  await frame();
  await frame();
  location.hash = id;
  await new Promise((resolve) => setTimeout(resolve, 300));
  return (""" + POSITION_JS + r""")(id);
}
"""

DRAWER_JS = "({pageKey, sections}) => {" + KEY_JS + r"""
  const visible = (marker) => {
    if (!marker) return false;
    const visual = marker.querySelector(".interactive-progress-rail__visual") || marker;
    const style = getComputedStyle(visual);
    const r = visual.getBoundingClientRect();
    return style.visibility !== "hidden" && style.display !== "none" && r.width > 0
      && r.height > 0 && r.left >= 0 && r.right <= innerWidth;
  };
  const page = navEntries(pageKey).some(({element, key}) => key === pageKey
    && visible(element.querySelector("[data-interactive-page-progress]")));
  const links = [...document.querySelectorAll(
    '.md-sidebar--primary [data-md-component="toc"] a[href]')];
  const result = {};
  for (const section of sections) {
    result[section] = links.some((link) => sectionOf(link) === section
      && visible(link.querySelector("[data-interactive-section-progress]")));
  }
  return {page, sections: result};
}
"""

RAILS_JS = "({pageKey}) => {" + KEY_JS + r"""
  const page = navEntries(pageKey)
    .filter(({element, key}) => key === pageKey)
    .map(({element}) => element.querySelector("[data-interactive-page-progress]"))
    .filter((marker) => marker !== null)
    .map((marker) => marker.getAttribute("data-state"));
  const sections = {};
  for (const link of document.querySelectorAll('[data-md-component="toc"] a[href]')) {
    const marker = link.querySelector("[data-interactive-section-progress]");
    const section = marker ? sectionOf(link) : null;
    if (section) {
      (sections[section] = sections[section] || []).push(marker.getAttribute("data-state"));
    }
  }
  return {page, sections};
}
"""

ACTIVITY_STATE_JS = r"""
(id) => {
  const section = [...document.querySelectorAll("section.interactive-activity")]
    .find((element) => element.dataset.activityId === id);
  return section ? section.dataset.progressState : null;
}
"""

COMPLETED_JS = "(id) => (" + ACTIVITY_STATE_JS + ")(id) === 'completed'"

TAG_LINK_JS = "(targetKey) => {" + KEY_JS + r"""
  const entry = navEntries(null).find(({element, key}) => element.tagName === "A"
    && key === targetKey);
  if (!entry) return false;
  entry.element.setAttribute("data-sprawdz-wydanie-cel", "");
  return true;
}
"""

INSTANT_FLAG = "bez przeładowania"


def slug(url: str) -> str:
    text = url.strip("/").replace("/", "_").removesuffix(".html")
    return text or "strona-glowna"


def first_line(error: BaseException) -> str:
    text = getattr(error, "message", None) or str(error)
    return (text.strip().splitlines() or [type(error).__name__])[0]


class VariantRun:
    """Przebieg kontroli w jednym wariancie okna (nowy kontekst przeglądarki)."""

    def __init__(self, browser, variant: Variant, plan: Plan, base: str, report: Report,
                 shots: Path | None, errors: tuple[type, type]) -> None:
        self.variant = variant
        self.plan = plan
        self.base = base
        self.report = report
        self.shots = shots
        self.error, self.timeout = errors  # playwright.sync_api.Error, TimeoutError
        self.context = browser.new_context(
            viewport={"width": variant.width, "height": variant.height},
            color_scheme=variant.scheme,
            device_scale_factor=1,
        )
        self.page = self.context.new_page()
        self.page.set_default_timeout(ACTION_TIMEOUT)
        self.page.set_default_navigation_timeout(NAVIGATION_TIMEOUT)
        self.where = "/"
        self.events: list[tuple[str, str, str, str | None]] = []
        self.page.on("console", self._console)
        self.page.on("pageerror", lambda error: self._event("pageerror", str(error), None))
        self.page.on(
            "requestfailed",
            lambda request: self._event(
                "requestfailed", f"{request.failure} {request.url}", request.url
            ),
        )
        self.page.on("response", self._response)

    # zdarzenia konsoli i sieci

    def _console(self, message) -> None:
        self._event(message.type, message.text, (message.location or {}).get("url"))

    def _response(self, response) -> None:
        if response.status >= 400:
            self._event("http", f"HTTP {response.status} {response.url}", response.url)

    def _event(self, kind: str, text: str, url: str | None) -> None:
        self.events.append((self.where, kind, text, url))

    def flush_events(self) -> None:
        """Ocenia zdarzenia kroku; powtórzone zdarzenie zgłasza raz z liczbą wystąpień."""
        self.report.mark("konsola", self.variant)
        labels = {
            "pageerror": "błąd strony", "requestfailed": "nieudane żądanie",
            "http": "odpowiedź serwera", "error": "błąd konsoli",
            "assert": "asercja konsoli", "warning": "ostrzeżenie konsoli",
        }
        counted: dict[tuple[str, str, str | None], int] = {}
        for where, kind, text, url in self.events:
            outcome = classify(kind, text, url, self.base)
            if outcome is not None:
                key = (where, f"{labels.get(kind, kind)}: {text}", outcome)
                counted[key] = counted.get(key, 0) + 1
        for (where, label, outcome), count in counted.items():
            if count > 1:
                label += f" (wystąpień: {count})"
            if outcome == "błąd":
                self.report.problem("konsola", self.variant, where, label)
            else:
                self.report.note(f"[{self.variant.label}] {where}: {label}")
        self.events.clear()

    # pomocnicze

    def key(self, src: str) -> str:
        return self.base + self.plan.urls[src]

    def path(self, src: str) -> str:
        return self.plan.urls[src] or "/"

    @property
    def exercise_keys(self) -> set[str]:
        return {self.key(page.src) for page in self.plan.exercise_pages}

    def exercise(self, src: str | None) -> ExercisePage | None:
        return next((page for page in self.plan.exercise_pages if page.src == src), None)

    def shot(self, name: str, locator=None) -> None:
        if self.shots is None:
            return
        path = self.shots / f"{self.variant.scheme}-{self.variant.width}-{name}.png"
        try:
            (locator or self.page).screenshot(path=str(path))
        except self.error as error:
            self.report.note(f"nie zapisano zrzutu {path.name}: {first_line(error)}")

    def wait_ready(self, check: str, page: ExercisePage | None,
                   gone: ExercisePage | None = None) -> bool:
        try:
            self.page.wait_for_load_state("networkidle", timeout=LAYER_TIMEOUT)
        except self.timeout:
            pass  # o gotowości rozstrzyga warunek warstwy
        try:
            self.page.wait_for_function(
                READY_JS,
                arg={
                    "slot": page.slot_id if page else None,
                    "activities": len(page.activities) if page else 0,
                    "goneSlot": gone.slot_id if gone else None,
                    "pageKeys": sorted(self.exercise_keys),
                },
                timeout=LAYER_TIMEOUT,
            )
        except self.timeout:
            self.report.problem(
                check, self.variant, self.where,
                f"warstwa ćwiczeń nie zakończyła pracy w ciągu {LAYER_TIMEOUT // 1000} s",
            )
            return False
        self.page.wait_for_timeout(300)
        return True

    def open(self, src: str, check: str, anchor: str = "") -> bool:
        self.where = self.path(src)
        self.page.goto(
            self.base + self.plan.urls[src] + (f"#{anchor}" if anchor else ""),
            wait_until="domcontentloaded",
        )
        return self.wait_ready(check, self.exercise(src))

    def state(self, src: str) -> dict:
        return self.page.evaluate(PAGE_STATE_JS, {"pageKey": self.key(src)})

    def common(self, src: str, state: dict) -> None:
        """Menu części i poziome przewijanie: kontrole każdej strony."""
        if self.plan.pill_menu:
            self.report.mark("menu", self.variant)
            expected = [title for title, _ in self.plan.parts]
            for problem in check_parts(state, expected, self.plan.owners.get(src)):
                self.report.problem("menu", self.variant, self.where, problem)
        self.report.mark("przewijanie", self.variant)
        for problem in check_overflow(state):
            self.report.problem("przewijanie", self.variant, self.where, problem)

    def open_drawer(self) -> None:
        if not self.page.evaluate("() => document.getElementById('__drawer')?.checked === true"):
            self.page.locator('label.md-header__button[for="__drawer"]').first.click()
            self.page.wait_for_timeout(600)

    # kontrole

    def exercise_page(self, page: ExercisePage) -> None:
        first = page.sections[0] if page.sections else ""
        self.open(page.src, "aktywnosci", first)
        state = self.state(page.src)
        self.common(page.src, state)
        self.report.extend(
            check_exercise_page(state, page, self.key(page.src), self.exercise_keys,
                                self.variant.wide),
            self.variant, self.where,
        )
        self.shot(slug(page.url))
        self.anchors(page)
        self.solve(page)
        if not self.variant.wide:
            self.drawer(page)

    def anchors(self, page: ExercisePage) -> None:
        """Pierwszą kotwicę zawiera adres otwarcia strony, kolejne ustawiamy w location.hash."""
        self.report.mark("kotwice", self.variant)
        for index, section_id in enumerate(page.sections):
            script = POSITION_JS if index == 0 else ANCHOR_JS
            problem = check_anchor(self.page.evaluate(script, section_id), section_id)
            if problem:
                self.report.problem("kotwice", self.variant, self.where, problem)

    def rails_problems(self, page: ExercisePage, quiz: Activity, moment: str) -> list[str]:
        """Porównuje stany wskaźników z oczekiwanymi; czeka do 5 s na aktualizację."""
        page_state = rail_state(1, len(page.activities))
        section_state = (
            rail_state(1, page.section_total(quiz.section_id))
            if quiz.section_id is not None else None
        )
        deadline = time.monotonic() + 5
        while True:
            rails = self.page.evaluate(RAILS_JS, {"pageKey": self.key(page.src)})
            problems = []
            if not rails["page"] or set(rails["page"]) != {page_state}:
                problems.append(
                    f"{moment}: wskaźnik strony ma stan {rails['page'] or 'brak'}, "
                    f"oczekiwano {page_state!r}"
                )
            if section_state is not None:
                states = rails["sections"].get(quiz.section_id) or []
                if not states or set(states) != {section_state}:
                    problems.append(
                        f"{moment}: wskaźnik sekcji #{quiz.section_id} ma stan "
                        f"{states or 'brak'}, oczekiwano {section_state!r}"
                    )
            if not problems or time.monotonic() > deadline:
                return problems
            self.page.wait_for_timeout(200)

    def solve(self, page: ExercisePage) -> None:
        self.report.mark("rozwiazanie", self.variant)
        quiz = page.quiz
        if quiz is None:
            self.report.note(
                f"{page.src}: brak pytania single_choice z poprawną odpowiedzią wśród "
                "wariantów; rozwiązania na tej stronie nie sprawdzono"
            )
            return
        problem = functools.partial(self.report.problem, "rozwiazanie", self.variant, self.where)
        selector = f'section.interactive-activity[data-activity-id="{quiz.activity_id}"]'
        try:
            group = self.page.locator("details.interactive-activity-group").first
            if not group.evaluate("(element) => element.open"):
                self.page.locator("summary.interactive-activity-group__summary").first.click()
            section = self.page.locator(selector)
            section.locator(f'input[type="radio"][value="{quiz.correct_option_id}"]').check()
            section.locator('button[type="submit"]').click()
            self.page.wait_for_function(COMPLETED_JS, arg=quiz.activity_id)
        except self.error as error:
            problem(f"{quiz.activity_id}: nie udało się rozwiązać pytania ({first_line(error)})")
            return
        for message in self.rails_problems(page, quiz, "po rozwiązaniu"):
            problem(message)
        self.shot(f"{slug(page.url)}-rozwiazane", self.page.locator(selector))
        self.page.reload(wait_until="domcontentloaded")
        if not self.wait_ready("rozwiazanie", page):
            return
        after = self.page.evaluate(ACTIVITY_STATE_JS, quiz.activity_id)
        if after != "completed":
            problem(f"{quiz.activity_id}: po przeładowaniu stan {after!r}, oczekiwano 'completed'")
        for message in self.rails_problems(page, quiz, "po przeładowaniu"):
            problem(message)

    def drawer(self, page: ExercisePage) -> None:
        """Wąskie okno: wskaźniki strony i sekcji widoczne w szufladzie nawigacji."""
        problem = functools.partial(self.report.problem, "wskazniki", self.variant, self.where)
        try:
            self.open_drawer()
            seen = self.page.evaluate(DRAWER_JS, {"pageKey": self.key(page.src), "sections": []})
            if not seen["page"]:
                problem("w szufladzie nawigacji wskaźnik postępu bieżącej strony jest niewidoczny")
            self.shot(f"{slug(page.url)}-szuflada")
            toc = self.page.locator('.md-sidebar--primary label.md-nav__link[for="__toc"]')
            if page.sections and toc.count():
                toc.first.click()
                self.page.wait_for_timeout(600)
                seen = self.page.evaluate(
                    DRAWER_JS, {"pageKey": self.key(page.src), "sections": page.sections}
                )
                for section_id, visible in seen["sections"].items():
                    if not visible:
                        problem(
                            f"w szufladzie nawigacji wskaźnik postępu sekcji #{section_id} "
                            "jest niewidoczny"
                        )
                self.shot(f"{slug(page.url)}-szuflada-spis")
        except self.error as error:
            problem(f"nie udało się otworzyć szuflady nawigacji ({first_line(error)})")

    def plain_page(self, src: str) -> None:
        self.report.mark("bez-cwiczen", self.variant)
        self.open(src, "bez-cwiczen")
        state = self.state(src)
        self.common(src, state)
        self.report.extend(check_plain_page(state, self.key(src), self.exercise_keys),
                           self.variant, self.where)
        self.shot(slug(self.plan.urls[src]))

    def instant(self) -> None:
        """Nawigacja natychmiastowa: strona → strona z ćwiczeniami → strona bez ćwiczeń."""
        self.report.mark("natychmiastowa", self.variant)
        start, target, leave = self.plan.route
        self.open(start, "natychmiastowa")
        self.page.evaluate(f"() => {{ window.__sprawdzWydanie = {json.dumps(INSTANT_FLAG)}; }}")
        current = start
        for destination in (target, leave):
            if destination is None:
                continue
            self.where = f"{self.path(current)} → {self.path(destination)}"
            if not self.follow(destination):
                return
            page, previous = self.exercise(destination), self.exercise(current)
            if not self.wait_ready("natychmiastowa", page, previous):
                return
            problem = functools.partial(
                self.report.problem, "natychmiastowa", self.variant, self.where
            )
            if self.page.evaluate("() => window.__sprawdzWydanie") != INSTANT_FLAG:
                problem("przejście przeładowało stronę zamiast nawigacji natychmiastowej")
            state = self.state(destination)
            if page:
                found = check_exercise_page(state, page, self.key(destination),
                                            self.exercise_keys, self.variant.wide)
            else:
                found = check_plain_page(state, self.key(destination), self.exercise_keys)
            for messages in found.values():
                for message in messages:
                    problem(message)
            self.shot(f"natychmiastowa-{slug(self.plan.urls[destination])}")
            current = destination

    def follow(self, destination: str) -> bool:
        """Klika odnośnik nawigacji do strony destination (w wąskim oknie w szufladzie)."""
        problem = functools.partial(self.report.problem, "natychmiastowa", self.variant, self.where)
        try:
            if not self.variant.wide:
                self.open_drawer()
            if not self.page.evaluate(TAG_LINK_JS, self.key(destination)):
                problem("w nawigacji nie ma odnośnika do strony docelowej")
                return False
            link = self.page.locator("[data-sprawdz-wydanie-cel]").first
            try:
                link.click(timeout=3000)
            except self.error:
                link.dispatch_event("click")  # odnośnik w zwiniętej sekcji nawigacji
            target = self.key(destination)
            self.page.wait_for_url(lambda url: url.split("#")[0] == target)
        except self.error as error:
            problem(f"przejście nie powiodło się ({first_line(error)})")
            return False
        return True

    def run(self) -> None:
        print(f"\n{self.variant.label} px ({self.variant.width}×{self.variant.height})", flush=True)
        steps = [
            (f"strona z ćwiczeniami {self.path(page.src)}",
             functools.partial(self.exercise_page, page))
            for page in self.plan.exercise_pages
        ]
        steps += [
            (f"strona bez ćwiczeń {self.path(src)}", functools.partial(self.plain_page, src))
            for src in self.plan.plain_pages
        ]
        if self.plan.route:
            steps.append(("nawigacja natychmiastowa", self.instant))
        try:
            for title, step in steps:
                print(f"  {title}", flush=True)
                try:
                    step()
                except self.error as error:
                    self.report.problem(
                        "konsola", self.variant, self.where,
                        f"kontrola przerwana błędem przeglądarki: {first_line(error)}",
                    )
                self.flush_events()
        finally:
            self.context.close()


def run_browser(browser, plan: Plan, base: str, report: Report, shots: Path | None,
                errors: tuple[type, type]) -> None:
    if not plan.pill_menu:
        report.note(
            "motyw nie włącza menu części (navigation.tabs i navigation.tabs.sticky); "
            "kontrolę menu pominięto"
        )
    if not plan.route:
        report.note(
            "nawigacja natychmiastowa jest wyłączona albo brak stron do przejścia; "
            "kontrolę przejścia pominięto"
        )
    for variant in VARIANTS:
        VariantRun(browser, variant, plan, base, report, shots, errors).run()


# ---------------------------------------------------------------- całość


def environment_problem(message: str) -> int:
    print(f"{message}; kontroli nie przeprowadzono (kod 2).", file=sys.stderr)
    return EXIT_ENVIRONMENT


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Kontrola wydania kursowego w przeglądarce (Microsoft Edge, Playwright)."
    )
    parser.add_argument(
        "--python", required=True,
        help="interpreter środowiska książki (mkdocs-material), którym budujemy wydanie",
    )
    parser.add_argument(
        "--katalog-roboczy", action="store_true",
        help="buduje kopię katalogu roboczego zamiast commitu HEAD (wynik roboczy)",
    )
    parser.add_argument("--zrzuty", metavar="KATALOG", help="katalog na zrzuty ekranu")
    args = parser.parse_args(argv)

    try:
        root = Path(gate.git("rev-parse", "--show-toplevel").strip())
        head = gate.git("rev-parse", "HEAD").strip()
        branch = gate.git("rev-parse", "--abbrev-ref", "HEAD").strip()
    except (gate.GateError, OSError) as error:
        return environment_problem(f"Kontrola wymaga repozytorium git: {error}")
    os.chdir(root)
    print(f"Kontrola wydania kursowego w przeglądarce: {branch} @ {head[:7]}")

    python = Path(args.python)
    try:
        probe = run_python(python, "-c", "import mkdocs, material, yaml", cwd=root, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as error:
        return environment_problem(f"Nie można uruchomić interpretera --python {python}: {error}")
    if probe.returncode != 0:
        return environment_problem(
            f"Interpreter --python {python} nie ma pakietów książki "
            "(mkdocs, mkdocs-material, PyYAML)"
        )
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        from playwright.sync_api import sync_playwright
    except ImportError:
        return environment_problem(f"Brak modułu playwright; uruchamiamy: {COMMAND}")

    shots = Path(args.zrzuty).resolve() if args.zrzuty else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    report = Report()
    workdir = Path(tempfile.mkdtemp(prefix="kurs-wydanie-"))
    site = workdir / "serwis"
    exported: Path | None = None
    bound = bind_first_free(PORTS, functools.partial(make_server, site))
    if bound is None:
        shutil.rmtree(workdir, ignore_errors=True)
        return environment_problem(
            f"Brak wolnego portu w zakresie {PORTS.start}–{PORTS.stop - 1}"
        )
    port, server = bound
    base = f"http://127.0.0.1:{port}/"
    serving = False
    try:
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(channel="msedge")
            except PlaywrightError as error:
                return environment_problem(
                    f"Nie można uruchomić Microsoft Edge (Playwright, kanał msedge): "
                    f"{first_line(error)}"
                )
            try:
                print(f"Przeglądarka: Microsoft Edge {browser.version}; serwer: {base}")
                if args.katalog_roboczy:
                    tree = workdir / "drzewo"
                    copy_working_tree(tree)
                    print("Sprawdzany stan: katalog roboczy z niezatwierdzonymi zmianami "
                          "(wynik roboczy)")
                else:
                    exported = gate.export_commit(head)
                    tree = exported / "drzewo"
                    print(f"Sprawdzany stan: commit {head[:7]} (czysty eksport drzewa)")
                (tree / CHECK_CONFIG).write_text(
                    f"INHERIT: {gate.COURSE_CONFIG}\nsite_url: {base}\n", encoding="utf-8"
                )
                print(f"  budowanie: wydanie kursowe ({gate.COURSE_CONFIG}, site_url {base})…",
                      flush=True)
                built = run_python(
                    python, "-m", "mkdocs", "build", "--strict", "-f", CHECK_CONFIG,
                    "-d", str(site), cwd=tree, timeout=BUILD_TIMEOUT,
                )
                if built.returncode != 0:
                    report.build_failed = True
                    report.build = f"BŁĄD (kod {built.returncode})"
                    print(f"  BŁĄD   mkdocs build --strict -f {gate.COURSE_CONFIG}: "
                          f"kod {built.returncode}")
                    gate.print_tail(built.stdout + built.stderr)
                else:
                    pages = len(list(site.rglob("*.html")))
                    report.build = "OK — " + gate.plural(pages, "strona", "strony", "stron")
                    plan = read_plan(python, tree, workdir)
                    print(
                        f"  stron: {pages}; strony z ćwiczeniami: {len(plan.exercise_pages)}; "
                        f"strony bez ćwiczeń w próbie: {len(plan.plain_pages)}"
                    )
                    threading.Thread(target=server.serve_forever, daemon=True).start()
                    serving = True
                    run_browser(browser, plan, base, report, shots,
                                (PlaywrightError, PlaywrightTimeout))
            finally:
                browser.close()
    except (gate.GateError, RuntimeError, subprocess.TimeoutExpired) as error:
        return environment_problem(f"Kontroli nie można było dokończyć: {error}")
    except Exception:  # noqa: BLE001 — błąd narzędzia nie może wyglądać na wynik kontroli
        traceback.print_exc()
        return environment_problem("Kontrolę przerwał błąd narzędzia (ślad wywołań wyżej)")
    finally:
        if serving:
            server.shutdown()
        server.server_close()
        if exported is not None:
            shutil.rmtree(exported, ignore_errors=True)
        shutil.rmtree(workdir, ignore_errors=True)

    print()
    state = "katalog roboczy" if args.katalog_roboczy else f"commit {head[:7]}"
    print(f"Podsumowanie: {branch} @ {head[:7]} ({state}), {gate.COURSE_CONFIG}, port {port}")
    print(f"Build --strict wydania kursowego: {report.build}")
    for line in summary_lines(report):
        print(line)
    code, sentence = verdict(report, head, args.katalog_roboczy)
    print(sentence)
    return code


if __name__ == "__main__":
    sys.exit(main())
