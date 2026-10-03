"""Bramka jakości gałęzi ćwiczeń (cwiczenia, fala/*, platform/*, sync/*).

Uruchamiamy ją z katalogu roboczego gałęzi ćwiczeń interpreterem, w którym
zainstalowano zależności książki (mkdocs-material); etap G6 wymaga ponadto
Node.js 22 lub nowszego (zalecany 24):

    python kurs/tools/gate.py [--book REF] [--pomin-testy]
                              [--katalog-roboczy | --przed-scaleniem]
    python kurs/tools/gate.py --zatwierdz-aktualnosc [--book REF]

--book             gałąź książki, względem której wyznaczamy merge-base
                   (domyślnie dev; podczas synchronizacji origin/dev).
--pomin-testy      pomija etap G6 (testy unittest i node).
--katalog-roboczy  sprawdza katalog roboczy razem z niezatwierdzonymi zmianami
                   zamiast commitu HEAD (szybka pętla robocza).
--przed-scaleniem  uruchamia wyłącznie etap G1 przed scaleniem książki
                   w gałęzi sync/*, łącznie z próbnym scaleniem.
--zatwierdz-aktualnosc
                   nie uruchamia etapów: po przeglądzie aktywności zapisuje
                   w kurs/aktualnosc.json odciski powiązanych sekcji książki
                   w stanie merge-base(HEAD, REF) i wypisuje zmiany pliku.
                   Definicje aktywności odczytuje z katalogu roboczego.

Bez --katalog-roboczy bramka ocenia commit HEAD: etapy G2–G7 działają na
czystym eksporcie jego drzewa w katalogu tymczasowym, dlatego niezatwierdzone
i nieśledzone pliki nie wpływają na wynik.

Etapy (każdy jest blokujący):
  G1  zasada wyłącznego dodawania: względem merge-base(HEAD, REF) gałąź ćwiczeń
      wyłącznie dodaje ścieżki z listy dozwolonej, a commit zawiera podstawowe
      pliki warstwy; książka (REF i merge-base) nie zawiera ścieżek z tej
      listy; ostatnie scalenie książki nie usunęło plików ćwiczeń; gałąź nie
      scaliła stanu książki spoza REF; żadna lokalna gałąź nie nosi nazwy
      śledzonej ścieżki; katalog roboczy nie zawiera niezatwierdzonych zmian
      plików książki;
  G2  nakładka mkdocs.kurs.yml dziedziczy mkdocs.yml, a każda jej lista zawiera
      wszystkie pozycje odpowiedniej listy książki (MkDocs zastępuje listy);
  G3  schemat definicji activities/**/*.yaml oraz wiązania: strona istnieje,
      a section_id jest identyfikatorem nagłówka h2–h6 wygenerowanym na tej
      stronie i nie ma sufiksu deduplikacji; przy zerwanym wiązaniu etap
      zestawia nagłówki strony sprzed ostatniego scalenia książki z obecnymi
      i wskazuje następcę dawnego nagłówka; zmiany wiązań względem tego stanu
      wypisuje razem z tekstami nagłówków;
  G4  aktualność: odcisk treści każdej powiązanej sekcji (od jej nagłówka do
      następnego nagłówka tego samego lub wyższego poziomu, a przy section_id:
      null cała strona) jest równy odciskowi zapisanemu przy ostatnim
      przeglądzie w kurs/aktualnosc.json; zmieniona treść, zmienione wiązanie
      oraz nowe i usunięte aktywności wymagają przeglądu, a etap pokazuje
      różnicę treści sekcji od stanu książki z przeglądu;
  G5  rozwiązanie wzorcowe i rozwiązania alternatywne każdego zadania code
      wypisują w CPython dokładnie checker.expected_lines, a starter_code ich
      nie wypisuje; każde pytanie single_choice ma blok verify, który wypisuje
      dokładnie etykietę poprawnej odpowiedzi, albo figuruje z uzasadnieniem
      w kurs/bez-weryfikacji.txt;
  G6  testy unittest (tests/ i kurs/tools/) oraz node --test (tests/interactive/);
  G7  buildy --strict książki (mkdocs.yml) i wydania kursowego (mkdocs.kurs.yml)
      do katalogu tymczasowego; książka nie może zawierać znaczników ćwiczeń
      ani ładować warstwy, a wydanie kursowe musi zawierać manifest i sloty.

Etapu G8 (liczby kontrolne i metadane wydania) jeszcze nie ma; numeracja
pozostaje zgodna z planem.

Kod wyjścia:
  0  pełna bramka przeszła dla commitu HEAD (wynik do odbioru);
  1  co najmniej jeden etap nie przeszedł;
  2  błąd wywołania (np. brak repozytorium git albo gałęzi książki);
  3  uruchomione etapy przeszły, lecz wynik jest częściowy lub roboczy
     (--pomin-testy, --katalog-roboczy, --przed-scaleniem) i nie służy do
     odbioru.
Z opcją --zatwierdz-aktualnosc: 0 — plik zapisano albo był aktualny;
1 — wiązania lub definicje wymagają poprawy i pliku nie zmieniono;
2 — błąd wywołania.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

sys.dont_write_bytecode = True

ALLOWED_PREFIXES = (
    "activities/",
    "docs/javascripts/interactive/",
    "tests/interactive/",
    "kurs/",
    # Skill Claude Code, który przeprowadza synchronizację w katalogu ćwiczeń.
    ".claude/skills/synchronizuj-cwiczenia/",
)
ALLOWED_FILES = frozenset(
    {
        "scripts/build_activities.py",
        "docs/stylesheets/interactive.css",
        "tests/test_build_activities.py",
        "mkdocs.kurs.yml",
        ".github/workflows/kurs.yml",
    }
)
# Bez tych plików gałąź nie jest gałęzią ćwiczeń, nawet jeśli reszta się zgadza.
CORE_FILES = ("kurs/README.md", "kurs/tools/gate.py", "mkdocs.kurs.yml")
BOOK_CONFIG = "mkdocs.yml"
COURSE_CONFIG = "mkdocs.kurs.yml"
EXEMPTIONS_FILE = "kurs/bez-weryfikacji.txt"
LOCK_FILE = "kurs/aktualnosc.json"
# Wersja algorytmu odcisku sekcji (etap G4); zmiana algorytmu ją podnosi.
FINGERPRINT_VERSION = 1
DIFF_LINES = 40  # tyle wierszy różnicy treści G4 pokazuje dla jednego wiązania
MANIFEST = Path("assets") / "generated" / "activities.json"
LAYER_SCRIPT = "javascripts/interactive/bootstrap.js"
EXERCISE_BRANCHES = ("cwiczenia",)
EXERCISE_PREFIXES = ("fala/", "platform/", "sync/")
# Python-Markdown dopisuje _1, _2… do identyfikatora, który już istnieje na stronie.
DEDUPLICATED_ID = re.compile(r"^(.+)_([0-9]+)$")
RUN_TIMEOUT = 20  # sekundy na jedno uruchomienie kodu w etapie G5
# Wzorce plików w node --test wymagają Node.js 21; 22 to najstarsza linia LTS.
NODE_MINIMUM = 22
LISTED_PATHS = 8  # tyle ścieżek wymieniamy w jednym komunikacie

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2
EXIT_PARTIAL = 3


class GateError(Exception):
    """Błąd polecenia pomocniczego (git), który uniemożliwia dany etap."""


@dataclass
class Stage:
    code: str
    title: str
    problems: list[str] = field(default_factory=list)
    detail: str = ""
    skipped: bool = False

    def start(self) -> None:
        print(f"\n{self.code}  {self.title}", flush=True)

    def problem(self, message: str) -> None:
        self.problems.append(message)
        print(f"  BŁĄD   {message}", flush=True)

    @staticmethod
    def note(message: str) -> None:
        print(f"  uwaga  {message}", flush=True)

    @property
    def result(self) -> str:
        if self.skipped:
            return "POMINIĘTO"
        return "OK" if not self.problems else f"BŁĄD ({len(self.problems)})"


@dataclass(frozen=True)
class BookMerge:
    """Scalenie, które wprowadziło do gałęzi ćwiczeń nowy stan książki."""

    commit: str
    exercise_parent: str


@dataclass
class Context:
    book: str
    head: str
    tree: Path
    working_tree: bool = False
    trial_merge: bool = False
    base: str | None = None
    book_merge: BookMerge | None = None
    dirty: int = 0
    activity_pages: set[str] = field(default_factory=set)


def is_allowed(path: str) -> bool:
    return path in ALLOWED_FILES or path.startswith(ALLOWED_PREFIXES)


def plural(count: int, one: str, few: str, many: str) -> str:
    """Dobiera polską formę liczebnika: 1 plik, 2 pliki, 5 plików."""
    if count == 1:
        return f"{count} {one}"
    if count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        return f"{count} {few}"
    return f"{count} {many}"


def listing(paths: list[str]) -> str:
    """Wymienia kilka pierwszych ścieżek i liczbę pozostałych."""
    shown = ", ".join(paths[:LISTED_PATHS])
    rest = len(paths) - LISTED_PATHS
    if rest > 0:
        shown += " i " + plural(rest, "kolejna", "kolejne", "kolejnych")
    return shown


def child_env() -> dict[str, str]:
    return dict(
        os.environ,
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONIOENCODING="utf-8",
        PYTHONUTF8="1",
    )


def run(command: list[str], *, cwd: Path, timeout: float | None = None):
    """Uruchamia polecenie pomocnicze; kod wyjścia ocenia wywołujący."""
    return subprocess.run(
        command,
        check=False,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=child_env(),
        stdin=subprocess.DEVNULL,
        timeout=timeout,
    )


def git_run(*args: str, env: dict[str, str] | None = None):
    return subprocess.run(
        ["git", "-c", "core.quotePath=false", *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        stdin=subprocess.DEVNULL,
    )


def git(*args: str, check: bool = True, env: dict[str, str] | None = None) -> str:
    result = git_run(*args, env=env)
    if check and result.returncode != 0:
        raise GateError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def is_ancestor(commit: str, ref: str) -> bool:
    result = git_run("merge-base", "--is-ancestor", commit, ref)
    if result.returncode not in (0, 1):
        raise GateError(
            f"git merge-base --is-ancestor {commit} {ref}: {result.stderr.strip()}"
        )
    return result.returncode == 0


def allowed_paths_in(commit: str) -> list[str]:
    """Zwraca śledzone w commicie ścieżki należące do listy dozwolonej ćwiczeń."""
    names = git("ls-tree", "-r", "--name-only", "-z", commit).split("\0")
    return [name for name in names if name and is_allowed(name)]


def name_status(*args: str) -> list[tuple[str, str]]:
    """Zwraca pary (status, ścieżka) z wyjścia git diff --name-status -z."""
    fields = git("diff", "--name-status", "--no-renames", "-z", *args).split("\0")
    return [
        (fields[index], fields[index + 1])
        for index in range(0, len(fields) - 1, 2)
        if fields[index]
    ]


def working_tree_changes() -> list[tuple[str, str]]:
    """Zwraca pary (kod, ścieżka) niezatwierdzonych i nieśledzonych zmian."""
    entries = git("status", "--porcelain=v1", "--untracked-files=all", "-z").split("\0")
    changes = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        code, path = entry[:2], entry[3:]
        if code[0] in "RC":
            index += 1  # pomijamy starą nazwę przenoszonego pliku
        changes.append((code, path))
    return changes


def export_commit(commit: str) -> Path:
    """Odtwarza drzewo commitu w katalogu tymczasowym (podkatalog drzewo/).

    Korzysta z tymczasowego pliku indeksu, więc nie zmienia indeksu, katalogu
    roboczego ani listy katalogów roboczych repozytorium.
    """
    workdir = Path(tempfile.mkdtemp(prefix="kurs-gate-commit-"))
    env = dict(os.environ, GIT_INDEX_FILE=str(workdir / "index"))
    try:
        git("read-tree", commit, env=env)
        git(
            "checkout-index", "--all", "--force",
            f"--prefix={(workdir / 'drzewo').as_posix()}/",
            env=env,
        )
    except GateError:
        shutil.rmtree(workdir, ignore_errors=True)
        raise
    return workdir


def print_tail(text: str, lines: int = 25) -> None:
    for line in text.strip().splitlines()[-lines:]:
        print(f"         | {line}")


# ---------------------------------------------------------------- G1


def exercise_side_merges(book: str) -> list[list[str]]:
    """Commity scalające osiągalne z HEAD, a nieosiągalne z książki.

    Każdy element to [scalenie, rodzic1, rodzic2, …]; kolejność topologiczna
    (najpierw najnowsze), więc późniejsze scalenie poprzedza wcześniejsze.
    """
    output = git("rev-list", "--merges", "--topo-order", "--parents", f"{book}..HEAD")
    return [line.split() for line in output.splitlines() if line.strip()]


def find_book_merge(merges: list[list[str]], from_book) -> BookMerge | None:
    """Wskazuje ostatnie scalenie, które wprowadziło stan książki.

    Takie scalenie ma co najmniej jednego rodzica z historii książki. Stroną
    ćwiczeń jest pierwszy rodzic spoza tej historii, a gdy wszyscy rodzice
    do niej należą (książka wchłonęła już gałąź ćwiczeń), pierwszy rodzic.
    """
    for merge, *parents in merges:
        flags = [from_book(parent) for parent in parents]
        if not any(flags):
            continue
        exercise = next(
            (parent for parent, flag in zip(parents, flags) if not flag), parents[0]
        )
        return BookMerge(merge, exercise)
    return None


def trial_merge(stage: Stage, book: str) -> None:
    """Scala próbnie książkę z HEAD (git merge-tree) bez zmiany katalogu roboczego."""
    result = git_run(
        "-c", "merge.directoryRenames=false",
        "merge-tree", "--write-tree", "--name-only", "HEAD", book,
    )
    if result.returncode not in (0, 1):
        stage.problem(f"próbne scalenie z {book} nie powiodło się: {result.stderr.strip()}")
        return
    lines = result.stdout.splitlines()
    tree = lines[0].strip() if lines else ""
    if result.returncode == 1:
        conflicted = []
        for line in lines[1:]:
            if not line.strip():
                break
            conflicted.append(line.strip())
        stage.note(
            f"próbne scalenie z {book}: konflikty w plikach ({len(conflicted)}): "
            f"{listing(conflicted)}; ścieżka spoza listy dozwolonej przyjmuje "
            "wersję z książki"
        )
    deleted = [
        path for status, path in name_status("--diff-filter=D", "HEAD", tree)
        if is_allowed(path)
    ]
    if deleted:
        stage.problem(
            f"próbne scalenie z {book} usunęłoby pliki ćwiczeń ({len(deleted)}): "
            f"{listing(deleted)}; nie scalamy, zob. procedurę naprawczą w kurs/README.md"
        )
    print(f"  próbne scalenie z {book}: drzewo {tree[:7]}")


def stage_g1(ctx: Context) -> Stage:
    stage = Stage("G1", "wyłączne dodawanie, kolizje i nazwy gałęzi")
    stage.start()
    book = ctx.book
    try:
        base = git("merge-base", "HEAD", book).strip()
    except GateError as error:
        stage.problem(f"nie można wyznaczyć merge-base z {book!r}: {error}")
        return stage
    ctx.base = base
    print(f"  merge-base(HEAD, {book}) = {base[:7]}")

    # Książka nie zawiera ścieżek ćwiczeń: ani w bieżącym stanie (kolizja),
    # ani we wspólnym przodku (książka wchłonęła historię ćwiczeń).
    in_book = allowed_paths_in(book)
    if in_book:
        stage.problem(
            f"kolizja: książka ({book}) zawiera ścieżki należące do ćwiczeń "
            f"({len(in_book)}): {listing(in_book)}"
        )
    book_commit = git("rev-parse", f"{book}^{{commit}}").strip()
    in_base = allowed_paths_in(base) if base != book_commit else in_book
    if in_base and base != book_commit:
        stage.problem(
            f"historia książki ({book}) zawiera stan z plikami ćwiczeń: merge-base "
            f"{base[:7]} ma "
            + plural(len(in_base), "ścieżkę", "ścieżki", "ścieżek")
            + " z listy dozwolonej"
        )
    if in_book or in_base:
        stage.note(
            "książka zawiera warstwę ćwiczeń. Przed przewinięciem dev do stanu po "
            "rozdzieleniu bramkę uruchamiamy z --book infra/rozdzielenie-cwiczen; "
            "jeżeli ćwiczenia trafiły do książki później, nie scalamy jej i "
            "stosujemy procedurę naprawczą z kurs/README.md"
        )

    added = 0
    for status, path in name_status(base, "HEAD"):
        if status == "A" and is_allowed(path):
            added += 1
        elif status == "A":
            stage.problem(f"dodany plik spoza listy dozwolonej: {path}")
        elif status == "D":
            stage.problem(f"usunięty plik istniejący w książce: {path}")
        else:
            stage.problem(f"zmieniony plik istniejący w książce ({status}): {path}")
    for path in CORE_FILES:
        if git_run("cat-file", "-e", f"HEAD:{path}").returncode != 0:
            stage.problem(
                f"commit HEAD nie zawiera podstawowego pliku warstwy: {path}; jeśli "
                "zniknął po scaleniu książki, zob. procedurę naprawczą w kurs/README.md"
            )

    ancestry: dict[str, bool] = {}

    def from_book(commit: str) -> bool:
        if commit not in ancestry:
            ancestry[commit] = is_ancestor(commit, book)
        return ancestry[commit]

    merges = exercise_side_merges(book)
    foreign: dict[str, str] = {}
    for merge, *parents in merges:
        for parent in parents:
            if parent in foreign or from_book(parent) or allowed_paths_in(parent):
                continue
            foreign[parent] = merge
    for parent, merge in foreign.items():
        stage.problem(
            f"scalenie {merge[:7]} wprowadza stan książki {parent[:7]}, którego nie "
            f"zawiera {book}; bramkę uruchamiamy z tą samą gałęzią książki, którą "
            "scalono (np. origin/dev po git fetch)"
        )

    ctx.book_merge = find_book_merge(merges, from_book)
    if ctx.book_merge:
        merge = ctx.book_merge
        print(
            f"  ostatnie scalenie książki: {merge.commit[:7]} "
            f"(stan ćwiczeń przed nim: {merge.exercise_parent[:7]})"
        )
        deleted = [
            path
            for status, path in name_status(
                "--diff-filter=D", merge.exercise_parent, merge.commit
            )
            if is_allowed(path)
        ]
        if deleted:
            stage.problem(
                f"scalenie książki {merge.commit[:7]} usunęło pliki ćwiczeń "
                f"({len(deleted)}): {listing(deleted)}; zob. procedurę naprawczą "
                "w kurs/README.md"
            )

    if ctx.trial_merge:
        trial_merge(stage, book)

    tracked = set(git("ls-tree", "-r", "-t", "--name-only", "-z", "HEAD").split("\0"))
    for name in git("for-each-ref", "--format=%(refname:short)", "refs/heads").split():
        if name in tracked:
            stage.problem(
                f"lokalna gałąź {name!r} ma nazwę równą śledzonej ścieżce; "
                "należy zmienić nazwę gałęzi"
            )
    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    if branch not in EXERCISE_BRANCHES and not branch.startswith(EXERCISE_PREFIXES):
        stage.note(
            f"bieżąca gałąź {branch!r} nie jest gałęzią ćwiczeń "
            "(cwiczenia, fala/*, platform/*, sync/*)"
        )

    uncommitted = []
    for code, path in working_tree_changes():
        if code != "??" and not is_allowed(path):
            stage.problem(
                f"niezatwierdzona zmiana pliku książki ({code.strip()}): {path}; "
                "w katalogu ćwiczeń nie zmieniamy plików książki"
            )
        elif ctx.working_tree and is_allowed(path):
            continue  # należy do sprawdzanego katalogu roboczego
        elif code == "??" and not is_allowed(path):
            stage.note(f"plik nieśledzony spoza listy dozwolonej: {path}")
        else:
            uncommitted.append(path)
    if uncommitted:
        stage.note(
            f"niezatwierdzone zmiany plików ćwiczeń nie wchodzą do wyniku "
            f"({len(uncommitted)}): {listing(uncommitted)}"
        )
    if not ctx.working_tree:
        ctx.dirty = len(uncommitted)

    stage.detail = (
        plural(added, "dodana ścieżka", "dodane ścieżki", "dodanych ścieżek")
        + f", merge-base {base[:7]}"
    )
    if ctx.book_merge:
        stage.detail += f", scalenie książki {ctx.book_merge.commit[:7]}"
    return stage


# ---------------------------------------------------------------- G2


def overlay_lists(overlay: dict, book: dict, prefix: tuple[str, ...] = ()):
    """Wylicza listy nakładki, które zastępują listy książki."""
    for key, value in overlay.items():
        if not prefix and key == "INHERIT":
            continue
        base = book.get(key) if isinstance(book, dict) else None
        if isinstance(value, dict) and isinstance(base, dict):
            yield from overlay_lists(value, base, (*prefix, key))
        elif isinstance(value, list) and isinstance(base, list):
            yield ".".join((*prefix, key)), value, base


def stage_g2(ctx: Context) -> Stage:
    stage = Stage("G2", "listy nakładki zachowują listy książki")
    stage.start()
    import yaml
    from mkdocs.utils.yaml import get_yaml_loader

    loader = get_yaml_loader()
    configs = []
    for name in (BOOK_CONFIG, COURSE_CONFIG):
        with open(ctx.tree / name, encoding="utf-8") as stream:
            configs.append(yaml.load(stream, Loader=loader) or {})
    book, overlay = configs

    if overlay.get("INHERIT") != BOOK_CONFIG:
        stage.problem(f"{COURSE_CONFIG} musi dziedziczyć konfigurację: INHERIT: {BOOK_CONFIG}")
    checked = 0
    for key, value, base in overlay_lists(overlay, book):
        checked += 1
        missing = [item for item in base if item not in value]
        if missing:
            stage.problem(
                f"lista {key!r} w {COURSE_CONFIG} zastępuje listę książki "
                f"i pomija: {missing}"
            )
    stage.detail = f"sprawdzone listy wspólne z książką: {checked}"
    return stage


# ---------------------------------------------------------------- G3


def load_hook(root: Path):
    spec = importlib.util.spec_from_file_location(
        "kurs_gate_build_activities", root / "scripts" / "build_activities.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_page(text: str, config) -> tuple[str, list[tuple[int, str, str]]]:
    """Przetwarza Markdown strony rozszerzeniami książki (etapy G3 i G4).

    Zwraca HTML treści strony oraz (poziom, id, tekst) jej nagłówków; te same
    rozszerzenia i ustawienia toc nadają identyfikatory nagłówkom w buildzie.
    """
    import markdown

    renderer = markdown.Markdown(
        extensions=config["markdown_extensions"],
        extension_configs=config["mdx_configs"],
    )
    html = renderer.convert(text.replace("\r\n", "\n").replace("\r", "\n"))
    headings: list[tuple[int, str, str]] = []

    def walk(tokens) -> None:
        for token in tokens:
            headings.append((token["level"], token["id"], token["name"]))
            walk(token["children"])

    walk(renderer.toc_tokens)
    return html, headings


def page_headings(text: str, config) -> list[tuple[int, str, str]]:
    """Zwraca (poziom, id, tekst) nagłówków strony z ustawieniami toc książki."""
    return render_page(text, config)[1]


def headings_at(commit: str, page: str, config) -> list[tuple[int, str, str]] | None:
    """Nagłówki strony docs/<page> w danym commicie albo None, gdy jej tam nie ma."""
    result = git_run("show", f"{commit}:docs/{page}")
    if result.returncode != 0:
        return None
    return page_headings(result.stdout, config)


def heading_key(heading: tuple[int, str, str]) -> tuple[int, str]:
    return heading[0], " ".join(heading[2].split()).casefold()


def align_heading(
    section_id: str,
    old: list[tuple[int, str, str]],
    new: list[tuple[int, str, str]],
) -> tuple[tuple[int, str, str], tuple[int, str, str]] | None:
    """Wskazuje następcę nagłówka section_id po zmianie strony.

    Zestawia sekwencje (poziom, tekst) nagłówków sprzed zmiany i po niej, więc
    rozpoznaje nagłówek, który zajął miejsce dawnego, także wtedy, gdy liczba
    nagłówków się zmieniła. Zwraca parę (dawny, nowy) albo None, gdy dawnego
    nagłówka nie było lub zniknął bez następcy na tym samym poziomie.
    """
    position = next(
        (index for index, heading in enumerate(old) if heading[1] == section_id), None
    )
    if position is None:
        return None
    target = old[position]
    matcher = difflib.SequenceMatcher(
        None, [heading_key(h) for h in old], [heading_key(h) for h in new],
        autojunk=False,
    )
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if not i1 <= position < i2:
            continue
        if tag == "equal":
            return target, new[j1 + position - i1]
        if tag != "replace":
            return None
        block = new[j1:j2]
        if i2 - i1 == j2 - j1 and block[position - i1][0] == target[0]:
            return target, block[position - i1]
        candidates = [heading for heading in block if heading[0] == target[0]]
        if not candidates:
            return None
        return target, max(
            candidates,
            key=lambda heading: difflib.SequenceMatcher(
                None, heading_key(target)[1], heading_key(heading)[1]
            ).ratio(),
        )
    return None


def describe_successor(before: tuple[int, str, str], after: tuple[int, str, str]) -> str:
    """Opis następcy nagłówka wspólny dla G3 i G4."""
    if heading_key(before)[1] == heading_key(after)[1]:
        return (
            f"identyfikator nagłówka „{after[2]}” zmienił się: {before[1]} → {after[1]}"
        )
    return (
        f"prawdopodobna zmiana nagłówka: „{before[2]}” → „{after[2]}” "
        f"({before[1]} → {after[1]})"
    )


def rebinding_hint(
    section_id: str,
    page: str,
    headings: list[tuple[int, str, str]],
    previous: str | None,
    config,
) -> str:
    """Podpowiedź do zerwanego wiązania: najpierw zestawienie nagłówków."""
    hint = ""
    old = headings_at(previous, page, config) if previous else None
    if old:
        match = align_heading(section_id, old, headings)
        if match:
            return "; " + describe_successor(*match)
        removed = next((h for h in old if h[1] == section_id), None)
        if removed:
            hint = (
                f"; nagłówek „{removed[2]}” zniknął ze strony, a zestawienie "
                "nagłówków nie wskazuje następcy"
            )
    bindable = [heading_id for level, heading_id, _ in headings if level >= 2]
    similar = difflib.get_close_matches(str(section_id), bindable, n=3, cutoff=0.5)
    if similar:
        hint += (
            "; identyfikatory o podobnym zapisie (wyłącznie podobieństwo napisów, "
            "treść wymaga sprawdzenia): " + ", ".join(similar)
        )
    return hint


def renamed_page(page: str, book: str) -> str | None:
    """Szuka w historii książki nowej nazwy strony przeniesionej przez git mv."""
    output = git(
        "log", book, "--format=", "--name-status", "-z",
        "--find-renames", "--diff-filter=R", "-n", "500",
        check=False,
    )
    fields = [item.strip("\n") for item in output.split("\0")]
    old = f"docs/{page}"
    for index, item in enumerate(fields[:-2]):
        if item.startswith("R") and fields[index + 1] == old:
            new = fields[index + 2]
            return new.removeprefix("docs/")
    return None


def activities_at(commit: str) -> dict[str, tuple[object, object]]:
    """Mapuje activity_id → (page, section_id) z definicji w danym commicie."""
    import yaml

    result: dict[str, tuple[object, object]] = {}
    names = git("ls-tree", "-r", "--name-only", "-z", commit, "--", "activities")
    for name in names.split("\0"):
        if not name.endswith(".yaml"):
            continue
        shown = git_run("show", f"{commit}:{name}")
        try:
            document = yaml.safe_load(shown.stdout) if shown.returncode == 0 else None
        except yaml.YAMLError:
            continue
        if not isinstance(document, dict):
            continue
        for activity in document.get("activities") or []:
            if isinstance(activity, dict) and isinstance(activity.get("activity_id"), str):
                result[activity["activity_id"]] = (
                    document.get("page"),
                    activity.get("section_id"),
                )
    return result


def describe_binding(page, section_id, headings, same_page: bool) -> str:
    if section_id is None:
        target = "cała strona"
    else:
        text = next((h[2] for h in headings or [] if h[1] == section_id), None)
        target = f"{section_id} („{text}”)" if text else f"{section_id}"
    return target if same_page else f"{page}: {target}"


def report_binding_changes(
    previous: str,
    current: dict[str, tuple[object, object]],
    headings_now: dict[str, list[tuple[int, str, str]]],
    config,
) -> int:
    """Wypisuje zmiany wiązań względem stanu ćwiczeń sprzed scalenia książki."""
    old = activities_at(previous)
    old_headings: dict[str, list[tuple[int, str, str]] | None] = {}
    changes = 0
    for activity_id, (page, section_id) in current.items():
        if activity_id not in old or old[activity_id] == (page, section_id):
            continue
        old_page, old_section = old[activity_id]
        if isinstance(old_page, str) and old_page not in old_headings:
            old_headings[old_page] = headings_at(previous, old_page, config)
        same_page = old_page == page
        before = describe_binding(
            old_page, old_section, old_headings.get(old_page), same_page
        )
        after = describe_binding(page, section_id, headings_now.get(page), same_page)
        prefix = "" if not same_page else f"{page}: "
        Stage.note(
            f"zmiana wiązania względem {previous[:7]}: {activity_id!r}, "
            f"{prefix}{before} → {after}"
        )
        changes += 1
    return changes


def stage_g3(ctx: Context) -> Stage:
    stage = Stage("G3", "schemat i wiązania aktywności")
    stage.start()
    import yaml
    from mkdocs.config import load_config

    config = load_config(str(ctx.tree / COURSE_CONFIG))
    try:
        load_hook(ctx.tree)._build_manifest(config)
    except ValueError as error:
        message = str(error).replace(str(ctx.tree.resolve()) + os.sep, "")
        message = message.replace(str(ctx.tree) + os.sep, "")
        stage.problem(f"schemat: {message.replace(os.sep, '/')}")

    previous = ctx.book_merge.exercise_parent if ctx.book_merge else None
    docs_dir = Path(config["docs_dir"])
    current: dict[str, tuple[object, object]] = {}
    headings_now: dict[str, list[tuple[int, str, str]]] = {}
    total = 0
    for source in sorted((ctx.tree / "activities").rglob("*.yaml")):
        relative = source.relative_to(ctx.tree).as_posix()
        try:
            document = yaml.safe_load(source.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            stage.problem(f"{relative}: niepoprawny YAML: {error}")
            continue
        if not isinstance(document, dict):
            stage.problem(f"{relative}: dokument YAML musi być mapą")
            continue

        page = document.get("page")
        if not isinstance(page, str) or not (docs_dir / page).is_file():
            hint = ""
            new_name = renamed_page(page, ctx.book) if isinstance(page, str) else None
            if new_name:
                hint = f"; w książce przeniesiono ją do {new_name} (popraw pole page)"
            stage.problem(f"{relative}: strona {page!r} nie istnieje w docs/{hint}")
            continue
        ctx.activity_pages.add(page)

        headings = page_headings((docs_dir / page).read_text(encoding="utf-8"), config)
        headings_now[page] = headings
        bindable = [heading_id for level, heading_id, _ in headings if level >= 2]
        all_ids = {heading_id for _, heading_id, _ in headings}
        for activity in document.get("activities") or []:
            if not isinstance(activity, dict):
                continue
            total += 1
            section_id = activity.get("section_id")
            activity_id = activity.get("activity_id")
            if isinstance(activity_id, str):
                current[activity_id] = (page, section_id)
            if section_id is None:
                continue
            if section_id not in bindable:
                hint = rebinding_hint(str(section_id), page, headings, previous, config)
                stage.problem(
                    f"{relative}: aktywność {activity_id!r} ma section_id "
                    f"{section_id!r}, którego nie ma wśród nagłówków h2–h6 "
                    f"strony {page}{hint}"
                )
                print(f"         dostępne: {', '.join(bindable) or 'brak'}")
                continue
            deduplicated = DEDUPLICATED_ID.fullmatch(section_id)
            if deduplicated and deduplicated.group(1) in all_ids:
                stage.problem(
                    f"{relative}: aktywność {activity_id!r} ma section_id "
                    f"{section_id!r} z sufiksem deduplikacji powtórzonego "
                    "nagłówka; należy ją powiązać z całą stroną (section_id: null)"
                )

    rebinds = 0
    if previous:
        rebinds = report_binding_changes(previous, current, headings_now, config)

    stage.detail = (
        plural(total, "aktywność", "aktywności", "aktywności")
        + " na "
        + plural(len(ctx.activity_pages), "stronie", "stronach", "stronach")
    )
    if previous:
        stage.detail += ", zmienione wiązania: " + str(rebinds)
    return stage


# ---------------------------------------------------------------- G4

# Źródło treści sekcji: Markdown strony przetworzony funkcją render_page, czyli
# tym samym rendererem i tymi samymi rozszerzeniami książki, z których G3 bierze
# identyfikatory nagłówków. Identyfikatory są więc z definicji zgodne z G3
# i z buildem, a granice sekcji wyznaczają elementy nagłówków wynikowego HTML:
# wiersz zaczynający się od # w bloku kodu nie jest nagłówkiem, a powtórzony
# nagłówek ma własny identyfikator z sufiksem. Bieżącą treść czytamy z katalogu
# docs sprawdzanego drzewa, a treść z przeglądu — z commitu książki zapisanego
# w kurs/aktualnosc.json (git show). Nie korzystamy z HTML budowanego w G7:
# zatwierdzenie i odtworzenie dawnej treści wymagałyby pełnego buildu, a strona
# zawiera szablon motywu i znaczniki hooka, które trzeba by usuwać.

BLOCK_TAGS = frozenset(
    {
        "address", "article", "aside", "blockquote", "caption", "dd", "details",
        "div", "dl", "dt", "figcaption", "figure", "footer", "header", "hr",
        "label", "li", "main", "nav", "ol", "p", "section", "summary", "table",
        "tbody", "td", "tfoot", "th", "thead", "tr", "ul",
    }
)
HEADING_LEVELS = {f"h{level}": level for level in range(1, 7)}
SKIPPED_TAGS = frozenset({"script", "style", "template"})
# Granica zdania: znak końca zdania, ewentualny cudzysłów albo nawias zamykający,
# odstęp i wielka litera (także po cudzysłowie albo nawiasie otwierającym).
SENTENCE_BREAK = re.compile(r"[.!?…]+[”\"»)\]]*\s+(?=[„\"«(\[]?[A-ZĄĆĘŁŃÓŚŹŻ])")
# Skróty, po których kropka zwykle nie kończy zdania.
ABBREVIATIONS = frozenset(
    {
        "ang", "cd", "ew", "godz", "m.in", "np", "nr", "ok", "pkt", "por",
        "rozdz", "rys", "str", "tab", "tj", "tzw", "wg", "zob",
    }
)
LOCK_FIELDS = (
    "page", "section_id", "heading", "activity_ids",
    "fingerprint", "book_commit", "reviewed_on",
)
FINGERPRINT_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
DATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def sentences(text: str) -> list[str]:
    """Dzieli tekst akapitu na zdania, po jednym w wierszu odcisku i różnicy.

    Podział służy czytelności różnicy: zmiana jednego słowa wskazuje zdanie,
    a nie cały akapit. Jest deterministyczny i działa na tekście po złączeniu
    białych znaków, więc nie zależy od łamania wierszy; skrót, liczba albo
    pojedyncza litera przed kropką nie kończą zdania.
    """
    parts: list[str] = []
    start = 0
    for match in SENTENCE_BREAK.finditer(text):
        words = text[start:match.start()].split()
        word = words[-1].lstrip("([„\"«").casefold() if words else ""
        if len(word) <= 1 or word.isdigit() or word in ABBREVIATIONS:
            continue
        parts.append(text[start:match.end()].rstrip())
        start = match.end()
    parts.append(text[start:])
    return [part for part in parts if part]


class SectionText(HTMLParser):
    """Wiersze tekstu strony i jej sekcji wyznaczonych przez nagłówki HTML.

    Sekcja trwa od swojego nagłówka do następnego nagłówka tego samego lub
    wyższego poziomu, więc obejmuje podsekcje. Tekst bloku (akapitu, punktu
    listy, komórki tabeli) po złączeniu białych znaków dzielimy na zdania;
    blok kodu zachowuje wiersze i wcięcia, bez spacji końcowych i skrajnych
    pustych wierszy. Znaki końca wiersza, spacje końcowe i ponowne łamanie
    akapitu nie zmieniają więc wierszy, a zmienia je każda zmiana słów, liczb
    i kodu. Znak ¶ odnośnika nagłówka, skrypty i style pomijamy, obraz wnosi
    tekst alternatywny, a adresy odnośników i atrybuty HTML nie należą do
    tekstu.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.page: list[str] = []
        self.sections: dict[str, list[str]] = {}
        self._open: list[tuple[int, str]] = []
        self._prose: list[str] = []
        self._code: list[str] | None = None
        self._heading: int | None = None
        self._skipped: list[str] = []

    def _emit(self, line: str) -> None:
        line = unicodedata.normalize("NFC", line)
        self.page.append(line)
        for _, section_id in self._open:
            self.sections[section_id].append(line)

    def _flush(self) -> None:
        text = " ".join("".join(self._prose).split())
        self._prose = []
        for sentence in sentences(text):
            self._emit(sentence)

    def _end_code(self) -> None:
        code = "".join(self._code or []).replace("\r\n", "\n").replace("\r", "\n")
        self._code = None
        lines = [line.rstrip() for line in code.split("\n")]
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        for line in ("```", *lines, "```"):
            self._emit(line)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if self._skipped:
            if tag == self._skipped[-1]:
                self._skipped.append(tag)
            return
        classes = (attributes.get("class") or "").split()
        if tag in SKIPPED_TAGS or (tag == "a" and "headerlink" in classes):
            self._skipped.append(tag)
            return
        if self._code is not None:
            if tag == "br":
                self._code.append("\n")
            return
        if tag in HEADING_LEVELS:
            self._flush()
            level = HEADING_LEVELS[tag]
            self._open = [item for item in self._open if item[0] < level]
            section_id = attributes.get("id")
            if section_id:
                self._open.append((level, section_id))
                self.sections[section_id] = []
            self._heading = level
        elif tag == "pre":
            self._flush()
            self._code = []
        elif tag in BLOCK_TAGS:
            self._flush()
        elif tag == "br":
            self._prose.append(" ")
        elif tag == "img" and attributes.get("alt"):
            self._prose.append(f" {attributes['alt']} ")

    def handle_endtag(self, tag: str) -> None:
        if self._skipped:
            if tag == self._skipped[-1]:
                self._skipped.pop()
            return
        if self._code is not None:
            if tag == "pre":
                self._end_code()
            return
        if tag in HEADING_LEVELS and self._heading is not None:
            text = " ".join("".join(self._prose).split())
            self._prose = []
            self._emit("#" * self._heading + " " + text)
            self._heading = None
        elif tag in BLOCK_TAGS:
            self._flush()

    def handle_data(self, data: str) -> None:
        if self._skipped:
            return
        if self._code is not None:
            self._code.append(data)
        else:
            self._prose.append(data)

    def close(self) -> None:
        super().close()
        if self._code is not None:
            self._end_code()
        self._flush()


