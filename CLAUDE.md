# CLAUDE.md — python-notatki

## Projekt

Polskojęzyczne notatki do kursu Pythona (podręcznik kursowy). Framework: **MkDocs Material**. Źródła w `docs/`, nawigacja w `mkdocs.yml`, checklista zrzutów ekranu w `ZRZUTY.md`.

- Build: `mkdocs build` — po każdej zmianie treści uruchom i sprawdź ostrzeżenia (WARNING o brakujących plikach z nav to błąd do zgłoszenia, nie do zignorowania).
- Podgląd: `mkdocs serve`.
- Środowisko: Windows, Git Bash; wymagany pakiet `mkdocs-material` (patrz `requirements.txt`).

## Styl tekstu

- Rejestr książkowy, formalny — bez potocznych sformułowań, kolokwializmów i metafor (np. nie: „w ciemno", „czysty komputer", „interpreter mieszka"). Autor zwraca na to szczególną uwagę.
- Narracja w 1. osobie liczby mnogiej: „instalujemy", „sprawdzamy". Dopuszczalna też forma bezokolicznikowa.
- Nagłówki sekcji w formie rzeczownikowej („Kontrola po instalacji", nie „Sprawdzamy co się zainstalowało").
- Terminy angielskie przy pierwszym użyciu: kursywa z dopiskiem, np. „przestarzały (ang. *deprecated*)".
- Terminologia ustalona: „interpreter" (słowa „runtime" używamy tylko przy wprowadzeniu pojęcia), „manager" dla Python Install Managera, „środowisko wirtualne / venv".

## Konwencje bloków kodu (krytyczne — nie odstępować)

- Polecenia terminalowe: ` ```powershell title="Terminal" ` lub ` ```bash title="Terminal" ` (język wg kontekstu) — zawsze szara belka z ikoną kopiowania. Dotyczy też bloków wewnątrz zakładek `=== "Nazwa"` (pymdownx.tabbed, wcięcie 4 spacje).
- Wyniki poleceń, sesje REPL (`>>>`), schematy ASCII: ` ```{ .text .no-copy } ` lub ` ```{ .python .no-copy } ` — bez belki, bez kopiowania.
- Zawartość plików: belka z nazwą pliku, np. ` ```json title="settings.json" `, ` ```text title="requirements.txt" `, ` ```bash title="~/.bashrc" `.
- Nigdy goły blok bez `title=` ani `.no-copy`.
- Polecenia celowo odradzane (np. goły `pip install`) pokazujemy jako `.no-copy`, żeby nie miały ikony kopiowania.

## Inne konwencje

- pip zawsze w formie `python -m pip ...` lub `py -V:<TAG> -m pip ...` — nigdy goły `pip`.
- Klawisze przez pymdownx.keys: `++ctrl+shift+p++`.
- Admonitions `!!! note/tip/warning/info "Polski tytuł"` z treścią wciętą 4 spacje.
- Obrazki: per rozdział w `docs/<rozdział>/img/`, nazwy od treści bez wersji (np. `vsc-select-interpreter.png`). Miejsca na przyszłe zrzuty oznaczaj `<!-- TODO: screenshot — opis -->` i dopisuj do `ZRZUTY.md` (kadr ciasny, stały motyw; szczegóły w tym pliku). Treści terminalowe i listowe odtwarzamy jako bloki tekstowe zamiast zrzutów; prawdziwe zrzuty tylko tam, gdzie obraz niesie informację niewyrażalną tekstem (kolory, układ okna).
- Odsyłacze wewnętrzne: względne do plików `.md`; tytuły H1 zgodne z etykietami nav w `mkdocs.yml`.
- Stan odniesienia treści: Python 3.14 z Python Install Managerem (klasyczny instalator deprecated), nowy REPL 3.13/3.14, lintery i formatery VSC jako osobne rozszerzenia. Przy nazwach produktów, wersjach i instrukcjach narzędzi weryfikuj aktualność w sieci przed napisaniem.

## Zasady współpracy

- Zmiany nawigacji w `mkdocs.yml` oraz reorganizację treści proponuj i uzasadniaj, nie wykonuj bez zgody.
- Poprawki stylu, aktualności i spójności nanoś śmiało, ale wyraźnie je wypunktuj w podsumowaniu, żeby autor mógł zawetować.
- Materiały źródłowe (podkatalog `sources/`) autora (pliki .txt) bywają pisane potocznie i pierwszoosobowo — treść integrujemy, styl przepisujemy na książkowy, sytuacje osobiste przedstawiamy jako przypadki hipotetyczne.
- Głównym i pierwotnym źródłem jest plik `sources/PythonNotatki.pdf`
- W podkatalogu `sources/` jest więcej plików .pdf, do których będziesz się odnosić podczas dalszego rozwijania projektu
- Również w podkatalogu `sources/lectures/` jest cały zestaw wykładów z Pythona, który porządkuje materiał - również z niego jako referencją, będziesz korzystać, gdy zostaniesz o to poproszony.