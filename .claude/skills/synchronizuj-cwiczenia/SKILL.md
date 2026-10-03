---
name: synchronizuj-cwiczenia
description: Synchronizuje projekt ćwiczeń (gałąź cwiczenia) z książką z origin/dev według kurs/README.md — scalenie na gałęzi sync/RRRR-MM-DD, bramka kurs/tools/gate.py z obsługą wiązań (G3) i przeglądem aktywności w sekcjach o zmienionej treści (G4), poprawki wyłącznie w plikach ćwiczeń, kontrola wydania w przeglądarce, jednostronicowy raport dla autora i oczekiwanie na akceptację. Uruchamiany ręcznie w katalogu ../python-notatki-cwiczenia.
argument-hint: "[RRRR-MM-DD]"
disable-model-invocation: true
---

# Synchronizacja ćwiczeń z książką

Skill przeprowadza procedurę „Synchronizacja z dev” z `kurs/README.md` od warunków wstępnych do raportu dla autora i zatrzymuje się przed jej krokiem 8 (przewinięcie `cwiczenia` i wypchnięcie). Wiążący jest `kurs/README.md`. Przed rozpoczęciem przeczytaj w nim sekcje „Zasada jednokierunkowa”, „Zasada wyłącznego dodawania (ang. *add-only*)”, „Bramka” (z podsekcją „Aktualność powiązanych sekcji (G4)”), „Kontrola wydania w przeglądarce”, „Synchronizacja z dev” i „Procedura naprawcza: ćwiczenia w książce”, a także `kurs/AGENTS.md`, reguły redakcyjne z `CLAUDE.md` i rozdział „10. Wersjonowanie aktywności” z `kurs/INTERACTIVE_SYSTEM_SPEC.md`. Jeśli skill i przewodnik się rozchodzą, przerwij pracę i zgłoś rozbieżność autorowi.

Data synchronizacji: `$ARGUMENTS`. Gdy argument jest pusty, przyjmij dzisiejszą datę w zapisie RRRR-MM-DD. Dalej oznaczamy ją DATA, a gałąź synchronizacji — SYNC (zwykle `sync/DATA`).

## Zasady stałe

- Pracujemy w katalogu `D:/PYTHON/NOTATKI/python-notatki-cwiczenia`. Katalogu książki `D:/PYTHON/NOTATKI/python-notatki` i jego gałęzi nie zmieniamy.
- Polecenia wykonujemy narzędziem Bash (Git Bash), a nie w PowerShell: zapis poleceń, zmienne środowiskowe przed poleceniem i ścieżki w tym skillu dotyczą Git Bash.
- Zmieniamy wyłącznie ścieżki z listy dozwolonej (`kurs/README.md`, „Zasada wyłącznego dodawania (ang. *add-only*)”). Plików książki (`docs/**`, `mkdocs.yml`, `CLAUDE.md` i pozostałych) nie poprawiamy, także wtedy, gdy książka wydaje się błędna: usterkę opisujemy w raporcie jako poprawkę dla gałęzi `content/*` tworzonej z `dev`.
- Niczego nie scalamy do `dev` ani `master` i niczego do nich nie wypychamy. Nie przebudowujemy historii (`rebase`), nie nadpisujemy jej (`push --force`, `commit --amend` po wypchnięciu) i nie pomijamy hooków (`--no-verify`).
- Do commitu dodajemy jawnie wskazane ścieżki (`git add <ścieżki>`), nigdy `git add -A` ani `git add .`.
- Każdy commit scalenia tworzymy z komunikatem podanym opcją `-m`. Jeśli sesja dopisuje do commitów wiersz atrybucji (np. `Co-Authored-By: …` z instrukcji sesji), dodajemy go do każdego commitu tej synchronizacji, także do każdego scalenia (`origin/dev` w punktach 1.1.2 i 2, `origin/cwiczenia` w punkcie 6), jako drugi akapit komunikatu, drugą opcją `-m`: `… -m "<temat>" -m "<wiersz atrybucji>"`. Treść wiersza bierzemy z instrukcji sesji i nie przepisujemy jej z wcześniejszych commitów.
- Każde polecenie Pythona uruchamiamy interpreterem środowiska książki z kodowaniem UTF-8, poprzedzając je zmiennymi środowiskowymi: `PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe …`. Bramkę uruchamiamy zawsze z `--book origin/dev`. Wyjątkiem jest kontrola wydania w przeglądarce (punkt 5): uruchamia ją uv, który dostarcza Playwright, a wydanie buduje ten sam interpreter książki, podany w opcji `--python`.
- Przed słowem „akceptuję” autora nie zmieniamy gałęzi `cwiczenia` i niczego nie wypychamy. Jedynym wyjątkiem jest przewinięcie lokalnej gałęzi `cwiczenia` do `origin/cwiczenia` w punkcie 1.5.
- Port 8000 należy do autora, a 8001 do innego projektu; podgląd ćwiczeń uruchamiamy wyłącznie na porcie 8002. Kontrola wydania w przeglądarce sama wybiera wolny port z zakresu 8050–8069 i zatrzymuje swój serwer przed zakończeniem.
- Aktywności nie usuwamy ani nie wiążemy z całą stroną bez decyzji autora. Teksty aktywności piszemy w rejestrze i konwencjach z `CLAUDE.md` (polskie cudzysłowy „…”, terminologia książki).

