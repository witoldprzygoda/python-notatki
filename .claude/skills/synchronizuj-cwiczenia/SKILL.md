---
name: synchronizuj-cwiczenia
description: Synchronizuje projekt ćwiczeń (gałąź cwiczenia) z książką z origin/dev według kurs/README.md — scalenie na gałęzi sync/RRRR-MM-DD, bramka kurs/tools/gate.py z obsługą wiązań (G3) i przeglądem aktywności w sekcjach o zmienionej treści (G4), poprawki wyłącznie w plikach ćwiczeń, jednostronicowy raport dla autora i oczekiwanie na akceptację. Uruchamiany ręcznie w katalogu ../python-notatki-cwiczenia.
argument-hint: "[RRRR-MM-DD]"
disable-model-invocation: true
---

# Synchronizacja ćwiczeń z książką

Skill przeprowadza procedurę „Synchronizacja z dev” z `kurs/README.md` od warunków wstępnych do raportu dla autora i zatrzymuje się przed jej krokiem 8 (przewinięcie `cwiczenia` i wypchnięcie). Wiążący jest `kurs/README.md`. Przed rozpoczęciem przeczytaj w nim sekcje „Zasada jednokierunkowa”, „Zasada wyłącznego dodawania”, „Bramka” (z podsekcją „Aktualność powiązanych sekcji (G4)”), „Synchronizacja z dev” i „Procedura naprawcza”, a także `kurs/AGENTS.md`, reguły redakcyjne z `CLAUDE.md` i rozdział „Wersjonowanie aktywności” z `kurs/INTERACTIVE_SYSTEM_SPEC.md`. Jeśli skill i przewodnik się rozchodzą, przerwij pracę i zgłoś rozbieżność autorowi.

Data synchronizacji: `$ARGUMENTS`. Gdy argument jest pusty, przyjmij dzisiejszą datę w zapisie RRRR-MM-DD. Dalej oznaczamy ją DATA, a gałąź synchronizacji — SYNC (zwykle `sync/DATA`).

## Zasady stałe

- Pracujemy w katalogu `D:/PYTHON/NOTATKI/python-notatki-cwiczenia`. Katalogu książki `D:/PYTHON/NOTATKI/python-notatki` i jego gałęzi nie zmieniamy.
- Polecenia wykonujemy narzędziem Bash (Git Bash), a nie w PowerShell: zapis poleceń, zmienne środowiskowe przed poleceniem i ścieżki w tym skillu dotyczą Git Bash.
- Zmieniamy wyłącznie ścieżki z listy dozwolonej (`kurs/README.md`, „Zasada wyłącznego dodawania”). Plików książki (`docs/**`, `mkdocs.yml`, `CLAUDE.md` i pozostałych) nie poprawiamy, także wtedy, gdy książka wydaje się błędna: usterkę opisujemy w raporcie jako poprawkę dla gałęzi `content/*` tworzonej z `dev`.
- Niczego nie scalamy do `dev` ani `master` i niczego do nich nie wypychamy. Nie przebudowujemy historii (`rebase`), nie nadpisujemy jej (`push --force`, `commit --amend` po wypchnięciu) i nie pomijamy hooków (`--no-verify`).
- Do commitu dodajemy jawnie wskazane ścieżki (`git add <ścieżki>`), nigdy `git add -A` ani `git add .`.
- Każde polecenie Pythona uruchamiamy interpreterem środowiska książki z kodowaniem UTF-8, poprzedzając je zmiennymi środowiskowymi: `PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe …`. Bramkę uruchamiamy zawsze z `--book origin/dev`.
- Przed słowem „akceptuję” autora nie zmieniamy gałęzi `cwiczenia` i niczego nie wypychamy. Jedynym wyjątkiem jest przewinięcie lokalnej gałęzi `cwiczenia` do `origin/cwiczenia` w punkcie 1.5.
- Port 8000 należy do autora, a 8001 do innego projektu; podgląd ćwiczeń uruchamiamy wyłącznie na porcie 8002.
- Aktywności nie usuwamy ani nie wiążemy z całą stroną bez decyzji autora. Teksty aktywności piszemy w rejestrze i konwencjach z `CLAUDE.md` (polskie cudzysłowy „…”, terminologia książki).

