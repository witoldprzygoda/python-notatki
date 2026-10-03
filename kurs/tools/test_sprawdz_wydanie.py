"""Testy kontroli wydania w przeglądarce (kurs/tools/sprawdz_wydanie.py).

Etap G6 bramki uruchamia je razem z testami bramki:

    python -m unittest discover -s kurs/tools -p "test_*.py"

Testy sprawdzają logikę narzędzia bez przeglądarki: plan kontroli z nav
i definicji aktywności (także odczytany interpreterem z MkDocs), ocenę stanu
strony, zdarzenia konsoli i sieci, wybór portu, kopię katalogu roboczego
i tabelę podsumowania. Same kontrole w przeglądarce wymagają Playwright
i Microsoft Edge (kurs/README.md, „Kontrola wydania w przeglądarce”).
"""

from __future__ import annotations

import functools
import importlib.util
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sprawdz_wydanie as sw  # noqa: E402

BASE = "http://127.0.0.1:8050/"
PETLE = "04-sterowanie/petle-i-iteratory.md"
WARUNKI = "04-sterowanie/wyrazenia-warunkowe.md"
NAV = [
    {"Strona główna": "index.md"},
    {
        "Python Podstawy": [
            {
                "1. Instalacja": [
                    {"Wprowadzenie": "01-instalacja/index.md"},
                    {"Pip": "01-instalacja/pip.md"},
                ]
            },
            {
                "4. Sterowanie przepływem": [
                    {"Wprowadzenie": "04-sterowanie/index.md"},
                    {"Wyrażenia warunkowe": WARUNKI},
                    {"Pętle i iteratory": PETLE},
                ]
            },
        ]
    },
    {
        "Python Zastosowania": [
            {"Wprowadzenie": "zastosowania/index.md"},
            {"1. Jupyter": [{"Wprowadzenie": "zastosowania/01-jupyter/index.md"}]},
            {"Zewnętrzny": "https://example.invalid/strona.md"},
        ]
    },
]


def activity(activity_id, kind, section, correct=None, options=()):
    return {
        "activity_id": activity_id, "type": kind, "section_id": section,
        "correct_option_id": correct, "option_ids": list(options),
    }


DEFINITIONS = [
    {
        "source": "activities/04-sterowanie/petle-i-iteratory.yaml",
        "page": PETLE,
        "slot_id": "petle-i-iteratory-activities",
        "activities": [
            activity("for-code", "code", "petla-for"),
            activity("for-quiz", "single_choice", "petla-for", "b", "abc"),
            activity("iterator-quiz", "single_choice", "iteratory", "a", "ab"),
        ],
    },
    {
        "source": "activities/04-sterowanie/wyrazenia-warunkowe.yaml",
        "page": WARUNKI,
        "slot_id": "wyrazenia-warunkowe-activities",
        "activities": [
            activity("match-code", "code", "pola-wyboru-match"),
            activity("broken-quiz", "single_choice", "if-else", "z", "ab"),
            activity("page-ack", "acknowledgement", None),
        ],
    },
]
FEATURES = ["navigation.instant", "navigation.tabs", "navigation.tabs.sticky"]
DATA = {"nav": NAV, "use_directory_urls": True, "features": FEATURES, "definitions": DEFINITIONS}
GIT_IDENTITY = {
    "GIT_AUTHOR_NAME": "Kontrola",
    "GIT_AUTHOR_EMAIL": "kontrola@example.invalid",
    "GIT_COMMITTER_NAME": "Kontrola",
    "GIT_COMMITTER_EMAIL": "kontrola@example.invalid",
}


def write_files(root: Path, files: dict[str, str]) -> None:
    for name, content in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")


class ImportTest(unittest.TestCase):
    def test_module_imports_without_playwright(self) -> None:
        code = (
            "import sys; sys.path.insert(0, sys.argv[1]); import sprawdz_wydanie; "
            "print(sorted(name for name in sys.modules if name.split('.')[0] == 'playwright'))"
        )
        result = subprocess.run(
            [sys.executable, "-c", code, str(Path(sw.__file__).parent)],
            capture_output=True, text=True, encoding="utf-8", check=False,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "[]")


