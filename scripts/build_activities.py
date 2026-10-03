from __future__ import annotations

import json
import logging
import re
from collections.abc import Mapping
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


log = logging.getLogger("mkdocs.hooks.activities")

SCHEMA_VERSION = 3
SUPPORTED_TYPES = {"acknowledgement", "single_choice", "code"}
REQUIRED_ACTIVITY_FIELDS = {
    "activity_id",
    "version",
    "section_id",
    "type",
    "label",
}
SECTION_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
PRESENTATION_MODES = {"clean", "interactive"}

_validated_manifest: dict[str, Any] | None = None
_page_contracts: dict[str, dict[str, Any]] = {}
_validated_pages: set[str] = set()
_physical_slot_pages: dict[str, str] = {}
_page_urls: dict[str, str] = {}


class _PageActivityMarkupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.slots: list[str] = []
        self.section_markers: list[tuple[str, str | None, str | None]] = []
        self.ids: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self._collect(tag, attrs)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self._collect(tag, attrs)

    def _collect(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.append(attributes["id"] or "")
        if "data-activity-slot" in attributes:
            self.slots.append(attributes["data-activity-slot"] or "")
        if "data-activity-section" in attributes:
            self.section_markers.append(
                (
                    tag,
                    attributes.get("id"),
                    attributes.get("data-activity-section"),
                )
            )


def _require_non_empty_string(value: Any, field: str, source: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{source}: pole {field!r} musi być niepustym tekstem")
    if value != value.strip():
        raise ValueError(f"{source}: pole {field!r} nie może mieć skrajnych spacji")
    return value


def _require_plain_text(value: Any, field: str, source: Path) -> str:
    """Validate author-facing prose and return a stable manifest value."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{source}: pole {field!r} musi być niepustym tekstem")
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def _require_code(value: Any, field: str, source: Path) -> str:
    """Validate code without changing author-provided whitespace."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{source}: pole {field!r} musi zawierać niepusty kod")
    return value


def _require_exact_fields(
    value: dict[str, Any],
    *,
    required: set[str],
    optional: set[str] | None = None,
    field: str,
    source: Path,
) -> None:
    allowed = required | (optional or set())
    missing = required - value.keys()
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"{source}: pole {field!r} nie zawiera pól: {names}")

    unexpected = value.keys() - allowed
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ValueError(f"{source}: pole {field!r} zawiera nieznane pola: {names}")


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
    slot_id: str,
    activity_ids: set[str],
) -> dict[str, Any]:
    if not isinstance(activity, dict):
        raise ValueError(f"{source}: każda aktywność musi być mapą YAML")

    if "slot_id" in activity:
        raise ValueError(
            f"{source}: w schema_version {SCHEMA_VERSION} pole 'slot_id' należy umieścić "
            "na poziomie dokumentu, nie aktywności"
        )
    if "page_url" in activity:
        raise ValueError(
            f"{source}: pole 'page_url' jest generowane przez MkDocs i nie może "
            "występować w definicji aktywności"
        )

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

    section_value = activity["section_id"]
    if section_value is None:
        section_id = None
    else:
        section_id = _require_non_empty_string(
            section_value, "section_id", source
        )
        if not SECTION_ID_PATTERN.fullmatch(section_id):
            raise ValueError(
                f"{source}: pole 'section_id' musi być stabilnym identyfikatorem "
                "złożonym z małych liter, cyfr i łączników"
            )

    activity_type = _require_non_empty_string(activity["type"], "type", source)
    if activity_type not in SUPPORTED_TYPES:
        supported = ", ".join(sorted(SUPPORTED_TYPES))
        raise ValueError(
            f"{source}: nieobsługiwany typ {activity_type!r}; dozwolone: {supported}"
        )

    label = _require_non_empty_string(activity["label"], "label", source)

    validated_activity = {
        "page": page,
        "activity_id": activity_id,
        "version": version,
        "slot_id": slot_id,
        "section_id": section_id,
        "type": activity_type,
        "label": label,
    }

    if activity_type == "single_choice":
        validated_activity.update(_validate_single_choice(activity, source))
    elif activity_type == "code":
        validated_activity.update(_validate_code(activity, source))

    return validated_activity