## 1. Warunki wstępne

1. `git rev-parse --show-toplevel` wskazuje katalog ćwiczeń, a `git branch --show-current` — gałąź `cwiczenia`; na gałęzi innej niż `cwiczenia` i `sync/…` przerywamy. Jeśli bieżąca gałąź to `sync/…` z przerwanej synchronizacji, nie tworzymy nowej: przedstawiamy autorowi jej stan (`git log --oneline --first-parent origin/cwiczenia..HEAD` i wynik pełnej bramki) i pytamy, czy ją kontynuować. Po zgodzie autora wznawiamy ją tak:
    1. `git fetch origin`;
    2. jeśli `git merge-base --is-ancestor origin/dev HEAD` kończy się kodem różnym od 0, książka zmieniła się od przerwania: scalamy `origin/dev` ponownie (punkt 2: próbne scalenie, potem scalenie) albo, jeśli autor tak woli, zaczynamy od nowa na nowej gałęzi (punkt 1.7);
    3. jeśli `git merge-base --is-ancestor origin/cwiczenia HEAD` kończy się kodem różnym od 0, scalamy `origin/cwiczenia` jak w punkcie 6;
    4. przeliczamy dane z punktu 1.8 i kontynuujemy od punktu 3 pełną bramką.
2. `git status --porcelain --untracked-files=no` nie zwraca nic; w przeciwnym razie przerywamy i pytamy autora. Pliki nieśledzone nie przeszkadzają, ponieważ dodajemy jawnie wskazane ścieżki; ich listę (`git status --porcelain --untracked-files=all | grep '^??'`) podajemy w raporcie.
3. `git fetch origin`.
4. Jeśli `git rev-list --count origin/cwiczenia..origin/dev` zwraca 0, odpowiadamy „nic do synchronizacji”, podajemy skrót `origin/dev` i ostatni wiersz `kurs/SYNC_LOG.md` i kończymy pracę.
5. `git rev-list --left-right --count cwiczenia...origin/cwiczenia` porównuje lokalną gałąź `cwiczenia` z `origin/cwiczenia`. Wynik `0 0` oznacza zgodność; `0 N` — gałąź lokalna jest za `origin/cwiczenia`, więc ją przewijamy (`git merge --ff-only origin/cwiczenia`); pierwsza liczba większa od 0 — gałąź lokalna zawiera commity spoza `origin/cwiczenia`, więc przerywamy i pytamy autora.
6. Jeśli `git rev-list --count origin/dev..dev` zwraca liczbę większą od 0, lokalna gałąź `dev` ma niewypchnięte commity: informujemy autora, że synchronizacja ich nie obejmie (scalamy wyłącznie `origin/dev`), i pytamy, czy kontynuować.
7. Gałąź SYNC: jeśli `git branch --list "sync/DATA*"` i `git branch -r --list "origin/sync/DATA*"` niczego nie zwracają, SYNC to `sync/DATA`. Istniejąca gałąź `sync/DATA` pochodzi zwykle z przerwanej synchronizacji: zanim ją pominiemy, pytamy autora, czy ją kontynuować (punkt 1.1 po przełączeniu na nią), czy rozpocząć nową. Nowa gałąź otrzymuje pierwszą wolną nazwę `sync/DATA-2`, `sync/DATA-3`…; istniejącej gałęzi nie tworzymy od nowa ani nie przestawiamy.
8. Do raportu zapisujemy zakres zmian książki: poprzedni stan `dev` to `git merge-base origin/cwiczenia origin/dev` (równy kolumnie `dev` ostatniego wiersza `kurs/SYNC_LOG.md`), commity podaje `git log --oneline --no-merges origin/cwiczenia..origin/dev`, a zmienione pliki — `git diff --stat origin/cwiczenia...origin/dev -- docs mkdocs.yml`.

