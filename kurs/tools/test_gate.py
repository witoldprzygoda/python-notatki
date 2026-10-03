"""Testy bramki gałęzi ćwiczeń (kurs/tools/gate.py).

Etap G6 bramki uruchamia je poleceniem:

    python -m unittest discover -s kurs/tools -p "test_*.py"

Scenariusze gałęzi powstają w tymczasowych repozytoriach git.
"""

from __future__ import annotations

import contextlib
import difflib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402

MARKDOWN_CONFIG = {"markdown_extensions": ["toc"], "mdx_configs": {}}
# Rozszerzenia Markdown książki (mkdocs.yml) wraz z wbudowanymi rozszerzeniami
# MkDocs, w kolejności, w jakiej podaje je load_config; służą testom etapu G4.
BOOK_MARKDOWN = {
    "markdown_extensions": [
        "toc", "tables", "fenced_code", "admonition", "attr_list", "md_in_html",
        "pymdownx.details", "pymdownx.highlight", "pymdownx.inlinehilite",
        "pymdownx.superfences", "pymdownx.tabbed", "pymdownx.keys",
        "pymdownx.smartsymbols",
    ],
    "mdx_configs": {
        "toc": {"permalink": True},
        "pymdownx.highlight": {"anchor_linenums": True},
        "pymdownx.tabbed": {"alternate_style": True},
    },
}
FENCE = "`" * 3
PAGE = f"""# Pętle

Wstęp do rozdziału.

## Pętla for

Pętla for przechodzi po elementach sekwencji.
Kolejne zdanie opisu.

{FENCE}python title="petla.py"
for znak in "abc":
    print(znak)
# a
{FENCE}

### Odmiana z else

Blok else wykonuje się po pełnym przejściu.

## Pętla while

Pętla while powtarza blok, dopóki warunek jest prawdziwy.

{FENCE}text
## To nie jest nagłówek
{FENCE}

## Przykład

Pierwszy przykład.

## Przykład

Drugi przykład.
"""
OTHER_PAGE = "# Inna strona\n\nTreść innej strony.\n"
ACTIVITIES = """page: petle.md
activities:
  - activity_id: for-quiz
    section_id: petla-for
  - activity_id: for-code
    section_id: petla-for
  - activity_id: while-quiz
    section_id: petla-while
  - activity_id: przyklad-quiz
    section_id: przykad
"""
OTHER_ACTIVITIES = """page: inna.md
activities:
  - activity_id: inna-ack
    section_id: null
"""
GIT_IDENTITY = {
    "GIT_AUTHOR_NAME": "Bramka",
    "GIT_AUTHOR_EMAIL": "bramka@example.invalid",
    "GIT_COMMITTER_NAME": "Bramka",
    "GIT_COMMITTER_EMAIL": "bramka@example.invalid",
}
LAYER = (
    "activities/rozdzial/strona.yaml",
    "kurs/README.md",
    "kurs/tools/gate.py",
    "mkdocs.kurs.yml",
)


