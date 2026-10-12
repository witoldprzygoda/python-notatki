# Sprawy do omówienia

Plik roboczy (poza katalogiem `docs/` — nie trafia na stronę).
Zbiera sprawy do ewentualnego omówienia, poprawy lub uzupełnienia w treści obu
części. Każda pozycja podaje miejsce, opis, propozycję i stan. Sprawę
rozstrzygniętą przenosimy do sekcji „Rozstrzygnięte” z datą i decyzją.

## Otwarte

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
- **Stan:** odłożone — decyzja autora z 12 X 2026: ćwiczenia są osobnym, dużym
  projektem; dobre ćwiczenia wymagają starannego doboru, tak aby były ciekawe,
  oraz przeglądu przez autora, a więc czasu. Realizujemy je później, w osobnym
  etapie; do tego czasu projekt ćwiczeń jedynie synchronizujemy z `dev`.

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
- **Stan:** w toku na osieroconej gałęzi `slajdy`; talie wykładów W01–W08
  i laboratorium L01 autor przyjął 11 X 2026, dalsze talie powstaną na jego
  polecenie (11 X 2026).

### Drobiazgi spoza zakresu poprawek z talii (11 X 2026)

- **Miejsce i opis:** `docs/01-instalacja/ai-tools.md`, ramka „Cel sesji:
  Local”: według recenzji gałęzi `content/uwagi-z-talii` eksperyment
  `chat.editor.localAgent.enabled` może w VS Code 1.141.0 ukryć pozycję Local
  na liście celów sesji — obserwacja, niesprawdzona.
- **Propozycja:** sprawdzić w VS Code przy najbliższym przeglądzie narzędzi AI
  (pozycja „Narzędzia AI” w sekcji „Do wykonania przy przejściu na Pythona
  3.15”).
- **Stan:** do sprawdzenia (11 X 2026); pozostałe punkty wpisu (`#file`,
  liczby w `cache_info()`, skrypt wykresu cyklu wydań) rozstrzygnięte 11 X 2026
  (sekcja „Rozstrzygnięte”).

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

### Rozdział 1 a stan z 5 X 2026 (11 X 2026)

Rozdział 1 opisuje stan narzędzi po wydaniu Pythona 3.15.0 i managera 26.4
(9 X 2026); bazą notatek pozostaje Python 3.14. Klasyczny instalator jest
przestarzały i wygaszany, nadal publikowany dla 3.14 i 3.15. Ramka „Wersja
odniesienia notatek” nie zawiera już sformułowań zależnych od daty pisania,
a nowa ramka ostrzeżenia opisuje drogi, którymi manager instaluje najnowszą
wersję bez jej wskazania (instalacja samoczynna, sprawdzanie konfiguracji,
`py install default`). Wykres cyklu wydań pobrano ponownie z devguide;
akapit o historii języka i sekcja „Python 3.15” w rozdziale 16 podają datę
wydania 3.15, a zdania o 3.15 w rozdziałach 9 i 13 oraz w części „Python
Zastosowania” opisują stan po premierze. Ustawienie automatycznej aktywacji
środowiska, skróty terminala, pakiet rozszerzeń Python, sugestie następnej
zmiany, plany Copilota (kredyty AI) i cel sesji czatu (**Local**) opisano
według dokumentacji z 11 X 2026 (branch `content/uwagi-z-talii`, przyjęty
przez autora 11 X 2026).

### Rozdział 7: pułapki importu i układ płaski (11 X 2026)

Pułapka `random.py` działa w osobnym podkatalogu `projekt\pulapka`, więc nie
psuje późniejszego `python -m pytest`; tekst wyjaśnia, dlaczego. Zdanie
o imporcie cyklicznym rozróżnia komunikat dla modułów z katalogu
`sys.path[0]` i dla importu z podmodułu pakietu, a zdanie o uruchamianiu
„z innego miejsca” wymienia przypadki, w których import rzeczywiście zawodzi
(branch `content/uwagi-z-talii`, przyjęty przez autora 11 X 2026).

### Rozdziały 7 i 8: uwagi z talii W07 i W08 (11 X 2026)

Poprawiono: opis funkcji klucza w `groupby()`, liczbę wywołań `fib(100)`,
zdanie o limicie rekurencji i tabelę modułów (`datetime` i `statistics` poza
zakresem części), `OrderedDict` bez „dziś”, `math.prod()` jako funkcję modułu
`math`, różnicę `isdigit()` i `int()` (`"²"`), wynik testu z wyjątkiem innego
typu (niezaliczony), budowę `pytest.raises()`, regułę wykonania jednej
instrukcji `yield` w `@contextmanager`, działanie `basicConfig(force=True)`
oraz zapis ścieżek w sesji pdb. Wszystkie wyniki sprawdzono na CPythonie
3.14.8 (branch `content/uwagi-z-talii`, przyjęty przez autora 11 X 2026).

### Tytuł strony „Instrukcje i wyrażenia warunkowe” (11 X 2026)