## 1. Warunki wstępne

1. `git rev-parse --show-toplevel` wskazuje katalog ćwiczeń, a `git branch --show-current` — gałąź `cwiczenia`; na gałęzi innej niż `cwiczenia` i `sync/…` przerywamy. Jeśli bieżąca gałąź to `sync/…` z przerwanej synchronizacji, nie tworzymy nowej: przedstawiamy autorowi jej stan (`git log --oneline --first-parent origin/cwiczenia..HEAD` i wynik pełnej bramki) i pytamy, czy ją kontynuować. Po zgodzie autora wznawiamy ją tak:
    1. `git fetch origin`;
    2. jeśli `git merge-base --is-ancestor origin/dev HEAD` kończy się kodem różnym od 0, książka zmieniła się od przerwania: na bieżącej gałęzi SYNC, bez tworzenia nowej gałęzi, wykonujemy próbne scalenie `PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe kurs/tools/gate.py --book origin/dev --przed-scaleniem` (kod 3 pozwala scalać), a potem `git -c merge.directoryRenames=false merge --no-ff origin/dev -m "Sync with dev (DATA)"` z wierszem atrybucji i obsługą konfliktów jak w punkcie 2; jeśli autor tak woli, zaczynamy zamiast tego od nowa na nowej gałęzi (punkt 1.7);
    3. jeśli `git merge-base --is-ancestor origin/cwiczenia HEAD` kończy się kodem różnym od 0, scalamy `origin/cwiczenia` jak w punkcie 6;
    4. przeliczamy dane z punktu 1.8 i kontynuujemy od punktu 3 pełną bramką.
2. `git status --porcelain --untracked-files=no` nie zwraca nic; w przeciwnym razie przerywamy i pytamy autora. Pliki nieśledzone nie przeszkadzają, ponieważ dodajemy jawnie wskazane ścieżki; ich listę (`git status --porcelain --untracked-files=all | grep '^??'`) podajemy w raporcie.
3. `git fetch origin`.
4. Jeśli `git rev-list --count origin/cwiczenia..origin/dev` zwraca 0, odpowiadamy „nic do synchronizacji”, podajemy skrót `origin/dev` i ostatni wiersz `kurs/SYNC_LOG.md` i kończymy pracę.
5. `git rev-list --left-right --count cwiczenia...origin/cwiczenia` porównuje lokalną gałąź `cwiczenia` z `origin/cwiczenia`. Wynik `0 0` oznacza zgodność; `0 N` — gałąź lokalna jest za `origin/cwiczenia`, więc ją przewijamy (`git merge --ff-only origin/cwiczenia`); pierwsza liczba większa od 0 — gałąź lokalna zawiera commity spoza `origin/cwiczenia`, więc przerywamy i pytamy autora.
6. Jeśli lokalna gałąź `dev` istnieje (`git rev-parse -q --verify refs/heads/dev` kończy się kodem 0; w przeciwnym razie pomijamy ten punkt), a `git rev-list --count origin/dev..refs/heads/dev` zwraca liczbę większą od 0, lokalna gałąź `dev` ma niewypchnięte commity: informujemy autora, że synchronizacja ich nie obejmie (scalamy wyłącznie `origin/dev`), i pytamy, czy kontynuować.
7. Gałąź SYNC: jeśli `git branch --list "sync/DATA*"` i `git branch -r --list "origin/sync/DATA*"` niczego nie zwracają, SYNC to `sync/DATA`. Istniejąca gałąź `sync/DATA` pochodzi zwykle z przerwanej synchronizacji: zanim ją pominiemy, pytamy autora, czy ją kontynuować (punkt 1.1 po przełączeniu na nią), czy rozpocząć nową. Nowa gałąź otrzymuje pierwszą wolną nazwę `sync/DATA-2`, `sync/DATA-3`…; istniejącej gałęzi nie tworzymy od nowa ani nie przestawiamy.
8. Do raportu zapisujemy zakres zmian książki:
    - poprzedni stan `dev`: `git merge-base origin/cwiczenia origin/dev` (równy kolumnie `dev` ostatniego wiersza `kurs/SYNC_LOG.md`);
    - commity: `git log --oneline --no-merges origin/cwiczenia..origin/dev`, a ich liczba: `git rev-list --count --no-merges origin/cwiczenia..origin/dev`;
    - zmienione pliki treści, konfiguracji i motywu: `git diff --stat origin/cwiczenia...origin/dev -- docs mkdocs.yml overrides`; katalog `overrides/` (szablony motywu, `theme.custom_dir`) zmienia także wydanie kursowe, które dziedziczy konfigurację książki;
    - pełne ścieżki zmienionych plików `docs/`: `git diff --name-status origin/cwiczenia...origin/dev -- docs`; podsumowanie `--stat` bez terminala skraca długie ścieżki znakami `...`, a przeniesiony plik zapisuje jako `{stara => nowa}`, dlatego strony z ćwiczeniami (punkt 5) wybieramy z tej listy;
    - pozostałe zmienione ścieżki książki: `git diff --name-status origin/cwiczenia...origin/dev -- . ':!docs' ':!mkdocs.yml' ':!overrides'` (wzorce wykluczeń piszemy w apostrofach, ponieważ w cudzysłowie interaktywna powłoka Git Bash traktuje znak `!` jako odwołanie do historii poleceń). Jeśli jest wśród nich `CLAUDE.md`, którego reguły redakcyjne obowiązują także teksty ćwiczeń, w punkcie 3 sprawdzamy teksty aktywności względem zmienionych reguł. Jeśli jest wśród nich `scripts/check_book_only.py` (strażnik gałęzi książki z własną kopią listy ścieżek warstwy) albo `scripts/install_git_hooks.py` (hooki chroniące gałęzie), porównujemy listę ścieżek warstwy w strażniku z listą dozwoloną (`kurs/README.md`, „Zasada wyłącznego dodawania (ang. *add-only*)”) i z `ALLOWED_PREFIXES` oraz `ALLOWED_FILES` w `kurs/tools/gate.py`, a reguły hooków — z opisem gałęzi w `kurs/README.md`; rozbieżność zgłaszamy w raporcie jako zadanie dla gałęzi `platform/*` albo, gdy błąd leży w strażniku książki, jako usterkę książki. Pozostałe pliki z tej listy tylko wymieniamy w raporcie;
    - zmiany wspólne wydania kursowego, które dotyczą każdej strony, także stron z ćwiczeniami: `git diff --name-status origin/cwiczenia...origin/dev -- mkdocs.yml overrides docs/stylesheets docs/javascripts`.

