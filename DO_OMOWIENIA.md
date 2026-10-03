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

### Zrzuty ekranu

- **Miejsce:** 18 znaczników `<!-- TODO: screenshot … -->` w obu częściach;
  lista w `ZRZUTY.md`.
- **Decyzje (2 X 2026):**
    - usunąć jako zbędne zrzuty 2 (panel Problems), 3 (otwieranie
      `settings.json`), 6 (menu New → Notebook), 17 i 18 (Excel, Word);
    - zrzuty wykonujemy automatycznie skryptami (zakres pracy rozszerzony
      o `scripts/`, branch `infra/zrzuty-ekranu`), autor tylko akceptuje
      wyniki; przebiegi z VS Code w Windows Sandbox (funkcja włączona
      2 X 2026, wymaga restartu komputera);
    - zrzuty REPL w jasnym schemacie Windows Terminal („One Half Light”).
- **Pilotaż:** gotowe zrzuty 16 (Swagger UI, `scripts/screenshots/fastapi_docs.py`)
  i 7 (kolorowy REPL: przechwycenie przez ConPTY, render xterm.js z czcionką
  Cascadia Mono; skrypty jeszcze w scratchpadzie). Pogrubienie w REPL rysujemy
  zwykłymi kolorami schematu (ustawienie Windows Terminal
  `intenseTextStyle: "bold"`) — lepszy kontrast na jasnym tle (decyzja 2 X 2026).
- **Do potwierdzenia:** zastąpienie zrzutów 4 (wynik Code Runnera) i 9
  (ostrzeżenie mypy) blokami tekstowymi.
- **Stan:** pilotaż VS Code (zrzut 10, pułapka w debugerze) po restarcie
  komputera; potem decyzja o całości.

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
