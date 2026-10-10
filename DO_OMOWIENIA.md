# Sprawy do omówienia

Plik roboczy (poza katalogiem `docs/` — nie trafia na stronę).
Zbiera sprawy do ewentualnego omówienia, poprawy lub uzupełnienia w treści obu
części. Każda pozycja podaje miejsce, opis, propozycję i stan. Sprawę
rozstrzygniętą przenosimy do sekcji „Rozstrzygnięte” z datą i decyzją.

## Otwarte

### Zależności pakietów i nowsze wersje w podrozdziale o pip

- **Miejsce:** `docs/01-instalacja/pip.md` — sekcje „Przykład instalacji”
  i „Przydatne polecenia”.
- **Opis:** część „Python Podstawy” nie mówi, że pip instaluje razem z pakietem
  jego zależności, ani jak sprawdzić, czy są dostępne nowsze wersje
  zainstalowanych pakietów. Część „Python Zastosowania” omawia już numery wersji
  i ostrzeżenia o wycofaniu (rozdział 1, `dokumentacja-bibliotek.md`, sekcja
  „Wersje, zmiany i ostrzeżenia o wycofaniu”) oraz deklarowanie zależności
  własnego pakietu (rozdział 17, `zaleznosci.md`).
- **Kontekst:** przy aktualizacji do 3.14.8 nowsze wersje bibliotek zmieniły
  swoje zależności (SQLAlchemy 2.1 nie instaluje już greenlet, FastAPI 0.142
  dociąga opentelemetry-api). Zmiany są automatyczne i niewidoczne dla
  czytelnika, dlatego nie opisujemy ich w treści — sprawa dotyczy wyłącznie
  ogólnego mechanizmu.
- **Propozycja** (szkic; liczby i wydruki do sprawdzenia na bieżącym pip przed
  wpisaniem):
    1. W „Przydatnych poleceniach” pozycja: `python -m pip list --outdated` —
       wypisanie pakietów, dla których dostępne są nowsze wersje, wraz z wersją
       zainstalowaną i najnowszą.
    2. W „Przykładzie instalacji”, po sesji IPython, akapit: pip zainstalował
       także kilkanaście innych pakietów — **zależności** (ang. *dependencies*)
       IPythona; zestaw zależności należy do konkretnego wydania pakietu
       (nowsze wydanie może z którejś zrezygnować albo wymagać nowej), a pip
       uwzględnia to samodzielnie; dla użytkownika istotne są zmiany w działaniu
       samego pakietu, opisywane w liście zmian (ang. *changelog*); odsyłacz do
       rozdziału 1 części „Python Zastosowania”.
- **Stan:** odłożone (2 X 2026).

### Zakładka „Ściągawki”

- **Opis:** pytanie z `PLAN_ZASTOSOWANIA.md` §3.2 — osobna zakładka z tabelami
  odniesienia po ukończeniu ścieżek (ścieżki są ukończone od 23 IX 2026).
  Książka zawiera 59 tabel (42 w części „Python Podstawy”, 17 w części „Python
  Zastosowania”); przy układzie z zakładkami czwarta zakładka pasowałaby
  naturalnie.
- **Rozważone warianty:** pełne ściągawki tematyczne (osobny projekt z planem,
  treść powielona z rozdziałów), spis istniejących tabel (niewiele ponad
  wyszukiwarkę serwisu), odłożenie.
- **Stan:** odłożone (2 X 2026). Wracamy, gdy pojawi się konkretna potrzeba
  (np. materiał do wydruku); wtedy zaczynamy od planu z listą ściągawek do
  akceptacji autora.

### Projekt ćwiczeń: plan fal, serwer kursu i synchronizacja

- **Miejsce:** projekt ćwiczeń na gałęzi `cwiczenia` (katalog
  `../python-notatki-cwiczenia`, zasady w `kurs/README.md` na tej gałęzi).
- **Opis:** model rozdzielenia książki i ćwiczeń jest rozstrzygnięty (sekcja
  „Rozstrzygnięte”, 3 X 2026). Przed startem kursu pozostaje ustalić:
    1. plan fal, czyli kolejność rozdziałów z ćwiczeniami względem planu
       wykładów;
    2. serwer wydania kursowego i dostęp do niego (wydanie publiczne albo
       wydanie dla wybranej grupy z kontrolą dostępu);
    3. częstotliwość synchronizacji `dev` → `cwiczenia`;
    4. termin etapu z postępem widocznym dla prowadzącego (Moodle) — osobny,
       późniejszy etap, wstępnie na przełomie semestrów.
- **Propozycja:** do przygotowania w projekcie ćwiczeń.
- **Stan:** do omówienia przed startem kursu (3 X 2026).

### Slajdy wykładowe

- **Miejsce:** osobna gałąź `slajdy` (katalog `slajdy/`), której zmiany nie
  trafiają do `dev` ani `master`.
