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


if __name__ == "__main__":
    unittest.main()