class AlignHeadingTest(unittest.TestCase):
    OLD = [
        (1, "petle-i-iteratory", "Pętle i iteratory"),
        (2, "petla-for", "Pętla for"),
        (2, "petla-while", "Pętla while"),
        (2, "iteratory", "Iteratory"),
    ]

    def test_renamed_heading_maps_to_successor_not_to_similar_id(self) -> None:
        new = [
            (1, "petle-i-iteratory", "Pętle i iteratory"),
            (2, "petla-for-i-sekwencje", "Pętla for i sekwencje"),
            (2, "petla-while", "Pętla while"),
            (2, "iteratory", "Iteratory"),
        ]
        bindable = [heading_id for level, heading_id, _ in new if level >= 2]
        similar = difflib.get_close_matches("petla-for", bindable, n=3, cutoff=0.5)
        self.assertEqual(similar[0], "petla-while")  # samo podobieństwo napisów myli

        before, after = gate.align_heading("petla-for", self.OLD, new)

        self.assertEqual(before[1], "petla-for")
        self.assertEqual(after[1], "petla-for-i-sekwencje")

    def test_successor_found_when_heading_count_changes(self) -> None:
        new = [
            (1, "petle-i-iteratory", "Pętle i iteratory"),
            (2, "wprowadzenie", "Wprowadzenie"),
            (2, "petla-for-i-sekwencje", "Pętla for i sekwencje"),
            (3, "zakres", "Zakres"),
            (2, "petla-while", "Pętla while"),
            (2, "iteratory", "Iteratory"),
        ]

        _, after = gate.align_heading("petla-for", self.OLD, new)

        self.assertEqual(after[1], "petla-for-i-sekwencje")

    def test_removed_heading_has_no_successor(self) -> None:
        new = [heading for heading in self.OLD if heading[1] != "petla-for"]

        self.assertIsNone(gate.align_heading("petla-for", self.OLD, new))

    def test_unknown_section_id_has_no_successor(self) -> None:
        self.assertIsNone(gate.align_heading("petla-do", self.OLD, self.OLD))

    def test_unchanged_text_with_new_id_is_reported(self) -> None:
        old = [(2, "przyklad", "Przykład"), (2, "wynik", "Wynik")]
        new = [(2, "przyklad-pierwszy", "Przykład"), (2, "wynik", "Wynik")]

        _, after = gate.align_heading("przyklad", old, new)

        self.assertEqual(after[1], "przyklad-pierwszy")


class ExemptionsTest(unittest.TestCase):
    def test_reads_entries_with_reasons_and_skips_comments(self) -> None:
        text = "# nagłówek\n\nflow-a-quiz-001  # pytanie pojęciowe\nflow-b-quiz-001 # z POC\n"

        exemptions, errors = gate.read_exemptions(text)

        self.assertEqual(
            exemptions,
            {"flow-a-quiz-001": "pytanie pojęciowe", "flow-b-quiz-001": "z POC"},
        )
        self.assertEqual(errors, [])

    def test_reports_missing_reason_duplicate_and_extra_words(self) -> None:
        text = "flow-a\nflow-b # powód\nflow-b # znowu\nflow-c flow-d # powód\n"

        exemptions, errors = gate.read_exemptions(text)

        self.assertEqual(exemptions, {"flow-b": "powód"})
        self.assertEqual(len(errors), 3)
        self.assertIn("wiersz 1", errors[0])
        self.assertIn("uzasadnienia", errors[0])
        self.assertIn("powtórzony", errors[1])
        self.assertIn("jednego identyfikatora", errors[2])


class NodeOutputTest(unittest.TestCase):
    def test_reads_counts_from_spec_and_tap_reports(self) -> None:
        spec = "✔ test (0.1ms)\nℹ tests 153\nℹ suites 0\nℹ pass 153\nℹ fail 0\n"
        tap = "TAP version 13\nok 1 - test\n1..153\n# tests 153\n# pass 152\n# fail 1\n"

        self.assertEqual(gate.node_counts(spec), (153, 0))
        self.assertEqual(gate.node_counts(tap), (152, 1))
        self.assertEqual(gate.node_counts("brak podsumowania"), (None, None))

    def test_reads_major_version(self) -> None:
        self.assertEqual(gate.node_major("v24.19.0"), 24)
        self.assertEqual(gate.node_major("v20.11.1\n"), 20)
        self.assertIsNone(gate.node_major(""))


class VerdictTest(unittest.TestCase):
    HEAD = "abcdef0123456789"

    def test_full_run_on_commit_passes_with_zero(self) -> None:
        code, sentence = gate.verdict([gate.Stage("G1", "a")], [], self.HEAD)

        self.assertEqual(code, gate.EXIT_OK)
        self.assertIn("abcdef0", sentence)

    def test_skipped_stage_never_gives_zero(self) -> None:
        stages = [gate.Stage("G1", "a"), gate.Stage("G6", "b", skipped=True)]

        code, sentence = gate.verdict(stages, [], self.HEAD)

        self.assertEqual(code, gate.EXIT_PARTIAL)
        self.assertIn("pominięto G6", sentence)
        self.assertIn("nie służy do odbioru", sentence)

    def test_working_tree_run_never_gives_zero(self) -> None:
        code, _ = gate.verdict([gate.Stage("G1", "a")], ["katalog roboczy"], self.HEAD)

        self.assertEqual(code, gate.EXIT_PARTIAL)

    def test_failure_takes_precedence(self) -> None:
        stages = [
            gate.Stage("G3", "a", problems=["błąd"]),
            gate.Stage("G6", "b", skipped=True),
        ]

        code, sentence = gate.verdict(stages, ["katalog roboczy"], self.HEAD)

        self.assertEqual(code, gate.EXIT_FAILED)
        self.assertIn("G3", sentence)