## 2. Scalenie książki (kroki 1–4 przewodnika)

```bash
git switch --no-track -c SYNC origin/cwiczenia
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe kurs/tools/gate.py --book origin/dev --przed-scaleniem
```

Opcja `--no-track` sprawia, że SYNC nie śledzi `origin/cwiczenia`: samo `git pull` nie scali wtedy `origin/cwiczenia`, a samo `git push` (np. przy `push.default=upstream`) nie przesunie `origin/cwiczenia` przed akceptacją autora; hook `pre-push` chroni wyłącznie `dev` i `master`. Kod 3 pozwala scalać. Przy kodzie 1 przerywamy i składamy raport: kolizję ścieżek rozstrzyga autor (zmiana nazwy po stronie ćwiczeń albo usunięcie ścieżki z książki), a książkę z plikami lub historią ćwiczeń naprawia procedura naprawcza, którą wykonujemy wyłącznie na polecenie autora. Kod 2 oznacza błąd wywołania (np. brak `origin/dev`).

```bash
git -c merge.directoryRenames=false merge --no-ff origin/dev -m "Sync with dev (DATA)"
```

Wiersz atrybucji sesji dodajemy według zasad stałych: `… -m "Sync with dev (DATA)" -m "<wiersz atrybucji>"`.

- Konflikt w ścieżce spoza listy dozwolonej rozstrzygamy zawsze na korzyść książki: `git checkout origin/dev -- <ścieżka>`, a po rozstrzygnięciu wszystkich konfliktów `git commit --no-edit --cleanup=strip`. Opcja `--cleanup=strip` usuwa wiersze komentarza „# Conflicts:”, które git dopisuje do komunikatu scalenia zatrzymanego na konflikcie, i zachowuje komunikat z opcji `-m` razem z wierszem atrybucji; tak samo zatwierdzamy każde inne scalenie zatrzymane na konflikcie (punkt 6). Plików książki nie poprawiamy ręcznie.
- Konflikt w pliku ćwiczeń albo usunięcie plików ćwiczeń przez scalenie zatrzymane na konflikcie: `git merge --abort`, przerwanie pracy i raport.
- Scalenie bez konfliktu zostaje zatwierdzone od razu i `git merge --abort` go nie cofa. Jeśli takie scalenie usunęło pliki ćwiczeń (G1 w punkcie 3 zgłasza „usunęło pliki ćwiczeń”), wracamy na gałąź `cwiczenia` (`git switch cwiczenia`), usuwamy gałąź SYNC (`git branch -D SYNC`) zgodnie z krokiem 1 procedury naprawczej, przerywamy pracę i składamy raport.
- Skrót commitu scalenia (`git rev-parse --short HEAD`) zapisujemy do dziennika i raportu.

## 3. Bramka i ustalenia (krok 5 przewodnika)

```bash
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe kurs/tools/gate.py --book origin/dev
```

Pełna bramka trwa około dwóch minut, czyli niemal tyle, ile wynosi domyślny limit czasu narzędzia Bash, dlatego uruchamiamy ją z limitem 600000 ms albo w tle (`run_in_background`) i czekamy na jej zakończenie. Czytamy cały wynik, nie tylko tabelę podsumowania. Ustalenia obsługujemy w kolejności etapów, każdą grupę poprawek zatwierdzamy osobnym commitem (np. „Rebind exercises after heading changes in dev”, „Adapt exercises to the changed loop sections”) i powtarzamy bramkę aż do kodu 0. Do odbioru służy wyłącznie kod 0; tryb `--katalog-roboczy` (kod 3) wolno stosować tylko w pętli roboczej.