Strona `docs/04-sterowanie/wyrazenia-warunkowe.md` nosi tytuł „Instrukcje
i wyrażenia warunkowe” (decyzja autora z 11 X 2026, wariant A), ponieważ
`if`/`elif`/`else` i `match` są instrukcjami, a wyrażeniem jest operator
trójskładnikowy. Zmieniono H1, etykietę nawigacji, spis rozdziału 4 i trzy
odsyłacze; nazwa pliku, adres strony i identyfikatory sekcji pozostały bez
zmian (branch `content/instrukcje-warunkowe`).

### Drobne poprawki redakcyjne (11 X 2026)

Przyjęte przez autora 11 X 2026: przecinki wokół wtrąceń z „zamiast”
(`deskryptory.md`, `zastosowania/07-ml-pojecia/warsztat.md`), „wielowierszowy”
i „w wielu wierszach” zamiast „wielolinijkowy” i „w wielu liniach”
(`pierwszy-skrypt.md`) oraz wzór liczby zmiennoprzecinkowej z operatorem `**`
zamiast `^` (`typy-proste.md`) (branch `content/drobne-poprawki-redakcyjne`).

### Przekierowanie `2>` w Windows PowerShell 5.1 (11 X 2026)

Ramka „Wersja PowerShell” w `docs/09-wejscie-wyjscie/print-i-strumienie.md`
mówi, że w Windows PowerShell 5.1 przekierowanie `2>` zapisuje do pliku rekord
błędu powłoki (`NativeCommandError`), a nie sam komunikat programu (sprawdzone
11 X 2026: Windows PowerShell 5.1.26100, PowerShell 7.6.6). Bez zakładek
i osobnego przykładu — książka zakłada PowerShell 7 (decyzja autora z 11 X 2026;
branch `content/ps51-przekierowanie`).

### Dołączanie pliku do czatu Copilota (11 X 2026)

Lista przedrostków w sekcji „Czat i agenci” `docs/01-instalacja/ai-tools.md`
opisuje dołączenie pliku jako znak `#` i nazwę pliku wybraną z listy zamiast
odwołania `#file`, którego dokumentacja VS Code nie wymienia; `#codebase`
pozostaje (code.visualstudio.com/docs/chat/copilot-chat-context, 10/7/2026;
decyzja autora z 11 X 2026, branch `content/ai-tools-kontekst`).

### Liczby w wyniku `cache_info()` (11 X 2026)

Zdanie po `fib-cache.py` w `docs/07-moduly/functools.md` nie nazywa już liczb
trafień i obliczeń szczegółem implementacji CPythona: wyjaśnia, że wynikają
z kolejności obliczania `fib(n - 1) + fib(n - 2)` (101 obliczeń i 98
trafień). Notatki talii W07 ujednolicono na gałęzi `slajdy` (decyzja autora
z 11 X 2026, branch `content/fib-cache-liczby`).

### Skrypt wykresu cyklu wydań (11 X 2026)

Rysunek `docs/01-instalacja/img/python-cykl-wydan.svg` odtwarza skrypt
`scripts/release_cycle_chart.py`, który pobiera stronę devguide.python.org/versions
i wycina z niej wykres bez zmian; sposób i zasadę odświeżania opisuje `ZRZUTY.md`
(decyzja autora z 11 X 2026, branch `infra/wykres-cyklu-wydan`).

### Zależności pakietów i nowsze wersje w podrozdziale o pip (12 X 2026)

`docs/01-instalacja/pip.md`: po przykładzie z IPythonem akapit o zależnościach
(pip instaluje je samodzielnie; zmiany w działaniu pakietu opisuje lista zmian)
z odsyłaczem do „Czytania dokumentacji bibliotek” w części „Python
Zastosowania”, a w „Przydatnych poleceniach” `python -m pip list --outdated`.
Bez listy zależności i bez wyniku polecenia, które szybko się zmieniają
(sprawdzone 12 X 2026: IPython 9.17.1 z 14 zależnościami, pip 26.2.1; decyzja
autora, branch `content/pip-zaleznosci`).

### Odtwarzalne zrzuty VS Code (12 X 2026)

Zrzuty `vsc-select-interpreter.png` i `vsc-environment-manager.png`
(konfiguracja.md) powstają scenariuszami `interpreter` i `menedzer`
z `scripts/screenshots/vscode/vsc_zrzuty.py`; `wsb/przygotuj.ps1` instaluje
w piaskownicy 3.14t i tworzy `.venv-t`. Oba obrazy pokazują tryb rozszerzenia
Python Environments (decyzja autora, wariant A): po **Create Virtual
Environment...** lista menedżerów z pozycją **Quick Create**; tekst opisuje
Quick Create, menedżer venv i zachowanie przy istniejącym `.venv` (ramka
ostrzeżenia), a ramka „Wygląd a wersja VSC” — zależność od trybu. Naprawiono
scenariusze pylint i mypy (dymek podpowiedzi w VS Code 1.141) oraz Code Runner
(obraz porzucony 4 X tylko jako wariant). Obraz `vsc-notatnik-jadro.png`
pokazuje także 3.14t (decyzja autora; branche `infra/zrzuty-scenariusze`
i `content/notatnik-jadro`).
