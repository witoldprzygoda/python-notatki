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
- Zmieniamy wyłącznie ścieżki z listy dozwolonej (`kurs/README.md`, „Zasada wyłącznego dodawania”). Plików książki (`docs/**`, `mkdocs.yml`, `CLAUDE.md` i pozostałych) nie poprawiamy, także wtedy, gdy książka wydaje się błędna: usterkę opisujemy w raporcie jako poprawkę dla gałęzi `content/*` tworzonej z `dev`.
- Niczego nie scalamy do `dev` ani `master` i niczego do nich nie wypychamy. Nie przebudowujemy historii (`rebase`), nie nadpisujemy jej (`push --force`, `commit --amend` po wypchnięciu) i nie pomijamy hooków (`--no-verify`).
- Do commitu dodajemy jawnie wskazane ścieżki (`git add <ścieżki>`), nigdy `git add -A` ani `git add .`.
- Każde polecenie Pythona uruchamiamy interpreterem środowiska książki z kodowaniem UTF-8; w Git Bash poprzedzamy je zmiennymi środowiskowymi: `PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe …`. Bramkę uruchamiamy zawsze z `--book origin/dev`.
- Przed słowem „akceptuję” autora nie zmieniamy gałęzi `cwiczenia` i niczego nie wypychamy.
- Port 8000 należy do autora, a 8001 do innego projektu; podgląd ćwiczeń uruchamiamy wyłącznie na porcie 8002.
- Aktywności nie usuwamy ani nie wiążemy z całą stroną bez decyzji autora. Teksty aktywności piszemy w rejestrze i konwencjach z `CLAUDE.md` (polskie cudzysłowy „…”, terminologia książki).

## 1. Warunki wstępne

1. `git rev-parse --show-toplevel` wskazuje katalog ćwiczeń, a `git branch --show-current` — gałąź `cwiczenia`. Jeśli bieżąca gałąź to `sync/…` z przerwanej synchronizacji, nie tworzymy nowej: przedstawiamy autorowi jej stan (`git log --oneline origin/cwiczenia..HEAD` i wynik bramki) i pytamy, czy ją kontynuować. Na każdej innej gałęzi przerywamy.
2. `git status --porcelain --untracked-files=no` nie zwraca nic. Pliki nieśledzone nie przeszkadzają, ponieważ dodajemy jawnie wskazane ścieżki; wymieniamy je w raporcie.
3. `git fetch origin`.
4. `git rev-list --count origin/cwiczenia..origin/dev` zwraca 0: odpowiadamy „nic do synchronizacji”, podajemy skrót `origin/dev` i ostatni wiersz `kurs/SYNC_LOG.md` i kończymy pracę.
5. Lokalna gałąź `cwiczenia` odpowiada `origin/cwiczenia`. Gdy jest za nią, przewijamy ją: `git merge --ff-only origin/cwiczenia`. Gdy zawiera commity spoza `origin/cwiczenia`, przerywamy i pytamy autora.
6. Gałęzi `sync/DATA` nie ma ani lokalnie (`git branch --list`), ani w `origin` (`git branch -r --list`). W przeciwnym razie SYNC to pierwsza wolna nazwa `sync/DATA-2`, `sync/DATA-3`…; istniejącej gałęzi nie tworzymy od nowa ani nie przestawiamy.
7. Do raportu zapisujemy zakres zmian książki: `git log --oneline --no-merges origin/cwiczenia..origin/dev` oraz `git diff --stat origin/cwiczenia...origin/dev -- docs mkdocs.yml`.

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
- Konflikt w pliku ćwiczeń albo usunięcie plików ćwiczeń przez scalenie: `git merge --abort`, przerwanie pracy i raport.
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
    - każdą zmianę wiązania zapisujemy do raportu jako parę: stary identyfikator („stary nagłówek”) → nowy identyfikator („nowy nagłówek”); G3 wypisuje te pary w notatkach „zmiana wiązania względem …”.
- **G4** (zmieniona treść sekcji, zmienione wiązanie, nowe lub usunięte aktywności). Dla każdego zgłoszenia:
    1. czytamy różnicę wypisaną przez G4, a gdy jest skrócona albo niejasna, pełne zmiany strony poleceniem `git diff …` podanym przez bramkę; czytamy też całą bieżącą sekcję w `docs/<strona>`;
    2. każdą wymienioną aktywność sprawdzamy względem nowej treści: polecenie (`prompt`), kod startowy (`starter_code`), oczekiwany wynik (`checker.expected_lines`), rozwiązanie wzorcowe i warianty, omówienie (`solution.discussion`), warianty odpowiedzi i `correct_option_id` (klucz odpowiedzi), informacje zwrotne (`feedback`) oraz blok `verify`; sprawdzamy także, czy terminy i zapis zgadzają się z książką i czy nowy przykład książki nie podaje gotowej odpowiedzi na pytanie;
    3. dostosowujemy wyłącznie pliki ćwiczeń; `version` podnosimy o 1, gdy zmienia się polecenie, poprawna odpowiedź, checker albo inny element semantyczny, a poprawka kosmetyczna wersji nie zmienia; wersje aktywności pilotażowych utrwala test `test_pilot_manifest_emits_all_solutions_and_preserves_versions` w `tests/test_build_activities.py`, więc po podniesieniu wersji zmieniamy w nim oczekiwaną wartość w tym samym commicie;
    4. dla każdej aktywności zapisujemy decyzję: „bez zmian” z jednozdaniowym uzasadnieniem, „dostosowano” z opisem zmiany i wersją albo „do decyzji autora”;
    5. błąd w książce (np. wynik przykładu niezgodny z kodem, sprzeczne zdanie) opisujemy w raporcie jako usterkę do poprawy na `content/*`; aktywność dostosowujemy tylko na tyle, by nie opierała się na błędnym fragmencie.

    Po przejrzeniu wszystkich zgłoszeń G4 i zatwierdzeniu poprawek zapisujemy nowy stan przeglądu:

    ```bash
    PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe kurs/tools/gate.py --zatwierdz-aktualnosc --book origin/dev
    ```

    Sprawdzamy, że wypisane wpisy („dodano”, „zmieniono”, „usunięto”) odpowiadają przeglądowi, i zatwierdzamy `kurs/aktualnosc.json` („Record the review of sections changed in dev (DATA)”). Polecenie odmawia zapisu (kod 1), dopóki którekolwiek wiązanie jest zerwane; nie uruchamiamy go przed zakończeniem przeglądu.