class AllowlistTest(unittest.TestCase):
    def test_only_the_sync_skill_is_allowed_under_claude(self) -> None:
        self.assertTrue(gate.is_allowed(".claude/skills/synchronizuj-cwiczenia/SKILL.md"))
        self.assertFalse(gate.is_allowed(".claude/skills/inny/SKILL.md"))
        self.assertFalse(gate.is_allowed(".claude/settings.json"))


class ListingTest(unittest.TestCase):
    def test_lists_first_paths_and_counts_the_rest(self) -> None:
        self.assertEqual(gate.listing(["a", "b"]), "a, b")
        self.assertTrue(gate.listing([f"p{i}" for i in range(10)]).endswith("i 2 kolejne"))
        self.assertTrue(gate.listing([f"p{i}" for i in range(13)]).endswith("i 5 kolejnych"))


class RepositoryTestCase(unittest.TestCase):
    """Tymczasowe repozytorium: dev (książka) i cwiczenia (warstwa)."""

    def setUp(self) -> None:
        self._directory = tempfile.TemporaryDirectory(
            prefix="kurs-gate-test-", ignore_cleanup_errors=True
        )
        self.path = Path(self._directory.name)
        self._previous_cwd = os.getcwd()
        self.git("init", "-q", "-b", "dev")
        self.book = self.commit("Book", {"docs/index.md": "# Książka\n", "mkdocs.yml": "site_name: t\n"})
        self.git("switch", "-q", "-c", "cwiczenia")
        self.layer = self.commit("Layer", {name: f"{name}\n" for name in LAYER})
        self.git("switch", "-q", "dev")
        os.chdir(self.path)

    def tearDown(self) -> None:
        os.chdir(self._previous_cwd)
        self._directory.cleanup()

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", "-c", "core.autocrlf=false", *args],
            cwd=self.path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, **GIT_IDENTITY},
            stdin=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(f"git {' '.join(args)}: {result.stderr}")
        return result.stdout.strip()

    def write(self, files: dict[str, str]) -> None:
        for name, text in files.items():
            target = self.path / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8", newline="\n")

    def commit(self, message: str, files: dict[str, str]) -> str:
        self.write(files)
        self.git("add", "--all")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def run_g1(self, **options) -> tuple[gate.Stage, gate.Context]:
        context = gate.Context(
            book=options.pop("book", "dev"),
            head=self.git("rev-parse", "HEAD"),
            tree=self.path,
            **options,
        )
        with contextlib.redirect_stdout(io.StringIO()):
            stage = gate.stage_g1(context)
        return stage, context

    def assertProblem(self, stage: gate.Stage, *fragments: str) -> None:
        for problem in stage.problems:
            if all(fragment in problem for fragment in fragments):
                return
        self.fail(f"brak problemu zawierającego {fragments}: {stage.problems}")