class PageUrlTest(unittest.TestCase):
    def test_urls_follow_mkdocs(self) -> None:
        cases = {
            "index.md": "",
            "04-sterowanie/index.md": "04-sterowanie/",
            "04-sterowanie/README.md": "04-sterowanie/",
            PETLE: "04-sterowanie/petle-i-iteratory/",
            "ą/łódź.md": "%C4%85/%C5%82%C3%B3d%C5%BA/",
        }
        for src, url in cases.items():
            with self.subTest(src):
                self.assertEqual(sw.page_url(src), url)

    def test_urls_without_directory_urls(self) -> None:
        self.assertEqual(sw.page_url("index.md", False), "index.html")
        self.assertEqual(sw.page_url("a/index.md", False), "a/index.html")
        self.assertEqual(sw.page_url("a/b.md", False), "a/b.html")


class NavTest(unittest.TestCase):
    items = sw.parse_nav(NAV)

    def test_parts_are_top_level_sections_with_their_landing_pages(self) -> None:
        self.assertEqual(
            sw.parts(self.items),
            [("Python Podstawy", "01-instalacja/index.md"),
             ("Python Zastosowania", "zastosowania/index.md")],
        )

    def test_owners_and_documents_skip_external_links(self) -> None:
        owners = sw.part_of(self.items)

        self.assertEqual(owners[PETLE], "Python Podstawy")
        self.assertEqual(owners["zastosowania/01-jupyter/index.md"], "Python Zastosowania")
        self.assertNotIn("index.md", owners)
        self.assertNotIn("https://example.invalid/strona.md", sw.documents(self.items))

    def test_chapter_index_is_the_first_page_of_the_nearest_section(self) -> None:
        self.assertEqual(sw.chapter_index(self.items, PETLE), "04-sterowanie/index.md")
        self.assertEqual(
            sw.chapter_index(self.items, "zastosowania/index.md"), "zastosowania/index.md"
        )
        self.assertIsNone(sw.chapter_index(self.items, "index.md"))
        self.assertIsNone(sw.chapter_index(self.items, "brak.md"))


class PlanTest(unittest.TestCase):
    def test_plan_follows_the_nav_and_the_definitions(self) -> None:
        plan = sw.build_plan(DATA)

        self.assertEqual([page.src for page in plan.exercise_pages], [WARUNKI, PETLE])
        self.assertEqual(
            plan.plain_pages,
            ["index.md", "04-sterowanie/index.md", "01-instalacja/index.md",
             "zastosowania/index.md"],
        )
        self.assertEqual(plan.route, (WARUNKI, PETLE, "04-sterowanie/index.md"))
        self.assertTrue(plan.pill_menu)
        self.assertEqual(plan.urls["index.md"], "")
        self.assertEqual(plan.exercise_pages[1].url, "04-sterowanie/petle-i-iteratory/")

    def test_quiz_sections_and_totals_of_an_exercise_page(self) -> None:
        warunki, petle = sw.build_plan(DATA).exercise_pages

        self.assertEqual(petle.quiz.activity_id, "for-quiz")
        self.assertIsNone(warunki.quiz)  # poprawnej odpowiedzi nie ma wśród wariantów
        self.assertEqual(petle.sections, ["petla-for", "iteratory"])
        self.assertEqual(warunki.sections, ["pola-wyboru-match", "if-else"])
        self.assertEqual(petle.section_total("petla-for"), 2)

    def test_one_exercise_page_starts_the_route_on_its_chapter_page(self) -> None:
        plan = sw.build_plan(dict(DATA, definitions=DEFINITIONS[:1]))

        self.assertEqual(
            plan.route, ("04-sterowanie/index.md", PETLE, "04-sterowanie/index.md")
        )

    def test_features_decide_about_the_menu_and_the_route(self) -> None:
        plan = sw.build_plan(dict(DATA, features=["navigation.tabs"]))

        self.assertFalse(plan.pill_menu)
        self.assertIsNone(plan.route)

    def test_rail_state_mirrors_the_layer(self) -> None:
        self.assertEqual(sw.rail_state(0, 3), "none_completed")
        self.assertEqual(sw.rail_state(1, 3), "partial")
        self.assertEqual(sw.rail_state(1, 1), "completed")


def pill(text, active=False, **changes):
    entry = {
        "text": text, "active": active, "shown": True, "clipped": False,
        "covered": False, "truncated": False,
        "box": {"left": 600, "right": 760, "top": 10, "bottom": 38},
    }
    entry.update(changes)
    return entry


