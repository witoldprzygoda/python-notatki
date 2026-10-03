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
- `.claude/skills/synchronizuj-cwiczenia/**` (skill Claude Code prowadzący synchronizację)

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
python kurs/tools/gate.py --zatwierdz-aktualnosc [--book dev] --przejrzane ID[,ID…]
```

Bramka ocenia commit `HEAD`: etapy G2–G7 działają na czystym eksporcie jego drzewa w katalogu tymczasowym, dlatego niezatwierdzone i nieśledzone pliki nie wpływają na wynik. Niezatwierdzona zmiana pliku książki w katalogu ćwiczeń jest jednak błędem w każdym trybie.

Etapy: G1 — wyłączne dodawanie, podstawowe pliki warstwy, kolizje ze ścieżkami ćwiczeń w książce, usunięcia plików ćwiczeń przez scalenie książki, scalenia stanu książki spoza `--book` i nazwy gałęzi; G2 — listy nakładki zawierają listy książki; G3 — schemat YAML i wiązania z nagłówkami; G4 — aktualność treści powiązanych sekcji względem ostatniego przeglądu (niżej); G5 — rozwiązania wzorcowe zadań `code` i bloki `verify` pytań; G6 — testy unittest (`tests/`, `kurs/tools/`) i node; G7 — buildy `--strict` książki i wydania kursowego. Etapu G8 (liczby kontrolne i metadane wydania) jeszcze nie ma. Każdy etap jest blokujący, a tabela na końcu podsumowuje wynik.

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

### Aktualność powiązanych sekcji (G4)

Etap G4 porównuje treść sekcji, z którymi wiążą się aktywności, ze stanem z ostatniego przeglądu zapisanym w `kurs/aktualnosc.json`. Plik zawiera jeden wpis dla każdej aktywności, w osobnym wierszu: identyfikator aktywności, jej wiązanie (strona i `section_id`), tekst nagłówka, odcisk SHA-256 treści sekcji (przy `section_id: null` całej strony), commit książki, przy którym aktywność przejrzano względem tej treści, oraz datę przeglądu. Stan przeglądu należy więc do aktywności, a nie do sekcji: aktywność dodana do sekcji nie przejmuje przeglądu innych aktywności tej sekcji.

Sekcja obejmuje tekst od swojego nagłówka do następnego nagłówka tego samego lub wyższego poziomu, łącznie z blokami kodu i wynikami. Sekcja h2 obejmuje więc swoje podsekcje h3–h6, a aktywność powiązana z podsekcją nie reaguje na zmiany wstępu sekcji nadrzędnej. Treść odczytujemy z Markdown strony przygotowanego tak jak w MkDocs (bez znaku BOM i bez metadanych na początku pliku) i przetworzonego tymi samymi rozszerzeniami książki, z których G3 wyznacza identyfikatory nagłówków, dlatego granice sekcji zgadzają się z identyfikatorami G3 i buildu, a wiersz zaczynający się od `#` w bloku kodu nie dzieli sekcji. Odcisku nie zmieniają znaki końca wiersza, spacje końcowe, ponowne łamanie akapitów, adresy odnośników, formatowanie tekstu, ścieżki i pliki obrazów (liczy się wyłącznie tekst alternatywny) ani rodzaj wyróżnienia (ang. *admonition*) przy niezmienionym tytule; zmienia go każda zmiana słów, liczb i kodu, także w tytułach wyróżnień, etykietach zakładek i tytułach bloków kodu.

G4 zgłasza jako błąd zmienioną treść sekcji, wiązanie zerwane w G3 (z tym samym następcą nagłówka co G3), zmienione wiązanie, nowe aktywności bez wpisu oraz wpisy aktywności, których już nie ma. Przy zmianie treści wypisuje aktywności do przejrzenia, różnicę treści sekcji od przeglądu (po jednym zdaniu w wierszu; różnicę dłuższą niż 40 wierszy skraca, zachowując pierwsze dodane wiersze i podając liczbę wszystkich usuniętych i dodanych) oraz polecenie `git diff`, które pokazuje pełne zmiany strony. Jeśli identyfikator powiązanego nagłówka należy już do innego nagłówka albo treść z przeglądu znajduje się teraz w innej sekcji (np. po zmianie nazwy nagłówka i dodaniu nowego o dawnej nazwie albo po wstawieniu powtórzonego nagłówka przed powiązanym), G4 wskazuje tę sekcję i pokazuje różnicę względem niej; poprawiamy wtedy wiązanie, a nie aktywność. Na końcu etap wymienia wszystkie aktywności wymagające przeglądu.