## 2. Scalenie książki (kroki 1–4 przewodnika)

```bash
git switch -c SYNC origin/cwiczenia
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe kurs/tools/gate.py --book origin/dev --przed-scaleniem
```

Kod 3 pozwala scalać. Przy kodzie 1 przerywamy i składamy raport: kolizję ścieżek rozstrzyga autor (zmiana nazwy po stronie ćwiczeń albo usunięcie ścieżki z książki), a książkę z plikami lub historią ćwiczeń naprawia procedura naprawcza, którą wykonujemy wyłącznie na polecenie autora. Kod 2 oznacza błąd wywołania (np. brak `origin/dev`).

```bash
git -c merge.directoryRenames=false merge --no-ff origin/dev -m "Sync with dev (DATA)"
```

- Konflikt w ścieżce spoza listy dozwolonej rozstrzygamy zawsze na korzyść książki: `git checkout origin/dev -- <ścieżka>`, a po rozstrzygnięciu wszystkich konfliktów `git commit --no-edit`. Plików książki nie poprawiamy ręcznie.
- Konflikt w pliku ćwiczeń albo usunięcie plików ćwiczeń przez scalenie zatrzymane na konflikcie: `git merge --abort`, przerwanie pracy i raport.
- Scalenie bez konfliktu zostaje zatwierdzone od razu i `git merge --abort` go nie cofa. Jeśli takie scalenie usunęło pliki ćwiczeń (G1 w punkcie 3 zgłasza „usunęło pliki ćwiczeń”), wracamy na gałąź `cwiczenia` (`git switch cwiczenia`), usuwamy gałąź SYNC (`git branch -D SYNC`) zgodnie z krokiem 1 procedury naprawczej, przerywamy pracę i składamy raport.
- Skrót commitu scalenia (`git rev-parse --short HEAD`) zapisujemy do dziennika i raportu.

## 3. Bramka i ustalenia (krok 5 przewodnika)

```bash
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe kurs/tools/gate.py --book origin/dev
```

Pełna bramka trwa około minuty. Czytamy cały wynik, nie tylko tabelę podsumowania. Ustalenia obsługujemy w kolejności etapów, każdą grupę poprawek zatwierdzamy osobnym commitem (np. „Rebind exercises after heading changes in dev”, „Adapt exercises to the changed loop sections”) i powtarzamy bramkę aż do kodu 0. Do odbioru służy wyłącznie kod 0; tryb `--katalog-roboczy` (kod 3) wolno stosować tylko w pętli roboczej.

- **G1** (kolizja, usunięte pliki ćwiczeń, stan książki spoza `origin/dev`, zmieniony plik książki): przerywamy i składamy raport; nie naprawiamy samodzielnie.
- **G2** (lista nakładki pomija pozycję listy książki): dopisujemy brakującą pozycję do `mkdocs.kurs.yml` w kolejności z `mkdocs.yml`.
- **G3** (zerwane wiązanie):
    - przy „prawdopodobnej zmianie nagłówka” czytamy nową sekcję w `docs/<strona>` i, jeśli omawia ten sam materiał, zmieniamy `section_id` w `activities/**/*.yaml` na identyfikator następcy;
    - przy przeniesionej stronie zmieniamy `page` na ścieżkę podaną przez G3; `slot_id` i `activity_id` pozostają bez zmian;
    - przy identyfikatorze z sufiksem `_1`, `_2`… oraz gdy zestawienie nagłówków nie wskazuje następcy, szukamy materiału w książce (`git grep` po charakterystycznych terminach) i przedstawiamy autorowi propozycję: nowe wiązanie, wiązanie z całą stroną (`section_id: null`) albo wycofanie aktywności;
    - przy każdej zmianie nagłówka szukamy odsyłaczy książki do dawnego identyfikatora: `git grep -n -F "#<stary-id>" origin/dev -- docs`, a spośród wyników bierzemy odsyłacze do tej strony (`<plik strony>#<stary-id>`) i odsyłacze wewnątrz niej (`(#<stary-id>`). Build zgłasza taki zerwany odsyłacz wyłącznie jako informację, więc `--strict` go nie zatrzymuje; znalezione odsyłacze wpisujemy do raportu jako usterki książki do poprawy na `content/*`;
    - każdą zmianę wiązania zapisujemy do raportu jako parę: stary identyfikator („stary nagłówek”) → nowy identyfikator („nowy nagłówek”); G3 wypisuje te pary w notatkach „zmiana wiązania względem …”.