class PartsCheckTest(unittest.TestCase):
    EXPECTED = ["Python Podstawy", "Python Zastosowania"]

    def state(self, *pills) -> dict:
        return {"parts": list(pills), "viewport": 1280, "header": {"top": 0, "bottom": 48}}

    def test_visible_menu_with_the_current_part_passes(self) -> None:
        state = self.state(pill("Python Podstawy", True), pill("Python Zastosowania"))

        self.assertEqual(sw.check_parts(state, self.EXPECTED, "Python Podstawy"), [])

    def test_wrong_entries_and_wrong_current_part(self) -> None:
        state = self.state(pill("Python Podstawy"), pill("Inna część", True))

        problems = sw.check_parts(state, self.EXPECTED, None)

        self.assertIn("menu części zawiera ['Python Podstawy', 'Inna część']", problems[0])
        self.assertEqual(problems[1], "oznaczona część: ['Inna część'], oczekiwano: żadna")

    def test_hidden_clipped_outside_and_truncated_entries(self) -> None:
        state = self.state(
            pill("Python Podstawy", True, shown=False),
            pill("Python Zastosowania", clipped=True, covered=True,
                 box={"left": 1200, "right": 1300, "top": 10, "bottom": 60}),
        )

        problems = sw.check_parts(state, self.EXPECTED, "Python Podstawy")

        self.assertIn("pozycja menu części „Python Podstawy” jest niewidoczna", problems)
        self.assertIn(
            "pozycja menu części „Python Zastosowania” wychodzi poza okno (od 1200 do "
            "1300 px przy szerokości 1280 px)",
            problems,
        )
        self.assertIn("pozycja menu części „Python Zastosowania” wystaje poza belkę nagłówka",
                      problems)
        self.assertIn(
            "pozycja menu części „Python Zastosowania” jest przycięta przez element nadrzędny",
            problems,
        )
        self.assertFalse(any("zasłonięta" in problem for problem in problems), problems)

    def test_covered_and_truncated_entry(self) -> None:
        state = self.state(
            pill("Python Podstawy", True, covered=True), pill("Python Zastosowania", truncated=True)
        )

        self.assertEqual(
            sw.check_parts(state, self.EXPECTED, "Python Podstawy"),
            [
                "pozycja menu części „Python Podstawy” jest zasłonięta przez inny element",
                "pozycja menu części „Python Zastosowania”: etykieta nie mieści się w pigułce",
            ],
        )

    def test_horizontal_overflow(self) -> None:
        self.assertEqual(sw.check_overflow({"overflow": 0}), [])
        self.assertEqual(
            sw.check_overflow({"overflow": 37.4}), ["strona przewija się poziomo o 37 px"]
        )


def nav(key, rail=True, shown=True, tag="a"):
    return {"tag": tag, "key": BASE + key, "rail": rail, "railShown": shown and rail}


def toc(section, rail=True, secondary=True, shown=True):
    return {"section": section, "secondary": secondary, "rail": rail, "railShown": shown and rail}