def _validate_single_choice(activity: dict[str, Any], source: Path) -> dict[str, Any]:
    prompt = _require_non_empty_string(activity.get("prompt"), "prompt", source)

    options = activity.get("options")
    if not isinstance(options, list) or len(options) < 2:
        raise ValueError(
            f"{source}: pole 'options' aktywności single_choice musi zawierać "
            "co najmniej dwa warianty"
        )

    validated_options: list[dict[str, str]] = []
    option_ids: set[str] = set()
    for option in options:
        if not isinstance(option, dict):
            raise ValueError(f"{source}: każdy wariant odpowiedzi musi być mapą YAML")

        option_id = _require_non_empty_string(
            option.get("option_id"), "option_id", source
        )
        if option_id in option_ids:
            raise ValueError(f"{source}: powtórzony option_id {option_id!r}")
        option_ids.add(option_id)

        option_label = _require_non_empty_string(
            option.get("label"), "label wariantu odpowiedzi", source
        )
        validated_options.append(
            {
                "option_id": option_id,
                "label": option_label,
            }
        )

    correct_option_id = _require_non_empty_string(
        activity.get("correct_option_id"), "correct_option_id", source
    )
    if correct_option_id not in option_ids:
        raise ValueError(
            f"{source}: correct_option_id {correct_option_id!r} nie wskazuje "
            "istniejącego wariantu"
        )

    feedback = activity.get("feedback")
    if not isinstance(feedback, dict):
        raise ValueError(
            f"{source}: pole 'feedback' aktywności single_choice musi być mapą"
        )

    validated_feedback = {
        "correct": _require_non_empty_string(
            feedback.get("correct"), "feedback.correct", source
        ),
        "incorrect": _require_non_empty_string(
            feedback.get("incorrect"), "feedback.incorrect", source
        ),
    }
    solution = _validate_solution(
        activity,
        source=source,
        activity_type="single_choice",
        feedback_correct=validated_feedback["correct"],
    )

    return {
        "prompt": prompt,
        "options": validated_options,
        "correct_option_id": correct_option_id,
        "feedback": validated_feedback,
        "solution": solution,
    }


def _validate_solution(
    activity: dict[str, Any],
    *,
    source: Path,
    activity_type: str,
    feedback_correct: str,
) -> dict[str, Any]:
    solution = activity.get("solution")
    if not isinstance(solution, dict):
        raise ValueError(
            f"{source}: pole 'solution' aktywności {activity_type} musi być mapą"
        )

    if activity_type == "single_choice":
        _require_exact_fields(
            solution,
            required={"discussion"},
            field="solution",
            source=source,
        )
    elif activity_type == "code":
        _require_exact_fields(
            solution,
            required={"code", "discussion"},
            optional={"alternatives"},
            field="solution",
            source=source,
        )
    else:  # pragma: no cover - callers are limited to the two active types
        raise ValueError(f"{source}: rozwiązanie nie obsługuje typu {activity_type!r}")

    discussion = _require_plain_text(
        solution.get("discussion"), "solution.discussion", source
    )
    normalized_feedback_correct = feedback_correct.replace("\r\n", "\n").replace(
        "\r", "\n"
    )
    if discussion == normalized_feedback_correct:
        raise ValueError(
            f"{source}: pole 'solution.discussion' nie może powtarzać dokładnie "
            "treści 'feedback.correct'"
        )

    validated_solution: dict[str, Any] = {"discussion": discussion}
    if activity_type == "single_choice":
        return validated_solution

    validated_solution["code"] = _require_code(
        solution.get("code"), "solution.code", source
    )

    if "alternatives" not in solution:
        return validated_solution

    alternatives = solution["alternatives"]
    if not isinstance(alternatives, list) or not alternatives:
        raise ValueError(
            f"{source}: pole 'solution.alternatives' musi być niepustą listą"
        )

    validated_alternatives: list[dict[str, str]] = []
    alternative_labels: set[str] = set()
    for index, alternative in enumerate(alternatives):
        field = f"solution.alternatives[{index}]"
        if not isinstance(alternative, dict):
            raise ValueError(f"{source}: pole {field!r} musi być mapą")
        _require_exact_fields(
            alternative,
            required={"label", "code", "discussion"},
            field=field,
            source=source,
        )

        label = _require_non_empty_string(
            alternative.get("label"), f"{field}.label", source
        )
        if label in alternative_labels:
            raise ValueError(
                f"{source}: powtórzona etykieta alternatywnego rozwiązania "
                f"{label!r}"
            )
        alternative_labels.add(label)

        validated_alternatives.append(
            {
                "label": label,
                "code": _require_code(
                    alternative.get("code"), f"{field}.code", source
                ),
                "discussion": _require_plain_text(
                    alternative.get("discussion"),
                    f"{field}.discussion",
                    source,
                ),
            }
        )

    validated_solution["alternatives"] = validated_alternatives
    return validated_solution


