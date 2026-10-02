# Sprawy do omówienia

Plik roboczy (poza katalogiem `docs/` — nie trafia na stronę).
Zbiera sprawy do ewentualnego omówienia, poprawy lub uzupełnienia w treści obu
części. Każda pozycja podaje miejsce, opis, propozycję i stan. Sprawę
rozstrzygniętą przenosimy do sekcji „Rozstrzygnięte” z datą i decyzją.

## Otwarte

### Zależności pakietów i nowsze wersje w podrozdziale o pip

- **Miejsce:** `docs/01-instalacja/pip.md` — sekcje „Przykład instalacji”
  i „Przydatne polecenia”.
- **Opis:** część „Python Notatki” nie mówi, że pip instaluje razem z pakietem
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
- **Stan:** do omówienia.

### Ćwiczenia interaktywne dla nowych rozdziałów

- **Opis:** pytania z `PLAN_ROZWOJU.md` §8.6 i `PLAN_ZASTOSOWANIA.md` §3.3 —
  które rozdziały mają dostać ćwiczenia; obecnie mają je dwie strony rozdziału 4
  części „Python Notatki” (`petle-i-iteratory.md`, `wyrazenia-warunkowe.md`).
- **Stan:** do omówienia.
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

### Etykiety nawigacji: półpauza (2 X 2026)

Etykiety z dopowiedzeniem zapisujemy z półpauzą, jak w pozostałych 16 etykietach.
Trzy etykiety z dwukropkiem ujednolicono: „Mini-projekt — menedżer kontaktów”
(rozdział 16 części „Python Zastosowania”), „Serwer — baza i API” i „Klient —
moduł API i okno” (rozdział 18) — w `mkdocs.yml`, nagłówkach H1 i spisach
rozdziałów; nazwy plików bez zmian (branch `content/etykiety-polpauza`).

### Zakładki w górnym pasku (2 X 2026)

Wariant C: części „Python Notatki” i „Python Zastosowania” (oraz strona główna)
jako zakładki w górnym pasku (`navigation.tabs`), rozdziały bieżącej części
zwijane w lewym panelu (bez `navigation.sections`). Usunięto komentarz
o wariantach układu w `mkdocs.yml` i reguły `docs/stylesheets/extra.css`
dla nagłówków grup `navigation.sections`, w tym ukrywanie etykiety „Python
Notatki” — w poprzednim układzie na stronach części „Python Zastosowania”
lewy panel nosił tytuł „Python Notatki” (nazwa serwisu). Porównanie
wariantów A–C na zrzutach (branch `content/zakladki-czesci`).