@dataclass
class PageText:
    """Nagłówki strony (jak w G3) oraz wiersze tekstu całej strony i sekcji."""

    headings: list[tuple[int, str, str]]
    page: list[str]
    sections: dict[str, list[str]]

    def lines(self, section_id: str | None) -> list[str] | None:
        return self.page if section_id is None else self.sections.get(section_id)

    def heading(self, section_id: str | None) -> str:
        """Tekst nagłówka sekcji; dla całej strony — tytuł h1."""
        for level, heading_id, name in self.headings:
            if heading_id == section_id or (section_id is None and level == 1):
                return name
        return ""


def page_text(text: str, config) -> PageText:
    html, headings = render_page(text, config)
    parser = SectionText()
    parser.feed(html)
    parser.close()
    return PageText(headings, parser.page, parser.sections)


def page_text_at(commit: str, page: str, config) -> PageText | None:
    """Tekst strony docs/<page> w danym commicie albo None, gdy jej tam nie ma."""
    result = git_run("show", f"{commit}:docs/{page}")
    if result.returncode != 0:
        return None
    return page_text(result.stdout, config)


def fingerprint(lines: list[str]) -> str:
    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def binding_order(key: tuple[str, str | None]) -> tuple[str, bool, str]:
    page, section_id = key
    return page, section_id is not None, section_id or ""