Po przejrzeniu zgłoszonych aktywności zapisujemy nowy stan, wymieniając przejrzane aktywności, np.:

```bash
python kurs/tools/gate.py --zatwierdz-aktualnosc --book origin/dev --przejrzane flow-for-code-001,flow-for-quiz-001
```

Polecenie nie uruchamia etapów bramki. Definicje aktywności odczytuje z katalogu roboczego, a odciski oblicza dla książki w stanie `merge-base(HEAD, origin/dev)`. Lista `--przejrzane` musi obejmować dokładnie aktywności, które wymagają przeglądu: nowe, o zmienionym wiązaniu i o zmienionej treści sekcji; w przeciwnym razie polecenie wypisuje oczekiwaną listę, kończy się kodem 1 i pliku nie zmienia. Kodem 1 kończy się także przy zerwanym wiązaniu, wiązaniu niedozwolonym według G3 (nagłówek h1, identyfikator z sufiksem deduplikacji) i błędnej definicji, a kod 2 oznacza błąd wywołania, w tym `--book`, którego stan zawiera pliki ćwiczeń. Zapisując plik, polecenie wypisuje każdy zmieniony wpis: „dodano” (nowa aktywność), „zmieniono” (zmiana wiązania, nagłówka albo treści sekcji, z dawnym i nowym commitem przeglądu) i „usunięto” (aktywności już nie ma). Wpis bez zmian zachowuje dawny commit i datę przeglądu, a wpis o niezmienionej treści, lecz zapisany dawną wersją odcisku, polecenie odświeża („odświeżono”) bez zmiany daty przeglądu. Bramka nigdy nie zapisuje tego pliku sama, a zmieniony plik zatwierdzamy osobnym commitem. W ten sam sposób fala dodająca aktywności zapisuje ich wpisy, gdy sprawdzi, że odpowiadają bieżącej treści sekcji.

Pliku `kurs/aktualnosc.json` nie scalamy wierszami: `kurs/.gitattributes` nadaje mu atrybut `-merge`, więc gdy obie scalane gałęzie go zmieniły, scalenie zatrzymuje się na konflikcie. Konflikt rozstrzygamy zawsze wersją z `origin/cwiczenia` (`git checkout origin/cwiczenia -- kurs/aktualnosc.json`). Pliku nie poprawiamy ręcznie, nie wybieramy fragmentów konfliktu i nie usuwamy go, aby zapisać go od nowa. Po zatwierdzeniu scalenia uruchamiamy bramkę, przeglądamy aktywności wskazane przez G4 i zapisujemy stan poleceniem `--zatwierdz-aktualnosc`.

## Utworzenie gałęzi `cwiczenia`

Gałąź powstaje jednorazowo, po odbiorze rozdzielenia: gdy `dev` w repozytorium zdalnym zawiera już commity, które usuwają warstwę ćwiczeń z książki i opisują nowy model pracy. Jej pierwszym commitem jest scalenie zaakceptowanej gałęzi podglądu:

```bash
git fetch origin
git switch -c cwiczenia origin/dev
git -c merge.directoryRenames=false merge --no-ff podglad/cwiczenia -m "Start the exercises branch from the accepted preview"
python kurs/tools/gate.py --book origin/dev
git push -u origin cwiczenia
```

Bramka opisze ten pierwszy commit scalający jako scalenie; jest to wejście warstwy ćwiczeń z gałęzi podglądu, a nie synchronizacja książki, i tak odnotowujemy go w raporcie dla autora. Po wypchnięciu gałąź `podglad/cwiczenia` usuwamy, a dalsze zmiany książki przyjmujemy wyłącznie według procedury synchronizacji.

## Synchronizacja z dev

