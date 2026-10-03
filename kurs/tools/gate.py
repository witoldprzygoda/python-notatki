"""Bramka jakości gałęzi ćwiczeń (cwiczenia, fala/*, platform/*, sync/*).

Uruchamiamy ją z katalogu roboczego gałęzi ćwiczeń interpreterem, w którym
zainstalowano zależności książki (mkdocs-material):

    python kurs/tools/gate.py [--book REF] [--pomin-testy]

--book         gałąź książki, względem której wyznaczamy merge-base
               (domyślnie dev; podczas synchronizacji origin/dev).
--pomin-testy  pomija etap G6 (testy unittest i node).

Etapy (każdy jest blokujący):
  G1  zasada add-only: względem merge-base(HEAD, REF) gałąź ćwiczeń wyłącznie
      dodaje ścieżki z listy dozwolonej; etap zgłasza także kolizje (książka
      zmieniła ścieżkę należącą do ćwiczeń), pliki ćwiczeń usunięte przez
      ostatnie scalenie i niezatwierdzone zmiany plików książki;
  G2  nakładka mkdocs.kurs.yml dziedziczy mkdocs.yml, a każda jej lista zawiera
      wszystkie pozycje odpowiedniej listy książki (MkDocs zastępuje listy);
  G3  schemat definicji activities/**/*.yaml oraz wiązania: strona istnieje,
      a section_id jest identyfikatorem nagłówka h2–h6 wygenerowanym na tej
      stronie i nie ma sufiksu deduplikacji;
  G5  rozwiązanie wzorcowe i rozwiązania alternatywne każdego zadania code
      wypisują w CPython dokładnie checker.expected_lines, a starter_code ich
      nie wypisuje; opcjonalny blok verify pytania single_choice wypisuje
      dokładnie etykietę poprawnej odpowiedzi;
  G6  testy unittest (tests/) i node --test (tests/interactive/);
  G7  buildy --strict książki (mkdocs.yml) i wydania kursowego (mkdocs.kurs.yml)
      do katalogu tymczasowego; książka nie może zawierać znaczników ćwiczeń
      ani ładować warstwy, a wydanie kursowe musi zawierać manifest i sloty.

Kod wyjścia: 0 — wszystkie etapy przeszły, 1 — co najmniej jeden etap nie
przeszedł, 2 — błąd wywołania (np. brak repozytorium git).
"""

from __future__ import annotations

import argparse
import difflib
import importlib.util
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

sys.dont_write_bytecode = True