def binding_name(key: tuple[str, str | None]) -> str:
    page, section_id = key
    return f"{page}#{section_id}" if section_id is not None else f"{page} (cała strona)"


def bindings_in(tree: Path) -> tuple[dict[tuple[str, str | None], list[str]], list[str]]:
    """Wiązania z definicji w drzewie: {(strona, section_id): [activity_id…]}.

    Zwraca też błędy definicji: etap G4 je pomija, ponieważ zgłasza je G3,
    a polecenie --zatwierdz-aktualnosc z ich powodu nie zapisuje pliku.
    """
    import yaml

    found: dict[tuple[str, str | None], list[str]] = {}
    errors: list[str] = []
    for source in sorted((tree / "activities").rglob("*.yaml")):
        relative = source.relative_to(tree).as_posix()
        try:
            document = yaml.safe_load(source.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            errors.append(f"{relative}: niepoprawny YAML: {error}")
            continue
        page = document.get("page") if isinstance(document, dict) else None
        if not isinstance(page, str):
            errors.append(f"{relative}: brak tekstowego pola page")
            continue
        for activity in document.get("activities") or []:
            if not isinstance(activity, dict):
                errors.append(f"{relative}: aktywność musi być mapą")
                continue
            activity_id = activity.get("activity_id")
            section_id = activity.get("section_id")
            if not isinstance(activity_id, str) or not (
                section_id is None or isinstance(section_id, str)
            ):
                errors.append(
                    f"{relative}: aktywność {activity_id!r} nie ma tekstowego "
                    "activity_id albo section_id"
                )
                continue
            found.setdefault((page, section_id), []).append(activity_id)
    return {key: sorted(ids) for key, ids in found.items()}, errors


def lock_entry_problem(entry) -> str | None:
    """Opis błędu formatu wpisu kurs/aktualnosc.json albo None."""
    if not isinstance(entry, dict) or set(entry) != set(LOCK_FIELDS):
        return "oczekiwano dokładnie pól: " + ", ".join(LOCK_FIELDS)
    ids = entry["activity_ids"]

    def text(name: str, pattern: re.Pattern[str] | None = None) -> bool:
        value = entry[name]
        return isinstance(value, str) and (pattern is None or bool(pattern.fullmatch(value)))

    valid = {
        "page": text("page"),
        "section_id": entry["section_id"] is None or text("section_id"),
        "heading": text("heading"),
        "activity_ids": isinstance(ids, list) and bool(ids)
        and all(isinstance(item, str) for item in ids) and len(set(ids)) == len(ids),
        "fingerprint": text("fingerprint", FINGERPRINT_PATTERN),
        "book_commit": text("book_commit", COMMIT_PATTERN),
        "reviewed_on": text("reviewed_on", DATE_PATTERN),
    }
    wrong = [name for name, ok in valid.items() if not ok]
    return "niepoprawne pola: " + ", ".join(wrong) if wrong else None


def read_lock(path: Path) -> tuple[dict | None, list[str]]:
    """Odczytuje kurs/aktualnosc.json.

    Zwraca ({"version": wersja odcisku, "entries": {wiązanie: wpis}}, błędy);
    przy błędzie formatu pierwszym elementem jest None.
    """
    if not path.is_file():
        return None, [f"brak pliku {LOCK_FILE}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        return None, [f"{LOCK_FILE}: niepoprawny JSON: {error}"]
    if (
        not isinstance(data, dict)
        or set(data) != {"fingerprint_version", "bindings"}
        or not isinstance(data["fingerprint_version"], int)
        or not isinstance(data["bindings"], list)
    ):
        return None, [
            f"{LOCK_FILE}: oczekiwano mapy z polami fingerprint_version (liczba) "
            "i bindings (lista)"
        ]
    entries: dict[tuple[str, str | None], dict] = {}
    owners: dict[str, tuple[str, str | None]] = {}
    errors: list[str] = []
    for number, entry in enumerate(data["bindings"], 1):
        problem = lock_entry_problem(entry)
        if problem:
            errors.append(f"{LOCK_FILE}: wpis {number}: {problem}")
            continue
        key = (entry["page"], entry["section_id"])
        if key in entries:
            errors.append(f"{LOCK_FILE}: wpis {number}: powtórzone wiązanie {binding_name(key)}")
            continue
        for activity_id in entry["activity_ids"]:
            if activity_id in owners:
                errors.append(
                    f"{LOCK_FILE}: wpis {number}: aktywność {activity_id!r} występuje "
                    f"także we wpisie {binding_name(owners[activity_id])}"
                )
            owners[activity_id] = key
        entries[key] = entry
    if errors:
        return None, errors
    return {"version": data["fingerprint_version"], "entries": entries}, []


def write_lock(path: Path, entries: dict[tuple[str, str | None], dict]) -> None:
    data = {
        "fingerprint_version": FINGERPRINT_VERSION,
        "bindings": [entries[key] for key in sorted(entries, key=binding_order)],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def content_diff(old: list[str], new: list[str], old_label: str, new_label: str) -> list[str]:
    """Różnica unified treści sekcji, skrócona do DIFF_LINES wierszy."""
    lines = list(difflib.unified_diff(old, new, old_label, new_label, n=1, lineterm=""))
    if len(lines) > DIFF_LINES:
        rest = len(lines) - DIFF_LINES
        lines = lines[:DIFF_LINES] + [
            "… pominięto " + plural(rest, "wiersz", "wiersze", "wierszy") + " różnicy"
        ]
    return lines


def quoted(text: str) -> str:
    return f"„{text}”" if text else "bez nagłówka"


class BookPages:
    """Teksty stron: bieżące z katalogu docs drzewa, dawne z commitów książki."""

    def __init__(self, docs_dir: Path, config) -> None:
        self.docs_dir = docs_dir
        self.config = config
        self._now: dict[str, PageText | None] = {}
        self._at: dict[tuple[str, str], PageText | None] = {}

    def now(self, page: str) -> PageText | None:
        if page not in self._now:
            source = self.docs_dir / page
            self._now[page] = (
                page_text(source.read_text(encoding="utf-8"), self.config)
                if source.is_file()
                else None
            )
        return self._now[page]

    def at(self, commit: str, page: str) -> PageText | None:
        if (commit, page) not in self._at:
            self._at[commit, page] = page_text_at(commit, page, self.config)
        return self._at[commit, page]


class CurrencyReview:
    """Porównanie wiązań sprawdzanego drzewa z wpisami kurs/aktualnosc.json."""

    def __init__(self, stage: Stage, pages: BookPages, lock: dict, current: dict,
                 book: str, base: str) -> None:
        self.stage = stage
        self.pages = pages
        self.entries: dict[tuple[str, str | None], dict] = lock["entries"]
        self.version = lock["version"]
        self.current = current
        self.book = book
        self.base = base
        self.unchanged = 0
        # activity_id → wiązanie z przeglądu oraz wiązanie bieżące
        self.reviewed = {
            activity_id: key
            for key, entry in self.entries.items()
            for activity_id in entry["activity_ids"]
        }
        self.placed = {activity_id: key for key, ids in current.items() for activity_id in ids}

    def run(self) -> None:
        if self.version != FINGERPRINT_VERSION:
            self.stage.problem(
                f"{LOCK_FILE} zawiera odciski w wersji {self.version}, a bramka "
                f"oblicza wersję {FINGERPRINT_VERSION}; treść porównujemy ze stanem "
                "książki z przeglądu, a plik należy odświeżyć"
            )
        for key in sorted(set(self.current) | set(self.entries), key=binding_order):
            ids = self.current.get(key)
            entry = self.entries.get(key)
            if ids is None:
                self.stale(key, entry)
            elif entry is None:
                self.unreviewed(key, ids)
            else:
                self.compare(key, entry, ids)

    def reviewed_lines(self, entry: dict) -> list[str] | None:
        text = self.pages.at(entry["book_commit"], entry["page"])
        return text.lines(entry["section_id"]) if text else None

    def expected(self, entry: dict) -> str | None:
        if self.version == FINGERPRINT_VERSION:
            return entry["fingerprint"]
        lines = self.reviewed_lines(entry)
        return fingerprint(lines) if lines is not None else None

    def show_diff(self, entry: dict, key: tuple[str, str | None], lines: list[str]) -> None:
        """Różnica treści od przeglądu i polecenie pokazujące pełne zmiany stron."""
        commit = entry["book_commit"]
        old_key = (entry["page"], entry["section_id"])
        old_lines = self.reviewed_lines(entry)
        if old_lines is None:
            Stage.note(
                f"treści z przeglądu nie można odtworzyć: commit {commit[:7]} nie "
                f"zawiera {binding_name(old_key)}"
            )
            return
        if self.version == FINGERPRINT_VERSION and fingerprint(old_lines) != entry["fingerprint"]:
            Stage.note(
                "treść odtworzona z commitu przeglądu nie odpowiada zapisanemu "
                "odciskowi (np. po zmianie rozszerzeń Markdown książki); różnica "
                "może obejmować także skutki tej zmiany"
            )
        diff = content_diff(
            old_lines,
            lines,
            f"{binding_name(old_key)} @ {commit[:7]} (przegląd {entry['reviewed_on']})",
            f"{binding_name(key)} @ {self.base[:7]}",
        )
        for line in diff:
            print(f"         {line}")
        paths = dict.fromkeys((f"docs/{entry['page']}", f"docs/{key[0]}"))
        print(
            f"         pełne zmiany: git diff {commit[:7]} {self.base[:7]} -- "
            + " ".join(paths)
        )

    def origin(self, activity_id: str) -> str:
        source = self.reviewed.get(activity_id)
        return f"{activity_id} (nowa)" if source is None else (
            f"{activity_id} (wcześniej {binding_name(source)})"
        )

    def destination(self, activity_id: str) -> str:
        target = self.placed.get(activity_id)
        return f"{activity_id} (usunięta)" if target is None else (
            f"{activity_id} (obecnie {binding_name(target)})"
        )

    def compare(self, key, entry: dict, ids: list[str]) -> None:
        page, section_id = key
        text = self.pages.now(page)
        lines = text.lines(section_id) if text else None
        if lines is None:
            self.broken(key, entry, ids)
            return
        changed = fingerprint(lines) != self.expected(entry)
        added = [item for item in ids if item not in entry["activity_ids"]]
        dropped = [item for item in entry["activity_ids"] if item not in ids]
        if not (changed or added or dropped):
            self.unchanged += 1
            return
        heading = text.heading(section_id)
        title = quoted(heading)
        if heading != entry["heading"]:
            title = f"{quoted(entry['heading'])} → {title}"
        parts = []
        if changed:
            parts.append(
                f"zmieniła się treść od przeglądu przy {entry['book_commit'][:7]} "
                f"({entry['reviewed_on']})"
            )
        if added:
            parts.append(
                "aktywności bez przeglądu tej sekcji: "
                + ", ".join(self.origin(item) for item in added)
            )
        if dropped:
            parts.append(
                "aktywności, które opuściły wiązanie: "
                + ", ".join(self.destination(item) for item in dropped)
            )
        message = f"{binding_name(key)} ({title}): " + "; ".join(parts)
        if changed:
            message += "; aktywności do przejrzenia: " + ", ".join(ids)
        self.stage.problem(message)
        if changed:
            self.show_diff(entry, key, lines)

    def broken(self, key, entry: dict, ids: list[str]) -> None:
        """Wiązanie z przeglądu, którego sekcji nie ma w książce (błąd G3)."""
        page, section_id = key
        target_page = page
        text = self.pages.now(page)
        if text is None:
            reason = "strony nie ma w książce (zob. G3)"
            moved = renamed_page(page, self.book)
            if moved:
                reason += f"; książka przeniosła ją do {moved}"
                target_page = moved
                text = self.pages.now(moved)
        else:
            reason = "nagłówka nie ma na stronie (zob. G3)"
        target = None
        if text is not None:
            if section_id is None or section_id in text.sections:
                target = (target_page, section_id)
            else:
                old = self.pages.at(entry["book_commit"], page)
                match = align_heading(section_id, old.headings, text.headings) if old else None
                if match:
                    reason += "; " + describe_successor(*match)
                    target = (target_page, match[1][1])
                else:
                    reason += "; zestawienie nagłówków nie wskazuje następcy"
        self.stage.problem(
            f"{binding_name(key)} ({quoted(entry['heading'])}): {reason}; aktywności "
            "do przejrzenia po poprawie wiązania: " + ", ".join(ids)
        )
        if target is not None:
            self.show_diff(entry, target, text.lines(target[1]))

    def unreviewed(self, key, ids: list[str]) -> None:
        """Wiązanie bez wpisu: aktywności przeniesione z innej sekcji albo nowe."""
        page, section_id = key
        text = self.pages.now(page)
        lines = text.lines(section_id) if text else None
        label = binding_name(key)
        if lines is not None:
            label += f" ({quoted(text.heading(section_id))})"
        sources = sorted({self.reviewed[item] for item in ids if item in self.reviewed},
                         key=binding_order)
        for source in sources:
            entry = self.entries[source]
            moved = [item for item in ids if self.reviewed.get(item) == source]
            message = (
                f"zmiana wiązania bez przeglądu: {', '.join(moved)} z "
                f"{binding_name(source)} ({quoted(entry['heading'])}, przegląd przy "
                f"{entry['book_commit'][:7]}) do {label}"
            )
            if lines is None:
                self.stage.problem(message + "; nowego wiązania nie ma w książce (zob. G3)")
                continue
            old_lines = self.reviewed_lines(entry)
            if old_lines == lines:
                message += "; treść sekcji bez zmian"
            elif old_lines is not None and old_lines[1:] == lines[1:]:
                message += "; poza nagłówkiem treść sekcji bez zmian"
            self.stage.problem(message + "; aktywności do przejrzenia: " + ", ".join(moved))
            if old_lines != lines:
                self.show_diff(entry, key, lines)
        new = [item for item in ids if item not in self.reviewed]
        if new:
            message = (
                f"nowe aktywności bez wpisu w {LOCK_FILE}: {', '.join(new)}; "
                f"wiązanie {label}"
            )
            if lines is None:
                message += " nie wskazuje sekcji książki (zob. G3)"
            self.stage.problem(message)

    def stale(self, key, entry: dict) -> None:
        """Wpis bez aktywności w tym wiązaniu; przeniesienia zgłasza nowe wiązanie."""
        removed = [item for item in entry["activity_ids"] if item not in self.placed]
        if removed:
            self.stage.problem(
                f"nieaktualny wpis {LOCK_FILE}: {binding_name(key)} "
                f"({quoted(entry['heading'])}); aktywności, których już nie ma: "
                + ", ".join(removed)
            )


def stage_g4(ctx: Context, config=None) -> Stage:
    stage = Stage("G4", "aktualność powiązanych sekcji")
    stage.start()
    if config is None:
        from mkdocs.config import load_config

        config = load_config(str(ctx.tree / COURSE_CONFIG))
    docs_dir = Path(config["docs_dir"]) if "docs_dir" in config else ctx.tree / "docs"
    current, _ = bindings_in(ctx.tree)  # błędy definicji zgłasza G3
    approve = f"python kurs/tools/gate.py --zatwierdz-aktualnosc --book {ctx.book}"
    lock, errors = read_lock(ctx.tree / LOCK_FILE)
    for error in errors:
        stage.problem(error)
    if lock is None:
        stage.note(f"plik tworzy i odświeża po przeglądzie aktywności polecenie: {approve}")
        stage.detail = f"wiązania: {len(current)}, brak poprawnego pliku {LOCK_FILE}"
        return stage
    base = ctx.base or git("merge-base", "HEAD", ctx.book).strip()
    review = CurrencyReview(stage, BookPages(docs_dir, config), lock, current, ctx.book, base)
    review.run()
    if stage.problems:
        stage.note(
            f"po przeglądzie aktywności: {approve}; zmieniony plik {LOCK_FILE} "
            "zatwierdzamy commitem"
        )
    stage.detail = (
        f"wiązania: {len(current)}, zgodne z przeglądem: {review.unchanged}"
    )
    return stage


def approve_currency(book: str, root: Path, config=None, today: str | None = None) -> int:
    """Polecenie --zatwierdz-aktualnosc: zapis odcisków po przeglądzie aktywności.

    Wiązania odczytuje z definicji w katalogu roboczym, a odciski oblicza dla
    książki w stanie merge-base(HEAD, book). Wpis bez zmian (ten sam odcisk,
    nagłówek i aktywności) zachowuje dawny commit i datę przeglądu. Gdy
    którekolwiek wiązanie jest zerwane, pliku nie zmienia.
    """
    print(f"Zatwierdzenie aktualności powiązanych sekcji ({LOCK_FILE}), książka: {book}")
    try:
        base = git("merge-base", "HEAD", book).strip()
    except GateError as error:
        print(f"Nie można wyznaczyć merge-base z {book!r}: {error}", file=sys.stderr)
        return EXIT_USAGE
    today = today or date.today().isoformat()
    print(f"  stan książki: merge-base(HEAD, {book}) = {base[:7]}, data przeglądu: {today}")
    if config is None:
        from mkdocs.config import load_config

        config = load_config(str(root / COURSE_CONFIG))
    current, errors = bindings_in(root)
    if not current and not errors:
        errors.append("activities/ nie zawiera żadnej aktywności")
    lock_path = root / LOCK_FILE
    previous: dict[tuple[str, str | None], dict] = {}
    up_to_date = lock_path.exists()  # plik istnieje i ma bieżącą wersję odcisku
    if lock_path.exists():
        lock, problems = read_lock(lock_path)
        if lock is None:
            errors += problems
            errors.append(f"należy poprawić {LOCK_FILE} albo go usunąć i zapisać od nowa")
        else:
            previous = lock["entries"]
            if lock["version"] != FINGERPRINT_VERSION:
                up_to_date = False
                print(
                    f"  uwaga  zmiana wersji odcisku {lock['version']} → "
                    f"{FINGERPRINT_VERSION}: zapisujemy wszystkie wpisy"
                )
    pages: dict[str, PageText | None] = {}
    entries: dict[tuple[str, str | None], dict] = {}
    for key in sorted(current, key=binding_order):
        page, section_id = key
        if page not in pages:
            pages[page] = page_text_at(base, page, config)
            if pages[page] is None:
                errors.append(f"docs/{page}: strony nie ma w książce w {base[:7]} (zob. G3)")
            elif (
                git_run("rev-parse", f"HEAD:docs/{page}").stdout
                != git_run("rev-parse", f"{base}:docs/{page}").stdout
            ):
                errors.append(
                    f"docs/{page} w HEAD różni się od książki w {base[:7]}; --book "
                    "musi wskazywać gałąź książki scaloną z HEAD (np. origin/dev "
                    "po git fetch)"
                )
        text = pages[page]
        if text is None:
            continue
        lines = text.lines(section_id)
        if lines is None:
            errors.append(
                f"{binding_name(key)}: strona nie ma nagłówka o tym identyfikatorze "
                "(zob. G3)"
            )
            continue
        entries[key] = {
            "page": page,
            "section_id": section_id,
            "heading": text.heading(section_id),
            "activity_ids": current[key],
            "fingerprint": fingerprint(lines),
            "book_commit": base,
            "reviewed_on": today,
        }
    if errors:
        for error in errors:
            print(f"  BŁĄD   {error}")
        print(f"Nie zapisano {LOCK_FILE}: najpierw należy poprawić definicje i wiązania.")
        return EXIT_FAILED

    result: dict[tuple[str, str | None], dict] = {}
    counts = {"dodano": 0, "zmieniono": 0, "usunięto": 0, "bez zmian": 0}
    for key, entry in entries.items():
        old = previous.get(key)
        if old is not None and all(
            old[name] == entry[name] for name in ("heading", "activity_ids", "fingerprint")
        ):
            result[key] = old
            counts["bez zmian"] += 1
            continue
        result[key] = entry
        label = f"{binding_name(key)} ({quoted(entry['heading'])})"
        if old is None:
            counts["dodano"] += 1
            print(f"  dodano     {label}: {', '.join(entry['activity_ids'])}")
            continue
        counts["zmieniono"] += 1
        what = []
        if old["fingerprint"] != entry["fingerprint"]:
            what.append("odcisk treści")
        if old["heading"] != entry["heading"]:
            what.append(f"nagłówek {quoted(old['heading'])} → {quoted(entry['heading'])}")
        if old["activity_ids"] != entry["activity_ids"]:
            what.append("aktywności: " + ", ".join(entry["activity_ids"]))
        print(
            f"  zmieniono  {label}: {'; '.join(what)}; przegląd {old['book_commit'][:7]} "
            f"({old['reviewed_on']}) → {base[:7]} ({today})"
        )
    for key in sorted(set(previous) - set(entries), key=binding_order):
        counts["usunięto"] += 1
        old = previous[key]
        print(
            f"  usunięto   {binding_name(key)} ({quoted(old['heading'])}): "
            + ", ".join(old["activity_ids"])
        )
    summary = ", ".join(f"{name}: {count}" for name, count in counts.items())
    if up_to_date and counts["bez zmian"] == len(result) == len(previous):
        print(f"Plik {LOCK_FILE} jest aktualny ({summary}); nie wprowadzono zmian.")
        return EXIT_OK
    write_lock(lock_path, result)
    print(f"Zapisano {LOCK_FILE} ({summary}). Plik zatwierdzamy commitem na bieżącej gałęzi.")
    return EXIT_OK


# ---------------------------------------------------------------- G5


def output_lines(output: str) -> list[str]:
    """Normalizuje stdout tak samo jak checker stdout_lines_exact w code.js."""
    normalized = output.replace("\r\n", "\n").replace("\r", "\n")
    if normalized == "":
        return []
    if normalized.endswith("\n"):
        normalized = normalized[:-1]
    return normalized.split("\n")


def run_python(code: str) -> tuple[bool, list[str], str]:
    """Uruchamia kod w CPython; zwraca (sukces, wiersze stdout, stderr)."""
    with tempfile.TemporaryDirectory(prefix="kurs-gate-g5-") as workdir:
        try:
            result = run(
                [sys.executable, "-I", "-X", "utf8", "-c", code],
                cwd=Path(workdir),
                timeout=RUN_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return False, [], f"przekroczono limit {RUN_TIMEOUT} s"
    success = result.returncode == 0 and result.stderr == ""
    return success, output_lines(result.stdout), result.stderr.strip()


def describe_run(lines: list[str], stderr: str) -> str:
    text = f"wypisuje {lines!r}"
    if stderr:
        text += f", stderr: {stderr.splitlines()[-1]!r}"
    return text


def check_code_activity(stage: Stage, where: str, activity: dict) -> int:
    checker = activity.get("checker") or {}
    if checker.get("type") != "stdout_lines_exact":
        stage.problem(f"{where}: nieobsługiwany checker {checker.get('type')!r}")
        return 0
    expected = checker.get("expected_lines")
    solution = activity.get("solution") or {}
    variants = [("rozwiązanie wzorcowe", solution.get("code"))]
    variants += [
        (f"wariant {alternative.get('label')!r}", alternative.get("code"))
        for alternative in solution.get("alternatives") or []
        if isinstance(alternative, dict)
    ]
    runs = 0
    for label, code in variants:
        if not isinstance(code, str):
            continue
        runs += 1
        success, lines, stderr = run_python(code)
        if not success or lines != expected:
            stage.problem(
                f"{where}: {label} {describe_run(lines, stderr)}, "
                f"oczekiwano {expected!r}"
            )
    starter = activity.get("starter_code")
    if isinstance(starter, str):
        runs += 1
        success, lines, _ = run_python(starter)
        if success and lines == expected:
            stage.problem(
                f"{where}: starter_code już wypisuje oczekiwany wynik, "
                "więc zadanie nie wymaga żadnej zmiany"
            )
    return runs


def check_verify_block(stage: Stage, where: str, activity: dict) -> int:
    verify = activity["verify"]
    if not isinstance(verify, dict) or set(verify) != {"code"}:
        stage.problem(f"{where}: blok verify musi być mapą z jednym polem code")
        return 0
    options = {
        option.get("option_id"): option.get("label")
        for option in activity.get("options") or []
        if isinstance(option, dict)
    }
    expected = options.get(activity.get("correct_option_id"))
    success, lines, stderr = run_python(str(verify["code"]))
    printed = "\n".join(lines)
    if not success or printed != expected:
        other = [
            option_id
            for option_id, label in options.items()
            if label == printed and option_id != activity.get("correct_option_id")
        ]
        hint = f" (to etykieta wariantu {other[0]!r})" if other else ""
        stage.problem(
            f"{where}: verify {describe_run(lines, stderr)}{hint}, a poprawna "
            f"odpowiedź ma etykietę {expected!r}"
        )
    return 1


def read_exemptions(text: str) -> tuple[dict[str, str], list[str]]:
    """Odczytuje listę zwolnień z bloku verify.

    Każdy wpis to identyfikator aktywności, po nim znak # i uzasadnienie;
    wiersze puste i wiersze zaczynające się od # pomijamy. Zwraca słownik
    {activity_id: uzasadnienie} i listę błędów formatu.
    """
    exemptions: dict[str, str] = {}
    errors: list[str] = []
    for number, line in enumerate(text.splitlines(), 1):
        content, _, reason = line.partition("#")
        activity_id = content.strip()
        if not activity_id:
            continue
        if len(activity_id.split()) != 1:
            errors.append(f"wiersz {number}: oczekiwano jednego identyfikatora aktywności")
        elif not reason.strip():
            errors.append(f"wiersz {number}: wpis {activity_id!r} nie ma uzasadnienia po znaku #")
        elif activity_id in exemptions:
            errors.append(f"wiersz {number}: powtórzony wpis {activity_id!r}")
        else:
            exemptions[activity_id] = reason.strip()
    return exemptions, errors


def stage_g5(ctx: Context) -> Stage:
    stage = Stage("G5", "rozwiązania wzorcowe i bloki verify")
    stage.start()
    import yaml

    exemptions_path = ctx.tree / EXEMPTIONS_FILE
    text = exemptions_path.read_text(encoding="utf-8") if exemptions_path.is_file() else ""
    exemptions, errors = read_exemptions(text)
    for error in errors:
        stage.problem(f"{EXEMPTIONS_FILE}: {error}")

    runs = verified = exempt = 0
    questions: set[str] = set()
    for source in sorted((ctx.tree / "activities").rglob("*.yaml")):
        relative = source.relative_to(ctx.tree).as_posix()
        try:
            document = yaml.safe_load(source.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue  # zgłoszone w G3
        if not isinstance(document, dict):
            continue  # zgłoszone w G3
        for activity in document.get("activities") or []:
            if not isinstance(activity, dict):
                continue
            activity_id = activity.get("activity_id")
            where = f"{relative}: {activity_id!r}"
            if activity.get("type") == "code":
                runs += check_code_activity(stage, where, activity)
            elif activity.get("type") == "single_choice":
                questions.add(activity_id)
                if "verify" in activity:
                    verified += check_verify_block(stage, where, activity)
                    if activity_id in exemptions:
                        stage.note(
                            f"{where}: pytanie ma blok verify, więc wpis w "
                            f"{EXEMPTIONS_FILE} jest zbędny"
                        )
                elif activity_id in exemptions:
                    exempt += 1
                else:
                    stage.problem(
                        f"{where}: pytanie single_choice nie ma bloku verify; "
                        f"należy go dodać albo wpisać identyfikator z uzasadnieniem "
                        f"do {EXEMPTIONS_FILE}"
                    )
    for activity_id in sorted(set(exemptions) - questions):
        stage.note(
            f"{EXEMPTIONS_FILE}: wpis {activity_id!r} nie wskazuje żadnego "
            "pytania single_choice"
        )
    stage.detail = (
        plural(runs, "uruchomienie", "uruchomienia", "uruchomień")
        + f" kodu, bloki verify: {verified}, pytania zwolnione z verify: {exempt}"
    )
    return stage


# ---------------------------------------------------------------- G6


def node_major(version: str) -> int | None:
    match = re.match(r"v?(\d+)\.", version.strip())
    return int(match.group(1)) if match else None


def node_counts(output: str) -> tuple[int | None, int | None]:
    """Liczby testów udanych i nieudanych z raportu spec (ℹ) albo TAP (#)."""
    counts = []
    for name in ("pass", "fail"):
        match = re.search(rf"^\s*(?:ℹ|#) {name} (\d+)\s*$", output, re.MULTILINE)
        counts.append(int(match.group(1)) if match else None)
    return counts[0], counts[1]


def stage_g6(ctx: Context, skip: bool) -> Stage:
    stage = Stage("G6", "testy unittest i node")
    stage.start()
    if skip:
        stage.skipped = True
        stage.detail = "pominięte na żądanie (--pomin-testy)"
        print("  pominięte na żądanie (--pomin-testy)")
        return stage

    details = []
    for label, start in (("unittest", "tests"), ("unittest kurs/tools", "kurs/tools")):
        result = run(
            [sys.executable, "-m", "unittest", "discover", "-s", start, "-p", "test_*.py"],
            cwd=ctx.tree,
        )
        ran = re.search(r"Ran (\d+) tests?", result.stderr)
        if result.returncode != 0 or not ran or ran.group(1) == "0":
            stage.problem(f"{label} zakończony kodem {result.returncode}")
            print_tail(result.stderr)
        details.append(f"{label} {ran.group(1) if ran else '?'}")

    node = shutil.which("node")
    if node is None:
        stage.problem(f"brak polecenia node w PATH (wymagany Node.js {NODE_MINIMUM}+)")
    else:
        version = run([node, "--version"], cwd=ctx.tree).stdout.strip()
        major = node_major(version)
        if major is None or major < NODE_MINIMUM:
            stage.problem(
                f"node {version or '?'}: wymagany Node.js {NODE_MINIMUM} lub nowszy "
                "(wzorce plików w node --test)"
            )
        else:
            result = run(
                [node, "--test", "--test-reporter=spec", "tests/interactive/*.test.mjs"],
                cwd=ctx.tree,
            )
            passed, failed = node_counts(result.stdout)
            if result.returncode != 0 or not passed or failed:
                stage.problem(
                    f"node --test zakończony kodem {result.returncode} "
                    f"(udane: {passed}, nieudane: {failed})"
                )
                print_tail(result.stdout + result.stderr)
            details.append(f"node {passed if passed is not None else '?'} ({version})")
    stage.detail = "liczba testów: " + ", ".join(details)
    return stage


# ---------------------------------------------------------------- G7


def html_pages(site: Path) -> list[tuple[Path, str]]:
    return [
        (path, path.read_text(encoding="utf-8", errors="replace"))
        for path in sorted(site.rglob("*.html"))
    ]


def stage_g7(ctx: Context) -> Stage:
    stage = Stage("G7", "buildy --strict: książka i wydanie kursowe")
    stage.start()
    workdir = Path(tempfile.mkdtemp(prefix="kurs-gate-g7-"))
    built = []
    try:
        for label, config, folder in (
            ("książka", BOOK_CONFIG, "ksiazka"),
            ("wydanie kursowe", COURSE_CONFIG, "kurs"),
        ):
            site = workdir / folder
            print(f"  budowanie: {label} ({config})…", flush=True)
            result = run(
                [sys.executable, "-m", "mkdocs", "build", "--strict",
                 "-f", config, "-d", str(site)],
                cwd=ctx.tree,
            )
            if result.returncode != 0:
                stage.problem(f"mkdocs build --strict -f {config}: kod {result.returncode}")
                print_tail(result.stdout + result.stderr)
                continue
            pages = html_pages(site)
            if folder == "ksiazka":
                marked = [p for p, text in pages if "data-activity-" in text]
                loading = [p for p, text in pages if LAYER_SCRIPT in text]
                if marked:
                    stage.problem(
                        "książka zawiera znaczniki ćwiczeń (stron: "
                        f"{len(marked)}, np. {marked[0].relative_to(site).as_posix()})"
                    )
                if loading:
                    stage.problem(
                        f"książka ładuje warstwę ćwiczeń (stron: {len(loading)})"
                    )
                copied = list((site / "javascripts" / "interactive").rglob("*.js"))
                if copied:
                    stage.note(
                        "build książki kopiuje pliki JS warstwy jako pliki statyczne "
                        f"(nieładowane, plików: {len(copied)}); wydanie bez ćwiczeń "
                        "musi je wykluczyć we własnej konfiguracji z listy dozwolonej "
                        "(nakładka w kurs/ albo ustawienie wydania w hooku), ponieważ "
                        "mkdocs.yml należy do książki"
                    )
                built.append("książka: " + plural(len(pages), "strona", "strony", "stron"))
            else:
                if not (site / MANIFEST).is_file():
                    stage.problem(f"wydanie kursowe nie zawiera {MANIFEST.as_posix()}")
                with_slot = [p for p, text in pages if "data-activity-slot=" in text]
                if len(with_slot) != len(ctx.activity_pages):
                    stage.problem(
                        f"liczba stron ze slotem ({len(with_slot)}) różni się od "
                        f"liczby stron z aktywnościami ({len(ctx.activity_pages)})"
                    )
                without_layer = [p for p, text in pages if LAYER_SCRIPT not in text]
                if without_layer:
                    stage.problem(
                        f"strony wydania kursowego bez {LAYER_SCRIPT}: "
                        f"{len(without_layer)}"
                    )
                built.append(
                    "kurs: " + plural(len(pages), "strona", "strony", "stron")
                    + f", w tym ze slotem: {len(with_slot)}"
                )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    stage.detail = "; ".join(built)
    return stage


# ---------------------------------------------------------------- całość


def guarded(stage_code: str, title: str, function, *args) -> Stage:
    """Uruchamia etap; nieoczekiwany wyjątek staje się błędem tego etapu."""
    try:
        return function(*args)
    except Exception as error:  # noqa: BLE001 — bramka ma zawsze wypisać tabelę
        stage = Stage(stage_code, title)
        stage.problem(f"nieoczekiwany błąd: {error!r}")
        return stage


def verdict(stages: list[Stage], partial: list[str], head: str) -> tuple[int, str]:
    """Kod wyjścia i zdanie podsumowania; wynik częściowy nigdy nie daje kodu 0."""
    failed = [stage.code for stage in stages if stage.problems]
    if failed:
        return EXIT_FAILED, f"Wynik: bramka nie przeszła ({', '.join(failed)})."
    reasons = list(partial) + [f"pominięto {stage.code}" for stage in stages if stage.skipped]
    if reasons:
        return EXIT_PARTIAL, (
            f"Wynik: sprawdzenie częściowe przeszło ({'; '.join(reasons)}); "
            "to wynik roboczy, który nie służy do odbioru (kod 3)."
        )
    return EXIT_OK, f"Wynik: bramka przeszła dla commitu {head[:7]}."


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Bramka jakości gałęzi ćwiczeń (etapy G1–G7)."
    )
    parser.add_argument(
        "--book", default="dev", help="gałąź książki dla merge-base (domyślnie dev)"
    )
    parser.add_argument(
        "--pomin-testy", action="store_true",
        help="pomija etap G6 (testy); wynik roboczy, kod 3",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--katalog-roboczy", action="store_true",
        help="sprawdza katalog roboczy zamiast commitu HEAD; wynik roboczy, kod 3",
    )
    mode.add_argument(
        "--przed-scaleniem", action="store_true",
        help="wyłącznie etap G1 z próbnym scaleniem książki; wynik częściowy, kod 3",
    )
    mode.add_argument(
        "--zatwierdz-aktualnosc", action="store_true",
        help=f"po przeglądzie aktywności zapisuje odciski sekcji w {LOCK_FILE}; "
        "nie uruchamia etapów",
    )
    args = parser.parse_args(argv)
    if args.zatwierdz_aktualnosc and args.pomin_testy:
        parser.error("opcji --pomin-testy nie łączymy z --zatwierdz-aktualnosc")

    try:
        root = Path(git("rev-parse", "--show-toplevel").strip())
        head = git("rev-parse", "HEAD").strip()
        branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    except GateError as error:
        print(f"Bramka wymaga repozytorium git: {error}", file=sys.stderr)
        return EXIT_USAGE
    os.chdir(root)
    if git_run("rev-parse", "--verify", "--quiet", f"{args.book}^{{commit}}").returncode:
        print(f"Gałąź książki {args.book!r} nie wskazuje commitu.", file=sys.stderr)
        return EXIT_USAGE
    logging.getLogger("mkdocs").setLevel(logging.ERROR)
    if args.zatwierdz_aktualnosc:
        return approve_currency(args.book, root)
    print(f"Bramka gałęzi ćwiczeń: {branch} @ {head[:7]}, książka: {args.book}")

    partial: list[str] = []
    export_dir: Path | None = None
    if args.katalog_roboczy:
        tree = root
        partial.append(f"sprawdzono katalog roboczy, a nie commit {head[:7]}")
        print("Sprawdzany stan: katalog roboczy z niezatwierdzonymi zmianami (tryb roboczy)")
    elif args.przed_scaleniem:
        tree = root
        partial.append("wyłącznie etap G1 przed scaleniem")
        print(f"Sprawdzany stan: commit {head[:7]} przed scaleniem książki (wyłącznie G1)")
    else:
        try:
            export_dir = export_commit(head)
        except GateError as error:
            print(f"Nie można odtworzyć drzewa commitu {head[:7]}: {error}", file=sys.stderr)
            return EXIT_USAGE
        tree = export_dir / "drzewo"
        print(f"Sprawdzany stan: commit {head[:7]} (czysty eksport drzewa do katalogu tymczasowego)")

    ctx = Context(
        book=args.book,
        head=head,
        tree=tree,
        working_tree=args.katalog_roboczy,
        trial_merge=args.przed_scaleniem,
    )
    try:
        stages = [guarded("G1", "wyłączne dodawanie, kolizje i nazwy gałęzi", stage_g1, ctx)]
        if not args.przed_scaleniem:
            stages.append(guarded("G2", "listy nakładki zachowują listy książki", stage_g2, ctx))
            stages.append(guarded("G3", "schemat i wiązania aktywności", stage_g3, ctx))
            stages.append(guarded("G4", "aktualność powiązanych sekcji", stage_g4, ctx))
            stages.append(guarded("G5", "rozwiązania wzorcowe i bloki verify", stage_g5, ctx))
            stages.append(guarded("G6", "testy unittest i node", stage_g6, ctx, args.pomin_testy))
            stages.append(guarded("G7", "buildy --strict: książka i wydanie kursowe", stage_g7, ctx))
    finally:
        if export_dir is not None:
            shutil.rmtree(export_dir, ignore_errors=True)

    print()
    summary = f"Podsumowanie: {branch} @ {head[:7]}, książka {args.book}"
    if ctx.base:
        summary += f" (merge-base {ctx.base[:7]})"
    print(summary)
    width = max(len(stage.title) for stage in stages)
    print(f"{'Etap':<5} {'Sprawdzenie':<{width}}  Wynik")
    for stage in stages:
        detail = f" — {stage.detail}" if stage.detail else ""
        print(f"{stage.code:<5} {stage.title:<{width}}  {stage.result}{detail}")
    if ctx.dirty:
        print(
            "Uwaga: katalog roboczy zawiera niezatwierdzone zmiany plików ćwiczeń "
            f"({ctx.dirty}); wynik dotyczy wyłącznie commitu {head[:7]}."
        )
    code, sentence = verdict(stages, partial, head)
    print(sentence)
    return code


if __name__ == "__main__":
    sys.exit(main())