class StageG1Test(RepositoryTestCase):
    def test_regular_sync_passes_and_finds_the_book_merge(self) -> None:
        self.commit("Book change", {"docs/strona.md": "## Nowa\n"})
        self.git("switch", "-q", "-c", "sync/2026-10-03", "cwiczenia")
        self.git("merge", "-q", "--no-ff", "-m", "Sync", "dev")

        stage, context = self.run_g1()

        self.assertEqual(stage.problems, [])
        self.assertEqual(context.book_merge.exercise_parent, self.layer)

    def test_collision_is_reported_after_the_merge(self) -> None:
        self.commit("Book adds a note under kurs/", {"kurs/notatka.md": "x\n"})
        self.git("switch", "-q", "-c", "sync/2026-10-03", "cwiczenia")
        self.git("merge", "-q", "--no-ff", "-m", "Sync", "dev")

        stage, _ = self.run_g1()

        self.assertProblem(stage, "kolizja", "kurs/notatka.md")

    def test_book_that_absorbed_the_layer_is_stopped_before_and_after_the_merge(self) -> None:
        self.git("merge", "-q", "--no-ff", "-m", "Contamination", "cwiczenia")
        self.git("rm", "-q", "-r", "activities", "kurs", "mkdocs.kurs.yml")
        self.git("commit", "-q", "-m", "Remove the layer from the book")
        self.git("switch", "-q", "-c", "sync/2026-10-03", "cwiczenia")

        before, _ = self.run_g1(trial_merge=True)
        self.git("merge", "-q", "--no-ff", "-m", "Sync", "dev")
        after, _ = self.run_g1()

        self.assertProblem(before, "historia książki", "merge-base")
        self.assertProblem(before, "próbne scalenie", "usunęłoby pliki ćwiczeń")
        self.assertProblem(after, "usunęło pliki ćwiczeń", "kurs/tools/gate.py")
        self.assertProblem(after, "podstawowego pliku warstwy", "kurs/README.md")

    def test_merging_a_book_state_outside_the_book_ref_is_reported(self) -> None:
        self.git("switch", "-q", "-c", "content/nowa-strona", "dev")
        state = self.commit("Unmerged book work", {"docs/nowa.md": "## Nowa\n"})
        self.git("switch", "-q", "-c", "sync/2026-10-03", "cwiczenia")
        self.git("merge", "-q", "--no-ff", "-m", "Sync", "content/nowa-strona")

        stage, _ = self.run_g1()

        self.assertProblem(stage, "wprowadza stan książki", state[:7])
        self.assertProblem(stage, "dodany plik spoza listy dozwolonej", "docs/nowa.md")

    def test_branch_named_like_a_tracked_path_is_reported(self) -> None:
        self.git("switch", "-q", "cwiczenia")
        self.git("branch", "kurs")

        stage, _ = self.run_g1()

        self.assertProblem(stage, "lokalna gałąź 'kurs'")

    def test_uncommitted_changes_do_not_enter_the_commit_result(self) -> None:
        self.git("switch", "-q", "cwiczenia")
        self.write({LAYER[0]: "zmiana robocza\n", "notatki.txt": "x\n"})

        stage, context = self.run_g1()
        _, working = self.run_g1(working_tree=True)

        self.assertEqual(stage.problems, [])
        self.assertEqual(context.dirty, 1)
        self.assertEqual(working.dirty, 0)

    def test_uncommitted_book_change_blocks_in_both_modes(self) -> None:
        self.git("switch", "-q", "cwiczenia")
        self.write({"docs/index.md": "# Zmieniona\n"})

        for options in ({}, {"working_tree": True}):
            stage, _ = self.run_g1(**options)
            self.assertProblem(stage, "niezatwierdzona zmiana pliku książki", "docs/index.md")


class ExportCommitTest(RepositoryTestCase):
    def test_export_holds_the_commit_and_leaves_the_index_untouched(self) -> None:
        self.git("switch", "-q", "cwiczenia")
        self.write({LAYER[0]: "zmiana robocza\n"})

        workdir = gate.export_commit("HEAD")
        try:
            exported = (workdir / "drzewo" / LAYER[0]).read_text(encoding="utf-8")
        finally:
            gate.shutil.rmtree(workdir, ignore_errors=True)

        self.assertEqual(exported.strip(), LAYER[0])
        self.assertEqual(self.git("status", "--porcelain"), f"M {LAYER[0]}")


class RebindingHintTest(RepositoryTestCase):
    def test_hint_names_the_renamed_heading_first(self) -> None:
        page = "# Pętle\n\n## Pętla for\n\n## Pętla while\n"
        previous = self.commit("Page", {"docs/petle.md": page})
        current = page.replace("## Pętla for\n", "## Pętla for i sekwencje\n")
        headings = gate.page_headings(current, MARKDOWN_CONFIG)

        hint = gate.rebinding_hint("petla-for", "petle.md", headings, previous, MARKDOWN_CONFIG)

        self.assertTrue(
            hint.startswith(
                "; prawdopodobna zmiana nagłówka: „Pętla for” → „Pętla for i sekwencje” "
                "(petla-for → petla-for-i-sekwencje)"
            ),
            hint,
        )

    def test_hint_falls_back_to_labelled_similarity(self) -> None:
        headings = gate.page_headings("# P\n\n## Pętla while\n", MARKDOWN_CONFIG)

        hint = gate.rebinding_hint("petla-whil", "petle.md", headings, None, MARKDOWN_CONFIG)

        self.assertIn("wyłącznie podobieństwo napisów", hint)
        self.assertIn("petla-while", hint)


