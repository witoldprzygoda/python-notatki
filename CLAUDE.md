# CLAUDE.md — python-notatki

## Projekt

Polskojęzyczne notatki do kursu Pythona (podręcznik kursowy). Framework: **MkDocs Material**. Źródła w `docs/`, nawigacja w `mkdocs.yml`, checklista zrzutów ekranu w `ZRZUTY.md`.

- Build: `mkdocs build` — po każdej zmianie treści uruchom i sprawdź ostrzeżenia (WARNING o brakujących plikach z nav to błąd do zgłoszenia, nie do zignorowania).
- Podgląd: `mkdocs serve`.
- Środowisko: Windows, Git Bash; wymagany pakiet `mkdocs-material` (patrz `requirements.txt`).

## Styl tekstu

- Rejestr książkowy, formalny — bez potocznych sformułowań, kolokwializmów i metafor (np. nie: „w ciemno”, „czysty komputer”, „interpreter mieszka”). Autor zwraca na to szczególną uwagę.
- Narracja w 1. osobie liczby mnogiej: „instalujemy”, „sprawdzamy”. Dopuszczalna też forma bezokolicznikowa.
- Nagłówki sekcji w formie rzeczownikowej („Kontrola po instalacji”, nie „Sprawdzamy co się zainstalowało”).
- Terminy angielskie przy pierwszym użyciu: kursywa z dopiskiem, np. „przestarzały (ang. *deprecated*)”.
- Terminologia ustalona: „interpreter” (słowa „runtime” używamy tylko przy wprowadzeniu pojęcia), „manager” dla Python Install Managera, „środowisko wirtualne / venv”.
- Cudzysłowy w prozie: wyłącznie polskie typograficzne „…” (dotyczy także cytowanych terminów obcych). Proste znaki `"` tylko tam, gdzie wymaga ich składnia: wnętrza bloków kodu i wstawek `...`, atrybuty `title="..."`, ograniczniki tytułów admonitions `!!! note "..."`, zakładki `=== "..."`; robocze komentarze `<!-- TODO -->` również prostymi znakami.

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
- Odsyłacze wewnętrzne: względne do plików `.md`; tytuły H1 zgodne z etykietami nav w `mkdocs.yml`. Wyjątki: strony `index.md` rozdziałów mają w nav etykietę „Wprowadzenie”, a ich H1 nazywa cały rozdział (np. „1. Instalacja i środowisko pracy”); strona główna `docs/index.md` ma etykietę nav „Strona główna”, a jej H1 nosi tytuł serwisu.
- Stan odniesienia treści: Python 3.14 z Python Install Managerem (klasyczny instalator deprecated), nowy REPL 3.13/3.14, lintery i formatery VSC jako osobne rozszerzenia. Przy nazwach produktów, wersjach i instrukcjach narzędzi weryfikuj aktualność w sieci przed napisaniem.

## Workflow repozytorium

Przed rozpoczęciem pracy przeczytaj `DEVELOPMENT_WORKFLOW.md`.

Gałąź `dev` zawiera wyłącznie książkę i narzędzia służące jej przygotowaniu
(tak samo `master`, `content/*` i `infra/*`). Nie dodajemy na niej plików
ćwiczeń (`activities/**` i pozostałych ścieżek warstwy ćwiczeń), atrybutów
`data-activity-*`, slotów aktywności, hooka ćwiczeń w `mkdocs.yml` ani slajdów
wykładowych (`slajdy/`, osobna gałąź `slajdy`); naruszenia wykrywa
`scripts/check_book_only.py`.

Ćwiczenia rozwijamy na gałęzi `cwiczenia` (katalog roboczy
`../python-notatki-cwiczenia`, gałęzie robocze `fala/*`, `platform/*`
i `sync/*`), która przyjmuje książkę z `dev` jednokierunkowo; jej zmiany nigdy
nie trafiają do `dev` ani `master`. Na tych gałęziach przed pracą przeczytaj
`kurs/README.md` i `kurs/AGENTS.md`.

Treść książki jest nadrzędna: nagłówki, strony i odsyłacze zmieniamy wyłącznie
ze względu na jakość książki. Jeśli zmiana książki zerwie powiązanie ćwiczenia
z nagłówkiem albo zmieni treść sekcji lub strony, z którą ćwiczenie jest
powiązane, dostosowuje się projekt ćwiczeń podczas synchronizacji z `dev`
(skill `/synchronizuj-cwiczenia` w katalogu `../python-notatki-cwiczenia`).

Kroki w `plans/*.md` i `PLAN_ROZWOJU.md` dotyczące `mkdocs.clean.yml`, testów
warstwy interaktywnej i ograniczeń zmian stron rozdziału 4 są nieaktualne
od 3 X 2026.

## Zasady współpracy

- Zmiany nawigacji w `mkdocs.yml` oraz reorganizację treści proponuj i uzasadniaj, nie wykonuj bez zgody.
- Poprawki stylu, aktualności i spójności nanoś śmiało, ale wyraźnie je wypunktuj w podsumowaniu, żeby autor mógł zawetować.
- Materiały źródłowe (podkatalog `sources/`) autora (pliki .txt) bywają pisane potocznie i pierwszoosobowo — treść integrujemy, styl przepisujemy na książkowy, sytuacje osobiste przedstawiamy jako przypadki hipotetyczne.
- Głównym i pierwotnym źródłem jest plik `sources/PythonNotatki.pdf`
- W podkatalogu `sources/` jest więcej plików .pdf, do których będziesz się odnosić podczas dalszego rozwijania projektu
- Również w podkatalogu `sources/lectures/` jest cały zestaw wykładów z Pythona, który porządkuje materiał - również z niego jako referencją, będziesz korzystać, gdy zostaniesz o to poproszony.