class PageCheckTest(unittest.TestCase):
    plan = sw.build_plan(DATA)
    petle = plan.exercise_pages[1]
    keys = {BASE + page.url for page in plan.exercise_pages}
    key = BASE + petle.url

    def good_state(self) -> dict:
        return {
            "slots": ["petle-i-iteratory-activities"],
            "activities": [{"id": "for-quiz"}, {"id": "for-code"}, {"id": "iterator-quiz"}],
            "marked": [
                {"tag": "h2", "id": "petla-for", "value": "true"},
                {"tag": "h3", "id": "iteratory", "value": "true"},
            ],
            "navLinks": [
                nav("04-sterowanie/", rail=False),
                nav("04-sterowanie/wyrazenia-warunkowe/"),
                nav("04-sterowanie/petle-i-iteratory/"),
                nav("04-sterowanie/petle-i-iteratory/", tag="label", shown=False),
            ],
            "tocLinks": [
                toc("petla-for"), toc("petla-while", rail=False), toc("iteratory"),
                toc("petla-for", secondary=False, shown=False),
            ],
            "sectionRails": 3,
        }

    def check(self, state: dict, wide: bool = True) -> dict[str, list[str]]:
        return sw.check_exercise_page(state, self.petle, self.key, self.keys, wide)

    def test_complete_exercise_page_passes(self) -> None:
        self.assertEqual(
            self.check(self.good_state()), {"aktywnosci": [], "naglowki": [], "wskazniki": []}
        )

    def test_slot_and_activities(self) -> None:
        state = self.good_state()
        state["slots"] = []
        state["activities"] = [{"id": "for-quiz"}, {"id": "obca"}]

        found = self.check(state)["aktywnosci"]

        self.assertEqual(
            found,
            [
                "oczekiwano jednego slotu 'petle-i-iteratory-activities', jest []",
                "wyrenderowano 2 z 3 aktywności; brak: for-code, iterator-quiz; "
                "nadmiarowe: obca",
            ],
        )

    def test_marked_headings(self) -> None:
        state = self.good_state()
        state["marked"] = [
            {"tag": "h2", "id": "petla-for", "value": "1"},
            {"tag": "p", "id": "petla-while", "value": "true"},
        ]

        found = self.check(state)["naglowki"]

        self.assertEqual(
            found,
            [
                "nagłówek #iteratory nie ma atrybutu data-activity-section",
                "#petla-for: data-activity-section ma wartość '1'",
                "atrybut data-activity-section ma element #petla-while, z którym nie wiąże "
                "się żadna aktywność",
            ],
        )

    def test_missing_stray_and_hidden_rails(self) -> None:
        state = self.good_state()
        state["navLinks"] = [
            nav("04-sterowanie/", rail=True),
            nav("04-sterowanie/wyrazenia-warunkowe/", rail=False),
            nav("04-sterowanie/petle-i-iteratory/", shown=False),
        ]
        state["tocLinks"] = [toc("petla-for", shown=False), toc("petla-while")]

        found = self.check(state)["wskazniki"]

        self.assertEqual(
            found,
            [
                f"brak wskaźnika postępu przy odnośnikach do stron: {BASE}04-sterowanie/"
                "wyrazenia-warunkowe/",
                f"wskaźnik postępu przy odnośnikach do stron bez ćwiczeń: {BASE}04-sterowanie/",
                "brak wskaźnika postępu sekcji #iteratory w spisie treści",
                "wskaźnik postępu przy sekcjach bez ćwiczeń: #petla-while",
                "wskaźnik postępu bieżącej strony w nawigacji jest niewidoczny",
                "wskaźnik postępu sekcji #petla-for w spisie treści jest niewidoczny",
            ],
        )

    def test_missing_rail_is_not_reported_again_as_hidden(self) -> None:
        state = self.good_state()
        state["navLinks"] = [
            link for link in state["navLinks"]
            if link["key"] != self.key
        ]
        state["tocLinks"] = [toc("petla-for")]

        found = self.check(state)["wskazniki"]

        self.assertEqual(
            found,
            [
                "brak wskaźnika postępu bieżącej strony w nawigacji",
                "brak wskaźnika postępu sekcji #iteratory w spisie treści",
            ],
        )

    def test_drawer_reports_only_rails_that_exist_elsewhere_on_the_page(self) -> None:
        state = self.good_state()
        shown = {"present": True, "visible": True}
        good = {"page": shown, "sections": {"petla-for": shown, "iteratory": shown}}
        bad = {
            "page": {"present": True, "visible": False},
            "sections": {
                "petla-for": {"present": False, "visible": False},
                "iteratory": {"present": True, "visible": False},
            },
        }
        absent = {"present": False, "visible": False}
        bare = dict(state, navLinks=[], tocLinks=[])

        self.assertEqual(sw.drawer_problems(good, state, self.key), [])
        self.assertEqual(
            sw.drawer_problems(bad, state, self.key),
            [
                "w szufladzie nawigacji wskaźnik postępu bieżącej strony jest niewidoczny",
                "w szufladzie nawigacji brak wskaźnika postępu sekcji #petla-for",
                "w szufladzie nawigacji wskaźnik postępu sekcji #iteratory jest niewidoczny",
            ],
        )
        self.assertEqual(
            sw.drawer_problems({"page": absent, "sections": {"petla-for": absent}}, bare, self.key),
            [],
        )

    def test_narrow_window_leaves_visibility_to_the_drawer_check(self) -> None:
        state = self.good_state()
        for link in state["navLinks"] + state["tocLinks"]:
            link["railShown"] = False

        self.assertEqual(self.check(state, wide=False)["wskazniki"], [])

    def test_page_without_exercises(self) -> None:
        clean = {"slots": [], "activities": [], "marked": [], "sectionRails": 0,
                 "navLinks": [nav("04-sterowanie/", rail=False),
                              nav("04-sterowanie/petle-i-iteratory/")]}
        leaked = dict(
            clean,
            slots=["x"],
            activities=[{"id": "a"}],
            marked=[{"tag": "h2", "id": "w-tym-rozdziale", "value": "true"}],
            sectionRails=2,
            navLinks=[nav("04-sterowanie/"), nav("04-sterowanie/petle-i-iteratory/", rail=False)],
        )
        key = BASE + "04-sterowanie/"

        self.assertEqual(
            sw.check_plain_page(clean, key, self.keys), {"bez-cwiczen": [], "wskazniki": []}
        )
        found = sw.check_plain_page(leaked, key, self.keys)
        self.assertEqual(len(found["bez-cwiczen"]), 5, found)
        self.assertIn(
            "strona ma elementy z atrybutem data-activity-section: #w-tym-rozdziale",
            found["bez-cwiczen"],
        )
        self.assertEqual(len(found["wskazniki"]), 2, found)

    def test_anchor_position(self) -> None:
        def position(top: float) -> dict:
            return {"top": top, "header": 48, "viewport": 900}

        self.assertIsNone(sw.check_anchor(position(68), "a"))
        self.assertIsNone(sw.check_anchor(position(47.5), "a"))
        self.assertIn("zasłonięty belką", sw.check_anchor(position(0), "a"))
        self.assertIn("poza oknem", sw.check_anchor(position(950), "a"))
        self.assertEqual(sw.check_anchor(None, "a"), "na stronie nie ma elementu #a")