def section_fingerprints(text: str) -> dict[str | None, str]:
    """Odciski całej strony (klucz None) i każdej jej sekcji."""
    page = gate.page_text(text, BOOK_MARKDOWN)
    prints = {None: gate.fingerprint(page.page)}
    prints.update({key: gate.fingerprint(lines) for key, lines in page.sections.items()})
    return prints


class SectionTextTest(unittest.TestCase):
    def test_section_runs_to_the_next_heading_of_the_same_or_higher_level(self) -> None:
        page = gate.page_text(PAGE, BOOK_MARKDOWN)

        loop = page.lines("petla-for")
        subsection = page.lines("odmiana-z-else")

        self.assertEqual(loop[0], "## Pętla for")
        self.assertIn("### Odmiana z else", loop)
        self.assertIn("Blok else wykonuje się po pełnym przejściu.", loop)
        self.assertNotIn("## Pętla while", loop)
        self.assertEqual(
            subsection, ["### Odmiana z else", "Blok else wykonuje się po pełnym przejściu."]
        )
        self.assertEqual(page.lines(None)[0], "# Pętle")
        self.assertIn("Drugi przykład.", page.lines(None))
        self.assertEqual(page.heading(None), "Pętle")
        self.assertEqual(page.heading("petla-for"), "Pętla for")

    def test_code_blocks_keep_lines_and_skip_the_permalink_sign(self) -> None:
        loop = gate.page_text(PAGE, BOOK_MARKDOWN).lines("petla-for")

        start = loop.index("```")
        self.assertEqual(loop[start - 1], "petla.py")
        self.assertEqual(
            loop[start:start + 5],
            ["```", 'for znak in "abc":', "    print(znak)", "# a", "```"],
        )
        self.assertNotIn("¶", "".join(loop))

    def test_heading_inside_fenced_code_does_not_split_the_section(self) -> None:
        page = gate.page_text(PAGE, BOOK_MARKDOWN)

        self.assertIn("## To nie jest nagłówek", page.lines("petla-while"))
        self.assertNotIn("to-nie-jest-naglowek", page.sections)

    def test_duplicate_headings_have_separate_sections(self) -> None:
        before = section_fingerprints(PAGE)
        after = section_fingerprints(PAGE.replace("Drugi przykład.", "Trzeci przykład."))

        page = gate.page_text(PAGE, BOOK_MARKDOWN)
        # Identyfikator pomija literę „ł” (slugify toc), a powtórzenie dostaje sufiks.
        self.assertEqual(page.lines("przykad"), ["## Przykład", "Pierwszy przykład."])
        self.assertEqual(page.lines("przykad_1"), ["## Przykład", "Drugi przykład."])
        self.assertEqual(before["przykad"], after["przykad"])
        self.assertNotEqual(before["przykad_1"], after["przykad_1"])

    def test_line_endings_trailing_spaces_and_rewrapping_keep_the_fingerprint(self) -> None:
        rewrapped = PAGE.replace(
            "Pętla for przechodzi po elementach sekwencji.\nKolejne zdanie opisu.\n",
            "Pętla for przechodzi\npo elementach sekwencji.   Kolejne\n\tzdanie opisu.\n",
        )
        trailing = "\n".join(line + "  " for line in rewrapped.split("\n"))

        self.assertEqual(section_fingerprints(PAGE), section_fingerprints(rewrapped))
        self.assertEqual(section_fingerprints(PAGE), section_fingerprints(trailing))
        self.assertEqual(
            section_fingerprints(PAGE), section_fingerprints(trailing.replace("\n", "\r\n"))
        )

    def test_changes_of_words_numbers_and_code_change_the_fingerprint(self) -> None:
        before = section_fingerprints(PAGE)
        variants = {
            "słowo": PAGE.replace("elementach sekwencji", "znakach sekwencji"),
            "liczba": PAGE.replace("Kolejne zdanie", "Kolejne 2 zdania"),
            "kod": PAGE.replace("print(znak)", "print(znak, end=' ')"),
            "wcięcie": PAGE.replace("    print(znak)", "        print(znak)"),
            "wynik": PAGE.replace("# a\n", "# a b c\n"),
            "tytuł bloku": PAGE.replace('title="petla.py"', 'title="petla-for.py"'),
        }
        for label, variant in variants.items():
            with self.subTest(label):
                after = section_fingerprints(variant)
                self.assertNotEqual(before["petla-for"], after["petla-for"])
                self.assertNotEqual(before[None], after[None])
                self.assertEqual(before["petla-while"], after["petla-while"])

    def test_sentences_split_without_breaking_on_abbreviations_and_numbers(self) -> None:
        text = "Zdanie pierwsze. Zdanie drugie, np. Python. Zob. rozdział 5. Typy złożone."

        self.assertEqual(
            gate.sentences(text),
            ["Zdanie pierwsze.", "Zdanie drugie, np. Python.", "Zob. rozdział 5. Typy złożone."],
        )