- **Opis:** decyzje autora z 3 X 2026: slajdy nie należą do książki, ale
  czerpią z niej logikę materiału. Pierwszy zestaw obejmuje część „Python
  Podstawy” (rozdziały 1–16); slajdy do części „Python Zastosowania” powstaną
  później jako osobny zestaw. Dobór treści i kolejność tematów przejmujemy
  z dawnych wykładów (`sources/lectures/`), lecz slajdy powstają od nowa,
  zgodnie z tekstem książki, metodą i w stylu projektu `cpp-notatki`.
- **Propozycja:** tryb gałęzi — gałąź osierocona (ang. *orphan branch*) albo
  gałąź przyjmująca zmiany z `dev` jednokierunkowo — do rekomendacji po
  analizie metody. Katalog `slajdy/` jest już niedozwolony na `dev`
  i `master` (`scripts/check_book_only.py`).
- **Stan:** do omówienia; prace ruszą po dalszych wskazówkach autora
  (3 X 2026).

### Przekierowanie `2>` w Windows PowerShell 5.1

- **Miejsce:** `docs/09-wejscie-wyjscie/print-i-strumienie.md` — opis
  przekierowania strumienia błędów do pliku (`2> strumienie-bledy.txt`).
- **Opis:** opis zgadza się z PowerShell 7. W Windows PowerShell 5.1 tekst,
  który program zewnętrzny wypisuje do strumienia błędów, trafia do pliku
  opakowany w rekord błędu PowerShell (`NativeCommandError`, numer wiersza,
  `CategoryInfo`), a nie jako sam komunikat programu. Zauważone przy przeglądzie
  bezpieczeństwa poleceń (4 X 2026).
- **Propozycja:** rozpatrzyć razem z pozostałymi różnicami powłok z raportu
  „Różnice między powłokami” (3 X 2026): jedno zdanie o Windows PowerShell 5.1
  albo zakładki z wariantami.
- **Stan:** do omówienia (4 X 2026).

### Tytuł strony „Wyrażenia warunkowe”

- **Miejsce:** `docs/04-sterowanie/wyrazenia-warunkowe.md` (H1), etykieta
  nawigacji w `mkdocs.yml`, spis rozdziału w `docs/04-sterowanie/index.md`
  oraz 3 odsyłacze z tekstem „Wyrażenia warunkowe” na innych stronach
  (pozostałe odsyłacze do tej strony mają tekst „4. Sterowanie przepływem”).
- **Opis:** pierwsza sekcja strony nosi od commita `39ce8cc` (gałąź
  `content/poprawki-z-talii`) tytuł „Instrukcja if, elif, else”, ponieważ
  `if`/`elif`/`else` jest instrukcją, a wyrażeniem jest wyłącznie forma
  trójskładnikowa. Tytuł strony, obejmującej także instrukcję `match`, nadal
  nazywa całość wyrażeniami. Zauważone przy przygotowaniu slajdów wykładowych.
- **Propozycja:** zmiana H1 i etykiety nawigacji, np. na „Instrukcje
  warunkowe”, bez zmiany nazwy pliku (adres strony pozostaje); zmiana
  nawigacji wymaga zgody autora. Ćwiczenia na gałęzi `cwiczenia` są powiązane
  z nagłówkami tej strony: zmianę identyfikatora sekcji
  (`#wyrazenie-if-elif-else` → `#instrukcja-if-elif-else`) i ewentualnie H1
  przejmie najbliższa synchronizacja.
- **Stan:** do decyzji autora (4 X 2026).

### Scenariusz zrzutu listy wyboru interpretera

- **Miejsce:** `docs/01-instalacja/img/vsc-select-interpreter.png`
  (konfiguracja.md), `ZRZUTY.md` (sekcja „Wykonane”),
  `scripts/screenshots/vscode/`.
- **Opis:** zrzut odświeżony 4 X 2026 (VS Code 1.140.0, rozszerzenie Python
  2026.6.0, Python 3.14.8 i 3.14t, projekt `moj-projekt` ze środowiskami
  `.venv` i `.venv-t`) powstał w Windows Sandbox przez wywołanie sterownika
  `vsc_zrzuty.py` scenariuszem spoza repozytorium, więc nie da się go odtworzyć
  skryptami z `scripts/screenshots/`, czego wymaga `ZRZUTY.md`. Skrypt
  `wsb/przygotuj.ps1` nie instaluje kompilacji 3.14t i nie tworzy `.venv-t`.
  Generatora nie ma także zrzut `vsc-environment-manager.png`
  (konfiguracja.md).
- **Propozycja:** na gałęzi `infra/*` dodać scenariusz listy wyboru
  interpretera do `SCENARIUSZE` w `vsc_zrzuty.py` i uzupełnić
  `wsb/przygotuj.ps1` o instalację 3.14t i środowisko `.venv-t` z venv.md;
  rozważyć scenariusz dla `vsc-environment-manager.png`.