- **G4** (zmieniona treść sekcji, zmienione wiązanie, nowe lub usunięte aktywności). Sekcja h2 obejmuje swoje podsekcje h3–h6, więc aktywność powiązana z podsekcją nie reaguje na zmiany wstępu sekcji nadrzędnej; odcisk pomija m.in. adresy odnośników, ścieżki obrazów i rodzaj wyróżnienia (szczegóły w `kurs/README.md`). Dla każdego zgłoszenia:
    1. jeśli G4 podaje, że identyfikator należy teraz do innego nagłówka albo że treść z przeglądu znajduje się teraz najpewniej w innej sekcji, poprawiamy wiązanie jak w G3, a nie aktywność; identyfikator z sufiksem deduplikacji przedstawiamy autorowi jak w G3;
    2. czytamy różnicę wypisaną przez G4, a gdy jest skrócona albo niejasna, pełne zmiany strony poleceniem `git diff …` podanym przez bramkę; czytamy też całą bieżącą sekcję w `docs/<strona>`;
    3. każdą wymienioną aktywność sprawdzamy względem nowej treści: polecenie (`prompt`), kod startowy (`starter_code`), oczekiwany wynik (`checker.expected_lines`), rozwiązanie wzorcowe i warianty, omówienie (`solution.discussion`), warianty odpowiedzi i `correct_option_id` (klucz odpowiedzi), informacje zwrotne (`feedback`) oraz blok `verify`; sprawdzamy także, czy terminy i zapis zgadzają się z książką i czy nowy przykład książki nie podaje gotowej odpowiedzi na pytanie;
    4. dostosowujemy wyłącznie pliki ćwiczeń; `version` podnosimy o 1, gdy zmienia się polecenie, poprawna odpowiedź, checker albo inny element semantyczny, a poprawka kosmetyczna wersji nie zmienia; wersje aktywności pilotażowych utrwala test `test_pilot_manifest_emits_all_solutions_and_preserves_versions` w `tests/test_build_activities.py`, więc po podniesieniu wersji zmieniamy w nim oczekiwaną wartość w tym samym commicie;
    5. jeśli nowa treść książki podaje gotową odpowiedź na pytanie `single_choice`, zmieniamy pytanie (np. jego scenariusz) i podnosimy `version`; jeśli podaje rozwiązanie zadania `code`, decyzję pozostawiamy autorowi;
    6. dla każdej aktywności zapisujemy decyzję: „bez zmian” z jednozdaniowym uzasadnieniem, „dostosowano” z opisem zmiany i wersją albo „do decyzji autora” z opisem sprawy. Decyzje można łączyć, np. „dostosowano; do decyzji autora: …”, gdy poprawiamy termin, a autor rozstrzyga, czy zadanie pozostaje sensowne. Decyzja „do decyzji autora” nie wstrzymuje zatwierdzenia aktualności; jeśli autor zmieni aktywność, jej przegląd i zatwierdzenie powtarzamy;
    7. błąd w książce (np. wynik przykładu niezgodny z kodem, sprzeczne zdanie) opisujemy w raporcie jako usterkę do poprawy na `content/*`; aktywność dostosowujemy tylko na tyle, by nie opierała się na błędnym fragmencie.

    Po przejrzeniu wszystkich aktywności, które G4 wymienia na końcu etapu („aktywności do przejrzenia (N): …”), i zatwierdzeniu poprawek zapisujemy nowy stan przeglądu, podając dokładnie te aktywności:

    ```bash
    PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe kurs/tools/gate.py --zatwierdz-aktualnosc --book origin/dev --przejrzane <identyfikatory rozdzielone przecinkami>
    ```

    Polecenie odmawia zapisu (kod 1), dopóki którekolwiek wiązanie jest zerwane albo lista nie obejmuje dokładnie aktywności wymagających przeglądu; wypisuje wtedy oczekiwaną listę z opisem każdej pozycji. Nie uruchamiamy go przed zakończeniem przeglądu i nie wpisujemy aktywności, których nie przejrzeliśmy. Wypisane wpisy porównujemy z przeglądem: „dodano” oznacza nową aktywność, „zmieniono” — zmianę wiązania (także po zmianie nagłówka), nagłówka albo treści sekcji tej aktywności, „usunięto” — aktywność, której już nie ma. Następnie zatwierdzamy `kurs/aktualnosc.json` („Record the review of sections changed in dev (DATA)”).
