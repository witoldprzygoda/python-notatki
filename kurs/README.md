# Gałąź ćwiczeń — przewodnik

Na gałęzi `cwiczenia` rozwijamy interaktywną warstwę ćwiczeń do książki „Python Notatki”. Książka powstaje na gałęzi `dev` (publikacja: `master`), a gałąź ćwiczeń jednokierunkowo przyjmuje jej zmiany i dodaje wyłącznie własne pliki. Wydanie kursowe budujemy z nakładki `mkdocs.kurs.yml`. Zwykły `mkdocs.yml` buduje na tej gałęzi te same strony co na `dev`; build dodatkowo kopiuje nieładowane pliki statyczne warstwy (zob. „Wydania”).

## Zasada jednokierunkowa

- Zmiany płyną wyłącznie w kierunku `dev` → `sync/*` → `cwiczenia`. Gałęzi `cwiczenia` ani jej gałęzi pomocniczych nigdy nie scalamy do `dev` ani `master` i nie przenosimy z nich pojedynczych commitów (ang. *cherry-pick*).
- Gałęzi `cwiczenia` i `sync/*` nie przebudowujemy (ang. *rebase*) i nie nadpisujemy ich historii (`push --force`). To samo dotyczy każdej gałęzi pomocniczej, którą już wypchnięto.
- Błąd w treści książki zauważony podczas pracy nad ćwiczeniami poprawiamy na gałęzi `content/*` utworzonej z `dev`, a następnie przeprowadzamy synchronizację.

## Zasada wyłącznego dodawania (ang. *add-only*)

Względem wspólnego przodka z `dev` (ang. *merge-base*) gałąź ćwiczeń może wyłącznie dodawać ścieżki z poniższej listy:

- `activities/**`
- `scripts/build_activities.py`
- `docs/javascripts/interactive/**`
- `docs/stylesheets/interactive.css`
- `tests/interactive/**` i `tests/test_build_activities.py`
- `mkdocs.kurs.yml`
- `kurs/**`
- `.github/workflows/kurs.yml`

Plików książki (`docs/**/*.md`, `mkdocs.yml`, `docs/stylesheets/extra.css`, `CLAUDE.md` i pozostałych) nie zmieniamy ani nie usuwamy. Markdown książki nie zawiera żadnych znaczników ćwiczeń: aktywność wiąże się z nagłówkiem przez identyfikator generowany przez MkDocs (`section_id` w YAML), a hook `scripts/build_activities.py` podczas budowania wydania kursowego oznacza takie nagłówki i dopisuje slot na końcu strony. Paski postępu („prostokąciki”) pojawiają się wyłącznie przy stronach i sekcjach z ćwiczeniami; stoją w lewym wcięciu nawigacji, więc etykiety wszystkich pozycji zostają tam, gdzie w książce.

## Katalog roboczy i podgląd

Gałąź ma własny katalog roboczy `../python-notatki-cwiczenia`, położony obok katalogu książki; katalog książki i port 8000 pozostają przy `dev`. Podgląd wydania kursowego uruchamiamy na porcie 8002 i zatrzymujemy po zakończeniu pracy:

```bash
D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe -m mkdocs serve -f mkdocs.kurs.yml -a 127.0.0.1:8002
```

Po zmianie hooka trzeba uruchomić `mkdocs serve` ponownie, ponieważ przebudowa strony korzysta z modułu wczytanego przy starcie. Wszystkie polecenia Pythona uruchamiamy tym samym interpreterem środowiska książki; w dalszych przykładach oznaczamy go krótko jako `python`. Testy JavaScript wymagają Node.js 22 lub nowszego (zalecany 24, jak w planowanym CI).

## Bramka

```bash
python kurs/tools/gate.py [--book dev] [--pomin-testy] [--katalog-roboczy | --przed-scaleniem]
```

Bramka ocenia commit `HEAD`: etapy G2–G7 działają na czystym eksporcie jego drzewa w katalogu tymczasowym, dlatego niezatwierdzone i nieśledzone pliki nie wpływają na wynik. Niezatwierdzona zmiana pliku książki w katalogu ćwiczeń jest jednak błędem w każdym trybie.

Etapy: G1 — wyłączne dodawanie, podstawowe pliki warstwy, kolizje ze ścieżkami ćwiczeń w książce, usunięcia plików ćwiczeń przez scalenie książki, scalenia stanu książki spoza `--book` i nazwy gałęzi; G2 — listy nakładki zawierają listy książki; G3 — schemat YAML i wiązania z nagłówkami; G5 — rozwiązania wzorcowe zadań `code` i bloki `verify` pytań; G6 — testy unittest (`tests/`, `kurs/tools/`) i node; G7 — buildy `--strict` książki i wydania kursowego. Etapów G4 (aktualność powiązanych sekcji) i G8 (kontrola opublikowanego wydania) jeszcze nie ma. Każdy etap jest blokujący, a tabela na końcu podsumowuje wynik.