- **Stan:** do wykonania na gałęzi `infra/*` (4 X 2026).

### Drobne poprawki redakcyjne spoza zakresu poprawek z talii

- **Miejsce i opis:**
    1. `docs/11-model-danych/deskryptory.md`, w. 7: „Python zamiast sięgać do
       słownika instancji wywołuje…” — brak przecinków wokół wtrącenia
       z „zamiast” (analogiczne miejsce w `zasieg-nazw-i-domkniecia.md`
       poprawiono w commicie `39ce8cc`);
    2. `docs/zastosowania/07-ml-pojecia/warsztat.md`, w. 73: „estymator,
       który zamiast przewidywać przekształca cechy” — jak wyżej;
    3. `docs/02-konsola/pierwszy-skrypt.md`, w. 53: „wielolinijkowego
       łańcucha znakowego” — pozostałe strony piszą „wielowierszowy”;
    4. `docs/03-nazwy-typy/typy-proste.md`, w. 170: wzór
       `(-1)^znak * 2^wykładnik * mantysa` używa znaku `^`, który w Pythonie
       oznacza bitową alternatywę wykluczającą (XOR); komentarze przy `**`
       poprawiono w `39ce8cc` z tego samego powodu.
- **Propozycja:** 1–2 — „Python, zamiast sięgać do słownika instancji,
  wywołuje…”, „estymator, który, zamiast przewidywać, przekształca cechy”
  (albo przebudowa zdań bez wtrącenia); 3 — „wielowierszowego”; 4 — zapis
  `(-1)**znak * 2**wykładnik * mantysa` albo wzór matematyczny w prozie.
- **Stan:** do decyzji autora (4 X 2026).

### Rozdział 1 a stan z 5 X 2026 (sprawdzenie przy laboratorium 1)

- **Miejsce:** `docs/01-instalacja/instalacja.md`, `sciezki-i-utrzymanie.md`,
  `konfiguracja.md`, `ai-tools.md` (rewizja `67bffc8`).
- **Opis:** przy przygotowaniu nowej wersji laboratorium 1 (talia L01 na
  gałęzi `slajdy`) sprawdzono w źródłach pierwotnych stan narzędzi z 5 X 2026.
  Wykryto miejsca nieaktualne albo nieścisłe:
    1. `instalacja.md`, w. 3: klasyczny instalator „został wycofany” — jest
       przestarzały (ang. *deprecated*) i nadal publikowany dla 3.14 i 3.15
       (python.org: „Or get the standalone installer for Python 3.14.8”);
       ramka ostrzeżenia poniżej jest poprawna. Propozycja: „uznany za
       przestarzały i wygaszany”.
    2. `instalacja.md` i `sciezki-i-utrzymanie.md`: wyniki `py list`
       i `py list --online --one` bez kolumny Alias (manager 26.3) — poprawione
       w commicie `39ce8cc`.
    3. `instalacja.md`, w. 74–76, ramka „Wersja odniesienia notatek”: zdanie
       o 3.15 jako wersji przedpremierowej zdezaktualizuje się po wydaniu
       3.15.0, planowo 9 X 2026 (PEP 790); dotyczy też wykresu
       `img/python-cykl-wydan.svg` i jego tekstu alternatywnego. Brak opisu
       kreatora pierwszego uruchomienia (`py install --configure`): po
       wydaniu 3.15 domyślna odpowiedź Y na „Install CPython now?” zainstaluje
       3.15, a polecenie `python` bez zainstalowanego interpretera — najnowszą
       wersję samoczynnie; `py install 3.15` instaluje do tego czasu wersję
       kandydującą 3.15.0rc3 (znacznik `3.15-dev`).
    4. `konfiguracja.md`, w. 153: automatyczną aktywację `.venv` w terminalu
       reguluje od VII 2026 ustawienie
       `python-envs.terminal.autoActivationType` (Python Environments jako
       domyślne, VS Code 1.131); `python.terminal.activateEnvironment` działa
       już tylko z wartością `false`.
    5. `konfiguracja.md`, w. 135: „Terminal → New Terminal (lub
       ++ctrl+grave++)” — ta pozycja menu ma skrót ++ctrl+shift+grave++,
       a ++ctrl+grave++ pokazuje i ukrywa panel terminala.
    6. `konfiguracja.md`, instalacja rozszerzeń: brak informacji, że
       rozszerzenie „Python” doinstalowuje Pylance, Python Debugger i Python
       Environments (pakiet rozszerzeń) — luka, nie błąd.
    7. `ai-tools.md`, w. 47: przy sugestii następnej zmiany pierwszy ++tab++
       przenosi kursor do proponowanego miejsca, drugi przyjmuje zmianę.
    8. `ai-tools.md`, w. 29: „Copilot Free z miesięcznymi limitami podpowiedzi
       i zapytań” — od 1 VI 2026 czat i agenci zużywają pulę kredytów AI, a nie
       liczbę zapytań; plany Free i Student mają tylko model Auto.
    9. `ai-tools.md`, sekcja „Czat i agenci”: opis Ask, Plan, Agent i Keep/Undo
       dotyczy sesji Local; od VS Code 1.140 domyślnym celem sesji może być
       silnik Copilot, w którym zmiany zapisują się bez Keep/Undo — wystarczy
       zdanie o wyborze Local.
    10. `ai-tools.md`, w. 71: odnośnik
        `https://code.visualstudio.com/docs/copilot/overview` przekierowuje na
        `https://code.visualstudio.com/docs/agents/overview`.
