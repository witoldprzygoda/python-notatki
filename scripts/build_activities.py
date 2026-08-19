from __future__ import annotations

import json
import logging
import re
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


log = logging.getLogger("mkdocs.hooks.activities")

SCHEMA_VERSION = 1
SUPPORTED_TYPES = {"acknowledgement", "single_choice", "code"}
REQUIRED_ACTIVITY_FIELDS = {
    "activity_id",
    "version",
    "slot_id",
    "type",
    "label",
}
SLOT_PATTERN = re.compile(r'data-activity-slot\s*=\s*["\']([^"\']+)["\']')

_validated_manifest: dict[str, Any] | None = None


def _require_non_empty_string(value: Any, field: str, source: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{source}: pole {field!r} musi być niepustym tekstem")
    if value != value.strip():
        raise ValueError(f"{source}: pole {field!r} nie może mieć skrajnych spacji")
    return value


def _source_page_path(page: Any, docs_dir: Path, source: Path) -> tuple[str, Path]:
    page_value = _require_non_empty_string(page, "page", source)
    page_path = PurePosixPath(page_value)

    if (
        page_path.is_absolute()
        or ".." in page_path.parts
        or "\\" in page_value
        or page_path.suffix != ".md"
    ):
        raise ValueError(
            f"{source}: pole 'page' musi być względną ścieżką POSIX do pliku .md"
        )

    resolved_docs_dir = docs_dir.resolve()
    resolved_page = (resolved_docs_dir / Path(*page_path.parts)).resolve()
    try:
        resolved_page.relative_to(resolved_docs_dir)
    except ValueError as error:
        raise ValueError(f"{source}: strona wykracza poza katalog docs") from error

    if not resolved_page.is_file():
        raise ValueError(f"{source}: strona {page_value!r} nie istnieje w docs")

    return page_value, resolved_page


def _validate_activity(
    activity: Any,
    *,
    source: Path,
    page: str,
    available_slots: set[str],
    activity_ids: set[str],
) -> dict[str, Any]:
    if not isinstance(activity, dict):
        raise ValueError(f"{source}: każda aktywność musi być mapą YAML")

    missing_fields = REQUIRED_ACTIVITY_FIELDS - activity.keys()
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValueError(f"{source}: aktywność nie zawiera pól: {missing}")

    activity_id = _require_non_empty_string(
        activity["activity_id"], "activity_id", source
    )
    if activity_id in activity_ids:
        raise ValueError(f"{source}: powtórzony activity_id {activity_id!r}")
    activity_ids.add(activity_id)

    version = activity["version"]
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise ValueError(f"{source}: pole 'version' musi być liczbą całkowitą >= 1")

    slot_id = _require_non_empty_string(activity["slot_id"], "slot_id", source)
    if slot_id not in available_slots:
        raise ValueError(
            f"{source}: slot {slot_id!r} nie istnieje na stronie {page!r}"
        )

    activity_type = _require_non_empty_string(activity["type"], "type", source)
    if activity_type not in SUPPORTED_TYPES:
        supported = ", ".join(sorted(SUPPORTED_TYPES))
        raise ValueError(
            f"{source}: nieobsługiwany typ {activity_type!r}; dozwolone: {supported}"
        )

    label = _require_non_empty_string(activity["label"], "label", source)

    return {
        "page": page,
        "activity_id": activity_id,
        "version": version,
        "slot_id": slot_id,
        "type": activity_type,
        "label": label,
    }


def _build_manifest(config: Any) -> dict[str, Any]:
    project_dir = Path(config.config_file_path).resolve().parent
    activities_dir = project_dir / "activities"
    docs_dir = Path(config.docs_dir)
    definition_files = sorted(activities_dir.rglob("*.yaml"))

    if not definition_files:
        raise ValueError(f"Nie znaleziono definicji YAML w {activities_dir}")

    manifest_activities: list[dict[str, Any]] = []
    activity_ids: set[str] = set()

    for source in definition_files:
        try:
            document = yaml.safe_load(source.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            raise ValueError(f"{source}: niepoprawny YAML: {error}") from error

        if not isinstance(document, dict):
            raise ValueError(f"{source}: dokument YAML musi być mapą")
        if document.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(
                f"{source}: schema_version musi mieć wartość {SCHEMA_VERSION}"
            )

        page, source_page = _source_page_path(document.get("page"), docs_dir, source)
        page_text = source_page.read_text(encoding="utf-8")
        available_slots = set(SLOT_PATTERN.findall(page_text))

        activities = document.get("activities")
        if not isinstance(activities, list) or not activities:
            raise ValueError(f"{source}: pole 'activities' musi być niepustą listą")

        for activity in activities:
            manifest_activities.append(
                _validate_activity(
                    activity,
                    source=source,
                    page=page,
                    available_slots=available_slots,
                    activity_ids=activity_ids,
                )
            )

    return {
        "schema_version": SCHEMA_VERSION,
        "activities": manifest_activities,
    }


def on_pre_build(*, config: Any, **kwargs: Any) -> None:
    """Parse and validate activity definitions before MkDocs builds the site."""
    del kwargs
    global _validated_manifest
    _validated_manifest = None
    _validated_manifest = _build_manifest(config)
    log.info(
        "Validated %d activity definition(s)",
        len(_validated_manifest["activities"]),
    )


def on_post_build(*, config: Any, **kwargs: Any) -> None:
    """Write the validated manifest directly to the completed site directory."""
    del kwargs
    if _validated_manifest is None:
        raise RuntimeError("Manifest aktywności nie został zwalidowany w on_pre_build")

    output_path = Path(config.site_dir) / "assets" / "generated" / "activities.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(_validated_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    log.info("Wrote activity manifest to %s", output_path)