class ReadLockTest(unittest.TestCase):
    ENTRY = {
        "page": "petle.md",
        "section_id": "petla-for",
        "heading": "Pętla for",
        "activity_ids": ["for-quiz"],
        "fingerprint": "sha256:" + "0" * 64,
        "book_commit": "a" * 40,
        "reviewed_on": "2026-10-03",
    }

    def read(self, data) -> tuple[dict | None, list[str]]:
        with tempfile.TemporaryDirectory(prefix="kurs-gate-lock-") as directory:
            path = Path(directory) / "aktualnosc.json"
            text = data if isinstance(data, str) else gate.json.dumps(data)
            path.write_text(text, encoding="utf-8")
            return gate.read_lock(path)

    def test_reads_a_valid_file(self) -> None:
        lock, errors = self.read({"fingerprint_version": 1, "bindings": [self.ENTRY]})

        self.assertEqual(errors, [])
        self.assertEqual(list(lock["entries"]), [("petle.md", "petla-for")])

    def test_reports_format_errors(self) -> None:
        broken = dict(self.ENTRY, fingerprint="md5:0", reviewed_on="3 X 2026")
        cases = {
            "niepoprawny JSON": "{",
            "fingerprint, reviewed_on": {"fingerprint_version": 1, "bindings": [broken]},
            "powtórzone wiązanie": {"fingerprint_version": 1, "bindings": [self.ENTRY] * 2},
            "oczekiwano mapy": {"bindings": []},
        }
        for fragment, data in cases.items():
            with self.subTest(fragment):
                lock, errors = self.read(data)
                self.assertIsNone(lock)
                self.assertTrue(any(fragment in error for error in errors), errors)