- **G5** (rozwiązanie albo blok `verify` nie daje oczekiwanego wyniku): poprawiamy aktywność tak, aby rozwiązanie wzorcowe i warianty wypisywały dokładnie `expected_lines`, a `starter_code` ich nie wypisywał; sprawdzenia nie osłabiamy.
- **G6** (testy): test, który utrwala dane aktywności (np. wersje w `tests/test_build_activities.py`), aktualizujemy razem ze świadomą zmianą aktywności i odnotowujemy w raporcie; awarię kodu warstwy (hook, JavaScript, bramka) zgłaszamy jako zadanie dla gałęzi `platform/*` i przerywamy.
- **G7** (buildy `--strict`): ostrzeżenie buildu książki (`mkdocs.yml`) jest usterką książki — przerywamy i zgłaszamy ją do poprawy na `content/*`; błąd wydania kursowego wynikający z wiązań poprawiamy jak w G3.

## 4. Dziennik i ostatnia bramka (krok 6 przewodnika)

Dopisujemy wiersz na końcu tabeli w `kurs/SYNC_LOG.md` (znaczenie kolumn opisuje ten plik):

```text
| DATA | `<origin/dev, 7 znaków>` | `<commit scalenia, 7 znaków>` | synchronizacja | 0 | <zmienione wiązania; decyzje przeglądu G4; podniesione wersje; usterki książki> |
```

Zatwierdzamy go („Log the sync with dev (DATA)”) i ostatni raz uruchamiamy pełną bramkę. Wynik inny niż 0 oznacza powrót do punktu 3. Jeśli po zapisaniu wiersza zmieniły się wiązania, decyzje przeglądu albo wersje (po powrocie do punktu 3 albo po uwagach autora), poprawiamy ten wiersz osobnym commitem („Update the sync log (DATA)”) i ponownie uruchamiamy pełną bramkę.

## 5. Raport dla autora (krok 7 przewodnika)

Przed uruchomieniem podglądu sprawdzamy, czy port 8002 jest zajęty: `netstat -ano | grep -E ':8002 +[^ ]+ +LISTENING'`. Puste wyjście oznacza wolny port; wiersze w stanie `TIME_WAIT` po wcześniejszym podglądzie nie mają znaczenia. Jeśli port nasłuchuje, a serwer uruchomiła ta sesja (podgląd tej synchronizacji z katalogu ćwiczeń), zatrzymujemy go; w przeciwnym razie pytamy autora i portu nie zmieniamy. Następnie uruchamiamy w tle podgląd z katalogu ćwiczeń:

```bash
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe -m mkdocs serve -f mkdocs.kurs.yml -a 127.0.0.1:8002
```