- **Źródła:** zestawienie faktów z 5 X 2026 (dokumentacja python.org,
  docs.python.org, code.visualstudio.com, docs.github.com, kod VS Code 1.140)
  oraz zrzuty z VS Code 1.140 z zalogowanym Copilotem. Książka poprawnie
  pomija `@workspace`, tryb Edit, `/optimize`, `/comment`, `/terminal`,
  ++alt+backslash++ i ++ctrl+enter++.
- **Propozycja:** poprawki na osobnej gałęzi `content/*`; punkt 3 najlepiej
  po wydaniu 3.15.0, razem z pozycjami z sekcji „Do wykonania przy przejściu
  na Pythona 3.15” (w tym „Narzędzia AI”).
- **Stan:** wykonane na gałęzi `content/uwagi-z-talii` (11 X 2026), czeka na
  odbiór autora.

### Rozdział 7: pułapki importu i układ płaski (sprawdzenie przy talii W06)

- **Miejsce:** `docs/07-moduly/moduly-i-import.md` (sekcja „Pułapki importu”),
  `docs/07-moduly/struktura-projektu.md` (akapit o układzie `src`).
- **Opis:** przy przygotowaniu talii W06 przykłady rozdziału uruchomiono
  w kolejności książki na CPythonie 3.14.8:
    1. Plik `random.py` z pierwszej pułapki importu zostaje w katalogu
       `projekt`. Późniejsze `python -m pytest` w tym katalogu (strona
       „Struktura projektu”) kończy się błędem `ImportError: cannot import
       name 'Random' from 'random'`, bo pytest korzysta z modułu `tempfile`,
       a ten importuje `random`.
    2. Zdanie o imporcie cyklicznym („interpreter nie odróżnia obu sytuacji”)
       jest zbyt ogólne: podpowiedź o zmianie nazwy pliku pojawia się tylko
       wtedy, gdy moduł z cyklu leży w katalogu z pierwszej pozycji
       `sys.path`; w pakiecie 3.14.8 wypisuje jednoznaczny komunikat
       „partially initialized module … (most likely due to a circular
       import)”. Tekst podpowiedzi różni się też od tego z pułapki
       `random.py`.
    3. Zdanie „Wystarczy uruchomić program z innego miejsca, by import
       zawiódł” przeczy przykładowi `python projekt\program.py`, który
       z katalogu nadrzędnego działa (katalog skryptu trafia do `sys.path`).
       Import zawodzi przy innym katalogu bieżącym albo innym punkcie wejścia
       (`python -c`, `python -m`, konsola, testy).
- **Propozycja:** (1) pułapkę `random.py` wykonujemy w osobnym podkatalogu
  (tak robi talia W06) albo dopisujemy usunięcie pliku utworzonego przez
  przykład wraz z uzasadnieniem; (2) „podobną podpowiedź” i jedno zdanie
  o komunikacie w pakiecie; (3) przeredagowanie zdania o katalogu roboczym.
  Poprawki na gałęzi `content/*`.
- **Stan:** do omówienia (10 X 2026).

### Rozdziały 7 i 8: uwagi z talii W07 i W08

- **Miejsce:** `docs/07-moduly/` (`biblioteka-standardowa.md`,
  `functools.md`, `itertools.md`) i `docs/08-wyjatki/`
  (`obsluga-wyjatkow.md`, `styl-i-testowanie.md`, `with-i-contextlib.md`,
  `logging.md`, `diagnostyka.md`).