class StageG4Test(RepositoryTestCase):
    """Synchronizacje w tymczasowym repozytorium: książka (dev) i ćwiczenia."""

    def setUp(self) -> None:
        super().setUp()
        self.reviewed = self.commit(
            "Book pages", {"docs/petle.md": PAGE, "docs/inna.md": OTHER_PAGE}
        )
        self.git("switch", "-q", "cwiczenia")
        self.git("merge", "-q", "--no-ff", "-m", "Sync", "dev")
        self.commit(
            "Activities",
            {LAYER[0]: ACTIVITIES, "activities/rozdzial/inna.yaml": OTHER_ACTIVITIES},
        )
        code, _ = self.approve("2026-10-01")
        self.assertEqual(code, gate.EXIT_OK)
        self.commit("Review", {})

    def approve(self, today: str = "2026-10-03") -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = gate.approve_currency("dev", self.path, BOOK_MARKDOWN, today=today)
        return code, output.getvalue()

    def lock(self) -> dict:
        return gate.read_lock(self.path / gate.LOCK_FILE)[0]["entries"]

    def sync_book(self, files: dict[str, str]) -> None:
        self.git("switch", "-q", "dev")
        self.commit("Book change", files)
        self.git("switch", "-q", "cwiczenia")
        self.git("merge", "-q", "--no-ff", "-m", "Sync", "dev")

    def run_g4(self) -> tuple[gate.Stage, str]:
        context = gate.Context(book="dev", head=self.git("rev-parse", "HEAD"), tree=self.path)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            stage = gate.stage_g4(context, BOOK_MARKDOWN)
        return stage, output.getvalue()

    def test_unchanged_book_passes(self) -> None:
        self.sync_book({"docs/index.md": "# Książka po zmianie\n"})

        stage, _ = self.run_g4()

        self.assertEqual(stage.problems, [])
        self.assertIn("zgodne z przeglądem: 4", stage.detail)

    def test_text_change_inside_a_bound_section_is_flagged_with_a_diff(self) -> None:
        changed = PAGE.replace("Kolejne zdanie opisu.", "Zmienione zdanie opisu.")
        self.sync_book({"docs/petle.md": changed})

        stage, output = self.run_g4()

        self.assertEqual(len(stage.problems), 1, stage.problems)
        self.assertProblem(
            stage, "petle.md#petla-for", "zmieniła się treść", "for-code, for-quiz"
        )
        self.assertIn("-Kolejne zdanie opisu.", output)
        self.assertIn("+Zmienione zdanie opisu.", output)
        self.assertIn(f"git diff {self.reviewed[:7]}", output)

    def test_code_example_change_is_flagged(self) -> None:
        self.sync_book({"docs/petle.md": PAGE.replace("# a\n", "# a\n# b\n# c\n")})

        stage, output = self.run_g4()

        self.assertEqual(len(stage.problems), 1, stage.problems)
        self.assertProblem(stage, "petle.md#petla-for")
        self.assertIn("+# b", output)

    def test_changes_in_other_sections_and_pages_are_not_flagged(self) -> None:
        self.sync_book(
            {
                "docs/petle.md": PAGE.replace("Drugi przykład.", "Drugi, zmieniony przykład.")
                .replace("Wstęp do rozdziału.", "Nowy wstęp do rozdziału."),
                "docs/index.md": "# Książka po zmianie\n",
            }
        )

        stage, _ = self.run_g4()

        self.assertEqual(stage.problems, [])

    def test_line_ending_and_trailing_space_changes_are_not_flagged(self) -> None:
        trailing = "\n".join(line + " " for line in PAGE.split("\n")).replace("\n", "\r\n")
        self.sync_book(
            {"docs/petle.md": trailing, "docs/inna.md": OTHER_PAGE.replace("\n", "\r\n")}
        )

        stage, _ = self.run_g4()

        self.assertEqual(stage.problems, [])

    def test_page_level_binding_covers_the_whole_page(self) -> None:
        self.sync_book({"docs/inna.md": OTHER_PAGE + "\n## Dodatek\n\nNowy akapit.\n"})

        stage, output = self.run_g4()

        self.assertEqual(len(stage.problems), 1, stage.problems)
        self.assertProblem(stage, "inna.md (cała strona)", "inna-ack")
        self.assertIn("+Nowy akapit.", output)

    def test_heading_rename_is_reported_like_in_g3_and_cleared_by_review(self) -> None:
        renamed = PAGE.replace("## Pętla while", "## Pętla while i warunek")
        self.sync_book({"docs/petle.md": renamed})
        headings = gate.page_headings(renamed, BOOK_MARKDOWN)
        hint = gate.rebinding_hint(
            "petla-while", "petle.md", headings, self.reviewed, BOOK_MARKDOWN
        )

        broken, output = self.run_g4()

        self.assertTrue(hint.startswith("; prawdopodobna zmiana nagłówka"), hint)
        self.assertProblem(broken, "petle.md#petla-while", "zob. G3", hint[2:], "while-quiz")
        self.assertIn("+## Pętla while i warunek", output)
        self.assertNotIn("+Pętla while powtarza", output)

        rebound_yaml = ACTIVITIES.replace("petla-while\n", "petla-while-i-warunek\n")
        self.commit("Rebind", {LAYER[0]: rebound_yaml})
        rebound, _ = self.run_g4()
        self.assertEqual(len(rebound.problems), 1, rebound.problems)
        self.assertProblem(
            rebound,
            "zmiana wiązania bez przeglądu: while-quiz",
            "petle.md#petla-while-i-warunek",
            "poza nagłówkiem treść sekcji bez zmian",
        )

        code, report = self.approve()
        self.commit("Review", {})
        reviewed, _ = self.run_g4()
        self.assertEqual(code, gate.EXIT_OK)
        self.assertIn("dodano     petle.md#petla-while-i-warunek", report)
        self.assertIn("usunięto   petle.md#petla-while", report)
        self.assertEqual(reviewed.problems, [])

    def test_new_moved_and_removed_activities_are_reported(self) -> None:
        changed = (
            ACTIVITIES.replace(  # nowa aktywność w wiązaniu z przeglądu
                "  - activity_id: while-quiz\n",
                "  - activity_id: for-nowa\n    section_id: petla-for\n"
                "  - activity_id: while-quiz\n",
            )
            .replace(  # przyklad-quiz usunięta, a nowa aktywność w nowym wiązaniu
                "  - activity_id: przyklad-quiz\n    section_id: przykad\n",
                "  - activity_id: else-quiz\n    section_id: odmiana-z-else\n",
            )
            .replace(  # for-code przeniesiona do podsekcji
                "for-code\n    section_id: petla-for", "for-code\n    section_id: odmiana-z-else"
            )
        )
        self.commit("Activities changed", {LAYER[0]: changed})

        stage, _ = self.run_g4()

        self.assertProblem(
            stage, "petle.md#petla-for", "for-nowa (nowa)",
            "for-code (obecnie petle.md#odmiana-z-else)",
        )
        self.assertProblem(
            stage, "zmiana wiązania bez przeglądu: for-code", "petle.md#odmiana-z-else"
        )
        self.assertProblem(stage, "nowe aktywności bez wpisu", "else-quiz")
        self.assertProblem(stage, "nieaktualny wpis", "petle.md#przykad", "przyklad-quiz")

        code, _ = self.approve()
        self.commit("Review", {})
        self.assertEqual(code, gate.EXIT_OK)
        self.assertEqual(self.run_g4()[0].problems, [])

    def test_missing_lock_blocks(self) -> None:
        self.git("rm", "-q", gate.LOCK_FILE)
        self.git("commit", "-q", "-m", "Remove the lock")

        stage, output = self.run_g4()

        self.assertProblem(stage, "brak pliku kurs/aktualnosc.json")
        self.assertIn("--zatwierdz-aktualnosc", output)

    def test_approval_refuses_broken_bindings_and_keeps_unchanged_entries(self) -> None:
        before = (self.path / gate.LOCK_FILE).read_bytes()
        renamed = PAGE.replace("## Pętla while", "## Pętla while i warunek")
        self.sync_book({"docs/petle.md": renamed})

        refused, report = self.approve()

        self.assertEqual(refused, gate.EXIT_FAILED)
        self.assertIn("petle.md#petla-while", report)
        self.assertEqual((self.path / gate.LOCK_FILE).read_bytes(), before)

        changed = PAGE.replace("Kolejne zdanie opisu.", "Inne zdanie opisu.")
        self.sync_book({"docs/petle.md": changed})
        code, report = self.approve("2026-10-05")
        entries = self.lock()
        book = self.git("rev-parse", "dev")

        self.assertEqual(code, gate.EXIT_OK)
        self.assertIn("zmieniono  petle.md#petla-for", report)
        self.assertEqual(entries["petle.md", "petla-for"]["book_commit"], book)
        self.assertEqual(entries["petle.md", "petla-for"]["reviewed_on"], "2026-10-05")
        self.assertEqual(entries["petle.md", "petla-while"]["book_commit"], self.reviewed)
        self.assertEqual(entries["petle.md", "petla-while"]["reviewed_on"], "2026-10-01")
        self.assertEqual(self.approve()[0], gate.EXIT_OK)
        self.assertIn("jest aktualny", self.approve()[1])


if __name__ == "__main__":
    unittest.main()
