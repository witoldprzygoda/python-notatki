"""Bramka jakości gałęzi ćwiczeń (cwiczenia, fala/*, platform/*, sync/*).

Uruchamiamy ją z katalogu roboczego gałęzi ćwiczeń interpreterem, w którym
zainstalowano zależności książki (mkdocs-material); etap G6 wymaga ponadto
Node.js 22 lub nowszego (zalecany 24):

    python kurs/tools/gate.py [--book REF] [--pomin-testy]
                              [--katalog-roboczy | --przed-scaleniem]
    python kurs/tools/gate.py --zatwierdz-aktualnosc [--book REF]
                              [--przejrzane ID[,ID…]]

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
--przejrzane       z --zatwierdz-aktualnosc: przejrzane aktywności, dokładnie
                   te, które wymagają przeglądu (nowe, o zmienionym wiązaniu
                   albo o zmienionej treści sekcji).

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
  G2  nakładka mkdocs.kurs.yml dziedziczy mkdocs.yml, a każda jej lista wspólna
      z książką zaczyna się dokładnie od listy książki (MkDocs zastępuje listy):
      te same pozycje, w tej samej postaci YAML i w tej samej kolejności,
      a własne pozycje nakładki dopiero po nich;
  G3  schemat definicji activities/**/*.yaml oraz wiązania: strona istnieje,
      a section_id jest identyfikatorem nagłówka h2–h6 wygenerowanym na tej
      stronie i nie ma sufiksu deduplikacji; przy zerwanym wiązaniu etap
      zestawia nagłówki strony sprzed ostatniego scalenia książki z obecnymi
      i wskazuje następcę dawnego nagłówka; zmiany wiązań względem tego stanu
      wypisuje razem z tekstami nagłówków;
  G4  aktualność: odcisk treści sekcji powiązanej z każdą aktywnością (od jej
      nagłówka do następnego nagłówka tego samego lub wyższego poziomu, a przy
      section_id: null cała strona) jest równy odciskowi zapisanemu we wpisie
      tej aktywności przy jej ostatnim przeglądzie w kurs/aktualnosc.json;
      zmieniona treść, zmienione wiązanie oraz nowe i usunięte aktywności
      wymagają przeglądu, a etap pokazuje różnicę treści sekcji od stanu
      książki z przeglądu i wskazuje sekcję, do której ta treść przeszła;
  G5  rozwiązanie wzorcowe i rozwiązania alternatywne każdego zadania code
      wypisują w CPython dokładnie checker.expected_lines, a starter_code ich
      nie wypisuje; każde pytanie single_choice ma blok verify, który wypisuje
      dokładnie etykietę poprawnej odpowiedzi, albo figuruje z uzasadnieniem
      w kurs/bez-weryfikacji.txt;
  G6  testy unittest (tests/ i kurs/tools/) oraz node --test (tests/interactive/);
  G7  buildy --strict książki (mkdocs.yml) i wydania kursowego (mkdocs.kurs.yml)
      do katalogu tymczasowego; książka nie może zawierać znaczników ćwiczeń
      ani ładować warstwy, a wydanie kursowe musi zawierać manifest i sloty;
      odsyłacze do brakujących kotwic, które build książki zgłasza wyłącznie
      jako informację, etap wypisuje jako uwagi z przedrostkiem
      „usterka książki:” (nie zatrzymują etapu).

Wiersze „uwaga” są informacyjne i nie zmieniają wyniku etapu; uwagi
z przedrostkiem „usterka książki:” przenosimy do raportu jako usterki książki
do poprawy na gałęzi content/*.

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
1 — wiązania lub definicje wymagają poprawy albo lista --przejrzane nie
obejmuje dokładnie aktywności wymagających przeglądu, a pliku nie zmieniono;
2 — błąd wywołania, w tym --book, którego stan zawiera pliki ćwiczeń.
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
            "takiej książki nie scalamy: kolizję pojedynczej ścieżki rozwiązuje "
            "zmiana jej nazwy po stronie ćwiczeń albo usunięcie jej z książki, "
            "a warstwę ćwiczeń w książce — procedura naprawcza z kurs/README.md"
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


# Reguła G2: lista nakładki wspólna z książką zaczyna się dokładnie od listy
# książki (te same pozycje, w tej samej postaci YAML i w tej samej kolejności),
# a własne pozycje nakładki stoją po niej. Dziś overlay_lists zwraca wyłącznie
# extra_css i extra_javascript, lecz regułę stosujemy do każdej wspólnej listy:
# MkDocs zastępuje całą listę, a kolejność pozycji ma znaczenie w każdej liście
# konfiguracji, którą nakładka mogłaby powtórzyć (kaskada arkuszy stylów,
# kolejność wykonania skryptów, kolejność obsługi zdarzeń przez wtyczki
# i hooki, wariant domyślny palety). Tylko dosłowny prefiks gwarantuje, że
# wydanie kursowe przetwarza książkę tak jak build książki, a warstwa jedynie
# dopisuje swoje pozycje na końcu; liście, w której kolejność nie ma znaczenia
# (np. theme.features), reguła niczego nie odbiera. Pozycje porównujemy przez
# równość, dlatego zmiana postaci (napis 'a.js' zamieniony na mapę z polem
# path) jest błędem: mapa może zmieniać sposób ładowania pliku.


def item_identity(item) -> str | None:
    """Plik, wtyczka albo rozszerzenie, które pozycja listy wskazuje.

    Ta sama pozycja może mieć postać napisu ('a.js', 'toc') albo mapy
    ({'path': 'a.js', 'type': 'module'}, {'toc': {'permalink': True}});
    tożsamość pozwala rozpoznać pozycję książki przepisaną w innej postaci.
    """
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        if isinstance(item.get("path"), str):
            return item["path"]
        if len(item) == 1:
            key = next(iter(item))
            return key if isinstance(key, str) else None
    return None


def list_problems(key: str, overlay: list, book: list) -> list[str]:
    """Zgłoszenia G2 dla jednej listy nakładki wspólnej z książką.

    Lista jest poprawna, gdy zaczyna się od listy książki, a dalej zawiera
    wyłącznie pozycje spoza niej (własne pozycje nakładki).
    """
    if overlay[:len(book)] == book and not any(
        item in book for item in overlay[len(book):]
    ):
        return []
    where = f"lista {key!r} w {COURSE_CONFIG}"
    problems: list[str] = []
    missing = []
    changed = []  # (pozycja książki, ta sama pozycja w innej postaci w nakładce)
    for item in book:
        if item in overlay:
            continue
        identity = item_identity(item)
        twin = next(
            (
                candidate for candidate in overlay
                if candidate not in book
                and identity is not None
                and item_identity(candidate) == identity
            ),
            None,
        )
        if twin is None:
            missing.append(item)
        else:
            changed.append((item, twin))
    if missing:
        problems.append(f"{where} zastępuje listę książki i pomija: {missing}")
    for item, twin in changed:
        problems.append(
            f"{where} zmienia postać pozycji książki: {item!r} → {twin!r}; "
            f"pozycję przepisujemy z {BOOK_CONFIG} dosłownie"
        )
    repeated = []
    for item in book:
        if overlay.count(item) > 1 and item not in repeated:
            repeated.append(item)
    if repeated:
        problems.append(f"{where} powtarza pozycje książki: {repeated}")
    present = []  # pozycje książki w kolejności nakładki (pierwsze wystąpienia)
    for item in overlay:
        if item in book and item not in present:
            present.append(item)
    expected = [item for item in book if item in present]
    if present != expected:
        problems.append(
            f"{where} podaje pozycje książki w innej kolejności niż {BOOK_CONFIG}: "
            f"{present} zamiast {expected}"
        )
    twins = [twin for _, twin in changed]
    last_book = max(
        (index for index, item in enumerate(overlay) if item in book), default=None
    )
    first_own = next(
        (
            index for index, item in enumerate(overlay)
            if item not in book and item not in twins
        ),
        None,
    )
    if last_book is not None and first_own is not None and first_own < last_book:
        problems.append(
            f"{where}: pozycja nakładki {overlay[first_own]!r} poprzedza pozycję "
            f"książki {overlay[last_book]!r}; pozycje książki stoją na początku "
            "listy, przed pozycjami nakładki"
        )
    if not problems:  # zabezpieczenie: prefiksu brak z innego powodu
        problems.append(f"{where} nie zaczyna się od listy książki {book}")
    return problems


def stage_g2(ctx: Context) -> Stage:
    stage = Stage("G2", "listy nakładki zaczynają się od list książki")
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
    checked = []
    for key, value, base in overlay_lists(overlay, book):
        checked.append(key)
        for problem in list_problems(key, value, base):
            stage.problem(problem)
    stage.detail = f"sprawdzone listy wspólne z książką: {len(checked)}"
    if checked:
        stage.detail += f" ({', '.join(checked)})"
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
    from mkdocs.utils import meta

    # Źródło przygotowujemy jak MkDocs (File.content_string i Page.read_source):
    # znaki końca wiersza \n, bez BOM i bez metadanych na początku pliku.
    text = text.replace("\r\n", "\n").replace("\r", "\n").removeprefix("\ufeff")
    text, _ = meta.get_data(text)
    renderer = markdown.Markdown(
        extensions=config["markdown_extensions"],
        extension_configs=config["mdx_configs"],
    )
    html = renderer.convert(text)
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


UNKNOWN_HEADING = "nie jest identyfikatorem nagłówka h2–h6 strony"
DEDUPLICATED_HEADING = "ma sufiks deduplikacji powtórzonego nagłówka"


def binding_problem(section_id, headings: list[tuple[int, str, str]]) -> str | None:
    """Reguły wiązania G3, wspólne dla etapu G3 i polecenia --zatwierdz-aktualnosc.

    Zwraca UNKNOWN_HEADING, gdy section_id nie jest identyfikatorem nagłówka
    h2–h6 strony, DEDUPLICATED_HEADING, gdy ma sufiks deduplikacji nagłówka
    powtórzonego na stronie, albo None, gdy wiązanie jest dozwolone (także
    wiązanie z całą stroną, section_id None).
    """
    if section_id is None:
        return None
    if not isinstance(section_id, str) or section_id not in {
        heading_id for level, heading_id, _ in headings if level >= 2
    }:
        return UNKNOWN_HEADING
    deduplicated = DEDUPLICATED_ID.fullmatch(section_id)
    if deduplicated and deduplicated.group(1) in {heading_id for _, heading_id, _ in headings}:
        return DEDUPLICATED_HEADING
    return None


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
    """Szuka w historii książki obecnej nazwy strony przeniesionej przez git mv.

    Śledzi kolejne przeniesienia (stara nazwa → nowa, od najnowszych), aż
    ścieżka istnieje w książce; zwraca None, gdy łańcuch do niej nie prowadzi.
    """
    output = git(
        "log", book, "--format=", "--name-status", "-z",
        "--find-renames", "--diff-filter=R", "-n", "500",
        check=False,
    )
    fields = [item.strip("\n") for item in output.split("\0")]
    renames: dict[str, str] = {}
    index = 0
    while index < len(fields) - 2:
        if fields[index].startswith("R"):
            renames.setdefault(fields[index + 1], fields[index + 2])  # najnowsze
            index += 3
        else:
            index += 1
    path = f"docs/{page}"
    seen = {path}
    while path in renames:
        path = renames[path]
        if path in seen:
            return None
        seen.add(path)
        if git_run("cat-file", "-e", f"{book}:{path}").returncode == 0:
            return path.removeprefix("docs/")
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
        for activity in document.get("activities") or []:
            if not isinstance(activity, dict):
                continue
            total += 1
            section_id = activity.get("section_id")
            activity_id = activity.get("activity_id")
            if isinstance(activity_id, str):
                current[activity_id] = (page, section_id)
            problem = binding_problem(section_id, headings)
            if problem is UNKNOWN_HEADING:
                hint = rebinding_hint(str(section_id), page, headings, previous, config)
                stage.problem(
                    f"{relative}: aktywność {activity_id!r} ma section_id "
                    f"{section_id!r}, którego nie ma wśród nagłówków h2–h6 "
                    f"strony {page}{hint}"
                )
                print(f"         dostępne: {', '.join(bindable) or 'brak'}")
            elif problem is DEDUPLICATED_HEADING:
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
# we wpisie aktywności w kurs/aktualnosc.json (git show). Nie korzystamy z HTML
# budowanego w G7: zatwierdzenie i odtworzenie dawnej treści wymagałyby pełnego
# buildu, a strona zawiera szablon motywu i znaczniki hooka, które trzeba by
# usuwać.
#
# Stan przeglądu należy do aktywności, a nie do sekcji: każda aktywność ma
# własny wpis w osobnym wierszu pliku, a kurs/.gitattributes nadaje plikowi
# atrybut -merge. Scalenie gałęzi nie może więc przypisać przeglądu jednej
# aktywności innej aktywności powiązanej z tą samą sekcją.

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
# Format pliku kurs/aktualnosc.json: 2 — wpis dla każdej aktywności
# (format 1, z wpisem dla wiązania, istniał wyłącznie na gałęzi roboczej).
LOCK_FORMAT = 2
RECORD_FIELDS = (
    "activity_id", "page", "section_id", "heading",
    "fingerprint", "book_commit", "reviewed_on",
)
FINGERPRINT_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
DATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
# Podobieństwo treści (od 0 do 1), od którego G4 wskazuje sekcję, w której
# znajduje się teraz treść z przeglądu.
RELOCATION_RATIO = 0.8
RESTORE_LOCK = f"git checkout origin/cwiczenia -- {LOCK_FILE}"
# Kolejność zgłoszeń G4 dotyczących jednego wiązania.
REPORT_ORDER = ("broken", "moved", "changed", "new", "stale")


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


def activity_bindings(tree: Path) -> tuple[dict[str, tuple[str, str | None]], list[str]]:
    """Wiązania z definicji w drzewie: {activity_id: (strona, section_id)}.

    Zwraca też błędy definicji: etap G4 je pomija, ponieważ zgłasza je G3,
    a polecenie --zatwierdz-aktualnosc z ich powodu nie zapisuje pliku.
    """
    import yaml

    found: dict[str, tuple[str, str | None]] = {}
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
            if activity_id in found:
                errors.append(f"{relative}: powtórzony activity_id {activity_id!r}")
                continue
            found[activity_id] = (page, section_id)
    return found, errors


def lock_record_problem(record) -> str | None:
    """Opis błędu formatu wpisu aktywności w kurs/aktualnosc.json albo None."""
    if not isinstance(record, dict) or set(record) != set(RECORD_FIELDS):
        return "oczekiwano dokładnie pól: " + ", ".join(RECORD_FIELDS)

    def text(name: str, pattern: re.Pattern[str] | None = None) -> bool:
        value = record[name]
        return isinstance(value, str) and (pattern is None or bool(pattern.fullmatch(value)))

    valid = {
        "activity_id": text("activity_id") and bool(record["activity_id"]),
        "page": text("page"),
        "section_id": record["section_id"] is None or text("section_id"),
        "heading": text("heading"),
        "fingerprint": text("fingerprint", FINGERPRINT_PATTERN),
        "book_commit": text("book_commit", COMMIT_PATTERN),
        "reviewed_on": text("reviewed_on", DATE_PATTERN),
    }
    wrong = [name for name, ok in valid.items() if not ok]
    return "niepoprawne pola: " + ", ".join(wrong) if wrong else None


def read_lock(path: Path) -> tuple[dict | None, list[str]]:
    """Odczytuje kurs/aktualnosc.json.

    Zwraca ({"version": wersja odcisku, "records": {activity_id: wpis}}, błędy);
    przy błędzie formatu pierwszym elementem jest None.
    """
    if not path.is_file():
        return None, [f"brak pliku {LOCK_FILE}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        return None, [
            f"{LOCK_FILE}: niepoprawny JSON (np. znaczniki konfliktu scalenia): {error}"
        ]
    version = data.get("fingerprint_version") if isinstance(data, dict) else None
    if (
        not isinstance(data, dict)
        or set(data) != {"format", "fingerprint_version", "activities"}
        or data["format"] != LOCK_FORMAT
        or not isinstance(version, int)
        or isinstance(version, bool)
        or not isinstance(data["activities"], list)
    ):
        return None, [
            f"{LOCK_FILE}: oczekiwano mapy z polami format ({LOCK_FORMAT}), "
            "fingerprint_version (liczba) i activities (lista wpisów aktywności)"
        ]
    records: dict[str, dict] = {}
    errors: list[str] = []
    for number, record in enumerate(data["activities"], 1):
        problem = lock_record_problem(record)
        if problem:
            errors.append(f"{LOCK_FILE}: wpis {number}: {problem}")
        elif record["activity_id"] in records:
            errors.append(
                f"{LOCK_FILE}: wpis {number}: powtórzona aktywność "
                f"{record['activity_id']!r}"
            )
        else:
            records[record["activity_id"]] = record
    if errors:
        return None, errors
    return {"version": version, "records": records}, []


def write_lock(path: Path, records: dict[str, dict]) -> None:
    """Zapisuje kurs/aktualnosc.json: wpis każdej aktywności w osobnym wierszu.

    Wiersz łączy identyfikator aktywności ze stanem jej przeglądu, więc ani
    scalenie wierszami, ani wybór fragmentu przy konflikcie nie przypisze
    przeglądu jednej aktywności innej aktywności.
    """
    rows = [
        "    " + json.dumps(
            {name: records[activity_id][name] for name in RECORD_FIELDS},
            ensure_ascii=False,
        )
        for activity_id in sorted(records)
    ]
    lines = [
        "{",
        f'  "format": {LOCK_FORMAT},',
        f'  "fingerprint_version": {FINGERPRINT_VERSION},',
        '  "activities": [',
        *(row + ("," if number < len(rows) else "") for number, row in enumerate(rows, 1)),
        "  ]",
        "}",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def content_diff(old: list[str], new: list[str], old_label: str, new_label: str) -> list[str]:
    """Różnica unified treści sekcji, skrócona do około DIFF_LINES wierszy.

    Skrócona różnica zawsze pokazuje pierwsze dodane wiersze (także wtedy, gdy
    poprzedza je długi ciąg usuniętych) i kończy się liczbą wszystkich
    usuniętych i dodanych wierszy.
    """
    lines = list(difflib.unified_diff(old, new, old_label, new_label, n=1, lineterm=""))
    if len(lines) <= DIFF_LINES:
        return lines
    body = lines[2:]
    removed = sum(line.startswith("-") for line in body)
    added = sum(line.startswith("+") for line in body)
    shown = lines[:DIFF_LINES]
    if added and not any(line.startswith("+") for line in shown[2:]):
        half = (DIFF_LINES - 2) // 2
        first = next(
            index for index in range(2, len(lines)) if lines[index].startswith("+")
        )
        shown = lines[:2 + half] + ["…"] + lines[first:first + half]
    return shown + [
        "… różnica skrócona; łącznie usunięto "
        + plural(removed, "wiersz", "wiersze", "wierszy")
        + ", dodano "
        + plural(added, "wiersz", "wiersze", "wierszy")
    ]


def quoted(text: str) -> str:
    return f"„{text}”" if text else "bez nagłówka"


def section_similarity(old: list[str], new: list[str]) -> float:
    """Podobieństwo treści dwóch sekcji bez wierszy nagłówków (od 0 do 1)."""
    return difflib.SequenceMatcher(None, old[1:], new[1:], autojunk=False).ratio()


def relocated_content(
    reviewed: list[str], text: PageText, section_id: str | None
) -> tuple[tuple[int, str, str], float] | None:
    """Nagłówek sekcji, w której znajduje się teraz treść z przeglądu.

    Wskazuje sekcję h2–h6 inną niż section_id, której treść jest podobna do
    treści z przeglądu co najmniej w stopniu RELOCATION_RATIO i bardziej niż
    treść sekcji section_id; w przeciwnym razie zwraca None.
    """
    if len(reviewed) < 2:
        return None  # sekcji bez treści poza nagłówkiem nie da się odnaleźć
    bound = text.lines(section_id) if section_id is not None else None
    bound_ratio = section_similarity(reviewed, bound) if bound is not None else None
    best: tuple[tuple[int, str, str], float] | None = None
    for heading in text.headings:
        level, heading_id, _ = heading
        lines = text.sections.get(heading_id)
        if level < 2 or heading_id == section_id or lines is None:
            continue
        ratio = section_similarity(reviewed, lines)
        if ratio < RELOCATION_RATIO or (bound_ratio is not None and ratio <= bound_ratio):
            continue
        if best is None or ratio > best[1]:
            best = (heading, ratio)
    return best


def describe_relocation(heading: tuple[int, str, str], headings) -> str:
    _, heading_id, name = heading
    message = (
        f"treść z przeglądu znajduje się teraz najpewniej w sekcji {heading_id} "
        f"(„{name}”)"
    )
    if binding_problem(heading_id, headings) is DEDUPLICATED_HEADING:
        return message + (
            "; z identyfikatorem z sufiksem deduplikacji G3 nie pozwala wiązać, "
            "więc o wiązaniu decyduje autor"
        )
    return message + "; należy sprawdzić wiązanie (jak w G3), zamiast dostosowywać aktywność"


class BookPages:
    """Teksty stron książki: bieżące (z katalogu docs albo z commitu) i dawne."""

    def __init__(self, config, *, docs_dir: Path | None = None,
                 commit: str | None = None) -> None:
        self.config = config
        self.docs_dir = docs_dir
        self.commit = commit
        self._now: dict[str, PageText | None] = {}
        self._at: dict[tuple[str, str], PageText | None] = {}

    def now(self, page: str) -> PageText | None:
        if page not in self._now:
            if self.docs_dir is None:
                self._now[page] = self.at(self.commit, page)
            else:
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


def reviewed_lines(record: dict, pages: BookPages) -> list[str] | None:
    """Treść sekcji z przeglądu odtworzona z commitu książki zapisanego we wpisie."""
    text = pages.at(record["book_commit"], record["page"])
    return text.lines(record["section_id"]) if text else None


def review_state(
    binding: tuple[str, str | None] | None,
    record: dict | None,
    pages: BookPages,
    version: int,
) -> str:
    """Stan przeglądu aktywności względem bieżącej treści książki.

    ok — treść i wiązanie jak przy przeglądzie; refresh — jak wyżej, ale wpis
    ma odcisk dawnej wersji; new — brak wpisu; moved — wiązanie inne niż przy
    przeglądzie; changed — zmieniona treść sekcji; broken — wiązanie nie
    wskazuje sekcji książki (G3); stale — wpis aktywności, której już nie ma.
    """
    if binding is None:
        return "stale"
    page, section_id = binding
    text = pages.now(page)
    lines = text.lines(section_id) if text else None
    if lines is None:
        return "broken"
    if record is None:
        return "new"
    if (record["page"], record["section_id"]) != binding:
        return "moved"
    if version == FINGERPRINT_VERSION:
        expected = record["fingerprint"]
    else:
        old = reviewed_lines(record, pages)
        expected = fingerprint(old) if old is not None else None
    if fingerprint(lines) != expected:
        return "changed"
    return "ok" if version == FINGERPRINT_VERSION else "refresh"


class CurrencyReview:
    """Porównanie wiązań sprawdzanego drzewa z wpisami kurs/aktualnosc.json."""

    def __init__(self, stage: Stage, pages: BookPages, lock: dict,
                 placed: dict[str, tuple[str, str | None]], book: str, base: str) -> None:
        self.stage = stage
        self.pages = pages
        self.records: dict[str, dict] = lock["records"]
        self.version = lock["version"]
        self.placed = placed
        self.book = book
        self.base = base
        self.unchanged = 0
        self.to_review: list[str] = []

    def run(self) -> None:
        if self.version != FINGERPRINT_VERSION:
            self.stage.problem(
                f"{LOCK_FILE} zawiera odciski w wersji {self.version}, a bramka "
                f"oblicza wersję {FINGERPRINT_VERSION}; treść porównujemy ze stanem "
                "książki z przeglądu, a wpisy odświeża polecenie --zatwierdz-aktualnosc"
            )
        groups: dict[tuple, list[str]] = {}
        for activity_id in sorted(set(self.placed) | set(self.records)):
            binding = self.placed.get(activity_id)
            record = self.records.get(activity_id)
            state = review_state(binding, record, self.pages, self.version)
            if state in ("ok", "refresh"):
                self.unchanged += 1
                continue
            if state != "stale":
                self.to_review.append(activity_id)
            signature = None if record is None else tuple(
                record[name] for name in RECORD_FIELDS[1:]
            )
            groups.setdefault((state, binding, signature), []).append(activity_id)

        def order(key: tuple) -> tuple:
            state, binding, signature = key
            target = binding or (signature[0], signature[1])
            return binding_order(target), REPORT_ORDER.index(state), str(signature)

        for key in sorted(groups, key=order):
            state, binding, signature = key
            ids = groups[key]
            record = self.records[ids[0]] if signature else None
            getattr(self, f"report_{state}")(binding, record, ids)

    def show_diff(self, record: dict, binding: tuple[str, str | None],
                  lines: list[str]) -> None:
        """Różnica treści od przeglądu i polecenie pokazujące pełne zmiany stron."""
        commit = record["book_commit"]
        source = (record["page"], record["section_id"])
        old_lines = reviewed_lines(record, self.pages)
        if old_lines is None:
            Stage.note(
                f"treści z przeglądu nie można odtworzyć: commit {commit[:7]} nie "
                f"zawiera {binding_name(source)}"
            )
            return
        if self.version == FINGERPRINT_VERSION and fingerprint(old_lines) != record["fingerprint"]:
            Stage.note(
                "treść odtworzona z commitu przeglądu nie odpowiada zapisanemu "
                "odciskowi (np. po zmianie rozszerzeń Markdown książki); różnica "
                "może obejmować także skutki tej zmiany"
            )
        if old_lines == lines:
            print("         treść sekcji bez zmian")
            return
        diff = content_diff(
            old_lines,
            lines,
            f"{binding_name(source)} @ {commit[:7]} (przegląd {record['reviewed_on']})",
            f"{binding_name(binding)} @ {self.base[:7]}",
        )
        for line in diff:
            print(f"         {line}")
        paths = dict.fromkeys((f"docs/{record['page']}", f"docs/{binding[0]}"))
        print(
            f"         pełne zmiany: git diff {commit[:7]} {self.base[:7]} -- "
            + " ".join(paths)
        )

    def relocation(self, binding: tuple[str, str | None],
                   record: dict) -> tuple[list[str], str | None]:
        """Wskazówki i sekcja, gdy treść z przeglądu przeszła pod inny nagłówek.

        Zwraca opisy oraz identyfikator sekcji, z którą należy porównać treść
        z przeglądu: najpierw sekcję o najbardziej podobnej treści, a gdy jej
        nie ma — następcę nagłówka z zestawienia nagłówków (jak w G3).
        """
        page, section_id = binding
        text = self.pages.now(page)
        if section_id is None or text is None:
            return [], None
        hints: list[str] = []
        target = None
        old = self.pages.at(record["book_commit"], record["page"])
        match = align_heading(section_id, old.headings, text.headings) if old else None
        if match and match[1][1] != section_id:
            target = match[1][1]
            hints.append(
                f"identyfikator {section_id} należy teraz do innego nagłówka: "
                + describe_successor(*match)
                + "; należy poprawić wiązanie (jak w G3), zamiast dostosowywać aktywność"
            )
        reviewed = reviewed_lines(record, self.pages)
        found = relocated_content(reviewed, text, section_id) if reviewed else None
        if found and found[0][1] != target:
            hints.append(describe_relocation(found[0], text.headings))
            target = found[0][1]
        return hints, target

    def report_changed(self, binding, record: dict, ids: list[str]) -> None:
        page, section_id = binding
        text = self.pages.now(page)
        heading = text.heading(section_id)
        title = quoted(heading)
        if heading != record["heading"]:
            title = f"{quoted(record['heading'])} → {title}"
        message = (
            f"{binding_name(binding)} ({title}): zmieniła się treść od przeglądu przy "
            f"{record['book_commit'][:7]} ({record['reviewed_on']}); aktywności do "
            "przejrzenia: " + ", ".join(ids)
        )
        hints, target = self.relocation(binding, record)
        self.stage.problem("; ".join([message, *hints]))
        if target is None:
            self.show_diff(record, binding, text.lines(section_id))
        else:  # różnica względem sekcji, do której przeszła treść z przeglądu
            self.show_diff(record, (page, target), text.lines(target))

    def report_moved(self, binding, record: dict, ids: list[str]) -> None:
        page, section_id = binding
        text = self.pages.now(page)
        lines = text.lines(section_id)
        source = (record["page"], record["section_id"])
        message = (
            f"zmiana wiązania bez przeglądu: {', '.join(ids)} z {binding_name(source)} "
            f"({quoted(record['heading'])}, przegląd przy {record['book_commit'][:7]}) "
            f"do {binding_name(binding)} ({quoted(text.heading(section_id))})"
        )
        old_lines = reviewed_lines(record, self.pages)
        if old_lines == lines:
            message += "; treść sekcji bez zmian"
        elif old_lines is not None and old_lines[1:] == lines[1:]:
            message += "; poza nagłówkiem treść sekcji bez zmian"
        self.stage.problem(message + "; aktywności do przejrzenia: " + ", ".join(ids))
        if old_lines != lines:
            self.show_diff(record, binding, lines)

    def report_new(self, binding, record: None, ids: list[str]) -> None:
        page, section_id = binding
        text = self.pages.now(page)
        self.stage.problem(
            f"nowe aktywności bez wpisu w {LOCK_FILE}: {', '.join(ids)}; wiązanie "
            f"{binding_name(binding)} ({quoted(text.heading(section_id))})"
        )

    def report_broken(self, binding, record: dict | None, ids: list[str]) -> None:
        """Wiązanie, którego sekcji nie ma w książce (błąd G3)."""
        if record is None:
            self.stage.problem(
                f"nowe aktywności bez wpisu w {LOCK_FILE}: {', '.join(ids)}; wiązanie "
                f"{binding_name(binding)} nie wskazuje sekcji książki (zob. G3)"
            )
            return
        source = (record["page"], record["section_id"])
        if source != binding:
            self.stage.problem(
                f"zmiana wiązania bez przeglądu: {', '.join(ids)} z "
                f"{binding_name(source)} ({quoted(record['heading'])}, przegląd przy "
                f"{record['book_commit'][:7]}) do {binding_name(binding)}; nowego "
                "wiązania nie ma w książce (zob. G3)"
            )
            return
        page, section_id = binding
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
                old = self.pages.at(record["book_commit"], page)
                match = align_heading(section_id, old.headings, text.headings) if old else None
                if match:
                    reason += "; " + describe_successor(*match)
                    target = (target_page, match[1][1])
                else:
                    reason += "; zestawienie nagłówków nie wskazuje następcy"
                    reviewed = reviewed_lines(record, self.pages)
                    found = relocated_content(reviewed, text, None) if reviewed else None
                    if found:
                        reason += "; " + describe_relocation(found[0], text.headings)
                        target = (target_page, found[0][1])
        self.stage.problem(
            f"{binding_name(binding)} ({quoted(record['heading'])}): {reason}; aktywności "
            "do przejrzenia po poprawie wiązania: " + ", ".join(ids)
        )
        if target is not None:
            self.show_diff(record, target, text.lines(target[1]))

    def report_stale(self, binding: None, record: dict, ids: list[str]) -> None:
        """Wpis aktywności, której nie ma już w definicjach."""
        source = (record["page"], record["section_id"])
        self.stage.problem(
            f"nieaktualny wpis {LOCK_FILE}: {binding_name(source)} "
            f"({quoted(record['heading'])}); aktywności, których już nie ma: "
            + ", ".join(ids)
        )


def stage_g4(ctx: Context, config=None) -> Stage:
    stage = Stage("G4", "aktualność powiązanych sekcji")
    stage.start()
    if config is None:
        from mkdocs.config import load_config

        config = load_config(str(ctx.tree / COURSE_CONFIG))
    docs_dir = Path(config["docs_dir"]) if "docs_dir" in config else ctx.tree / "docs"
    placed, _ = activity_bindings(ctx.tree)  # błędy definicji zgłasza G3
    approve = (
        f"python kurs/tools/gate.py --zatwierdz-aktualnosc --book {ctx.book} "
        "--przejrzane ID[,ID…]"
    )
    counted = f"aktywności: {len(placed)} (wiązania: {len(set(placed.values()))})"
    lock_path = ctx.tree / LOCK_FILE
    lock, errors = read_lock(lock_path)
    for error in errors:
        stage.problem(error)
    if lock is None:
        if lock_path.is_file():
            stage.note(
                f"pliku nie poprawiamy ręcznie: przywracamy wersję z origin/cwiczenia "
                f"({RESTORE_LOCK}), uruchamiamy bramkę, a po przeglądzie wskazanych "
                f"aktywności zapisujemy stan poleceniem: {approve}"
            )
        else:
            stage.note(f"plik tworzy po przeglądzie aktywności polecenie: {approve}")
        stage.detail = f"{counted}, brak poprawnego pliku {LOCK_FILE}"
        return stage
    base = ctx.base or git("merge-base", "HEAD", ctx.book).strip()
    review = CurrencyReview(
        stage, BookPages(config, docs_dir=docs_dir), lock, placed, ctx.book, base
    )
    review.run()
    if review.to_review:
        stage.note(
            f"aktywności do przejrzenia ({len(review.to_review)}): "
            + ", ".join(review.to_review)
        )
    if stage.problems:
        stage.note(
            f"po przeglądzie: {approve}; zmieniony plik {LOCK_FILE} zatwierdzamy commitem"
        )
    stage.detail = f"{counted}, zgodne z przeglądem: {review.unchanged}"
    return stage


def describe_review(state: str, record: dict | None, entry: dict) -> str:
    """Opis wpisu, który zapisuje zatwierdzenie aktywności wymagającej przeglądu."""
    binding = (entry["page"], entry["section_id"])
    if record is None:
        return f"{binding_name(binding)} ({quoted(entry['heading'])})"
    what = []
    source = (record["page"], record["section_id"])
    if state == "moved":
        what.append(f"wiązanie {binding_name(source)} → {binding_name(binding)}")
    if record["heading"] != entry["heading"]:
        what.append(f"nagłówek {quoted(record['heading'])} → {quoted(entry['heading'])}")
    if state == "changed":
        what.append("odcisk treści")
    what.append(
        f"przegląd {record['book_commit'][:7]} ({record['reviewed_on']}) → "
        f"{entry['book_commit'][:7]} ({entry['reviewed_on']})"
    )
    return "; ".join(what)


def approve_currency(book: str, root: Path, reviewed: list[str] | None = None,
                     config=None, today: str | None = None) -> int:
    """Polecenie --zatwierdz-aktualnosc: zapis stanu przeglądu aktywności.

    Wiązania odczytuje z definicji w katalogu roboczym, a odciski oblicza dla
    książki w stanie merge-base(HEAD, book). Aktywność nowa, o zmienionym
    wiązaniu albo o zmienionej treści sekcji wymaga przeglądu: lista reviewed
    (--przejrzane) musi obejmować dokładnie takie aktywności, inaczej pliku nie
    zmienia. Wpis bez zmian zachowuje dawny commit i datę przeglądu, wpis
    o niezmienionej treści, lecz z odciskiem dawnej wersji, dostaje bieżący
    odcisk z tym samym commitem i datą, a wpis aktywności, której już nie ma,
    znika. Gdy któreś wiązanie jest zerwane albo niedozwolone według G3, pliku
    nie zmienia.
    """
    print(
        f"Zatwierdzenie aktualności powiązanych sekcji ({LOCK_FILE}), książka: {book}",
        flush=True,
    )
    try:
        base = git("merge-base", "HEAD", book).strip()
    except GateError as error:
        print(f"Nie można wyznaczyć merge-base z {book!r}: {error}", file=sys.stderr)
        return EXIT_USAGE
    exercise_paths = allowed_paths_in(base)
    if exercise_paths:
        print(
            f"--book musi wskazywać gałąź książki: stan merge-base(HEAD, {book}) = "
            f"{base[:7]} zawiera pliki ćwiczeń ({len(exercise_paths)}, np. "
            f"{exercise_paths[0]}).",
            file=sys.stderr,
        )
        return EXIT_USAGE
    today = today or date.today().isoformat()
    print(f"  stan książki: merge-base(HEAD, {book}) = {base[:7]}, data przeglądu: {today}")
    if config is None:
        from mkdocs.config import load_config

        config = load_config(str(root / COURSE_CONFIG))
    placed, errors = activity_bindings(root)
    if not placed and not errors:
        errors.append("activities/ nie zawiera żadnej aktywności")
    lock_path = root / LOCK_FILE
    lock = None
    if lock_path.exists():
        lock, problems = read_lock(lock_path)
        if lock is None:
            errors += problems
            errors.append(
                f"pliku nie poprawiamy ręcznie: należy przywrócić wersję z "
                f"origin/cwiczenia ({RESTORE_LOCK}) i uruchomić bramkę"
            )
    pages = BookPages(config, commit=base)
    for page in sorted({page for page, _ in placed.values()}):
        if pages.now(page) is None:
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
    for activity_id, binding in sorted(placed.items()):
        text = pages.now(binding[0])
        problem = binding_problem(binding[1], text.headings) if text else None
        if problem:
            errors.append(f"{activity_id}: {binding_name(binding)}: {problem} (zob. G3)")
    if errors:
        for error in errors:
            print(f"  BŁĄD   {error}")
        print(f"Nie zapisano {LOCK_FILE}: najpierw należy poprawić definicje i wiązania.")
        return EXIT_FAILED

    records: dict[str, dict] = lock["records"] if lock else {}
    version = lock["version"] if lock else FINGERPRINT_VERSION
    result: dict[str, dict] = {}
    pending: dict[str, str] = {}  # aktywność wymagająca przeglądu → opis wpisu
    changes: list[tuple[str, str, str]] = []  # (aktywność, rodzaj zmiany, opis)
    unchanged = 0
    for activity_id in sorted(set(placed) | set(records)):
        binding = placed.get(activity_id)
        record = records.get(activity_id)
        state = review_state(binding, record, pages, version)
        if state == "broken":  # wykluczone przez kontrole wyżej; dla pewności
            print(f"  BŁĄD   {activity_id}: wiązanie nie wskazuje sekcji książki (zob. G3)")
            print(f"Nie zapisano {LOCK_FILE}: najpierw należy poprawić definicje i wiązania.")
            return EXIT_FAILED
        if state == "stale":
            source = (record["page"], record["section_id"])
            changes.append(
                (activity_id, "usunięto", f"{binding_name(source)} ({quoted(record['heading'])})")
            )
            continue
        if state == "ok":
            result[activity_id] = record
            unchanged += 1
            continue
        page, section_id = binding
        text = pages.now(page)
        current = fingerprint(text.lines(section_id))
        if state == "refresh":
            result[activity_id] = dict(record, fingerprint=current)
            changes.append(
                (
                    activity_id, "odświeżono",
                    f"odcisk w wersji {version} → {FINGERPRINT_VERSION}, treść bez zmian "
                    f"od przeglądu {record['book_commit'][:7]} ({record['reviewed_on']})",
                )
            )
            continue
        entry = {
            "activity_id": activity_id,
            "page": page,
            "section_id": section_id,
            "heading": text.heading(section_id),
            "fingerprint": current,
            "book_commit": base,
            "reviewed_on": today,
        }
        result[activity_id] = entry
        pending[activity_id] = describe_review(state, record, entry)
        changes.append(
            (activity_id, "dodano" if record is None else "zmieniono", pending[activity_id])
        )

    listed = list(dict.fromkeys(reviewed or []))
    if set(listed) != set(pending):
        if reviewed is None:
            print(
                "  BŁĄD   zatwierdzenie wymaga wskazania przejrzanych aktywności: "
                "--przejrzane ID[,ID…]"
            )
        missing = [item for item in pending if item not in listed]
        extra = [item for item in listed if item not in pending]
        if missing and reviewed is not None:
            print("  BŁĄD   nie wymieniono aktywności wymagających przeglądu: " + ", ".join(missing))
        if extra:
            print(
                "  BŁĄD   wymienione aktywności nie wymagają przeglądu albo nie "
                "istnieją: " + ", ".join(extra)
            )
        print(f"  Aktywności wymagające przeglądu ({len(pending)}):" + ("" if pending else " brak"))
        for activity_id, what in pending.items():
            print(f"    {activity_id}: {what}")
        print(
            f"Nie zapisano {LOCK_FILE}: lista --przejrzane musi obejmować dokładnie "
            "aktywności wymagające przeglądu."
        )
        return EXIT_FAILED

    counts = dict.fromkeys(("dodano", "zmieniono", "odświeżono", "usunięto"), 0)
    for activity_id, kind, what in changes:
        counts[kind] += 1
        print(f"  {kind:<10} {activity_id}: {what}")
    counts["bez zmian"] = unchanged
    summary = ", ".join(f"{name}: {count}" for name, count in counts.items())
    if lock is not None and not changes:
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

# Odsyłacze do brakujących kotwic. MkDocs 1.6 sprawdza je po zbudowaniu stron
# (validation.links.anchors, domyślnie poziom info), więc --strict ich nie
# zatrzymuje. Gdy wyjście nie trafia do terminala, MkDocs wypisuje każdy
# komunikat w jednym wierszu, bez kolorów i bez łamania (format
# '%(levelname)-8s-  %(message)s'), w jednej z dwóch postaci:
#   Doc file 'a.md' contains a link 'b.md#x', but the doc 'b.md' does not
#   contain an anchor '#x'.
#   Doc file 'a.md' contains a link '#x', but there is no such anchor on this
#   page.
# Etap G7 wypisuje je jako uwagi z przedrostkiem BOOK_DEFECT: to usterki
# książki do poprawy na gałęzi content/*, które nie zatrzymują etapu.
BOOK_DEFECT = "usterka książki:"
ANSI_CODE = re.compile(r"\x1b\[[0-9;]*m")
ANCHOR_MESSAGE = re.compile(
    r"^(?:INFO|WARNING)\s*-\s+Doc file '(?P<source>.+?)' contains a link "
    r"'(?P<link>.*)', but (?:there is no such anchor on this page|the doc "
    r"'(?P<target>.+?)' does not contain an anchor '#(?P<anchor>.*)')\.(?P<context>.*)$"
)
# Komunikat o kotwicy w postaci, której ANCHOR_MESSAGE nie rozpoznaje (np. po
# zmianie tekstu w nowej wersji MkDocs); wypisujemy go w całości.
ANCHOR_LINE = re.compile(r"^(?:INFO|WARNING)\s*-\s+(?P<message>Doc file '.*\banchor\b.*)$")


def anchor_defects(output: str) -> list[str]:
    """Opisy odsyłaczy do brakujących kotwic zgłoszonych przez build MkDocs."""
    found: list[str] = []
    for line in output.splitlines():
        line = ANSI_CODE.sub("", line).rstrip()
        match = ANCHOR_MESSAGE.match(line)
        if match is None:
            loose = ANCHOR_LINE.match(line)
            if loose:
                found.append(
                    f"{BOOK_DEFECT} {loose['message']} (komunikat MkDocs w nierozpoznanej postaci)"
                )
            continue
        link, target = match["link"], match["target"]
        if target is None:
            anchor = link.partition("#")[2]
            place = "której nie ma na tej stronie"
        else:
            anchor = match["anchor"]
            place = f"której nie ma na stronie docs/{target}"
        text = (
            f"{BOOK_DEFECT} docs/{match['source']}: odsyłacz {link} wskazuje "
            f"kotwicę #{anchor}, {place}"
        )
        if "footnote" in match["context"]:
            text += " (według MkDocs to przypis, do którego nic się nie odwołuje)"
        found.append(text)
    return list(dict.fromkeys(found))


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
            defects: list[str] = []
            if folder == "ksiazka":
                # Wydanie kursowe buduje te same strony i zgłasza te same
                # odsyłacze, dlatego czytamy wyłącznie build książki.
                defects = anchor_defects(result.stdout + result.stderr)
                for defect in defects:
                    stage.note(defect)
                if defects:
                    stage.note(
                        "usterki książki nie zatrzymują etapu: wpisujemy je do raportu "
                        "jako usterki do poprawy na gałęzi content/*"
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
                        f"(nieładowane, plików: {len(copied)}); na tej gałęzi to stan "
                        "oczekiwany, który nie wymaga działania, a wydanie bez ćwiczeń "
                        "musi je wykluczyć we własnej konfiguracji z listy dozwolonej "
                        "(nakładka w kurs/ albo ustawienie wydania w hooku), ponieważ "
                        "mkdocs.yml należy do książki"
                    )
                built.append(
                    "książka: " + plural(len(pages), "strona", "strony", "stron")
                    + f", usterki książki: {len(defects)}"
                )
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
    parser.add_argument(
        "--przejrzane", action="append", metavar="ID[,ID…]",
        help="z --zatwierdz-aktualnosc: przejrzane aktywności, dokładnie te, "
        "które wymagają przeglądu",
    )
    args = parser.parse_args(argv)
    if args.zatwierdz_aktualnosc and args.pomin_testy:
        parser.error("opcji --pomin-testy nie łączymy z --zatwierdz-aktualnosc")
    if args.przejrzane and not args.zatwierdz_aktualnosc:
        parser.error("opcję --przejrzane łączymy wyłącznie z --zatwierdz-aktualnosc")
    reviewed = None
    if args.przejrzane:
        reviewed = [
            item.strip() for value in args.przejrzane for item in value.split(",")
            if item.strip()
        ]

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
        return approve_currency(args.book, root, reviewed)
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
            stages.append(
                guarded("G2", "listy nakładki zaczynają się od list książki", stage_g2, ctx)
            )
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