- **Opis:** przy przygotowaniu talii W07 i W08 przykłady uruchomiono na
  CPythonie 3.14.8; niezależni recenzenci potwierdzili poniższe miejsca:
    1. `itertools.md`, `groupby()`: proza mówi, że funkcja klucza jest tą
       samą funkcją, którą podajemy `sorted()`, a program sortuje
       `sorted(slowa)` bez klucza (działa, bo sortowanie całych słów porządkuje
       je także według pierwszej litery).
    2. `functools.md`, w. 30: „kilkaset wywołań” — dla `fib(100)` jest ich
       199 (98 trafień i 101 obliczeń).
    3. `biblioteka-standardowa.md`: ostrzeżenie, że zbyt wysoki limit
       rekurencji grozi awarią interpretera, jest zgodne z dokumentacją, ale
       w 3.14.8 sprawdzone przypadki (rekurencja przez funkcje C) kończą się
       `RecursionError: Stack overflow …`; tabela modułów wymienia
       `statistics` i `datetime` jako omawiane w dalszych rozdziałach, choć
       część „Python Podstawy” do nich nie wraca (obserwacja).
    4. `obsluga-wyjatkow.md` i `styl-i-testowanie.md`: `isdigit()` nie jest
       po prostu „węższe” od `int()` — `"²".isdigit()` daje `True`, a
       `int("²")` zgłasza `ValueError` (podobnie `"①"`).
    5. `styl-i-testowanie.md`, w. 158: „wyjątek innego typu … kończy test
       błędem” — pytest zgłasza taki test jako niezaliczony (F), nie jako
       błąd (E); opis `pytest.raises()` sugeruje menedżer oparty na
       generatorze, a jest to klasa, której `__exit__()` zwraca wartość
       prawdziwą.
    6. `with-i-contextlib.md`, w. 118: „dokładnie jedną instrukcję `yield`” —
       reguła dotyczy wykonania: `yield` w gałęziach `if`/`else` działa,
       drugi wykonany `yield` daje `RuntimeError: generator didn't stop`,
       brak wykonanego — `generator didn't yield`; ponowne użycie menedżera
       zgłasza `AttributeError: '_GeneratorContextManager' object has no
       attribute 'args'` (uzupełnienie opcjonalne).
    7. `logging.md`: „kolejne `basicConfig()` nic nie zmienia” nie dotyczy
       wywołania z `force=True`.
    8. `diagnostyka.md`: pdb w Windows wypisuje ścieżkę małymi literami
       (`c:\…`), nie `C:\…` (kosmetyczne).
- **Propozycja:** poprawki na gałęzi `content/*`; slajdy W07 i W08 pokazują
  już stan rzeczywisty.
- **Stan:** do omówienia (10 X 2026).

## Do wykonania przy przejściu na Pythona 3.15

- **Pomiary czasu w rozdziale 13** — powtórzyć wszystkie pomiary
  (`pomiar-i-profilowanie.md`, `optymalizacja-kodu.md`,
  `przyspieszanie-pythona.md`) na nieobciążonym komputerze, zaktualizować
  opis ich pochodzenia (wiersz 3 pierwszej i trzeciej strony) oraz zdania
  cytujące wartości i proporcje (np. stosunek dla `deque`, „kilkanaście
  procent” dla złożeń listowych). Decyzja z 2 X 2026.
- **Wersje bibliotek** — podbić przypięte wersje w obu częściach do bieżących,
  przejrzeć listy zmian wydań mniejszych i głównych pod kątem zachowania
  opisanego w tekście, ponownie zweryfikować wydruki. Decyzja z 2 X 2026.
- **Narzędzia AI** — sprawdzić w dokumentacji GitHub i VSC aktualność
  `docs/01-instalacja/ai-tools.md`: nazwy planów Copilota, sposób włączania,
  wbudowanych agentów, skróty klawiszowe, ustawienie `chat.disableAIFeatures`,
  przedrostki `#`, `/`, `@`; zaktualizować datę stanu we wstępie.

## Rozstrzygnięte

### Wersje bibliotek po aktualizacji do Pythona 3.14.8 (2 X 2026)

Przypięte wersje bibliotek pozostają bez zmian (wariant A). Najnowsze wersje
(m.in. pandas 3.0.6, torch 2.14.1, SQLAlchemy 2.1.2, FastAPI 0.142.2) dają na
3.14.8 te same wydruki co wersje przypięte; jedyna różnica to wynik
`torch.__version__`. Wersje podbijamy przy przejściu książki na Pythona 3.15
albo wtedy, gdy nowe wydanie zmieni zachowanie opisane w tekście.

### Pomiary czasu w rozdziale 13 (2 X 2026)

Opis pochodzenia pomiarów (Python 3.14.7, wrzesień 2026) i liczby pozostają bez
zmian (wariant A). Na tym samym komputerze 3.14.7 i 3.14.8 dają czasy różniące
się w granicach rozrzutu między uruchomieniami, a proporcje opisane w tekście
się zgadzają. Nowe pomiary — przy przejściu na 3.15 (sekcja wyżej).

### Drzewa katalogów w rozdziale 7 (2 X 2026)

Obowiązuje styl ramkowy (`├──`, `└──`, `│`), używany we wszystkich drzewach
katalogów obu części. Dwa drzewa w `docs/07-moduly/pakiety.md`, zapisane
wcięciami, przerysowano w tym stylu bez zmiany treści (branch
`content/drzewa-katalogow`).

### Podrozdział o narzędziach AI (2 X 2026)

