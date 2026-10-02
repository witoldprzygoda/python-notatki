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

### Podrozdział o narzędziach AI

- **Miejsce:** `docs/01-instalacja/ai-tools.md`.
- **Opis:** ramka „Podrozdział w rozbudowie” i komentarz `TODO-AKTUALIZACJA`;
  rozbudowa przewidziana w `PLAN_ROZWOJU.md` §6 nie została wykonana.
- **Stan:** do omówienia.

### Przykłady z PDF w podrozdziale o typach prostych

- **Miejsce:** `docs/03-nazwy-typy/typy-proste.md`, komentarz `TODO` przy
  „niepoważnych” pomysłach składniowych.
- **Opis:** przykłady istnieją w `sources/PythonNotatki.pdf` (s. 17–18) tylko
  jako obrazy; do odtworzenia jako bloki kodu (`PLAN_ROZWOJU.md` §6).
- **Stan:** do omówienia.

### Zrzuty ekranu

- **Miejsce:** 18 znaczników `<!-- TODO: screenshot … -->` w obu częściach;
  lista w `ZRZUTY.md`.
- **Opis:** do ustalenia, które zrzuty są potrzebne i kto je wykonuje.
- **Stan:** do omówienia.

### Pytania otwarte w planach

- **Miejsce:** `PLAN_ROZWOJU.md` §8, `PLAN_ZASTOSOWANIA.md` §2–3.
- **Opis:** zakładki w górnym pasku (`navigation.tabs`), osobna zakładka
  „Ściągawki”, ćwiczenia interaktywne dla nowych rozdziałów, półpauza
  w etykietach nawigacji; porządki: zamknięcie pytań już rozstrzygniętych
  (np. moduł `re` — rozdział 19 części „Python Zastosowania”), oznaczenie
  domkniętej zapowiedzi tkinter w `PLAN_ZASTOSOWANIA.md` §2.
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