Raport przedstawiamy w odpowiedzi, nie w pliku, według wzoru (puste części wypełniamy słowem „brak”). Tabela „Przegląd aktywności” ma jeden wiersz dla każdej aktywności, której wpis w `kurs/aktualnosc.json` zmienia ta synchronizacja (`git diff origin/cwiczenia...SYNC -- kurs/aktualnosc.json`; jeden wiersz pliku odpowiada jednej aktywności), oraz dla każdej aktywności, której definicję zmieniono z innego powodu (np. wersję podniesioną po ustaleniu G5 albo G6), tak aby autor mógł porównać tabelę z różnicą pliku. Kolumna „Wpis” podaje „dodano”, „zmieniono”, „usunięto” albo „bez zmian”, a kolumna „Wersja” — „n (bez zmian)” albo „n → n+1”.

```markdown
## Synchronizacja ćwiczeń z książką — DATA

Gałąź `SYNC` od `origin/cwiczenia` (`<sha>`); scalono `origin/dev` (`<sha>`) commitem `<sha>`.

**Zmiany książki** (`<poprzedni dev>..<nowy dev>`, <liczba> commitów):
- `<sha>` <temat commitu>

Zmienione pliki: <podsumowanie `git diff --stat` z punktu 1.8>

**Strony z ćwiczeniami, których dotyczą zmiany:**

| Strona | Sekcja (nagłówek) | Aktywności | Zmiana w książce |
|---|---|---|---|

**Zmienione wiązania (G3):**

| Aktywność | Było | Jest |
|---|---|---|

**Przegląd aktywności (G4 i inne zmiany definicji):**

| Aktywność | Wpis | Decyzja | Wersja | Uzasadnienie |
|---|---|---|---|---|

**Usterki książki do poprawy na `content/*`:** <lista albo „brak”>

**Pliki nieśledzone w katalogu ćwiczeń:** <lista albo „brak”>

**Bramka** (`--book origin/dev`, commit `<sha>`): kod 0

| Etap | Wynik |
|---|---|
| G1 | <wynik z tabeli bramki> |
| … | … |
| G7 | <wynik z tabeli bramki> |

**Podgląd:** http://127.0.0.1:8002/ (gałąź `SYNC`), serwer uruchomiony poleceniem:
`PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe -m mkdocs serve -f mkdocs.kurs.yml -a 127.0.0.1:8002`

Proszę o „akceptuję” albo o uwagi.
```

Następnie czekamy na odpowiedź autora. Uwagi wprowadzamy na gałęzi SYNC (wyłącznie w plikach ćwiczeń), powtarzamy bramkę, a po zmianie aktywności z przeglądu G4 także zatwierdzenie aktualności; jeśli zmieniają się przy tym wiązania, decyzje albo wersje, poprawiamy wiersz dziennika (punkt 4). Potem przedstawiamy poprawiony raport i ponownie czekamy na „akceptuję”. Serwer podglądu działa do decyzji autora; jeśli sesja kończy się bez akceptacji, zatrzymujemy go przed jej zakończeniem, a gałąź SYNC pozostaje do kontynuacji (punkt 1.1).

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

Jeśli `git merge-base --is-ancestor` kończy się kodem 1, przewinięcie się nie udaje albo `git push` zostaje odrzucony, ponieważ na `cwiczenia` trafiła w międzyczasie inna zmiana, nie przebudowujemy gałęzi: `git fetch origin`, `git switch SYNC`, `git merge --no-ff origin/cwiczenia`, pełna bramka do kodu 0 (z przeglądem G4 i zatwierdzeniem, jeśli bramka go wymaga), krótkie uzupełnienie raportu i ponowne oczekiwanie na akceptację. Lokalna gałąź `cwiczenia` przewinięta przed odrzuconym wypchnięciem pozostaje przodkiem SYNC, więc po akceptacji przewija się ponownie. Konflikt w `kurs/aktualnosc.json` rozstrzygamy wyłącznie poleceniem `git checkout origin/cwiczenia -- kurs/aktualnosc.json` (pliku nie scalamy ręcznie, nie wybieramy fragmentów i nie usuwamy go), a po zatwierdzeniu scalenia przeglądamy ponownie wszystkie aktywności wskazane przez G4.