Warunek wstępny: autor wypchnął `dev`. Wszystkie kroki odwołują się do tej samej gałęzi książki, `origin/dev`; scalanie lokalnego `dev` nie jest dozwolone, ponieważ bramka uznałaby jego commity za zmiany plików książki. Synchronizacja nie musi następować po każdej zmianie książki. Jeśli po `git fetch origin` polecenie `git rev-list --count origin/cwiczenia..origin/dev` zwraca 0, nie ma czego synchronizować.

Procedurę przeprowadza skill Claude Code `/synchronizuj-cwiczenia` (`.claude/skills/synchronizuj-cwiczenia/SKILL.md`), uruchamiany w katalogu `../python-notatki-cwiczenia`. Skill wykonuje kroki 1–7 i przed krokiem 8 czeka na akceptację autora; wiążący pozostaje niniejszy opis.

1. `git fetch origin`
2. `git switch -c sync/RRRR-MM-DD origin/cwiczenia`
3. `python kurs/tools/gate.py --book origin/dev --przed-scaleniem` — kod 3 pozwala scalać. Przy kodzie 1 przerywamy i składamy raport: kolizję rozwiązuje zmiana nazwy ścieżki po stronie ćwiczeń albo usunięcie ścieżki z książki, a książkę z plikami lub historią ćwiczeń — procedura naprawcza (niżej).
4. `git -c merge.directoryRenames=false merge --no-ff origin/dev -m "Sync with dev (RRRR-MM-DD)"`. W razie konfliktu ścieżka spoza listy dozwolonej zawsze przyjmuje wersję z książki: `git checkout origin/dev -- <ścieżka>`; plików książki nie poprawiamy ręcznie. Jeśli scalenie usunęło pliki ćwiczeń, nie zatwierdzamy go (`git merge --abort`) i stosujemy procedurę naprawczą.
5. `python kurs/tools/gate.py --book origin/dev`. Poprawiamy wyłącznie pliki ćwiczeń, zatwierdzamy poprawki i powtarzamy bramkę aż do kodu 0:
   - wiązania zerwane według G3: `section_id` po zmianie nagłówka (następcę wskazuje bramka) albo `page` po przeniesieniu strony;
   - aktywności z sekcji, których treść według G4 zmieniła się od przeglądu: polecenie, kod startowy, oczekiwany wynik, rozwiązania i klucz odpowiedzi sprawdzamy względem nowej treści, a `version` podnosimy, gdy zmienia się polecenie, poprawna odpowiedź albo checker (`kurs/INTERACTIVE_SYSTEM_SPEC.md`, „Wersjonowanie aktywności”), razem z wersją oczekiwaną w teście aktywności pilotażowych (`tests/test_build_activities.py`); błędu w książce nie poprawiamy na tej gałęzi, lecz zgłaszamy go w raporcie do poprawki na gałęzi `content/*`;
   - po przejrzeniu wszystkich aktywności zgłoszonych przez G4 zapisujemy nowy stan poleceniem `python kurs/tools/gate.py --zatwierdz-aktualnosc --book origin/dev --przejrzane <identyfikatory>` z listą dokładnie tych aktywności i zatwierdzamy `kurs/aktualnosc.json`.
6. Dopisujemy wiersz do `kurs/SYNC_LOG.md` (data, commit `origin/dev`, commit scalenia z kroku 4, rodzaj „synchronizacja”, kod bramki z kroku 5 i uwagi: zmienione wiązania, decyzje przeglądu G4, podniesione wersje), zatwierdzamy go i ostatni raz uruchamiamy bramkę (kod 0).
7. Przygotowujemy dla autora jednostronicowy raport: zakres zmian `dev` (commity), strony z ćwiczeniami, których dotyczą zmiany, zmienione wiązania (stary → nowy identyfikator wraz z tekstami nagłówków z etapu G3), decyzje przeglądu G4 dla każdej aktywności, podniesione wersje, usterki książki do poprawy na gałęzi `content/*`, wynik bramki i polecenie podglądu.
8. Po „akceptuję”: `git switch cwiczenia`, `git merge --ff-only sync/RRRR-MM-DD` i `git push origin cwiczenia`. Następnie usuwamy gałąź `sync/…` lokalnie (`git branch -d sync/RRRR-MM-DD`), a jeśli ją wypchnięto — także w repozytorium zdalnym (`git push origin --delete sync/RRRR-MM-DD`).