Ustaleniami są wiersze `BŁĄD`. Wiersze `uwaga` nie zmieniają wyniku etapu. Działania wymagają wyłącznie uwagi wskazane w regułach etapów niżej: zmiany wiązań z G3 („zmiana wiązania względem …”, do raportu), lista „aktywności do przejrzenia (N): …” i polecenie „po przeglądzie: …” z G4 (przegląd, potem `--zatwierdz-aktualnosc`), uwagi G5 o zbędnym albo osieroconym wpisie w `kurs/bez-weryfikacji.txt` oraz uwagi G7 z przedrostkiem `usterka książki:` (do raportu). Pozostałe uwagi objaśniają stan albo sąsiedni wiersz `BŁĄD` i nie wymagają osobnego działania, np. powtarzana w każdym przebiegu uwaga G7 o plikach JS warstwy, które build książki kopiuje jako pliki statyczne. Ostrzeżenie albo błąd buildu nie jest uwagą: obsługujemy je według reguły G7.

- **G1** (kolizja, usunięte pliki ćwiczeń, stan książki spoza `origin/dev`, zmieniony plik książki): przerywamy i składamy raport; nie naprawiamy samodzielnie.
- **G2** (lista nakładki nie zaczyna się dokładnie od listy książki: pomija jej pozycję, zmienia postać pozycji, podaje pozycje książki w innej kolejności, stawia pozycję nakładki przed pozycją książki albo powtarza pozycję książki, także w innej postaci; w listach plików `extra_css` i `extra_javascript` własna pozycja nakładki wskazuje plik spoza warstwy ćwiczeń): poprawiamy listę w `mkdocs.kurs.yml` tak, aby zaczynała się od wszystkich pozycji listy książki, przepisanych dosłownie (w tej samej postaci YAML, np. napis pozostaje napisem i nie staje się mapą z polem `path`) i w kolejności z `mkdocs.yml`, a własne pozycje nakładki stały po nich. Brakującą pozycję dopisujemy więc na jej miejscu z listy książki, przed pozycjami warstwy, a powtórzenie usuwamy. Pozycję, którą książka usunęła albo przemianowała (`git diff origin/cwiczenia...origin/dev -- mkdocs.yml`), usuwamy także z nakładki; w listach plików G2 zgłasza ją jako plik spoza warstwy ćwiczeń, a w innej liście wspólnej wskazuje ją wyłącznie ta różnica. Poprawkę odnotowujemy w raporcie (część „Zmiany plików ćwiczeń poza definicjami aktywności”) i w uwagach dziennika.
- **G3** (zerwane wiązanie):
    - przy „prawdopodobnej zmianie nagłówka” czytamy nową sekcję w `docs/<strona>` i, jeśli omawia ten sam materiał, zmieniamy `section_id` w `activities/**/*.yaml` na identyfikator następcy;
    - przy przeniesionej stronie zmieniamy `page` na ścieżkę podaną przez G3; `slot_id` i `activity_id` pozostają bez zmian;
    - przy identyfikatorze z sufiksem `_1`, `_2`… oraz gdy zestawienie nagłówków nie wskazuje następcy, szukamy materiału w książce (`git grep` po charakterystycznych terminach) i przedstawiamy autorowi propozycję: nowe wiązanie, wiązanie z całą stroną (`section_id: null`) albo wycofanie aktywności;
    - odsyłacze książki do brakujących kotwic, także do dawnego identyfikatora zmienionego nagłówka, na innej stronie albo na tej samej, wypisuje etap G7 jako uwagi z przedrostkiem `usterka książki:` (plik, odsyłacz i brakująca kotwica). Build zgłasza taki odsyłacz wyłącznie jako informację, więc `--strict` go nie zatrzymuje; każdą taką uwagę wpisujemy do raportu w części „Usterki książki do poprawy na `content/*`”, niezależnie od tego, czy dotyczy nagłówka powiązanego z aktywnością;
    - każdą zmianę wiązania zapisujemy do raportu jako parę: stary identyfikator („stary nagłówek”) → nowy identyfikator („nowy nagłówek”); G3 wypisuje te pary w uwagach „zmiana wiązania względem …”.
