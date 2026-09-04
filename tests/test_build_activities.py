import json
import unittest
from collections import UserDict
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import scripts.build_activities as build_activities
from scripts.build_activities import (
    _build_manifest,
    _manifest_with_page_urls,
    _presentation_mode,
    _validate_rendered_page,
)


def _config(project_dir: Path) -> SimpleNamespace:
    return SimpleNamespace(
        config_file_path=project_dir / "mkdocs.yml",
        docs_dir=project_dir / "docs",
    )


class ActivitySchemaValidationTest(unittest.TestCase):
    def test_reads_clean_mode_from_mapping_like_mkdocs_extra(self) -> None:
        config = SimpleNamespace(extra=UserDict(presentation_mode="clean"))

        self.assertEqual(_presentation_mode(config), "clean")

    def test_inherits_one_slot_and_preserves_definition_order(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            project_dir = Path(temporary_directory)
            docs_dir = project_dir / "docs"
            activities_dir = project_dir / "activities"
            docs_dir.mkdir()
            activities_dir.mkdir()
            (docs_dir / "page.md").write_text("# Test\n", encoding="utf-8")
            (activities_dir / "page.yaml").write_text(
                """\
schema_version: 3
page: page.md
slot_id: shared-slot
activities:
  - activity_id: first-read-001
    version: 1
    section_id: basics
    type: acknowledgement
    label: Pierwsza
  - activity_id: second-read-001
    version: 1
    section_id: basics
    type: acknowledgement
    label: Druga
""",
                encoding="utf-8",
            )

            manifest = _build_manifest(_config(project_dir))

            self.assertEqual(manifest["schema_version"], 3)
            self.assertEqual(
                [activity["activity_id"] for activity in manifest["activities"]],
                ["first-read-001", "second-read-001"],
            )
            self.assertEqual(
                {activity["slot_id"] for activity in manifest["activities"]},
                {"shared-slot"},
            )
            self.assertEqual(
                {activity["section_id"] for activity in manifest["activities"]},
                {"basics"},
            )
            self.assertTrue(
                all("page_url" not in activity for activity in manifest["activities"])
            )

    def test_rejects_one_top_level_slot_assigned_to_two_pages(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            project_dir = Path(temporary_directory)
            docs_dir = project_dir / "docs"
            activities_dir = project_dir / "activities"
            docs_dir.mkdir()
            activities_dir.mkdir()
            for name in ("first", "second"):
                (docs_dir / f"{name}.md").write_text("# Test\n", encoding="utf-8")
                (activities_dir / f"{name}.yaml").write_text(
                    f"""\
schema_version: 3
page: {name}.md
slot_id: shared-slot
activities:
  - activity_id: {name}-read-001
    version: 1
    section_id: null
    type: acknowledgement
    label: Test
""",
                    encoding="utf-8",
                )

            with self.assertRaises(ValueError) as raised:
                _build_manifest(_config(project_dir))

            self.assertIn("slot 'shared-slot'", str(raised.exception))
            self.assertIn("'first.md'", str(raised.exception))
            self.assertIn("'second.md'", str(raised.exception))

    def test_rejects_missing_section_id(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            project_dir = Path(temporary_directory)
            docs_dir = project_dir / "docs"
            activities_dir = project_dir / "activities"
            docs_dir.mkdir()
            activities_dir.mkdir()
            (docs_dir / "page.md").write_text("# Test\n", encoding="utf-8")
            (activities_dir / "page.yaml").write_text(
                """\
schema_version: 3
page: page.md
slot_id: page-activities
activities:
  - activity_id: test-read-001
    version: 1
    type: acknowledgement
    label: Test
""",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError) as raised:
                _build_manifest(_config(project_dir))

            self.assertIn("section_id", str(raised.exception))

    def test_rejects_generated_page_url_at_document_level(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            project_dir = Path(temporary_directory)
            docs_dir = project_dir / "docs"
            activities_dir = project_dir / "activities"
            docs_dir.mkdir()
            activities_dir.mkdir()
            (docs_dir / "page.md").write_text("# Test\n", encoding="utf-8")
            (activities_dir / "page.yaml").write_text(
                """\
schema_version: 3
page: page.md
page_url: page/
slot_id: page-activities
activities:
  - activity_id: test-read-001
    version: 1
    section_id: null
    type: acknowledgement
    label: Test
""",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError) as raised:
                _build_manifest(_config(project_dir))

            self.assertIn(
                "pole 'page_url' jest generowane przez MkDocs",
                str(raised.exception),
            )

    def test_rejects_previous_schema_version(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            project_dir = Path(temporary_directory)
            docs_dir = project_dir / "docs"
            activities_dir = project_dir / "activities"
            docs_dir.mkdir()
            activities_dir.mkdir()
            (docs_dir / "page.md").write_text("# Test\n", encoding="utf-8")
            (activities_dir / "page.yaml").write_text(
                """\
schema_version: 2
page: page.md
slot_id: page-activities
activities:
  - activity_id: test-read-001
    version: 1
    section_id: null
    type: acknowledgement
    label: Test
""",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError) as raised:
                _build_manifest(_config(project_dir))

            self.assertIn("schema_version musi mieć wartość 3", str(raised.exception))

    def test_rejects_generated_page_url_at_activity_level(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            project_dir = Path(temporary_directory)
            docs_dir = project_dir / "docs"
            activities_dir = project_dir / "activities"
            docs_dir.mkdir()
            activities_dir.mkdir()
            (docs_dir / "page.md").write_text("# Test\n", encoding="utf-8")
            (activities_dir / "page.yaml").write_text(
                """\
schema_version: 3
page: page.md
slot_id: page-activities
activities:
  - activity_id: test-read-001
    version: 1
    section_id: null
    page_url: page/
    type: acknowledgement
    label: Test
""",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError) as raised:
                _build_manifest(_config(project_dir))

            self.assertIn(
                "pole 'page_url' jest generowane przez MkDocs",
                str(raised.exception),
            )


class SolutionSchemaValidationTest(unittest.TestCase):
    source = Path("test-activity.yaml")

    @staticmethod
    def _single_choice() -> dict:
        return {
            "activity_id": "choice-001",
            "version": 1,
            "section_id": "basics",
            "type": "single_choice",
            "label": "Pytanie",
            "prompt": "Wybierz odpowiedź.",
            "options": [
                {"option_id": "a", "label": "Pierwsza"},
                {"option_id": "b", "label": "Druga"},
            ],
            "correct_option_id": "b",
            "feedback": {
                "correct": "Krótka wskazówka po poprawnej odpowiedzi.",
                "incorrect": "Krótka wskazówka po błędnej odpowiedzi.",
            },
            "solution": {
                "discussion": "  Szersze omówienie.\r\nDrugi akapit.  ",
            },
        }

    @staticmethod
    def _code() -> dict:
        return {
            "activity_id": "code-001",
            "version": 1,
            "section_id": "basics",
            "type": "code",
            "label": "Kod",
            "prompt": "Popraw program.",
            "starter_code": "print('start')\n",
            "checker": {
                "type": "stdout_lines_exact",
                "expected_lines": ["wynik"],
            },
            "feedback": {
                "correct": "Krótka wskazówka po poprawnym wyniku.",
                "incorrect": "Krótka wskazówka po błędnym wyniku.",
            },
            "solution": {
                "code": "\nprint('wynik')\r\n",
                "discussion": "  Wyjaśnienie rozwiązania.\r\nDrugi akapit.  ",
                "alternatives": [
                    {
                        "label": "Wariant alternatywny",
                        "code": "print('wynik', end='')\r\n",
                        "discussion": "  Inny sposób uzyskania wyniku.  ",
                    }
                ],
            },
        }

    def _validate(self, activity: dict) -> dict:
        return build_activities._validate_activity(
            activity,
            source=self.source,
            page="page.md",
            slot_id="page-activities",
            activity_ids=set(),
        )

    def test_single_choice_emits_only_normalized_discussion(self) -> None:
        validated = self._validate(self._single_choice())

        self.assertEqual(
            validated["solution"],
            {"discussion": "Szersze omówienie.\nDrugi akapit."},
        )

    def test_code_emits_solution_and_preserves_code_verbatim(self) -> None:
        activity = self._code()

        validated = self._validate(activity)

        self.assertEqual(validated["solution"]["code"], "\nprint('wynik')\r\n")
        self.assertEqual(
            validated["solution"]["discussion"],
            "Wyjaśnienie rozwiązania.\nDrugi akapit.",
        )
        self.assertEqual(
            validated["solution"]["alternatives"],
            [
                {
                    "label": "Wariant alternatywny",
                    "code": "print('wynik', end='')\r\n",
                    "discussion": "Inny sposób uzyskania wyniku.",
                }
            ],
        )

    def test_code_alternatives_are_optional(self) -> None:
        activity = self._code()
        del activity["solution"]["alternatives"]

        validated = self._validate(activity)

        self.assertNotIn("alternatives", validated["solution"])

    def test_requires_solution_for_each_exercise_type(self) -> None:
        for activity in (self._single_choice(), self._code()):
            with self.subTest(activity_type=activity["type"]):
                del activity["solution"]

                with self.assertRaises(ValueError) as raised:
                    self._validate(activity)

                self.assertIn("pole 'solution'", str(raised.exception))
                self.assertIn("musi być mapą", str(raised.exception))

    def test_rejects_non_mapping_solution(self) -> None:
        for invalid_solution in ("tekst", ["tekst"], None):
            with self.subTest(solution=invalid_solution):
                activity = self._single_choice()
                activity["solution"] = invalid_solution

                with self.assertRaises(ValueError) as raised:
                    self._validate(activity)

                self.assertIn("musi być mapą", str(raised.exception))

    def test_single_choice_solution_has_exact_shape(self) -> None:
        cases = {
            "missing": {},
            "unexpected": {
                "discussion": "Omówienie.",
                "correct_option_id": "b",
            },
        }
        for case, solution in cases.items():
            with self.subTest(case=case):
                activity = self._single_choice()
                activity["solution"] = solution

                with self.assertRaises(ValueError) as raised:
                    self._validate(activity)

                self.assertIn("pole 'solution'", str(raised.exception))

    def test_code_solution_has_exact_shape(self) -> None:
        cases = {
            "missing code": {"discussion": "Omówienie."},
            "missing discussion": {"code": "print('wynik')\n"},
            "unexpected": {
                "code": "print('wynik')\n",
                "discussion": "Omówienie.",
                "html": "<strong>tekst</strong>",
            },
        }
        for case, solution in cases.items():
            with self.subTest(case=case):
                activity = self._code()
                activity["solution"] = solution

                with self.assertRaises(ValueError) as raised:
                    self._validate(activity)

                self.assertIn("pole 'solution'", str(raised.exception))

    def test_solution_fields_must_be_non_empty_plain_strings(self) -> None:
        cases = (
            ("single discussion mapping", "single", "discussion", {"text": "x"}),
            ("single discussion blank", "single", "discussion", "   "),
            ("code mapping", "code", "code", {"text": "print()"}),
            ("code blank", "code", "code", "\n  \n"),
            ("code discussion list", "code", "discussion", ["Omówienie"]),
        )
        for case, activity_type, field, invalid_value in cases:
            with self.subTest(case=case):
                activity = (
                    self._single_choice()
                    if activity_type == "single"
                    else self._code()
                )
                activity["solution"][field] = invalid_value

                with self.assertRaises(ValueError):
                    self._validate(activity)

    def test_rejects_solution_discussion_duplicating_correct_feedback(self) -> None:
        for activity in (self._single_choice(), self._code()):
            with self.subTest(activity_type=activity["type"]):
                activity["feedback"]["correct"] = "Pierwszy wiersz.\r\nDrugi wiersz."
                activity["solution"]["discussion"] = (
                    "  Pierwszy wiersz.\nDrugi wiersz.  "
                )

                with self.assertRaises(ValueError) as raised:
                    self._validate(activity)

                self.assertIn(
                    "nie może powtarzać dokładnie",
                    str(raised.exception),
                )

    def test_code_alternatives_must_be_a_non_empty_list(self) -> None:
        for invalid_alternatives in ([], {}, "wariant"):
            with self.subTest(alternatives=invalid_alternatives):
                activity = self._code()
                activity["solution"]["alternatives"] = invalid_alternatives

                with self.assertRaises(ValueError) as raised:
                    self._validate(activity)

                self.assertIn("musi być niepustą listą", str(raised.exception))

    def test_code_alternative_has_exact_shape(self) -> None:
        cases = {
            "not mapping": "wariant",
            "missing discussion": {
                "label": "Wariant",
                "code": "print('wynik')\n",
            },
            "unexpected": {
                "label": "Wariant",
                "code": "print('wynik')\n",
                "discussion": "Omówienie.",
                "html": "<em>tekst</em>",
            },
        }
        for case, alternative in cases.items():
            with self.subTest(case=case):
                activity = self._code()
                activity["solution"]["alternatives"] = [alternative]

                with self.assertRaises(ValueError) as raised:
                    self._validate(activity)

                self.assertIn("solution.alternatives[0]", str(raised.exception))

    def test_code_alternative_fields_must_be_non_empty_plain_strings(self) -> None:
        for field, invalid_value in (
            ("label", "  "),
            ("code", "\n"),
            ("discussion", {"text": "Omówienie"}),
        ):
            with self.subTest(field=field):
                activity = self._code()
                activity["solution"]["alternatives"][0][field] = invalid_value

                with self.assertRaises(ValueError):
                    self._validate(activity)

    def test_rejects_duplicate_alternative_labels(self) -> None:
        activity = self._code()
        duplicate = deepcopy(activity["solution"]["alternatives"][0])
        activity["solution"]["alternatives"].append(duplicate)

        with self.assertRaises(ValueError) as raised:
            self._validate(activity)

        self.assertIn("powtórzona etykieta", str(raised.exception))

    def test_pilot_manifest_emits_all_solutions_and_preserves_versions(self) -> None:
        project_dir = Path(__file__).resolve().parents[1]

        manifest = _build_manifest(_config(project_dir))
        activities = {
            activity["activity_id"]: activity
            for activity in manifest["activities"]
        }

        expected_versions = {
            "flow-for-quiz-001": 2,
            "flow-for-code-001": 2,
            "flow-range-quiz-001": 1,
            "flow-iterator-quiz-001": 1,
            "flow-continue-code-001": 1,
            "flow-if-quiz-001": 1,
            "flow-ternary-quiz-001": 1,
            "flow-match-code-001": 2,
        }
        self.assertEqual(
            {
                activity_id: activities[activity_id]["version"]
                for activity_id in expected_versions
            },
            expected_versions,
        )
        self.assertTrue(
            all(
                "solution" in activities[activity_id]
                for activity_id in expected_versions
            )
        )
        self.assertEqual(
            {
                activity_id
                for activity_id in expected_versions
                if "alternatives" in activities[activity_id]["solution"]
            },
            {"flow-for-code-001", "flow-continue-code-001"},
        )


class PageUrlManifestTest(unittest.TestCase):
    def _manifest(self, *pages: str) -> dict:
        return {
            "schema_version": 3,
            "activities": [
                {
                    "page": page,
                    "activity_id": f"activity-{index}",
                }
                for index, page in enumerate(pages)
            ],
        }

    def test_enriches_copy_and_accepts_empty_home_page_url(self) -> None:
        manifest = self._manifest("index.md")

        published = _manifest_with_page_urls(manifest, {"index.md": ""})

        self.assertEqual(published["activities"][0]["page_url"], "")
        self.assertNotIn("page_url", manifest["activities"][0])
        self.assertIsNot(published["activities"][0], manifest["activities"][0])

    def test_rejects_missing_page_url(self) -> None:
        with self.assertRaises(RuntimeError) as raised:
            _manifest_with_page_urls(self._manifest("missing.md"), {})

        self.assertIn("'missing.md'", str(raised.exception))

    def test_rejects_page_url_shared_by_two_source_pages(self) -> None:
        manifest = self._manifest("first.md", "second.md")

        with self.assertRaises(ValueError) as raised:
            _manifest_with_page_urls(
                manifest,
                {
                    "first.md": "shared/",
                    "second.md": "shared/",
                },
            )

        message = str(raised.exception)
        self.assertIn("page_url 'shared/'", message)
        self.assertIn("'first.md'", message)
        self.assertIn("'second.md'", message)

    def test_hook_publishes_real_mkdocs_page_url(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            project_dir = Path(temporary_directory)
            docs_dir = project_dir / "docs"
            activities_dir = project_dir / "activities"
            site_dir = project_dir / "site"
            docs_dir.mkdir()
            activities_dir.mkdir()
            (docs_dir / "page.md").write_text("# Test\n", encoding="utf-8")
            (activities_dir / "page.yaml").write_text(
                """\
schema_version: 3
page: page.md
slot_id: page-activities
activities:
  - activity_id: test-read-001
    version: 1
    section_id: null
    type: acknowledgement
    label: Test
""",
                encoding="utf-8",
            )
            config = SimpleNamespace(
                config_file_path=project_dir / "mkdocs.yml",
                docs_dir=docs_dir,
                site_dir=site_dir,
                extra={"presentation_mode": "interactive"},
            )
            page = SimpleNamespace(
                file=SimpleNamespace(src_uri="page.md"),
                url="generated/by-mkdocs/",
            )

            build_activities.on_pre_build(config=config)
            build_activities.on_page_content(
                '<div data-activity-slot="page-activities"></div>',
                page=page,
                config=config,
            )
            build_activities.on_post_build(config=config)

            output_path = site_dir / "assets" / "generated" / "activities.json"
            manifest = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(
                manifest["activities"][0]["page_url"],
                "generated/by-mkdocs/",
            )

    def test_clean_hook_validates_but_does_not_publish_manifest(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            project_dir = Path(temporary_directory)
            docs_dir = project_dir / "docs"
            activities_dir = project_dir / "activities"
            site_dir = project_dir / "site"
            docs_dir.mkdir()
            activities_dir.mkdir()
            (docs_dir / "index.md").write_text("# Test\n", encoding="utf-8")
            (activities_dir / "index.yaml").write_text(
                """\
schema_version: 3
page: index.md
slot_id: home-activities
activities:
  - activity_id: test-read-001
    version: 1
    section_id: null
    type: acknowledgement
    label: Test
""",
                encoding="utf-8",
            )
            config = SimpleNamespace(
                config_file_path=project_dir / "mkdocs.yml",
                docs_dir=docs_dir,
                site_dir=site_dir,
                extra={"presentation_mode": "clean"},
            )
            page = SimpleNamespace(
                file=SimpleNamespace(src_uri="index.md"),
                url="",
            )

            build_activities.on_pre_build(config=config)
            build_activities.on_page_content(
                '<div data-activity-slot="home-activities"></div>',
                page=page,
                config=config,
            )
            build_activities.on_post_build(config=config)

            output_path = site_dir / "assets" / "generated" / "activities.json"
            self.assertFalse(output_path.exists())


class RenderedPageValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contracts = {
            "first.md": {
                "slot_id": "first-activities",
                "section_ids": {"basics"},
            }
        }

    def test_accepts_exact_slot_and_marked_anchor(self) -> None:
        physical_slots = {}

        _validate_rendered_page(
            html=(
                '<h2 id="basics" data-activity-section="true">Podstawy</h2>'
                '<div data-activity-slot="first-activities"></div>'
            ),
            page="first.md",
            page_contracts=self.contracts,
            physical_slot_pages=physical_slots,
        )

        self.assertEqual(physical_slots, {"first-activities": "first.md"})

    def test_rejects_duplicate_slot_on_one_page(self) -> None:
        with self.assertRaises(ValueError) as raised:
            _validate_rendered_page(
                html=(
                    '<h2 id="basics" data-activity-section="true">Podstawy</h2>'
                    '<div data-activity-slot="first-activities"></div>'
                    '<div data-activity-slot="first-activities"></div>'
                ),
                page="first.md",
                page_contracts=self.contracts,
                physical_slot_pages={},
            )

        self.assertIn("występuje więcej niż raz", str(raised.exception))

    def test_rejects_same_physical_slot_on_second_page_with_both_names(self) -> None:
        contracts = {
            **self.contracts,
            "second.md": {
                "slot_id": "second-activities",
                "section_ids": set(),
            },
        }

        with self.assertRaises(ValueError) as raised:
            _validate_rendered_page(
                html='<div data-activity-slot="first-activities"></div>',
                page="second.md",
                page_contracts=contracts,
                physical_slot_pages={"first-activities": "first.md"},
            )

        self.assertIn("slot 'first-activities'", str(raised.exception))
        self.assertIn("'first.md'", str(raised.exception))
        self.assertIn("'second.md'", str(raised.exception))

    def test_rejects_section_without_explicit_marker(self) -> None:
        with self.assertRaises(ValueError) as raised:
            _validate_rendered_page(
                html=(
                    '<h2 id="basics">Podstawy</h2>'
                    '<div data-activity-slot="first-activities"></div>'
                ),
                page="first.md",
                page_contracts=self.contracts,
                physical_slot_pages={},
            )

        self.assertIn("section_id 'basics'", str(raised.exception))

    def test_ignores_slot_markup_rendered_as_code(self) -> None:
        with self.assertRaises(ValueError) as raised:
            _validate_rendered_page(
                html=(
                    '<h2 id="basics" data-activity-section="true">Podstawy</h2>'
                    '<code>&lt;div data-activity-slot="first-activities"&gt;'
                    "&lt;/div&gt;</code>"
                ),
                page="first.md",
                page_contracts=self.contracts,
                physical_slot_pages={},
            )

        self.assertIn("brakuje wymaganego slotu", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
