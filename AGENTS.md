# AGENTS.md — python-notatki

Repozytorium zawiera polskojęzyczny podręcznik do kursu Pythona, publikowany
przez MkDocs Material. Gałęzie `master`, `dev`, `content/*` i `infra/*`
zawierają wyłącznie książkę i narzędzia służące jej przygotowaniu.

- Zasady redakcyjne i konwencje bloków kodu zawiera `CLAUDE.md`; obowiązują
  one wszystkie narzędzia AI. Przed każdą zmianą treści przeczytaj ten plik.
- Model gałęzi, kierunki przepływu zmian, odbiór prac i porty podglądu opisuje
  `DEVELOPMENT_WORKFLOW.md`; przeczytaj go przed rozpoczęciem pracy.
- Kontrola przed oddaniem pracy: `mkdocs build --strict` bez ostrzeżeń oraz
  `python scripts/check_book_only.py --robocze` (katalog roboczy, łącznie ze
  zmianami niezatwierdzonymi); po utworzeniu commitu także
  `python scripts/check_book_only.py` (commit `HEAD`).
- Projekt ćwiczeń interaktywnych jest rozwijany na gałęzi `cwiczenia` (katalog
  `../python-notatki-cwiczenia`, gałęzie robocze `fala/*`, `platform/*`
  i `sync/*`); na tych gałęziach przed pracą przeczytaj `kurs/README.md`
  i `kurs/AGENTS.md`.
- Na `dev` nie dodajemy materiału ćwiczeń: plików `activities/**`, atrybutów
  `data-activity-*`, slotów aktywności, hooka ćwiczeń ani kodu warstwy
  interaktywnej; nie dodajemy też slajdów wykładowych (`slajdy/`). Zmiany
  z gałęzi `cwiczenia` nigdy nie trafiają do `dev` ani `master`.