ALLOWED_PREFIXES = (
    "activities/",
    "docs/javascripts/interactive/",
    "tests/interactive/",
    "kurs/",
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
BOOK_CONFIG = "mkdocs.yml"
COURSE_CONFIG = "mkdocs.kurs.yml"
MANIFEST = Path("assets") / "generated" / "activities.json"
LAYER_SCRIPT = "javascripts/interactive/bootstrap.js"
# Python-Markdown dopisuje _1, _2… do identyfikatora, który już istnieje na stronie.
DEDUPLICATED_ID = re.compile(r"^(.+)_([0-9]+)$")
RUN_TIMEOUT = 20  # sekundy na jedno uruchomienie kodu w etapie G5


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


def is_allowed(path: str) -> bool:
    return path in ALLOWED_FILES or path.startswith(ALLOWED_PREFIXES)


def plural(count: int, one: str, few: str, many: str) -> str:
    """Dobiera polską formę liczebnika: 1 plik, 2 pliki, 5 plików."""
    if count == 1:
        return f"{count} {one}"
    if count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        return f"{count} {few}"
    return f"{count} {many}"


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


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-c", "core.quotePath=false", *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode != 0:
        raise GateError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def name_status(*args: str) -> list[tuple[str, str]]:
    """Zwraca pary (status, ścieżka) z wyjścia git diff --name-status -z."""
    fields = git("diff", "--name-status", "--no-renames", "-z", *args).split("\0")
    return [
        (fields[index], fields[index + 1])
        for index in range(0, len(fields) - 1, 2)
        if fields[index]
    ]


def print_tail(text: str, lines: int = 25) -> None:
    for line in text.strip().splitlines()[-lines:]:
        print(f"         | {line}")


# ---------------------------------------------------------------- G1


def stage_g1(book: str) -> tuple[Stage, str | None]:
    stage = Stage("G1", "zasada add-only względem książki")
    stage.start()
    try:
        base = git("merge-base", "HEAD", book).strip()
    except GateError as error:
        stage.problem(f"nie można wyznaczyć merge-base z {book!r}: {error}")
        return stage, None
    print(f"  merge-base(HEAD, {book}) = {base[:7]}")

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

    for status, path in name_status(base, book):
        if is_allowed(path):
            stage.problem(
                f"kolizja: książka ({book}) zmieniła ścieżkę należącą do "
                f"ćwiczeń ({status}): {path}"
            )

    parents = git("rev-list", "--parents", "-n", "1", "HEAD").split()
    if len(parents) > 2:
        for status, path in name_status("--diff-filter=D", "HEAD^1", "HEAD"):
            if is_allowed(path):
                stage.problem(f"ostatnie scalenie usunęło plik ćwiczeń: {path}")

    entries = git("status", "--porcelain=v1", "--untracked-files=all", "-z").split("\0")
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        code, path = entry[:2], entry[3:]
        if code[0] in "RC":
            index += 1  # pomijamy starą nazwę przenoszonego pliku
        if is_allowed(path):
            continue
        if code == "??":
            stage.note(f"plik nieśledzony spoza listy dozwolonej: {path}")
        else:
            stage.problem(
                f"niezatwierdzona zmiana pliku spoza listy dozwolonej "
                f"({code.strip()}): {path}"
            )

    stage.detail = (
        plural(added, "dodana ścieżka", "dodane ścieżki", "dodanych ścieżek")
        + f", merge-base {base[:7]}"
    )
    return stage, base


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


def stage_g2(root: Path) -> Stage:
    stage = Stage("G2", "listy nakładki zachowują listy książki")
    stage.start()
    import yaml
    from mkdocs.utils.yaml import get_yaml_loader

    loader = get_yaml_loader()
    configs = []
    for name in (BOOK_CONFIG, COURSE_CONFIG):
        with open(root / name, encoding="utf-8") as stream:
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


def page_headings(path: Path, config) -> list[tuple[int, str, str]]:
    """Zwraca (poziom, id, tekst) nagłówków strony z ustawieniami toc książki."""
    import markdown

    renderer = markdown.Markdown(
        extensions=config["markdown_extensions"],
        extension_configs=config["mdx_configs"],
    )
    renderer.convert(path.read_text(encoding="utf-8"))
    headings: list[tuple[int, str, str]] = []

    def walk(tokens) -> None:
        for token in tokens:
            headings.append((token["level"], token["id"], token["name"]))
            walk(token["children"])

    walk(renderer.toc_tokens)
    return headings


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


def stage_g3(root: Path, book: str) -> tuple[Stage, set[str]]:
    stage = Stage("G3", "schemat i wiązania aktywności")
    stage.start()
    import yaml
    from mkdocs.config import load_config

    config = load_config(str(root / COURSE_CONFIG))
    try:
        load_hook(root)._build_manifest(config)
    except ValueError as error:
        message = str(error).replace(str(root.resolve()) + os.sep, "")
        stage.problem(f"schemat: {message.replace(os.sep, '/')}")

    docs_dir = Path(config["docs_dir"])
    activity_pages: set[str] = set()
    total = 0
    for source in sorted((root / "activities").rglob("*.yaml")):
        relative = source.relative_to(root).as_posix()
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
            new_name = renamed_page(page, book) if isinstance(page, str) else None
            if new_name:
                hint = f"; w książce przeniesiono ją do {new_name} (popraw pole page)"
            stage.problem(f"{relative}: strona {page!r} nie istnieje w docs/{hint}")
            continue
        activity_pages.add(page)

        headings = page_headings(docs_dir / page, config)
        bindable = [heading_id for level, heading_id, _ in headings if level >= 2]
        all_ids = {heading_id for _, heading_id, _ in headings}
        for activity in document.get("activities") or []:
            if not isinstance(activity, dict):
                continue
            total += 1
            section_id = activity.get("section_id")
            activity_id = activity.get("activity_id")
            if section_id is None:
                continue
            if section_id not in bindable:
                similar = difflib.get_close_matches(
                    str(section_id), bindable, n=3, cutoff=0.5
                )
                hint = (
                    "; podobne (tylko sugestia): " + ", ".join(similar)
                    if similar
                    else ""
                )
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

    stage.detail = (
        plural(total, "aktywność", "aktywności", "aktywności")
        + " na "
        + plural(len(activity_pages), "stronie", "stronach", "stronach")
    )
    return stage, activity_pages


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


def stage_g5(root: Path) -> Stage:
    stage = Stage("G5", "rozwiązania wzorcowe i bloki verify")
    stage.start()
    import yaml

    runs = verified = without_verify = 0
    for source in sorted((root / "activities").rglob("*.yaml")):
        relative = source.relative_to(root).as_posix()
        try:
            document = yaml.safe_load(source.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue  # zgłoszone w G3
        for activity in (document or {}).get("activities") or []:
            if not isinstance(activity, dict):
                continue
            where = f"{relative}: {activity.get('activity_id')!r}"
            if activity.get("type") == "code":
                runs += check_code_activity(stage, where, activity)
            elif activity.get("type") == "single_choice":
                if "verify" in activity:
                    verified += check_verify_block(stage, where, activity)
                else:
                    without_verify += 1
    stage.detail = (
        plural(runs, "uruchomienie", "uruchomienia", "uruchomień")
        + f" kodu, bloki verify: {verified}, pytania bez verify: {without_verify}"
    )
    return stage


# ---------------------------------------------------------------- G6


def stage_g6(root: Path, skip: bool) -> Stage:
    stage = Stage("G6", "testy unittest i node")
    stage.start()
    if skip:
        stage.skipped = True
        stage.detail = "pominięte na żądanie (--pomin-testy)"
        print("  pominięte na żądanie (--pomin-testy)")
        return stage

    details = []
    result = run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        cwd=root,
    )
    ran = re.search(r"Ran (\d+) tests?", result.stderr)
    if result.returncode != 0:
        stage.problem(f"unittest zakończony kodem {result.returncode}")
        print_tail(result.stderr)
    details.append(f"unittest {ran.group(1) if ran else '?'}")

    node = shutil.which("node")
    if node is None:
        stage.problem("brak polecenia node w PATH")
    else:
        result = run([node, "--test", "tests/interactive/*.test.mjs"], cwd=root)
        passed = re.search(r"ℹ pass (\d+)", result.stdout)
        failed = re.search(r"ℹ fail (\d+)", result.stdout)
        if result.returncode != 0 or not passed or (failed and failed.group(1) != "0"):
            stage.problem(f"node --test zakończony kodem {result.returncode}")
            print_tail(result.stdout + result.stderr)
        details.append(f"node {passed.group(1) if passed else '?'}")
    stage.detail = "liczba testów: " + ", ".join(details)
    return stage


# ---------------------------------------------------------------- G7


def html_pages(site: Path) -> list[tuple[Path, str]]:
    return [
        (path, path.read_text(encoding="utf-8", errors="replace"))
        for path in sorted(site.rglob("*.html"))
    ]


def stage_g7(root: Path, activity_pages: set[str]) -> Stage:
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
                cwd=root,
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
                        "powinno je wykluczyć przez exclude_docs"
                    )
                built.append("książka: " + plural(len(pages), "strona", "strony", "stron"))
            else:
                if not (site / MANIFEST).is_file():
                    stage.problem(f"wydanie kursowe nie zawiera {MANIFEST.as_posix()}")
                with_slot = [p for p, text in pages if "data-activity-slot=" in text]
                if len(with_slot) != len(activity_pages):
                    stage.problem(
                        f"liczba stron ze slotem ({len(with_slot)}) różni się od "
                        f"liczby stron z aktywnościami ({len(activity_pages)})"
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


def guarded(stage_code: str, title: str, function, *args):
    """Uruchamia etap; nieoczekiwany wyjątek staje się błędem tego etapu."""
    try:
        return function(*args)
    except Exception as error:  # noqa: BLE001 — bramka ma zawsze wypisać tabelę
        stage = Stage(stage_code, title)
        stage.problem(f"nieoczekiwany błąd: {error!r}")
        return stage


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Bramka jakości gałęzi ćwiczeń (etapy G1–G3, G5–G7)."
    )
    parser.add_argument(
        "--book", default="dev", help="gałąź książki dla merge-base (domyślnie dev)"
    )
    parser.add_argument(
        "--pomin-testy", action="store_true", help="pomija etap G6 (testy)"
    )
    args = parser.parse_args(argv)

    try:
        root = Path(git("rev-parse", "--show-toplevel").strip())
        head = git("rev-parse", "--short", "HEAD").strip()
        branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    except GateError as error:
        print(f"Bramka wymaga repozytorium git: {error}", file=sys.stderr)
        return 2
    os.chdir(root)
    logging.getLogger("mkdocs").setLevel(logging.ERROR)
    print(f"Bramka gałęzi ćwiczeń: {branch} @ {head}, książka: {args.book}")

    stages: list[Stage] = []
    first = guarded("G1", "zasada add-only względem książki", stage_g1, args.book)
    if isinstance(first, Stage):
        stages.append(first)
        base = None
    else:
        stages.append(first[0])
        base = first[1]
    stages.append(guarded("G2", "listy nakładki zachowują listy książki", stage_g2, root))
    third = guarded("G3", "schemat i wiązania aktywności", stage_g3, root, args.book)
    activity_pages: set[str] = set()
    if isinstance(third, Stage):
        stages.append(third)
    else:
        stages.append(third[0])
        activity_pages = third[1]
    stages.append(guarded("G5", "rozwiązania wzorcowe i bloki verify", stage_g5, root))
    stages.append(guarded("G6", "testy unittest i node", stage_g6, root, args.pomin_testy))
    stages.append(
        guarded("G7", "buildy --strict: książka i wydanie kursowe", stage_g7, root, activity_pages)
    )

    print()
    summary = f"Podsumowanie: {branch} @ {head}, książka {args.book}"
    if base:
        summary += f" (merge-base {base[:7]})"
    print(summary)
    width = max(len(stage.title) for stage in stages)
    print(f"{'Etap':<5} {'Sprawdzenie':<{width}}  Wynik")
    for stage in stages:
        detail = f" — {stage.detail}" if stage.detail else ""
        print(f"{stage.code:<5} {stage.title:<{width}}  {stage.result}{detail}")
    failed = [stage.code for stage in stages if stage.problems]
    if failed:
        print(f"Wynik: bramka nie przeszła ({', '.join(failed)}).")
        return 1
    print("Wynik: bramka przeszła.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