- **G5** (rozwiązanie albo blok `verify` nie daje oczekiwanego wyniku): poprawiamy aktywność tak, aby rozwiązanie wzorcowe i warianty wypisywały dokładnie `expected_lines`, a `starter_code` ich nie wypisywał; sprawdzenia nie osłabiamy.
- **G6** (testy): test, który utrwala dane aktywności (np. wersje w `tests/test_build_activities.py`), aktualizujemy razem ze świadomą zmianą aktywności i odnotowujemy w raporcie; awarię kodu warstwy (hook, JavaScript, bramka) zgłaszamy jako zadanie dla gałęzi `platform/*` i przerywamy.
- **G7** (buildy `--strict`): ostrzeżenie buildu książki (`mkdocs.yml`) jest usterką książki — przerywamy i zgłaszamy ją do poprawy na `content/*`; błąd wydania kursowego wynikający z wiązań poprawiamy jak w G3.

## 4. Dziennik i ostatnia bramka (krok 6 przewodnika)

Dopisujemy wiersz na końcu tabeli w `kurs/SYNC_LOG.md` (znaczenie kolumn opisuje ten plik):

```text
| DATA | `<origin/dev, 7 znaków>` | `<commit scalenia, 7 znaków>` | synchronizacja | 0 | <zmienione wiązania; decyzje przeglądu G4; podniesione wersje; usterki książki> |
```

Zatwierdzamy go („Log the sync with dev (DATA)”) i ostatni raz uruchamiamy pełną bramkę. Wynik inny niż 0 oznacza powrót do punktu 3.

## 5. Raport dla autora (krok 7 przewodnika)

Sprawdzamy, że port 8002 jest wolny (`netstat -ano | grep -w 8002` niczego nie zwraca), i uruchamiamy w tle podgląd z katalogu ćwiczeń:

```bash
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 D:/PYTHON/NOTATKI/python-notatki/.venv/Scripts/python.exe -m mkdocs serve -f mkdocs.kurs.yml -a 127.0.0.1:8002
```

Raport przedstawiamy w odpowiedzi, nie w pliku, według wzoru (puste części wypełniamy słowem „brak”):

```markdown
## Synchronizacja ćwiczeń z książką — DATA

Gałąź `SYNC` od `origin/cwiczenia` (`<sha>`); scalono `origin/dev` (`<sha>`) commitem `<sha>`.

**Zmiany książki** (`<poprzedni dev>..<nowy dev>`, <liczba> commitów):
- `<sha>` <temat commitu>

**Strony z ćwiczeniami, których dotyczą zmiany:**

| Strona | Sekcja (nagłówek) | Aktywności | Zmiana w książce |
|---|---|---|---|

**Zmienione wiązania (G3):**

| Aktywność | Było | Jest |
|---|---|---|

**Przegląd treści (G4):**

| Aktywność | Decyzja | Wersja | Uzasadnienie |
|---|---|---|---|

**Usterki książki do poprawy na `content/*`:** <lista albo „brak”>

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

Następnie czekamy na odpowiedź autora. Uwagi wprowadzamy na gałęzi SYNC (wyłącznie w plikach ćwiczeń), powtarzamy bramkę, a po zmianie aktywności z przeglądu G4 także zatwierdzenie aktualności; potem przedstawiamy poprawiony raport i ponownie czekamy na „akceptuję”. Serwer podglądu działa do decyzji autora; jeśli sesja kończy się bez akceptacji, zatrzymujemy go przed jej zakończeniem, a gałąź SYNC pozostaje do kontynuacji (punkt 1.1).

## 6. Po akceptacji (krok 8 przewodnika)

Dopiero po słowie „akceptuję”:

```bash
git switch cwiczenia
git merge --ff-only SYNC
git push origin cwiczenia
git branch -d SYNC
```

Następnie zatrzymujemy serwer podglądu i podajemy autorowi skrót nowego `origin/cwiczenia`. Gałęzi SYNC nie wypychamy; jeśli jednak ją wypchnięto, usuwamy ją także w `origin` (`git push origin --delete SYNC`).

Jeśli przewinięcie się nie udaje, ponieważ na `cwiczenia` trafiła w międzyczasie inna zmiana, nie przebudowujemy gałęzi: `git fetch origin`, na gałęzi SYNC `git merge --no-ff origin/cwiczenia`, pełna bramka do kodu 0 (z przeglądem G4 i zatwierdzeniem, jeśli bramka go wymaga), krótkie uzupełnienie raportu i ponowne oczekiwanie na akceptację.
