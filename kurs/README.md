# Gałąź ćwiczeń — przewodnik

Gałąź `cwiczenia` rozwija interaktywną warstwę ćwiczeń do książki „Python Notatki”. Książka powstaje na gałęzi `dev` (publikacja: `master`), a gałąź ćwiczeń jednokierunkowo przyjmuje jej zmiany i dodaje wyłącznie własne pliki. Wydanie kursowe budujemy z nakładki `mkdocs.kurs.yml`; zwykły `mkdocs.yml` buduje na tej gałęzi tę samą książkę co na `dev`.

## Zasada jednokierunkowa

- Zmiany płyną wyłącznie w kierunku `dev` → `sync/*` → `cwiczenia`. Gałęzi `cwiczenia` ani jej gałęzi pomocniczych nigdy nie scalamy do `dev` ani `master` i nie przenosimy z nich pojedynczych commitów (ang. *cherry-pick*).
- Gałęzi `cwiczenia` i `sync/*` nie przebudowujemy (ang. *rebase*) i nie nadpisujemy ich historii (`push --force`).
- Błąd w treści książki zauważony podczas pracy nad ćwiczeniami poprawiamy na gałęzi `content/*` utworzonej z `dev`, a następnie przeprowadzamy synchronizację.

## Zasada add-only

Względem wspólnego przodka z `dev` (ang. *merge-base*) gałąź ćwiczeń może wyłącznie dodawać ścieżki z poniższej listy:

- `activities/**`
- `scripts/build_activities.py`
- `docs/javascripts/interactive/**`
- `docs/stylesheets/interactive.css`
- `tests/interactive/**` i `tests/test_build_activities.py`
- `mkdocs.kurs.yml`
- `kurs/**`
- `.github/workflows/kurs.yml`

Plików książki (`docs/**/*.md`, `mkdocs.yml`, `docs/stylesheets/extra.css`, `CLAUDE.md` i pozostałych) nie zmieniamy ani nie usuwamy. Markdown książki nie zawiera żadnych znaczników ćwiczeń: aktywność wiąże się z nagłówkiem przez identyfikator generowany przez MkDocs (`section_id` w YAML), a hook `scripts/build_activities.py` podczas budowania wydania kursowego oznacza takie nagłówki i dopisuje slot na końcu strony. Raile postępu pojawiają się wyłącznie przy stronach i sekcjach z ćwiczeniami.

## Katalog roboczy i podgląd

Gałąź ma własny katalog roboczy `../python-notatki-cwiczenia`, położony obok katalogu książki; katalog książki i port 8000 pozostają przy `dev`. Podgląd wydania kursowego uruchamiamy na porcie 8002 i zatrzymujemy po zakończeniu pracy:

```bash
D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe -m mkdocs serve -f mkdocs.kurs.yml -a 127.0.0.1:8002
```

Po zmianie hooka trzeba uruchomić `mkdocs serve` ponownie, ponieważ przebudowa strony korzysta z modułu wczytanego przy starcie. Wszystkie polecenia Pythona uruchamiamy tym samym interpreterem środowiska książki; w dalszych przykładach oznaczamy go krótko jako `python`.

## Bramka

```bash
python kurs/tools/gate.py [--book dev] [--pomin-testy]
```

Etapy: G1 — zasada add-only, kolizje i usunięcia; G2 — listy nakładki zawierają listy książki; G3 — schemat YAML i wiązania z nagłówkami; G5 — rozwiązania wzorcowe zadań `code` i opcjonalne bloki `verify` pytań; G6 — testy unittest i node; G7 — buildy `--strict` książki i wydania kursowego. Każdy etap jest blokujący, a tabela na końcu podsumowuje wynik.

## Synchronizacja z dev

1. `git fetch origin`
2. `git switch -c sync/RRRR-MM-DD cwiczenia`
3. `git -c merge.directoryRenames=false merge --no-ff origin/dev` (albo `dev`, jeśli lokalna gałąź jest aktualna). W razie konfliktu ścieżka spoza listy add-only zawsze przyjmuje wersję z `dev`: `git checkout origin/dev -- <ścieżka>`.
4. `python kurs/tools/gate.py --book origin/dev`
5. Poprawiamy wyłącznie pliki ćwiczeń, np. `section_id` po zmianie nagłówka albo `page` po przeniesieniu strony, i powtarzamy bramkę aż do pełnego wyniku OK.
6. Przygotowujemy dla autora jednostronicowy raport: zakres zmian `dev`, dotknięte strony z ćwiczeniami, zmienione wiązania (stare → nowe), wynik bramki i polecenie podglądu.
7. Po „akceptuję”: `git switch cwiczenia` i `git merge --ff-only sync/RRRR-MM-DD`, a następnie usuwamy gałąź `sync/…`.

Jeśli w międzyczasie na `cwiczenia` trafiła inna zmiana i przewinięcie (ang. *fast-forward*) się nie udaje, nie przebudowujemy gałęzi: scalamy `cwiczenia` do gałęzi `sync/…` albo tworzymy ją od nowa, a następnie ponownie uruchamiamy bramkę. Zmian z gałęzi ćwiczeń nigdy nie scalamy z powrotem do `dev`.

## Gałęzie pomocnicze

Gałęzie pomocnicze tworzymy z `cwiczenia`; wracają do niej przez `git merge --ff-only` po przejściu bramki i akceptacji autora.

| Prefiks | Przeznaczenie |
|---|---|
| `fala/<NN-rozdzial>` | fala ćwiczeń do jednego rozdziału |
| `platform/<temat>` | hook, JavaScript, CSS, bramka, CI i wydania |
| `sync/<RRRR-MM-DD>` | synchronizacja z `dev`; jedyne gałęzie, które scalają `dev` |

Nazwa gałęzi nie może być równa śledzonej ścieżce (stąd brak gałęzi `activities/…` i `kurs`), a obok gałęzi `cwiczenia` nie mogą istnieć gałęzie `cwiczenia/…`.

## Wydania

Następnym etapem są wydania, czyli nazwane zestawy ustawień (np. wydanie na rok akademicki i wydanie bez ćwiczeń), wybierane w jednym pliku konfiguracyjnym. Do tego czasu jedynym wydaniem z ćwiczeniami jest pełna warstwa z `mkdocs.kurs.yml`. Wydanie bez ćwiczeń powstaje z `mkdocs.yml`; powinno ono dodatkowo wykluczyć przez `exclude_docs` statyczne pliki warstwy (`javascripts/interactive/**`, `stylesheets/interactive.css`), które build książki na tej gałęzi kopiuje, choć ich nie ładuje.

## Dokumenty

- `kurs/INTERACTIVE_SYSTEM_SPEC.md` — specyfikacja architektury warstwy;
- `kurs/AGENTS.md` — zasady pracy nad warstwą;
- `CLAUDE.md` — reguły redakcyjne książki, obowiązujące także w tekstach ćwiczeń.

W razie rozbieżności co do modelu gałęzi, poleceń i procedur obowiązuje niniejszy przewodnik.