Jeśli w międzyczasie na `cwiczenia` trafiła inna zmiana i przewinięcie (ang. *fast-forward*) się nie udaje, nie przebudowujemy gałęzi: scalamy `origin/cwiczenia` do gałęzi `sync/…` i ponownie uruchamiamy bramkę. Konflikt w `kurs/aktualnosc.json` rozstrzygamy wersją z `origin/cwiczenia` i ponownym przeglądem aktywności wskazanych przez G4 (podsekcja „Aktualność powiązanych sekcji (G4)”). Gałęzi o tej samej nazwie nie tworzymy od nowa; jeśli trzeba zacząć od początku, tworzymy nową gałąź `sync/RRRR-MM-DD-2` od aktualnego `origin/cwiczenia`. Zmian z gałęzi ćwiczeń nigdy nie scalamy z powrotem do `dev`.

## Procedura naprawcza: ćwiczenia w książce

Stosujemy ją, gdy G1 zgłasza historię książki ze stanem zawierającym pliki ćwiczeń, próbne scalenie usuwające pliki ćwiczeń albo scalenie książki, które je usunęło. Oznacza to, że historia gałęzi ćwiczeń trafiła do `dev`, a zwykła synchronizacja usunęłaby całą warstwę, łącznie z bramką.

1. Nie scalamy `dev` i nie zatwierdzamy takiego scalenia; lokalną gałąź `sync/…` usuwamy.
2. Po stronie książki warstwę usuwa z `dev` jeden commit X, który zmienia wyłącznie ścieżki z listy dozwolonej (`git diff --name-only X^ X`). Jeśli `dev` ma już drzewo samej książki, ponieważ ćwiczenia scalono strategią `ours`, za X przyjmujemy commit scalający, który wprowadził historię ćwiczeń.
3. Na nowej gałęzi `sync/…` utworzonej z `origin/cwiczenia` wykonujemy najpierw `git -c merge.directoryRenames=false merge --no-ff X^`, a następnie `git merge -s ours X`. Bezpośrednie scalenie X strategią `ours` pominęłoby zmiany książki między poprzednią synchronizacją a X.
4. Bramka z `--book origin/dev` musi zakończyć się kodem 0, a G1 pokazuje wyłącznie dodane ścieżki. Dalsze synchronizacje przebiegają zwykłym trybem.

## Gałęzie pomocnicze

Gałęzie pomocnicze tworzymy z `origin/cwiczenia`. Po przejściu pełnej bramki (kod 0) i akceptacji autora wracają do `cwiczenia` przez `git merge --ff-only`, po czym wypychamy `cwiczenia` (`git push origin cwiczenia`) i usuwamy gałąź pomocniczą lokalnie oraz, jeśli ją wypchnięto, zdalnie. Gdy przewinięcie się nie udaje, scalamy `origin/cwiczenia` do gałęzi pomocniczej i ponownie uruchamiamy bramkę; gałęzi już wypchniętych nie przebudowujemy. Konflikt w `kurs/aktualnosc.json` rozstrzygamy wersją z `origin/cwiczenia`, po czym przeglądamy aktywności wskazane przez G4 (zwykle aktywności tej gałęzi, które trzeba porównać z nowszą książką) i zapisujemy ich stan poleceniem `--zatwierdz-aktualnosc`.

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
- `kurs/aktualnosc.json` — stan ostatniego przeglądu każdej aktywności: odcisk powiązanej sekcji, commit książki i data (etap G4);
- `kurs/.gitattributes` — atrybut `-merge` pliku `kurs/aktualnosc.json`, który zatrzymuje scalenie na konflikcie;
- `kurs/bez-weryfikacji.txt` — pytania zwolnione z bloku `verify`;
- `kurs/SYNC_LOG.md` — dziennik synchronizacji;
- `.claude/skills/synchronizuj-cwiczenia/SKILL.md` — skill przeprowadzający synchronizację;
- `CLAUDE.md` — reguły redakcyjne książki, obowiązujące także w tekstach ćwiczeń.

W razie rozbieżności co do modelu gałęzi, poleceń i procedur obowiązuje niniejszy przewodnik.