class EventTest(unittest.TestCase):
    def test_classification_of_console_and_network_events(self) -> None:
        local = BASE + "javascripts/interactive/bootstrap.js"
        font = "https://fonts.gstatic.com/s/roboto/v1.woff2"
        cases = [
            ("pageerror", "TypeError: x", None, "błąd"),
            ("error", "Uncaught ReferenceError", BASE, "błąd"),
            ("error", "Failed to load resource: net::ERR_NAME_NOT_RESOLVED", font, "uwaga"),
            ("assert", "Assertion failed", local, "błąd"),
            ("warning", "Nie udało się zainicjalizować warstwy interaktywnej.", local, "błąd"),
            ("warning", "Deprecated API", BASE + "assets/javascripts/bundle.js", "uwaga"),
            ("requestfailed", "net::ERR_CONNECTION_REFUSED " + local, local, "błąd"),
            ("requestfailed", "net::ERR_ABORTED " + local, local, None),
            ("requestfailed", "net::ERR_NAME_NOT_RESOLVED " + font, font, "uwaga"),
            ("http", "HTTP 404 " + BASE + "brak/", BASE + "brak/", "błąd"),
            ("http", "HTTP 503 " + font, font, "uwaga"),
            ("info", "komunikat", BASE, None),
        ]
        for kind, text, url, expected in cases:
            with self.subTest(kind=kind, text=text):
                self.assertEqual(sw.classify(kind, text, url, BASE), expected)


class ReportTest(unittest.TestCase):
    def test_summary_table_and_verdict(self) -> None:
        report = sw.Report()
        light, dark = sw.VARIANTS[0], sw.VARIANTS[3]
        for check, _ in sw.CHECKS:
            report.mark(check, light)
        report.mark("menu", dark)
        report.problems[("menu", dark.label)] = ["a", "b"]

        lines = sw.summary_lines(report)
        code, sentence = sw.verdict(report, "abcdef0123", False)

        self.assertEqual(lines[0].split(), ["Kontrola", "jasny", "1280", "ciemny", "1280",
                                            "jasny", "375", "ciemny", "375"])
        menu = next(line for line in lines if line.startswith("menu części w belce"))
        self.assertEqual(menu.split()[-5:], ["OK", "—", "—", "BŁĄD", "(2)"])
        self.assertEqual(code, sw.EXIT_FAILED)
        self.assertEqual(sentence, "Wynik: kontrola wydania nie przeszła (menu części w belce).")

    def test_passing_and_failed_build(self) -> None:
        report = sw.Report()
        self.assertEqual(
            sw.verdict(report, "abcdef0123", False),
            (sw.EXIT_OK, "Wynik: kontrola wydania przeszła dla commitu abcdef0."),
        )
        self.assertEqual(
            sw.verdict(report, "abcdef0123", True),
            (
                sw.EXIT_PARTIAL,
                "Wynik: kontrola wydania przeszła dla katalogu roboczego; to wynik roboczy, "
                "który nie służy do odbioru (kod 3).",
            ),
        )
        report.build_failed = True
        self.assertEqual(sw.verdict(report, "abcdef0123", False)[0], sw.EXIT_FAILED)
        self.assertEqual(sw.verdict(report, "abcdef0123", True)[0], sw.EXIT_FAILED)
        self.assertIn("(build --strict)", sw.verdict(report, "abcdef0123", False)[1])