Wariant B: trwały rdzeń zamiast przewodnika po interfejsie, który zmienia się
niemal codziennie. Strona `docs/01-instalacja/ai-tools.md` zawiera rodzaje
narzędzi (z przykładami nazw), zwięzły przegląd GitHub Copilot w VSC (dostęp:
Copilot Free i Copilot Student; podpowiedzi i ich obsługa; czat z agentami
Ask, Plan i Agent; przegląd zmian i uprawnienia; kontekst `#`, `/`, `@`) oraz
zasady pracy z asystentem. Usunięto ramkę „Podrozdział w rozbudowie”, komentarz
`TODO-AKTUALIZACJA` i odsyłacz do artykułu Real Python z 2022 roku (zastąpiony
dokumentacją VSC). Wątek uczciwości na zajęciach z planu pominięto zgodnie
z decyzją o braku odwołań do zajęć. Fakty sprawdzone w dokumentacji GitHub
i VSC 2 X 2026 (branch `content/narzedzia-ai`).

### Przykłady z PDF w podrozdziale o typach prostych (2 X 2026)

Trzy sesje REPL ze stron 17–18 `sources/PythonNotatki.pdf` (w źródle tylko
jako obrazy) odtworzono jako bloki `.python .no-copy` w sekcji „Typ bool”
`docs/03-nazwy-typy/typy-proste.md`, w dwóch miejscach: „niepoważne”
konstrukcje (`-True`, `True + 1.1 + True`, `"abcdef"[False]`) po zdaniu
o nieczytelnej składni, z odsyłaczem do rozdziału 10; wynik `or` zależny od
wartości i wartość domyślna dla `None` po omówieniu zwracania operandów.
Dodano zastrzeżenie, że `or` zastępuje każdą wartość fałszywą (`0`), z formą
`wynik if wynik is not None else …` i odsyłaczem do operatora
trójskładnikowego. Usunięto komentarz `TODO` (branch
`content/typy-proste-przyklady`).

### Archiwum `docs/01-instalacja.zip` (2 X 2026)

Usunięto z repozytorium archiwum dawnej wersji rozdziału 1 (pierwszy commit,
18 VIII 2026), publikowane przez MkDocs jako `site/01-instalacja.zip`, choć nic
do niego nie odsyłało. Osiem stron w archiwum było nieaktualnych, a strona
`instalacja-klasyczna.md` została usunięta z treści przy rewizji rozdziałów 1–2
(commit `16009be`); archiwum i strona pozostają w historii Git (branch
`content/usuniecie-archiwum`).

### Porządki w pytaniach otwartych planów (2 X 2026)

W `PLAN_ROZWOJU.md` §8 i `PLAN_ZASTOSOWANIA.md` §2–3 oznaczono pytania
rozstrzygnięte (moduł `re` — rozdział 19 części „Python Zastosowania”; pliki
danych — katalogi `dane/` i `pliki/` rozdziałów; weryfikacje — redaktor,
skryptami `scripts/verify_page.py` i `scripts/verify_cells.py`; zapowiedź
tkinter domknięta 22 IX 2026), a pozostałe przeniesiono do tego pliku jako
osobne sprawy. Historia pytań w planach pozostaje bez zmian (branch
`content/porzadki-planow`).

### Etykiety nawigacji: pauza (2 X 2026)

Etykiety z dopowiedzeniem zapisujemy z pauzą (—, U+2014), jak w pozostałych 16 etykietach.
Znak nazwano tu pierwotnie omyłkowo półpauzą, także w nazwie gałęzi
`content/etykiety-polpauza` i w opisie commita `2158425`; książka konsekwentnie
używa pauzy, a półpauza (–) występuje wyłącznie w zakresach liczb i dat.
Trzy etykiety z dwukropkiem ujednolicono: „Mini-projekt — menedżer kontaktów”
(rozdział 16 części „Python Zastosowania”), „Serwer — baza i API” i „Klient —
moduł API i okno” (rozdział 18) — w `mkdocs.yml`, nagłówkach H1 i spisach
rozdziałów; nazwy plików bez zmian (branch `content/etykiety-polpauza`).

### Zakładki w górnym pasku (2 X 2026)

Wariant C: części „Python Notatki” (obecnie „Python Podstawy”) i „Python
Zastosowania” (oraz strona główna) jako zakładki w górnym pasku
(`navigation.tabs`), rozdziały bieżącej części zwijane w lewym panelu (bez
`navigation.sections`). Usunięto komentarz o wariantach układu w `mkdocs.yml`
i reguły `docs/stylesheets/extra.css` dla nagłówków grup `navigation.sections`,
w tym ukrywanie etykiety „Python Notatki” — w poprzednim układzie na stronach
części „Python Zastosowania” lewy panel nosił tytuł „Python Notatki” (nazwa
serwisu). Porównanie wariantów A–C na zrzutach (branch
`content/zakladki-czesci`). Osobny pasek zakładek zastąpiło
3 X 2026 menu części w belce tytułowej (wpis „Menu części w belce tytułowej”).

### Ćwiczenia interaktywne dla nowych rozdziałów (3 X 2026)