def _validate_code(activity: dict[str, Any], source: Path) -> dict[str, Any]:
    prompt = _require_non_empty_string(activity.get("prompt"), "prompt", source)

    starter_code = _require_code(activity.get("starter_code"), "starter_code", source)

    checker = activity.get("checker")
    if not isinstance(checker, dict):
        raise ValueError(f"{source}: pole 'checker' aktywności code musi być mapą")

    checker_type = _require_non_empty_string(
        checker.get("type"), "checker.type", source
    )
    if checker_type != "stdout_lines_exact":
        raise ValueError(
            f"{source}: nieobsługiwany checker code {checker_type!r}; "
            "dozwolony: 'stdout_lines_exact'"
        )

    expected_lines = checker.get("expected_lines")
    if not isinstance(expected_lines, list) or not expected_lines:
        raise ValueError(
            f"{source}: pole 'checker.expected_lines' musi być niepustą listą"
        )

    validated_lines: list[str] = []
    for line in expected_lines:
        if not isinstance(line, str):
            raise ValueError(
                f"{source}: każdy element 'checker.expected_lines' musi być tekstem"
            )
        if "\n" in line or "\r" in line:
            raise ValueError(
                f"{source}: element 'checker.expected_lines' nie może zawierać "
                "znaku końca linii"
            )
        validated_lines.append(line)

    feedback = activity.get("feedback")
    if not isinstance(feedback, dict):
        raise ValueError(f"{source}: pole 'feedback' aktywności code musi być mapą")

    validated_feedback = {
        "correct": _require_non_empty_string(
            feedback.get("correct"), "feedback.correct", source
        ),
        "incorrect": _require_non_empty_string(
            feedback.get("incorrect"), "feedback.incorrect", source
        ),
    }
    solution = _validate_solution(
        activity,
        source=source,
        activity_type="code",
        feedback_correct=validated_feedback["correct"],
    )

    return {
        "prompt": prompt,
        "starter_code": starter_code,
        "checker": {
            "type": checker_type,
            "expected_lines": validated_lines,
        },
        "feedback": validated_feedback,
        "solution": solution,
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
    definition_pages: dict[str, Path] = {}
    slot_pages: dict[str, str] = {}

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
        if "page_url" in document:
            raise ValueError(
                f"{source}: pole 'page_url' jest generowane przez MkDocs i nie "
                "może występować w źródłowym YAML"
            )

        page, _ = _source_page_path(document.get("page"), docs_dir, source)
        previous_source = definition_pages.get(page)
        if previous_source is not None:
            raise ValueError(
                f"{source}: strona {page!r} ma już definicję aktywności "
                f"w {previous_source}"
            )
        definition_pages[page] = source

        slot_id = _require_non_empty_string(
            document.get("slot_id"), "slot_id", source
        )
        previous_page = slot_pages.get(slot_id)
        if previous_page is not None:
            raise ValueError(
                f"slot {slot_id!r} jest przypisany do więcej niż jednej strony: "
                f"{previous_page!r} i {page!r}"
            )
        slot_pages[slot_id] = page

        activities = document.get("activities")
        if not isinstance(activities, list) or not activities:
            raise ValueError(f"{source}: pole 'activities' musi być niepustą listą")

        for activity in activities:
            manifest_activities.append(
                _validate_activity(
                    activity,
                    source=source,
                    page=page,
                    slot_id=slot_id,
                    activity_ids=activity_ids,
                )
            )

    return {
        "schema_version": SCHEMA_VERSION,
        "activities": manifest_activities,
    }


def _contracts_from_manifest(
    manifest: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    contracts: dict[str, dict[str, Any]] = {}
    for activity in manifest["activities"]:
        page = activity["page"]
        contract = contracts.setdefault(
            page,
            {
                "slot_id": activity["slot_id"],
                "section_ids": set(),
            },
        )
        if activity["section_id"] is not None:
            contract["section_ids"].add(activity["section_id"])
    return contracts


def _presentation_mode(config: Any) -> str:
    extra = getattr(config, "extra", None)
    if extra is None and hasattr(config, "get"):
        extra = config.get("extra", {})
    if not isinstance(extra, Mapping):
        extra = {}

    mode = extra.get("presentation_mode", "interactive")
    if mode not in PRESENTATION_MODES:
        supported = ", ".join(sorted(PRESENTATION_MODES))
        raise ValueError(
            f"Nieobsługiwany tryb prezentacji {mode!r}; dozwolone: {supported}"
        )
    return mode


def _page_source_name(page: Any) -> str:
    page_file = getattr(page, "file", None)
    for attribute in ("src_uri", "src_path"):
        value = getattr(page_file, attribute, None)
        if value:
            return str(value).replace("\\", "/")
    raise RuntimeError("Nie można ustalić ścieżki źródłowej strony MkDocs")


def _manifest_with_page_urls(
    manifest: dict[str, Any], page_urls: Mapping[str, str]
) -> dict[str, Any]:
    """Return a published-manifest copy enriched with MkDocs page URLs."""
    source_pages = sorted({activity["page"] for activity in manifest["activities"]})
    missing_pages = [page for page in source_pages if page not in page_urls]
    if missing_pages:
        raise RuntimeError(
            "Nie ustalono page.url MkDocs dla strony z aktywnościami: "
            f"{missing_pages[0]!r}"
        )

    source_pages_by_url: dict[str, str] = {}
    for source_page in source_pages:
        page_url = page_urls[source_page]
        if not isinstance(page_url, str):
            raise RuntimeError(
                f"{source_page}: page.url MkDocs musi być tekstem"
            )

        previous_page = source_pages_by_url.get(page_url)
        if previous_page is not None and previous_page != source_page:
            raise ValueError(
                f"page_url {page_url!r} jest przypisany do więcej niż jednej "
                f"strony: {previous_page!r} i {source_page!r}"
            )
        source_pages_by_url[page_url] = source_page

    published_activities: list[dict[str, Any]] = []
    for activity in manifest["activities"]:
        published_activity = dict(activity)
        published_activity["page_url"] = page_urls[activity["page"]]
        published_activities.append(published_activity)

    return {
        **manifest,
        "activities": published_activities,
    }


def _parse_page_activity_markup(
    html: str,
) -> tuple[
    list[str],
    list[tuple[str, str | None, str | None]],
    list[str],
]:
    parser = _PageActivityMarkupParser()
    parser.feed(html)
    parser.close()
    return parser.slots, parser.section_markers, parser.ids


def _validate_rendered_page(
    *,
    html: str,
    page: str,
    page_contracts: dict[str, dict[str, Any]],
    physical_slot_pages: dict[str, str],
) -> None:
    slots, section_markers, page_ids = _parse_page_activity_markup(html)
    contract = page_contracts.get(page)
    configured_slot_pages = {
        details["slot_id"]: source_page
        for source_page, details in page_contracts.items()
    }

    for slot_id in slots:
        if not slot_id or slot_id != slot_id.strip():
            raise ValueError(
                f"{page}: data-activity-slot musi mieć niepustą wartość bez "
                "skrajnych spacji"
            )

        configured_page = configured_slot_pages.get(slot_id)
        if configured_page is not None and configured_page != page:
            raise ValueError(
                f"slot {slot_id!r} występuje na więcej niż jednej stronie "
                f"Markdown: {configured_page!r} i {page!r}"
            )

        previous_page = physical_slot_pages.get(slot_id)
        if previous_page is not None and previous_page != page:
            raise ValueError(
                f"slot {slot_id!r} występuje na więcej niż jednej stronie "
                f"Markdown: {previous_page!r} i {page!r}"
            )
        physical_slot_pages[slot_id] = page

    duplicate_slots = sorted(
        slot_id for slot_id in set(slots) if slots.count(slot_id) > 1
    )
    if duplicate_slots:
        raise ValueError(
            f"{page}: slot {duplicate_slots[0]!r} występuje więcej niż raz"
        )

    if contract is None:
        if slots:
            raise ValueError(
                f"{page}: slot {slots[0]!r} nie ma definicji strony w activities/"
            )
    else:
        expected_slot = contract["slot_id"]
        if slots != [expected_slot]:
            if expected_slot not in slots:
                raise ValueError(
                    f"{page}: brakuje wymaganego slotu {expected_slot!r}"
                )
            unexpected = next(slot for slot in slots if slot != expected_slot)
            raise ValueError(
                f"{page}: znaleziono nieoczekiwany dodatkowy slot {unexpected!r}"
            )

    marked_section_ids: set[str] = set()
    for tag, section_id, marker_value in section_markers:
        if tag not in {"h2", "h3", "h4", "h5", "h6"}:
            raise ValueError(
                f"{page}: data-activity-section może oznaczać tylko nagłówek "
                "od h2 do h6"
            )
        if marker_value != "true":
            raise ValueError(
                f"{page}: data-activity-section musi mieć wartość 'true'"
            )
        if section_id is None or not SECTION_ID_PATTERN.fullmatch(section_id):
            raise ValueError(
                f"{page}: oznaczony nagłówek musi mieć stabilne id złożone "
                "z małych liter, cyfr i łączników"
            )
        if section_id in marked_section_ids:
            raise ValueError(
                f"{page}: oznaczony section_id {section_id!r} występuje więcej "
                "niż raz"
            )
        marked_section_ids.add(section_id)
        if page_ids.count(section_id) > 1:
            raise ValueError(
                f"{page}: id {section_id!r} oznaczonej sekcji nie jest unikalne "
                "w wyrenderowanym HTML"
            )

    if contract is not None:
        missing_sections = sorted(contract["section_ids"] - marked_section_ids)
        if missing_sections:
            raise ValueError(
                f"{page}: section_id {missing_sections[0]!r} nie wskazuje "
                "oznaczonego nagłówka"
            )


def on_pre_build(*, config: Any, **kwargs: Any) -> None:
    """Parse and validate activity definitions before MkDocs builds the site."""
    del kwargs
    global _validated_manifest, _page_contracts
    global _validated_pages, _physical_slot_pages, _page_urls
    _validated_manifest = None
    _page_contracts = {}
    _validated_pages = set()
    _physical_slot_pages = {}
    _page_urls = {}
    _presentation_mode(config)
    _validated_manifest = _build_manifest(config)
    _page_contracts = _contracts_from_manifest(_validated_manifest)
    log.info(
        "Validated %d activity definition(s)",
        len(_validated_manifest["activities"]),
    )


def on_page_content(
    html: str, *, page: Any, config: Any, **kwargs: Any
) -> str:
    """Validate activity slots and stable section anchors after Markdown renders."""
    del config, kwargs
    if _validated_manifest is None:
        raise RuntimeError("Manifest aktywności nie został zwalidowany w on_pre_build")

    page_name = _page_source_name(page)
    _validate_rendered_page(
        html=html,
        page=page_name,
        page_contracts=_page_contracts,
        physical_slot_pages=_physical_slot_pages,
    )
    if page_name in _page_contracts:
        page_url = getattr(page, "url", None)
        if not isinstance(page_url, str):
            raise RuntimeError(
                f"{page_name}: MkDocs nie udostępnił tekstowego page.url"
            )

        previous_url = _page_urls.get(page_name)
        if page_name in _page_urls and previous_url != page_url:
            raise RuntimeError(
                f"{page_name}: page.url zmienił się podczas jednego buildu "
                f"z {previous_url!r} na {page_url!r}"
            )
        _page_urls[page_name] = page_url
    _validated_pages.add(page_name)
    return html


def on_post_build(*, config: Any, **kwargs: Any) -> None:
    """Write the validated manifest directly to the completed site directory."""
    del kwargs
    if _validated_manifest is None:
        raise RuntimeError("Manifest aktywności nie został zwalidowany w on_pre_build")

    missing_pages = sorted(set(_page_contracts) - _validated_pages)
    if missing_pages:
        raise RuntimeError(
            "Nie zwalidowano wyrenderowanej strony z aktywnościami: "
            f"{missing_pages[0]!r}"
        )

    published_manifest = _manifest_with_page_urls(
        _validated_manifest,
        _page_urls,
    )

    if _presentation_mode(config) == "clean":
        log.info("Clean presentation: activity manifest was not published")
        return

    output_path = Path(config.site_dir) / "assets" / "generated" / "activities.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(published_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    log.info("Wrote activity manifest to %s", output_path)