Kody wyjścia:

| Kod | Znaczenie |
|---|---|
| 0 | pełna bramka przeszła dla commitu `HEAD`; wyłącznie ten wynik służy do odbioru i do raportu synchronizacji |
| 1 | co najmniej jeden etap nie przeszedł |
| 2 | błąd wywołania, np. nieistniejąca gałąź książki |
| 3 | wynik częściowy albo roboczy: `--pomin-testy`, `--katalog-roboczy` lub `--przed-scaleniem` |

Opcja `--katalog-roboczy` sprawdza katalog roboczy razem z niezatwierdzonymi zmianami i służy wyłącznie do szybkiej pętli roboczej. Opcja `--przed-scaleniem` uruchamia tylko etap G1 i próbne scalenie książki (`git merge-tree`) bez zmiany katalogu roboczego.

Przy zerwanym wiązaniu G3 zestawia nagłówki strony sprzed ostatniego scalenia książki z obecnymi i wskazuje następcę dawnego nagłówka, np. `prawdopodobna zmiana nagłówka: „Pętla for” → „Pętla for i sekwencje”`. Identyfikatory o podobnym zapisie podaje tylko wtedy, gdy zestawienie nie wskazuje następcy, i opisuje je jako samo podobieństwo napisów. Etap wypisuje też każdą zmianę wiązania względem stanu sprzed scalenia, razem z tekstami nagłówków, które przenosimy do raportu dla autora.

Każde pytanie `single_choice` ma blok `verify`, którego kod wypisuje dokładnie etykietę poprawnej odpowiedzi. Pytanie pojęciowe, którego nie da się tak sprawdzić, wpisujemy z uzasadnieniem do `kurs/bez-weryfikacji.txt`.

Do czasu przewinięcia `dev` do stanu po rozdzieleniu (gałąź `infra/rozdzielenie-cwiczen`) książka na `dev` zawiera jeszcze warstwę ćwiczeń, a G1 zgłasza to jako kolizję. W tym okresie bramkę uruchamiamy z `--book infra/rozdzielenie-cwiczen`, a gałąź `cwiczenia` tworzymy dopiero po przewinięciu `dev`.

## Synchronizacja z dev

Warunek wstępny: autor wypchnął `dev`. Wszystkie kroki odwołują się do tej samej gałęzi książki, `origin/dev`; scalanie lokalnego `dev` nie jest dozwolone, ponieważ bramka uznałaby jego commity za zmiany plików książki.

1. `git fetch origin`
2. `git switch -c sync/RRRR-MM-DD origin/cwiczenia`
3. `python kurs/tools/gate.py --book origin/dev --przed-scaleniem` — kod 3 pozwala scalać. Przy kodzie 1 przerywamy i składamy raport: kolizję rozwiązuje zmiana nazwy ścieżki po stronie ćwiczeń albo usunięcie ścieżki z książki, a książkę z plikami lub historią ćwiczeń — procedura naprawcza (niżej).
4. `git -c merge.directoryRenames=false merge --no-ff origin/dev -m "Sync with dev (RRRR-MM-DD)"`. W razie konfliktu ścieżka spoza listy dozwolonej zawsze przyjmuje wersję z książki: `git checkout origin/dev -- <ścieżka>`; plików książki nie poprawiamy ręcznie. Jeśli scalenie usunęło pliki ćwiczeń, nie zatwierdzamy go (`git merge --abort`) i stosujemy procedurę naprawczą.
5. `python kurs/tools/gate.py --book origin/dev`. Poprawiamy wyłącznie pliki ćwiczeń, np. `section_id` po zmianie nagłówka albo `page` po przeniesieniu strony, zatwierdzamy poprawki i powtarzamy bramkę aż do kodu 0.
6. Dopisujemy wiersz do `kurs/SYNC_LOG.md`, zatwierdzamy go i ostatni raz uruchamiamy bramkę (kod 0).
7. Przygotowujemy dla autora jednostronicowy raport: zakres zmian `dev`, strony z ćwiczeniami, których dotyczą zmiany, zmienione wiązania (stary → nowy identyfikator wraz z tekstami nagłówków z etapu G3), wynik bramki i polecenie podglądu.
8. Po „akceptuję”: `git switch cwiczenia`, `git merge --ff-only sync/RRRR-MM-DD` i `git push origin cwiczenia`. Następnie usuwamy gałąź `sync/…` lokalnie (`git branch -d sync/RRRR-MM-DD`), a jeśli ją wypchnięto — także w repozytorium zdalnym (`git push origin --delete sync/RRRR-MM-DD`).