- **G4** (zmieniona treść sekcji, zmienione wiązanie, nowe lub usunięte aktywności). Sekcja h2 obejmuje swoje podsekcje h3–h6, więc aktywność powiązana z podsekcją nie reaguje na zmiany wstępu sekcji nadrzędnej; odcisk pomija m.in. adresy odnośników, ścieżki obrazów i rodzaj wyróżnienia (szczegóły w `kurs/README.md`). Dla każdego zgłoszenia:
    1. jeśli G4 podaje, że identyfikator należy teraz do innego nagłówka albo że treść z przeglądu znajduje się teraz najpewniej w innej sekcji, poprawiamy wiązanie jak w G3, a nie aktywność; identyfikator z sufiksem deduplikacji przedstawiamy autorowi jak w G3;
    2. czytamy różnicę wypisaną przez G4, a gdy jest skrócona albo niejasna, pełne zmiany strony poleceniem `git diff …` podanym przez bramkę; czytamy też całą bieżącą sekcję w `docs/<strona>`;
    3. każdą wymienioną aktywność sprawdzamy względem nowej treści: polecenie (`prompt`), kod startowy (`starter_code`), oczekiwany wynik (`checker.expected_lines`), rozwiązanie wzorcowe i warianty, omówienie (`solution.discussion`), warianty odpowiedzi i `correct_option_id` (klucz odpowiedzi), informacje zwrotne (`feedback`) oraz blok `verify`; sprawdzamy także, czy terminy i zapis zgadzają się z książką i czy nowy przykład książki nie podaje gotowej odpowiedzi na pytanie;
    4. dostosowujemy wyłącznie pliki ćwiczeń. Zmiana brzmienia polecenia bez zmiany jego sensu (pisownia, cudzysłowy, termin, nawiasy przy nazwie funkcji) jest poprawką kosmetyczną i nie zmienia `version`; `version` podnosimy o 1, gdy zmienia się sens polecenia, poprawna odpowiedź, checker albo inny element semantyczny uzasadniający ponowne rozpatrzenie wcześniejszego postępu (rozdział „10. Wersjonowanie aktywności” specyfikacji). Wersje aktywności pilotażowych utrwala test `test_pilot_manifest_emits_all_solutions_and_preserves_versions` w `tests/test_build_activities.py`, więc po podniesieniu wersji zmieniamy w nim oczekiwaną wartość w tym samym commicie;
    5. jeśli nowa treść książki podaje gotową odpowiedź na pytanie `single_choice`, zmieniamy pytanie (np. jego scenariusz) i podnosimy `version`; jeśli podaje rozwiązanie zadania `code`, decyzję pozostawiamy autorowi;
    6. dla każdej aktywności zapisujemy decyzję: „bez zmian” z jednozdaniowym uzasadnieniem, „dostosowano” z opisem zmiany i wersją albo „do decyzji autora” z opisem sprawy. Decyzje można łączyć, np. „dostosowano; do decyzji autora: …”, gdy poprawiamy termin, a autor rozstrzyga, czy zadanie pozostaje sensowne. Decyzja „do decyzji autora” nie wstrzymuje zatwierdzenia aktualności; jeśli autor zmieni aktywność, jej przegląd i zatwierdzenie powtarzamy;
    7. błąd w książce (np. wynik przykładu niezgodny z kodem, sprzeczne zdanie) opisujemy w raporcie jako usterkę do poprawy na `content/*`; aktywność dostosowujemy tylko na tyle, by nie opierała się na błędnym fragmencie.

    Po przejrzeniu wszystkich aktywności, które G4 wymienia na końcu etapu („aktywności do przejrzenia (N): …”), i zatwierdzeniu poprawek zapisujemy nowy stan przeglądu, podając dokładnie te aktywności:

    ```bash
    PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe kurs/tools/gate.py --zatwierdz-aktualnosc --book origin/dev --przejrzane <identyfikatory rozdzielone przecinkami>
    ```

    Polecenie odmawia zapisu (kod 1), dopóki którekolwiek wiązanie jest zerwane albo lista nie obejmuje dokładnie aktywności wymagających przeglądu; wypisuje wtedy oczekiwaną listę z opisem każdej pozycji. Nie uruchamiamy go przed zakończeniem przeglądu i nie wpisujemy aktywności, których nie przejrzeliśmy. Wypisane wpisy porównujemy z przeglądem: „dodano” oznacza nową aktywność, „zmieniono” — zmianę wiązania (także po zmianie nagłówka), nagłówka albo treści sekcji tej aktywności, „usunięto” — aktywność, której już nie ma. Następnie zatwierdzamy `kurs/aktualnosc.json` („Record the review of sections changed in dev (DATA)”).

    Jeśli G4 przechodzi bez zgłoszeń (wynik OK, bez listy „aktywności do przejrzenia”), polecenia `--zatwierdz-aktualnosc` nie uruchamiamy: plik `kurs/aktualnosc.json` pozostaje bez zmian, a tabela „Przegląd aktywności” w raporcie zawiera „brak”, chyba że definicje aktywności zmieniono z innego powodu (np. po ustaleniu G5 albo G6 albo po zmianie reguł redakcyjnych).
- **Reguły redakcyjne** (`CLAUDE.md` wśród pozostałych zmienionych ścieżek z punktu 1.8): czytamy różnicę pliku (`git diff origin/cwiczenia...origin/dev -- CLAUDE.md`) i sprawdzamy teksty wszystkich aktywności (polecenia, warianty odpowiedzi, informacje zwrotne, omówienia, komentarze w kodzie) względem zmienionych reguł. Tekst niezgodny z nową regułą poprawiamy w plikach ćwiczeń, a o `version` rozstrzyga reguła z kroku 4 G4 (zmiana brzmienia bez zmiany sensu jest poprawką kosmetyczną). Każdą zmienioną aktywność wpisujemy do tabeli „Przegląd aktywności” jako inną zmianę definicji.
- **G5** (rozwiązanie albo blok `verify` nie daje oczekiwanego wyniku): poprawiamy aktywność tak, aby rozwiązanie wzorcowe i warianty wypisywały dokładnie `expected_lines`, a `starter_code` ich nie wypisywał; sprawdzenia nie osłabiamy. Wpis w `kurs/bez-weryfikacji.txt`, który G5 opisuje w uwadze jako zbędny (pytanie ma blok `verify`) albo niewskazujący żadnego pytania `single_choice`, usuwamy z pliku i odnotowujemy w części „Zmiany plików ćwiczeń poza definicjami aktywności”.
- **G6** (testy): test, który utrwala dane aktywności (np. wersje w `tests/test_build_activities.py`), aktualizujemy razem ze świadomą zmianą aktywności i odnotowujemy w raporcie; awarię kodu warstwy (hook, JavaScript, bramka) zgłaszamy jako zadanie dla gałęzi `platform/*` i przerywamy.
- **G7** (buildy `--strict`): ostrzeżenie buildu książki (`mkdocs.yml`) jest usterką książki — przerywamy i zgłaszamy ją do poprawy na `content/*`; błąd wydania kursowego wynikający z wiązań poprawiamy jak w G3. Błąd wydania kursowego, który wynika ze zmiany książki, a usuwa go poprawka nakładki (np. ustawienie `mkdocs.kurs.yml` odwołujące się do ścieżki usuniętej przez książkę), poprawiamy w `mkdocs.kurs.yml` i odnotowujemy jak poprawkę G2. Uwagi `usterka książki:` (odsyłacze do brakujących kotwic) nie zatrzymują etapu ani synchronizacji: przenosimy je do raportu jak w G3, a ich liczbę podaje szczegół etapu w tabeli bramki.