Diagnoza: warstwa ćwiczeń trafiła na `dev` 4 IX 2026 przez przewinięcie
(ang. *fast-forward*) gałęzi `feature/interactive-poc`, zgodnie z ówczesnym
poleceniem; cel — rozwój książki niezależny od ćwiczeń — pozostaje ten sam,
zmienia się mechanizm: osobna gałąź zamiast przełącznika konfiguracji
budowania na jednej gałęzi. Model: `dev`, `master`, `content/*` i `infra/*`
zawierają wyłącznie książkę; ćwiczenia rozwija długotrwała gałąź `cwiczenia`
(katalog `../python-notatki-cwiczenia`, gałęzie robocze `fala/*`, `platform/*`
i `sync/*`), która przyjmuje książkę z `dev` jednokierunkowo przez `sync/*`
i jedynie dodaje własne pliki, a ćwiczenia wiążą się z nagłówkami przez
identyfikatory generowane przez MkDocs, bez znaczników w Markdown. Dotychczasowe
ćwiczenia rozdziału 4 przechodzą na gałąź `cwiczenia`; stan sprzed rozdzielenia
zachowuje tag `przed-rozdzieleniem-cwiczen`.

Ćwiczenia wraz z rozwiązaniami mogą być publiczne. Paski postępu w nawigacji
(„prostokąciki”) pojawiają się tylko na stronach z ćwiczeniami; na stronach bez
ćwiczeń są ukryte. Zatwierdzone zabezpieczenia: strażnik
`scripts/check_book_only.py`, hooki Git `pre-push` i `pre-rebase` (instalator
`scripts/install_git_hooks.py`, instalacja po odbiorze rozdzielenia) oraz
reguły na GitHubie: zakaz nadpisywania historii i zakaz usuwania gałęzi `dev`,
`master` i `cwiczenia`. Wymóg liniowej historii `dev` i `master` (bez commitów
scalających, ang. *merge commits*) autor zatwierdził 3 X 2026 także jako
regułę GitHuba, aktywną od tego dnia w zestawie reguł `ksiazka`; lokalnie
pilnuje go hook `pre-push`. Sprawy do ustalenia przed
startem kursu (plan fal, serwer wydania kursowego, częstotliwość
synchronizacji) zbiera pozycja „Projekt ćwiczeń: plan fal, serwer kursu
i synchronizacja” w sekcji „Otwarte”. Zasady pracy opisuje
`DEVELOPMENT_WORKFLOW.md`.

### Nazwa części pierwszej: „Python Podstawy” (3 X 2026)

Część pierwsza (rozdziały 1–16) nosi nazwę „Python Podstawy”, a „Python
Notatki” pozostaje nazwą serwisu, książki i repozytorium (`site_name`, tytuł
strony głównej, zdania o całej książce). Uzasadnienie autora: nazwa ma
wskazywać to, co należy do samego języka, bez nadmiernego udziału bibliotek
zewnętrznych, choć słowo „podstawy” może się kojarzyć z węższym zakresem, niż
obejmuje część. Nowa nazwa usuwa też powtórzenie nazwy serwisu w nazwie części.
Rozważone warianty: „Python Język”, „Python Fundamenty” oraz zmiana nazwy
serwisu zamiast nazwy części.

Zakres zmiany: etykieta części w nawigacji (`mkdocs.yml`); na stronie głównej
nagłówek listy rozdziałów, wstęp i akapit o części „Python Zastosowania”;
odwołania w treści obu części (133 wystąpienia na 80 stronach, w większości
wskazania rozdziałów części pierwszej na stronach części „Python Zastosowania”);
zapisy bieżące w `PLAN_ZASTOSOWANIA.md` i w tym pliku. Nagłówek listy rozdziałów
ma obecnie identyfikator `python-podstawy` zamiast `python-notatki_1`, do
którego nie prowadził żaden odsyłacz; identyfikator `python-notatki` należy do
tytułu strony i się nie zmienia. Zapisy datowane zachowują dawną nazwę,
z dopiskiem obecnej nazwy tam, gdzie dawna mogłaby wprowadzać w błąd; plany
rozdziałów w `plans/` pozostają bez zmian jako zapis historii (branch
`content/python-podstawy`).

### Menu części w belce tytułowej (3 X 2026)