Jeśli w międzyczasie na `cwiczenia` trafiła inna zmiana i przewinięcie (ang. *fast-forward*) się nie udaje, nie przebudowujemy gałęzi: scalamy `origin/cwiczenia` do gałęzi `sync/…` i ponownie uruchamiamy bramkę. Gałęzi o tej samej nazwie nie tworzymy od nowa; jeśli trzeba zacząć od początku, tworzymy nową gałąź `sync/RRRR-MM-DD-2` od aktualnego `origin/cwiczenia`. Zmian z gałęzi ćwiczeń nigdy nie scalamy z powrotem do `dev`.

## Procedura naprawcza: ćwiczenia w książce

Stosujemy ją, gdy G1 zgłasza historię książki ze stanem zawierającym pliki ćwiczeń, próbne scalenie usuwające pliki ćwiczeń albo scalenie książki, które je usunęło. Oznacza to, że historia gałęzi ćwiczeń trafiła do `dev`, a zwykła synchronizacja usunęłaby całą warstwę, łącznie z bramką.

1. Nie scalamy `dev` i nie zatwierdzamy takiego scalenia; lokalną gałąź `sync/…` usuwamy.
2. Po stronie książki warstwę usuwa z `dev` jeden commit X, który zmienia wyłącznie ścieżki z listy dozwolonej (`git diff --name-only X^ X`). Jeśli `dev` ma już drzewo samej książki, ponieważ ćwiczenia scalono strategią `ours`, za X przyjmujemy commit scalający, który wprowadził historię ćwiczeń.
3. Na nowej gałęzi `sync/…` utworzonej z `origin/cwiczenia` wykonujemy najpierw `git -c merge.directoryRenames=false merge --no-ff X^`, a następnie `git merge -s ours X`. Bezpośrednie scalenie X strategią `ours` pominęłoby zmiany książki między poprzednią synchronizacją a X.
4. Bramka z `--book origin/dev` musi zakończyć się kodem 0, a G1 pokazuje wyłącznie dodane ścieżki. Dalsze synchronizacje przebiegają zwykłym trybem.

## Gałęzie pomocnicze

Gałęzie pomocnicze tworzymy z `origin/cwiczenia`. Po przejściu pełnej bramki (kod 0) i akceptacji autora wracają do `cwiczenia` przez `git merge --ff-only`, po czym wypychamy `cwiczenia` (`git push origin cwiczenia`) i usuwamy gałąź pomocniczą lokalnie oraz, jeśli ją wypchnięto, zdalnie. Gdy przewinięcie się nie udaje, scalamy `origin/cwiczenia` do gałęzi pomocniczej i ponownie uruchamiamy bramkę; gałęzi już wypchniętych nie przebudowujemy.

| Prefiks | Przeznaczenie |
|---|---|
| `fala/<NN-rozdzial>` | fala ćwiczeń do jednego rozdziału |
| `platform/<temat>` | hook, JavaScript, CSS, bramka, CI i wydania |
| `sync/<RRRR-MM-DD>` | synchronizacja z `dev`; jedyne gałęzie, które scalają `dev` |

Nazwa gałęzi nie może być równa śledzonej ścieżce (stąd brak gałęzi `activities/…` i `kurs`); bramka sprawdza to w etapie G1. Obok gałęzi `cwiczenia` nie mogą istnieć gałęzie `cwiczenia/…`, czego pilnuje sam git.

## Wydania

Następnym etapem są wydania, czyli nazwane zestawy ustawień (np. wydanie na rok akademicki i wydanie bez ćwiczeń), wybierane w jednym pliku konfiguracyjnym. Do tego czasu jedynym wydaniem z ćwiczeniami jest pełna warstwa z `mkdocs.kurs.yml`. Wydanie bez ćwiczeń musi wykluczyć statyczne pliki warstwy (`javascripts/interactive/**`, `stylesheets/interactive.css`), które build `mkdocs.yml` na tej gałęzi kopiuje, choć ich nie ładuje. Wykluczenie należy do własnej konfiguracji wydania z listy dozwolonej (nakładka w `kurs/` albo ustawienie wydania w hooku), ponieważ `mkdocs.yml` należy do książki.

## Dokumenty

- `kurs/INTERACTIVE_SYSTEM_SPEC.md` — specyfikacja architektury warstwy;
- `kurs/AGENTS.md` — zasady pracy nad warstwą;
- `kurs/tools/gate.py` i `kurs/tools/test_gate.py` — bramka i jej testy;
- `kurs/bez-weryfikacji.txt` — pytania zwolnione z bloku `verify`;
- `kurs/SYNC_LOG.md` — dziennik synchronizacji;
- `CLAUDE.md` — reguły redakcyjne książki, obowiązujące także w tekstach ćwiczeń.

W razie rozbieżności co do modelu gałęzi, poleceń i procedur obowiązuje niniejszy przewodnik.
