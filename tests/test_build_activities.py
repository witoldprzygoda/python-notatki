import json
import unittest
from collections import UserDict
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
schema_version: 2
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

            self.assertEqual(manifest["schema_version"], 2)
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
schema_version: 2
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
schema_version: 2
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
schema_version: 2
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
schema_version: 2
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


class PageUrlManifestTest(unittest.TestCase):
    def _manifest(self, *pages: str) -> dict:
        return {
            "schema_version": 2,
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
schema_version: 2
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