class PortTest(unittest.TestCase):
    def test_first_free_port_is_chosen(self) -> None:
        def factory(port: int) -> str:
            if port < 8052:
                raise OSError("zajęty")
            return f"serwer {port}"

        free = functools.partial(sw.bind_first_free, taken=lambda port: False)

        self.assertEqual(free(sw.PORTS, factory), (8052, "serwer 8052"))
        self.assertIsNone(free(range(8050, 8052), factory))

    def test_taken_port_is_skipped_before_binding(self) -> None:
        tried = []

        def factory(port: int) -> str:
            tried.append(port)
            return f"serwer {port}"

        bound = sw.bind_first_free([1, 2, 3], factory, taken=lambda port: port < 3)

        self.assertEqual(bound, (3, "serwer 3"))
        self.assertEqual(tried, [3])

    def test_port_held_by_another_socket_on_any_address_is_skipped(self) -> None:
        # Gniazdo pod adresem wieloznacznym (0.0.0.0, :: z obsługą IPv4, jak
        # python -m http.server) nie blokuje w Windows powiązania z 127.0.0.1;
        # bez próby port_taken serwer narzędzia przejąłby jego ruch.
        cases = [("127.0.0.1", socket.AF_INET, None), ("0.0.0.0", socket.AF_INET, None)]
        if socket.has_ipv6:
            cases += [("::", socket.AF_INET6, 0), ("::1", socket.AF_INET6, None)]
        for address, family, v6only in cases:
            with self.subTest(address=address), socket.socket(family) as other:
                if v6only is not None:
                    other.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, v6only)
                try:
                    other.bind((address, 0))
                except OSError as error:
                    self.skipTest(f"adres {address} niedostępny: {error}")
                other.listen()
                port = other.getsockname()[1]

                self.assertTrue(sw.port_taken(port))
                self.assertIsNone(
                    sw.bind_first_free([port], functools.partial(sw.make_server, Path(".")))
                )

    def test_released_port_is_free(self) -> None:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]

        self.assertFalse(sw.port_taken(port))
        bound = sw.bind_first_free([port], functools.partial(sw.make_server, Path(".")))
        self.assertIsNotNone(bound)
        bound[1].server_close()

    def test_ports_and_slugs(self) -> None:
        self.assertEqual((sw.PORTS.start, sw.PORTS.stop), (8050, 8070))
        self.assertEqual(sw.slug(""), "strona-glowna")
        self.assertEqual(sw.slug("04-sterowanie/petle/"), "04-sterowanie_petle")
        self.assertEqual(sw.slug("a/b.html"), "a_b")


class InterpreterPathTest(unittest.TestCase):
    def test_relative_paths_are_fixed_before_the_tool_changes_directory(self) -> None:
        relative = os.path.join("srodowisko", "Scripts", "python.exe")

        self.assertEqual(sw.interpreter_path("python"), Path("python"))
        self.assertEqual(sw.interpreter_path(relative), Path(os.path.abspath(relative)))
        self.assertTrue(sw.interpreter_path("./python").is_absolute())