Osobny pasek zakładek znikał przy przewijaniu strony. Zastąpiło go menu
w nieruchomej belce tytułowej, między tytułem serwisu a przełącznikiem motywu,
w wariancie „pigułki” wybranym przez autora spośród trzech („podkreślenie”,
„pigułki”, „segment”), ze zrzutami i podglądem. Menu zawiera tylko dwie
części, „Python Podstawy” i „Python Zastosowania”, zawsze z pełnymi nazwami;
odnośnik „Strona główna” usunięto z menu (strona pozostaje dostępna przez logo
i tytuł serwisu, który prowadzi do strony głównej). Od szerokości 640 px belka
ma jeden rząd, poniżej — dwa rzędy z parą części w drugim; skrypt
`docs/javascripts/naglowek.js` dopasowuje odstęp przeskoków do sekcji do
rzeczywistej wysokości belki. Autor zaakceptował też ciemniejszą belkę
w motywie ciemnym (#1975d2; kontrast białego tekstu 4,65:1 zamiast 3,19:1).
Zmiany: `custom_dir: overrides` i `navigation.tabs.sticky` w `mkdocs.yml`,
`overrides/partials/header.html` (kopia szablonu Material 9.7.7 z trzema
opisanymi zmianami — po każdej aktualizacji Material porównać z oryginałem),
`overrides/partials/czesci.html` i style w `docs/stylesheets/extra.css`. Nie
wprowadzono: proponowanej poprawki widoczności fokusu przy nawigacji
klawiaturą pod wysoką belką (WCAG 2.4.11) — do ewentualnej decyzji (branch
`infra/menu-czesci-w-belce`).

### Bezpieczne polecenia i przykłady (4 X 2026)

Polecenie `New-Item -ItemType File -Force $PROFILE` z podrozdziału o venv po
cichu opróżniało istniejący profil PowerShell (sprawdzone w Windows PowerShell
5.1 i PowerShell 7). Autor ustalił zasadę: „NIGDY nie może być tak, że
sugerujesz jakąś komendę niebezpieczną, nadpisującą czyjś zasób”. Zasadę
rozwija wpis w `CLAUDE.md` (sekcja „Konwencje bloków kodu”): polecenia
i przykłady nie mogą nadpisać, wyczyścić ani usunąć zasobu, którego nie
utworzył sam przykład; zasób tworzymy tylko wtedy, gdy go nie ma, do plików
konfiguracyjnych dopisujemy, przykłady działają na własnych plikach
i katalogach, a zamierzone usunięcie poprzedza ostrzeżenie.

Przegląd obu części objął wszystkie polecenia, pliki konfiguracyjne
i przykłady uruchamiane przez czytelnika; każde zagrożenie i każdą poprawkę
sprawdzono na plikach próbnych. Poprawiono 41 stron, m.in.:
`pip freeze > requirements.txt` zapisuje tylko wtedy, gdy pliku nie ma;
przykład w `pathlib.md` nie usuwa już katalogu `archiwum`, a skrypt kontrolny
narzędzia porządkującego (rozdział 20 części „Python Zastosowania”) — katalogu
`pobrane`; polecenia odinstalowania poprzedzają ostrzeżenia. Decyzje autora:
zmianę zasady wykonywania skryptów (`Set-ExecutionPolicy`) wykonujemy tylko
wtedy, gdy uruchamianie skryptów jest zablokowane; `przewiduj.py` (rozdział 12
części „Python Zastosowania”) i zbieracz stron (rozdział 21) odmawiają zapisu,
gdy plik wynikowy już istnieje, przy czym zbieracz sprawdza to przed pierwszym
żądaniem. Strona odbioru ze stanem przed i po każdej poprawce została
opublikowana jako artefakt (branch `content/bezpieczne-polecenia`).
Wskazówkę o zablokowanym uruchamianiu skryptów przeniesiono do pierwszej
aktywacji venv (sekcja „Aktywacja”), a przy profilu i w rozdziale 1 części
„Python Zastosowania” zostały odsyłacze (decyzja autora z 4 X 2026).

### Zrzuty ekranu (4 X 2026)

Wszystkie 18 znaczników `<!-- TODO: screenshot … -->` rozstrzygnięto.
W treści jest 12 zrzutów: pylint, strona główna Jupyter Notebook, kolorowy
REPL, podpowiedzi typów Pylance, błąd typu mypy, trzy zrzuty debuggera,
widok Testing, nowy notatnik i wybór jądra w VS Code oraz Swagger UI. Wynik
Code Runnera pokazuje blok tekstowy (zasada bloków tekstowych z `CLAUDE.md`),
a zrzuty 2, 3, 6, 17 i 18 usunięto zgodnie z decyzją autora z 2 X 2026.
Zrzuty powstają automatycznie skryptami z `scripts/screenshots/`; zrzuty
VS Code — w Windows Sandbox, bez naruszania profilu użytkownika, w motywie
Light+ i skali 1,5 jak wcześniejsze zrzuty z rozdziału 1, a kolorowy REPL —
w schemacie One Half Light z pogrubieniem rysowanym zwykłymi kolorami.
Sposób odtworzenia każdego zrzutu opisuje `ZRZUTY.md`. Przy wykonywaniu
zrzutów poprawiono opisy, które rozminęły się z VS Code 1.140: Code Runner
pisze do panelu Output, klawisz F5 pyta najpierw o debugger, **Select Kernel**
proponuje najpierw **Python Environments…**, mypy zgłasza błąd typu,
a podpowiedzi Pylance pokazuje krótki listing bez adnotacji (branch
`infra/zrzuty-ekranu`).