## 4. Dziennik i ostatnia bramka (krok 6 przewodnika)

Dopisujemy wiersz na końcu tabeli w `kurs/SYNC_LOG.md` (znaczenie kolumn opisuje ten plik):

```text
| DATA | `<origin/dev, 7 znaków>` | `<commit scalenia, 7 znaków>` | synchronizacja | 0 | <zmienione wiązania; decyzje przeglądu G4 i inne zmiany definicji aktywności (np. po zmianie reguł redakcyjnych); podniesione wersje; zmiany plików ćwiczeń poza definicjami aktywności (np. poprawki nakładki po G2); usterki książki> |
```

Zatwierdzamy go („Log the sync with dev (DATA)”) i ostatni raz uruchamiamy pełną bramkę. Wynik inny niż 0 oznacza powrót do punktu 3. Jeśli po zapisaniu wiersza zmieniła się którakolwiek informacja z kolumny „Uwagi” (po powrocie do punktu 3, po kontroli w przeglądarce albo po uwagach autora), poprawiamy ten wiersz osobnym commitem („Update the sync log (DATA)”) i ponownie uruchamiamy pełną bramkę.

## 5. Raport dla autora (krok 7 przewodnika)

Po ostatniej bramce z kodem 0, a przed raportem, zawsze uruchamiamy kontrolę wydania w przeglądarce (`kurs/README.md`, „Kontrola wydania w przeglądarce”). Sprawdza ona commit `HEAD` gałęzi SYNC i trwa zwykle około półtorej minuty, a gdy warstwa ćwiczeń nie działa — kilka minut. Domyślny limit czasu narzędzia Bash (2 minuty) nie wystarcza, dlatego polecenie uruchamiamy z limitem 600000 ms albo w tle (`run_in_background`) i czekamy na jego zakończenie:

```bash
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 uv run --no-project --with playwright==1.63.0 python kurs/tools/sprawdz_wydanie.py --python D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe
```

Do raportu służy wyłącznie przebieg bez opcji `--katalog-roboczy`, która daje wynik roboczy (kod 3).

- Kod 0: tabelę podsumowania narzędzia przenosimy do raportu, a jego uwagi (np. niedostępne zewnętrzne serwery czcionek) streszczamy jednym zdaniem.
- Kod 1: każde zgłoszenie `BŁĄD` przenosimy do raportu z oceną przyczyny. Usterkę plików ćwiczeń, którą usuwa poprawka na gałęzi SYNC — w nakładce `mkdocs.kurs.yml` (listy, `watch`) albo w wiązaniach, także gdy wynika ze zmiany książki (np. pozycja usunięta z listy książki) — poprawiamy na gałęzi SYNC i wracamy do punktu 3. Awarię kodu warstwy (hook, JavaScript, CSS warstwy) zgłaszamy jako zadanie dla gałęzi `platform/*`, a usterkę samej książki (np. jej stylów, skryptów albo szablonów motywu) — jako usterkę książki do poprawy na `content/*`; w tych dwóch przypadkach plików nie poprawiamy, raport podaje kod 1, a o dalszym postępowaniu decyduje autor.
- Kod 2: kontroli nie przeprowadzono (np. brak Playwright, Microsoft Edge albo wolnego portu z zakresu 8050–8069, albo błąd narzędzia). Raport podaje to wraz z przyczyną z wyniku narzędzia i przenosi listę kontrolną podglądu z `kurs/README.md` („Kontrola wydania w przeglądarce”), którą autor wykonuje w podglądzie na porcie 8002.

Przed uruchomieniem podglądu sprawdzamy, czy port 8002 jest zajęty: `netstat -ano | grep -E ':8002 +[^ ]+ +LISTENING'`. Puste wyjście oznacza wolny port; wiersze w stanie `TIME_WAIT` po wcześniejszym podglądzie nie mają znaczenia. Jeśli port nasłuchuje, a serwer uruchomiła ta sesja (podgląd tej synchronizacji z katalogu ćwiczeń), zatrzymujemy go; w przeciwnym razie pytamy autora i portu nie zmieniamy. Następnie uruchamiamy w tle podgląd z katalogu ćwiczeń:

```bash
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe -m mkdocs serve -f mkdocs.kurs.yml -a 127.0.0.1:8002 --watch-theme
```

Raport przedstawiamy w odpowiedzi, nie w pliku, według wzoru (puste części wypełniamy słowem „brak”).

- Część „Strony z ćwiczeniami, których Markdown zmienia synchronizacja” wymienia strony wskazane polem `page` definicji w `activities/`, których plik `docs/<page>` jest na liście `--name-status` plików `docs/` z punktu 1.8; przy przeniesionej stronie (wiersz `R…`) liczy się nowa ścieżka. Zmiany wspólne, które dotyczą każdej strony (np. etykieta części w `nav` albo menu w belce), trafiają do części „Zmiany wspólne wydania kursowego” razem z wynikiem kontroli w przeglądarce.
- Kontrola w przeglądarce nie ocenia wyglądu (np. kolorów i odstępów). Jeśli zmiany wspólne obejmują style (`docs/stylesheets/`) albo szablony motywu (`overrides/`), część „Zmiany wspólne wydania kursowego” prosi autora o obejrzenie w podglądzie na porcie 8002, w trybie jasnym i ciemnym oraz w oknie szerokim i wąskim, wskazanych stron: jednej strony z ćwiczeniami i jednej strony bez ćwiczeń, na której widać zmieniony element.
- Tabela „Przegląd aktywności” ma jeden wiersz dla każdej aktywności, której wpis w `kurs/aktualnosc.json` zmienia ta synchronizacja (`git diff origin/cwiczenia...SYNC -- kurs/aktualnosc.json`; jeden wiersz pliku odpowiada jednej aktywności), oraz dla każdej aktywności, której definicję zmieniono z innego powodu (np. wersję podniesioną po ustaleniu G5 albo G6), tak aby autor mógł porównać tabelę z różnicą pliku. Kolumna „Wpis” podaje „dodano”, „zmieniono”, „usunięto” albo „bez zmian”, a kolumna „Wersja” — „n (bez zmian)” albo „n → n+1”.
- Część „Zmiany plików ćwiczeń poza definicjami aktywności” opisuje zmiany ścieżek ćwiczeń, które wprowadza gałąź SYNC (np. poprawkę listy w `mkdocs.kurs.yml` po ustaleniu G2, usunięty wpis `kurs/bez-weryfikacji.txt` albo wersję w teście aktywności pilotażowych). Polecenie porównuje SYNC ze wspólnym przodkiem z `origin/cwiczenia` (zapis z trzema kropkami), czyli z ostatnim stanem `origin/cwiczenia`, który SYNC zawiera, wyłącznie na ścieżkach z listy dozwolonej, których książka nigdy nie zmienia (G1). Wynik nie zależy więc od liczby scaleń `origin/dev` i `origin/cwiczenia` ani od tego, czy `origin/cwiczenia` przesunęła się od utworzenia SYNC. Polecenie pomija definicje aktywności (`activities/`) i `kurs/aktualnosc.json`, które opisuje tabela przeglądu, oraz `kurs/SYNC_LOG.md`, czyli dziennik tej synchronizacji.