@unittest.skipUnless(
    importlib.util.find_spec("mkdocs") and importlib.util.find_spec("yaml"),
    "odczyt planu wymaga MkDocs i PyYAML (środowisko książki, etap G6)",
)
class ReadPlanTest(unittest.TestCase):
    def test_plan_comes_from_the_inherited_config_and_the_definitions(self) -> None:
        files = {
            "mkdocs.yml": (
                "site_name: Test\nuse_directory_urls: false\n"
                "theme:\n  name: mkdocs\n  features:\n    - navigation.tabs\n"
                "nav:\n  - Strona główna: index.md\n  - Część:\n      - Rozdział:\n"
                "          - Wprowadzenie: r/index.md\n          - Strona: r/strona.md\n"
            ),
            "mkdocs.kurs.yml": (
                "INHERIT: mkdocs.yml\ntheme:\n  features:\n    - navigation.instant\n"
                "    - navigation.tabs\n    - navigation.tabs.sticky\n"
            ),
            "activities/r/strona.yaml": (
                "page: r/strona.md\nslot_id: strona-activities\nactivities:\n"
                "  - activity_id: pytanie\n    type: single_choice\n    section_id: sekcja\n"
                "    correct_option_id: b\n    options:\n      - option_id: a\n"
                "      - option_id: b\n"
                "  - activity_id: potwierdzenie\n    type: acknowledgement\n"
                "    section_id: null\n"
            ),
            "activities/lista.yaml": "- definicja w postaci listy jest pomijana\n",
        }
        with tempfile.TemporaryDirectory(prefix="kurs-wydanie-test-") as directory:
            tree, work = Path(directory) / "drzewo", Path(directory) / "praca"
            write_files(tree, files)
            work.mkdir()

            plan = sw.read_plan(Path(sys.executable), tree, work)

        (page,) = plan.exercise_pages
        self.assertEqual((page.src, page.url, page.slot_id),
                         ("r/strona.md", "r/strona.html", "strona-activities"))
        self.assertEqual(
            page.activities,
            [
                sw.Activity("pytanie", "single_choice", "sekcja", "b", ("a", "b")),
                sw.Activity("potwierdzenie", "acknowledgement", None, None, ()),
            ],
        )
        self.assertEqual(plan.plain_pages, ["index.md", "r/index.md"])
        self.assertEqual(plan.parts, [("Część", "r/index.md")])
        self.assertTrue(plan.pill_menu)  # cechy motywu z nakładki zastępują cechy książki
        self.assertEqual(plan.route, ("r/index.md", "r/strona.md", "r/index.md"))
        self.assertEqual(plan.urls["index.md"], "index.html")

    def test_failed_reading_is_reported(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kurs-wydanie-test-") as directory:
            tree, work = Path(directory) / "drzewo", Path(directory) / "praca"
            write_files(tree, {"mkdocs.kurs.yml": "INHERIT: brak.yml\n"})
            work.mkdir()

            with self.assertRaises(RuntimeError) as raised:
                sw.read_plan(Path(sys.executable), tree, work)

        self.assertIn("odczyt nav i definicji aktywności nie powiódł się", str(raised.exception))


class CopyWorkingTreeTest(unittest.TestCase):
    def git(self, repo: Path, *args: str) -> None:
        subprocess.run(
            ["git", "-c", "core.autocrlf=false", *args], cwd=repo, check=True,
            capture_output=True, env={**os.environ, **GIT_IDENTITY}, stdin=subprocess.DEVNULL,
        )

    def test_copy_holds_changes_and_untracked_files_but_no_ignored_ones(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kurs-wydanie-test-") as directory:
            repo, target = Path(directory) / "repo", Path(directory) / "kopia"
            write_files(repo, {
                ".gitignore": "*.log\n", "a.txt": "a\n", "b.txt": "b\n", "e.txt": "e\n",
                "katalog/ą.txt": "ą\n",
            })
            self.git(repo, "init", "-q")
            self.git(repo, "add", "--all")
            self.git(repo, "commit", "-q", "-m", "Start")
            write_files(repo, {"b.txt": "b zmienione\n", "c.txt": "c\n", "d.log": "d\n"})
            (repo / "e.txt").unlink()
            previous = os.getcwd()
            os.chdir(repo)
            try:
                sw.copy_working_tree(target)
            finally:
                os.chdir(previous)

            copied = sorted(
                path.relative_to(target).as_posix() for path in target.rglob("*")
                if path.is_file()
            )
            changed = (target / "b.txt").read_text(encoding="utf-8")

        self.assertEqual(copied, [".gitignore", "a.txt", "b.txt", "c.txt", "katalog/ą.txt"])
        self.assertEqual(changed, "b zmienione\n")


if __name__ == "__main__":
    unittest.main()