```markdown
## Synchronizacja ćwiczeń z książką — DATA

Gałąź `SYNC` od `origin/cwiczenia` (`<sha>`); scalono `origin/dev` (`<sha>`) commitem `<sha>`.

**Zmiany książki** (`<poprzedni dev>..<nowy dev>`, liczba commitów: <N>):
- `<sha>` <temat commitu>

Zmienione pliki `docs/`, `mkdocs.yml` i `overrides/`: <podsumowanie `git diff --stat` z punktu 1.8>

Pozostałe zmienione ścieżki książki: <lista `git diff --name-status` z punktu 1.8; przy `CLAUDE.md` wynik sprawdzenia tekstów aktywności>

**Commity gałęzi SYNC** (`git log --oneline --first-parent origin/cwiczenia..SYNC`):
- `<sha>` <temat commitu>

**Strony z ćwiczeniami, których Markdown zmienia synchronizacja:**

| Strona | Sekcja (nagłówek) | Aktywności | Zmiana w książce |
|---|---|---|---|

**Zmiany wspólne wydania kursowego** (`mkdocs.yml`, `overrides/`, `docs/stylesheets/`, `docs/javascripts/`; dotyczą każdej strony, także stron z ćwiczeniami): <lista z punktu 1.8 albo „brak”>; kontrola w przeglądarce: kod <0, 1 albo 2> (niżej). <przy zmianie stylów albo szablonów motywu: „Proszę obejrzeć w podglądzie, w trybie jasnym i ciemnym oraz w oknie szerokim i wąskim, strony: <adres strony z ćwiczeniami>, <adres strony bez ćwiczeń>”>

**Kontrola wydania w przeglądarce** (`kurs/tools/sprawdz_wydanie.py`, commit `<sha>`): kod <0, 1 albo 2>

| Kontrola | jasny 1280 | ciemny 1280 | jasny 375 | ciemny 375 |
|---|---|---|---|---|
| <wiersz z tabeli narzędzia> | … | … | … | … |

<przy kodzie 2 zamiast tabeli: przyczyna z wyniku narzędzia i lista kontrolna podglądu z `kurs/README.md`>

**Zmienione wiązania (G3):**

| Aktywność | Było | Jest |
|---|---|---|

**Przegląd aktywności (G4 i inne zmiany definicji):**

| Aktywność | Wpis | Decyzja | Wersja | Uzasadnienie |
|---|---|---|---|---|

**Zmiany plików ćwiczeń poza definicjami aktywności** (`git diff --name-status origin/cwiczenia...SYNC -- mkdocs.kurs.yml kurs scripts/build_activities.py docs/javascripts/interactive docs/stylesheets/interactive.css tests/interactive tests/test_build_activities.py .github/workflows/kurs.yml .claude/skills/synchronizuj-cwiczenia ':!kurs/aktualnosc.json' ':!kurs/SYNC_LOG.md'`): <pliki z opisem zmiany albo „brak”>

**Usterki książki do poprawy na `content/*`:** <uwagi G7 `usterka książki:`, usterki z przeglądu G4 i z kontroli w przeglądarce albo „brak”>

**Pliki nieśledzone w katalogu ćwiczeń:** <lista albo „brak”>

**Bramka** (`--book origin/dev`, commit `<sha>`): kod 0

| Etap | Wynik |
|---|---|
| G1 | <wynik z tabeli bramki> |
| … | … |
| G7 | <wynik z tabeli bramki> |

**Podgląd:** http://127.0.0.1:8002/ (gałąź `SYNC`), serwer uruchomiony poleceniem:
`PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe -m mkdocs serve -f mkdocs.kurs.yml -a 127.0.0.1:8002 --watch-theme`

Proszę o „akceptuję” albo o uwagi.
```

Następnie czekamy na odpowiedź autora. Uwagi wprowadzamy na gałęzi SYNC (wyłącznie w plikach ćwiczeń), powtarzamy bramkę i kontrolę wydania w przeglądarce, a po zmianie aktywności z przeglądu G4 także zatwierdzenie aktualności; jeśli zmienia się przy tym którakolwiek informacja z kolumny „Uwagi” dziennika, poprawiamy jego wiersz (punkt 4). Potem przedstawiamy poprawiony raport i ponownie czekamy na „akceptuję”. Serwer podglądu działa do decyzji autora; jeśli sesja kończy się bez akceptacji, zatrzymujemy go przed jej zakończeniem, a gałąź SYNC pozostaje do kontynuacji (punkt 1.1).

## 6. Po akceptacji (krok 8 przewodnika)

Dopiero po słowie „akceptuję” sprawdzamy, czy SYNC zawiera aktualny stan `origin/cwiczenia`:

```bash
git fetch origin
git merge-base --is-ancestor origin/cwiczenia SYNC
```

Przy kodzie 0 przewijamy `cwiczenia` i wypychamy wynik:

```bash
git switch cwiczenia
git merge --ff-only SYNC
git push origin cwiczenia
git branch -d SYNC
```

Następnie zatrzymujemy serwer podglądu i podajemy autorowi skrót nowego `origin/cwiczenia`. Gałęzi SYNC nie wypychamy; jeśli jednak ją wypchnięto, usuwamy ją także w `origin` (`git push origin --delete SYNC`).

Jeśli `git merge-base --is-ancestor` kończy się kodem 1, przewinięcie się nie udaje albo `git push` zostaje odrzucony, ponieważ na `cwiczenia` trafiła w międzyczasie inna zmiana, nie przebudowujemy gałęzi: `git fetch origin`, `git switch SYNC`, `git merge --no-ff origin/cwiczenia -m "Merge origin/cwiczenia into SYNC"` (z wierszem atrybucji według zasad stałych), pełna bramka do kodu 0 (z przeglądem G4 i zatwierdzeniem, jeśli bramka go wymaga), kontrola wydania w przeglądarce (punkt 5), krótkie uzupełnienie raportu i ponowne oczekiwanie na akceptację. Lokalna gałąź `cwiczenia` przewinięta przed odrzuconym wypchnięciem pozostaje przodkiem SYNC, więc po akceptacji przewija się ponownie. Konflikt w `kurs/aktualnosc.json` (git zgłasza go jako konflikt pliku binarnego) rozstrzygamy wyłącznie poleceniem `git checkout origin/cwiczenia -- kurs/aktualnosc.json` (pliku nie scalamy ręcznie, nie wybieramy fragmentów i nie usuwamy go) i zatwierdzamy scalenie poleceniem `git commit --no-edit --cleanup=strip` (punkt 2), a po zatwierdzeniu scalenia przeglądamy ponownie wszystkie aktywności wskazane przez G4. Plik `kurs/aktualnosc.json` zapisuje odcisk treści książki, a nie definicji aktywności, dlatego przed tym przeglądem wypisujemy także pliki aktywności zmienione po drugiej stronie (`git diff --name-only SYNC^1...origin/cwiczenia -- activities`, gdzie `SYNC^1` to stan SYNC sprzed scalenia `origin/cwiczenia`). Każdą aktywność z tych plików, której sekcję przeglądaliśmy w tej synchronizacji, sprawdzamy ponownie wobec nowej treści książki i odnotowujemy w raporcie.
