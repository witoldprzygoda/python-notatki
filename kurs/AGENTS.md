# AGENTS.md — python-notatki: interaktywna warstwa podręcznika

> **Uwaga (październik 2026).** Dokument dotyczy projektu ćwiczeń na gałęzi `cwiczenia` i jej gałęziach pomocniczych (`fala/*`, `platform/*`, `sync/*`); książka na `dev` i `master` nie zawiera warstwy ćwiczeń. Wiązanie nie wymaga już znaczników w Markdown: aktywności wiążą się z identyfikatorami nagłówków generowanymi przez MkDocs, a hook `scripts/build_activities.py` podczas budowania wydania kursowego (`mkdocs.kurs.yml`) dodaje atrybut `data-activity-section` i slot strony. Paski postępu („prostokąciki”) pojawiają się wyłącznie przy stronach i sekcjach z ćwiczeniami. Model gałęzi, polecenia i procedury opisuje `kurs/README.md`, który ma pierwszeństwo przed niniejszym dokumentem.

## Cel projektu

Repozytorium `python-notatki` jest źródłem polskojęzycznego podręcznika do kursu języka Python, publikowanego przez MkDocs Material. Rozwijamy go w kierunku **interaktywnego podręcznika**, nie systemu oceniania kursu i nie zamiennika Moodle.

Interaktywna warstwa ma dodawać do istniejącej treści m.in.:

- krótkie przykłady wykonywalnego kodu,
- wprawki i małe zadania,
- pytania i mini-quizy towarzyszące tekstowi,
- aktywności typu „przeczytaj / obejrzyj / zapoznaj się” z prostym potwierdzeniem,
- zapisywanie postępu użytkownika.

Formalne zestawy zadań, duże quizy, kolokwia i projekty oceniane **nie należą do tego systemu**. Będą rozwijane oddzielnie i mogą być powiązane z Moodle/GitHub innymi mechanizmami.

## Nadrzędne zasady architektoniczne

1. **Podręcznik pozostaje statycznym serwisem MkDocs.** Nie przepisuj treści do frameworka SPA ani do aplikacji serwerowej.
2. **Treść i aktywności są rozdzielone.** Nie wpisuj do tekstu Markdown książki definicji quizów, odpowiedzi, testów, logiki postępu ani żadnych znaczników ćwiczeń; wiązanie z tekstem powstaje podczas budowania wydania kursowego.
3. **Jeden frontend działa w dwóch trybach:**
   - kursowym: użytkownik wchodzi przez Moodle/LTI, postęp zapisuje się po stronie serwera;
   - publicznym: brak logowania, pełna funkcjonalność dydaktyczna, postęp zapisuje się lokalnie w przeglądarce.
4. **Moodle jest opcjonalnym dostawcą tożsamości i miejscem raportowania, a nie zależnością silnika aktywności.** Komponent quizu lub ćwiczenia nie może zawierać logiki specyficznej dla Moodle.
5. **Nie buduj własnego systemu kont.** Brak rejestracji, haseł, resetowania haseł i aktywacji adresów e-mail. Użytkownik kursowy jest identyfikowany wyłącznie przez LTI.
6. **Nie importuj automatycznie lokalnego postępu do konta Moodle.** Szczególnie na komputerach pracowni stan przeglądarki może pochodzić od innej osoby. W pierwszej wersji nie implementuj żadnego merge/importu postępu publicznego do kursowego.
7. **Nie traktuj wyników sprawdzonych wyłącznie w przeglądarce jako formalnej oceny kursu.** Interaktywny podręcznik służy nauce i lekkiej kontroli postępu.
8. **Dostęp do treści może być zamknięty lub publiczny bez przebudowy podręcznika.** Tryb dostępu jest własnością wdrożenia, nie treści Markdown.
9. **LTI ma otwierać materiał jako stronę najwyższego poziomu / nową kartę, nie jako główny podręcznik osadzony w iframe Moodle.**
10. **Minimalizuj zależności.** W MVP preferuj standardowy JavaScript/ES modules i małe, jawne komponenty zamiast dużego frameworka frontendowego.

## Obecny kontrakt z repozytorium

- Źródła treści: `docs/` (pliki książki; na gałęzi ćwiczeń ich nie zmieniamy).
- Konfiguracja i nawigacja książki: `mkdocs.yml`; wydanie kursowe: nakładka `mkdocs.kurs.yml`.
- Build wydania kursowego: `mkdocs build --strict -f mkdocs.kurs.yml`; build samej książki: `mkdocs build --strict`.
- Podgląd lokalny: `mkdocs serve -f mkdocs.kurs.yml -a 127.0.0.1:8002`.
- Po zmianie kodu hooków MkDocs w `scripts/` należy zrestartować `mkdocs serve`; sam rebuild może nadal używać modułu zaimportowanego przy starcie procesu.
- Istniejące zasady redakcyjne i konwencje bloków kodu znajdują się w `CLAUDE.md`; przed modyfikacją treści **przeczytaj ten plik i stosuj jego reguły**.
- Nie wykonuj reorganizacji nawigacji ani większych zmian treści tylko po to, aby ułatwić implementację interaktywności.

## Kontrakt treść ↔ aktywność

Aktywność ma stabilny `activity_id`. Miejsce osadzenia na stronie ma stabilny `slot_id`, deklarowany w YAML.

Do Markdown książki nie dodaje się żadnych punktów osadzenia: ani elementów z `data-activity-slot`, ani atrybutów `data-activity-section`, ani identyfikatorów `{#…}` wprowadzanych ze względu na ćwiczenia. Aktywność wiąże się z sekcją przez `section_id` równy identyfikatorowi nagłówka h2–h6, który MkDocs generuje z jego tekstu, albo z całą stroną przez `section_id: null`. Hook `scripts/build_activities.py`, włączany wyłącznie przez `mkdocs.kurs.yml`, podczas budowania oznacza takie nagłówki i dopisuje slot na końcu strony. Zmianę nagłówka w książce wykrywa build wydania kursowego i bramka `kurs/tools/gate.py`, która wskazuje następcę dawnego nagłówka; wiązanie poprawia się w YAML. Zmianę treści powiązanej sekcji przy niezmienionym nagłówku wykrywa etap G4 bramki, porównując odcisk treści z zapisanym przy ostatnim przeglądzie w `kurs/aktualnosc.json`; aktywności przegląda się wtedy względem nowej treści. Wiązanie z numerem linii lub pozycją elementu DOM jest niedopuszczalne.

Przykład ideowy slotu dopisywanego przez hook:

```html
<div data-activity-slot="petle-i-iteratory-activities"></div>
```

Definicja aktywności pozostaje poza tekstem książki, np. w `activities/04-sterowanie/petle-i-iteratory.yaml`.

## Typy aktywności w zakresie MVP

MVP musi wspierać dokładnie trzy reprezentatywne typy:

- `acknowledgement` — użytkownik potwierdza zapoznanie się ze wskazanym fragmentem;
- `single_choice` — jedno krótkie pytanie jednokrotnego wyboru z informacją zwrotną;
- `code` — mała wprawka wykonywana lokalnie w Pyodide, opcjonalnie sprawdzana prostymi testami.

Nie implementuj kolejnych typów, dopóki powyższe trzy nie działają w jednym spójnym przepływie i nie mają wspólnego API postępu.

## Silnik aktywności

Komponenty UI nie zapisują postępu bezpośrednio do `localStorage` ani nie wywołują endpointów Moodle/LTI.

Wszystkie aktywności komunikują się z abstrakcją `ProgressStore`.

Minimalny kontrakt logiczny:

```text
get(activityId)
save(activityId, state)
getSummary()
reset()          # tylko tam, gdzie tryb na to pozwala
```

Pierwsza implementacja:

```text
BrowserProgressStore -> localStorage
```

Późniejsza implementacja:

```text
RemoteProgressStore -> HTTP API -> baza danych
```

Kod aktywności nie może wiedzieć, która implementacja jest aktywna.

## Model postępu

Postęp ma być oparty na stabilnym identyfikatorze aktywności, nie na pozycji na stronie.

Minimalny zapis powinien móc przechować:

```text
activity_id
activity_version
status
score          # opcjonalnie
attempts       # opcjonalnie
updated_at
payload        # opcjonalny, mały stan specyficzny dla aktywności
```

Nie przechowuj danych osobowych w `localStorage`.

## Wykonywalny Python

Dla krótkich przykładów i wprawek korzystamy z Pyodide uruchamianego w przeglądarce.

Zasady:

- uruchamiaj interpreter leniwie, dopiero przy pierwszym użyciu;
- docelowo wykonuj kod w Web Workerze, aby nie blokować UI;
- zapewnij możliwość przerwania lub zresetowania środowiska wykonawczego;
- nie zakładaj, że środowisko WebAssembly zachowuje się identycznie jak lokalny system operacyjny;
- aktywności dotyczące funkcji niedostępnych w przeglądarce muszą być oznaczone jako niewykonywalne lokalnie;
- kod klienta i klientowe testy nie stanowią zabezpieczenia ocen formalnych.

## Tryby dostępu

Projekt ma przewidywać co najmniej:

```text
MOODLE_ONLY
PUBLIC_FULL
```

`MOODLE_ONLY`:

- wejście do treści wymaga poprawnej sesji powstałej po uruchomieniu LTI;
- postęp zapisuje `RemoteProgressStore`;
- nie twórz alternatywnego formularza logowania.

`PUBLIC_FULL`:

- cała treść i wszystkie towarzyszące aktywności są dostępne anonimowo;
- postęp zapisuje `BrowserProgressStore`;
- publiczny użytkownik nie otrzymuje formalnego statusu kursowego ani oceny Moodle.

Przełącznik trybu ma należeć do konfiguracji wdrożenia, nie do źródeł poszczególnych stron.

## Granica odpowiedzialności Moodle

Interaktywny podręcznik może raportować do Moodle informacje o postępie modułu, ale nie przejmuje odpowiedzialności za:

- formalne zestawy zadań,
- poważne quizy oceniane,
- kolokwia,
- projekty/repozytoria studenckie,
- końcowy system punktowy kursu.

Nie projektuj teraz integracji tych elementów.

## Zakres pierwszego POC

Pierwszy pionowy wycinek wykonujemy na jednej istniejącej stronie podręcznika. Preferowana strona: `docs/04-sterowanie/petle-i-iteratory.md` albo jedna strona z rozdziału 2.

POC ma pokazać:

1. statyczny tekst MkDocs bez regresji wyglądu;
2. jeden stabilny slot aktywności;
3. `acknowledgement`;
4. `single_choice`;
5. `code` uruchamiane przez Pyodide;
6. wspólny `BrowserProgressStore`;
7. pasek/krótkie podsumowanie postępu na stronie;
8. odtworzenie stanu po przeładowaniu strony;
9. brak jakiejkolwiek zależności od Moodle.

Dopiero po zaakceptowaniu POC projektujemy backend LTI.

## Repozytoria

**Nie twórz osobnego repozytorium frontendowego.** Interaktywna warstwa to część sposobu publikacji podręcznika; rozwijamy ją w tym samym repozytorium, na gałęzi `cwiczenia`, w osobnych katalogach i plikach, które jednokierunkowo przyjmują zmiany książki z `dev`.

Nowe repozytorium tworzymy dla usługi serwerowej, roboczo `python-notatki-service`, gdy rozpocznie się etap LTI i zdalnego postępu.

Usługa serwerowa nie przechowuje kopii treści podręcznika. Jej odpowiedzialności to wyłącznie:

- LTI 1.3,
- sesja użytkownika kursowego,
- API postępu,
- baza postępu,
- opcjonalne raportowanie do Moodle,
- kontrola trybu `MOODLE_ONLY` / `PUBLIC_FULL` na poziomie wdrożenia.

## Struktura warstwy w repozytorium

Wszystkie pliki warstwy leżą na liście dozwolonej z `kurs/README.md`; plik spoza tej listy (np. nowy skrypt w `scripts/` albo dokument w katalogu głównym) bramka odrzuca w etapie G1.

```text
activities/
  04-sterowanie/
    petle-i-iteratory.yaml
    wyrazenia-warunkowe.yaml

docs/
  javascripts/
    interactive/          moduły ES warstwy (bootstrap.js, silnik, magazyn
                          postępu, rendery aktywności, Pyodide, paski postępu)
  stylesheets/
    interactive.css

scripts/
  build_activities.py     hook MkDocs włączany wyłącznie przez mkdocs.kurs.yml

tests/
  interactive/            testy node --test modułów warstwy
  test_build_activities.py

kurs/
  README.md               przewodnik gałęzi: model, procedury, bramka
  AGENTS.md               niniejszy dokument
  INTERACTIVE_SYSTEM_SPEC.md
  SYNC_LOG.md             dziennik synchronizacji z dev
  aktualnosc.json         odciski sekcji powiązanych z aktywnościami (etap G4)
  bez-weryfikacji.txt     pytania zwolnione z bloku verify
  tools/
    gate.py               bramka jakości (etapy G1–G7)
    test_gate.py

mkdocs.kurs.yml           nakładka wydania kursowego
```

Główne `AGENTS.md` i `CLAUDE.md` należą do książki; na gałęzi ćwiczeń ich nie zmieniamy.

## Walidacja i jakość

Po każdej zmianie uruchom bramkę gałęzi ćwiczeń (etapy G1–G7, w tym aktualność powiązanych sekcji, testy i buildy `--strict` książki oraz wydania kursowego; etap G8 jest planowany):

```bash
python kurs/tools/gate.py --book origin/dev
```

Do odbioru służy wyłącznie pełne uruchomienie zakończone kodem 0. Kod 3 oznacza wynik częściowy albo roboczy (`--pomin-testy`, `--katalog-roboczy`, `--przed-scaleniem`). Do czasu przewinięcia `dev` do stanu po rozdzieleniu bramkę uruchamiamy z `--book infra/rozdzielenie-cwiczen`.

Każda nowa aktywność musi mieć:

- unikalny `activity_id`,
- jawny `version`,
- `slot_id` strony zadeklarowany w YAML,
- `section_id` wskazujący nagłówek h2–h6 tej strony albo `null`,
- wpis w `kurs/aktualnosc.json`, zapisany poleceniem `python kurs/tools/gate.py --zatwierdz-aktualnosc --book origin/dev` po sprawdzeniu, że aktywność odpowiada bieżącej treści powiązanej sekcji,
- poprawną definicję zgodną ze schematem,
- zachowanie po odświeżeniu strony,
- sensowny stan początkowy i zakończony.

Każda zmiana JavaScript powinna zostać sprawdzona przynajmniej w trybie jasnym i ciemnym oraz przy wąskim oknie przeglądarki.

Każde pytanie `single_choice` ma blok `verify`, który wypisuje dokładnie etykietę poprawnej odpowiedzi; pytanie pojęciowe bez takiej możliwości wpisujemy z uzasadnieniem do `kurs/bez-weryfikacji.txt`.

## Bezpieczeństwo i prywatność

- Nigdy nie commituj sekretów LTI, kluczy prywatnych, tokenów ani danych studentów.
- Nie umieszczaj sekretów w JavaScript dostarczanym do przeglądarki.
- Nie ufaj identyfikatorom użytkownika ani wynikom przesłanym przez klienta w zastosowaniach formalnie ocenianych.
- Nie dodawaj analityki śledzącej ani zewnętrznych usług telemetrycznych bez jawnej decyzji autora.
- Minimalizuj zbieranie danych. Postęp kursowy powinien używać technicznego identyfikatora LTI; e-mail nie jest kluczem użytkownika.

## Zasady pracy narzędzi AI

Przed rozpoczęciem pracy:

1. sprawdź bieżącą gałąź;
2. przeczytaj `kurs/README.md`;
3. zastosuj zasady wynikające z prefiksu gałęzi.

```text
cwiczenia      → gałąź długotrwała; zmiany wyłącznie przez --ff-only
fala/*         → fala ćwiczeń do rozdziału
platform/*     → hook, JavaScript, CSS, bramka, CI i wydania
sync/*         → synchronizacja z dev (jedyne gałęzie scalające dev)
```

`kurs/README.md` jest autorytatywnym źródłem modelu gałęzi, zasady wyłącznego dodawania i procedury synchronizacji; `DEVELOPMENT_WORKFLOW.md` opisuje pracę nad książką.

- Najpierw przeczytaj `CLAUDE.md` oraz `kurs/INTERACTIVE_SYSTEM_SPEC.md`, jeśli zadanie dotyczy interaktywnej warstwy. Specyfikacja czeka na pełną rewizję po zmianie modelu gałęzi: tam, gdzie różni się od `kurs/README.md`, rozstrzyga `kurs/README.md`.
- Przy zadaniu obejmującym architekturę przedstaw najpierw minimalny plan i wskaż pliki, które zamierzasz zmienić.
- Nie dodawaj frameworka frontendowego, bundlera, bazy danych ani nowej usługi bez wyraźnej potrzeby i uzasadnienia.
- Preferuj małe, odwracalne kroki oraz działający pionowy wycinek zamiast dużej jednorazowej przebudowy.
- Nie zmieniaj istniejącego tekstu dydaktycznego tylko po to, aby uprościć kod.
- Nie rozszerzaj zakresu na formalny system oceniania.
- Po implementacji podsumuj: zmienione pliki, zachowanie, testy, znane ograniczenia i proponowany następny krok.

## Zasady przeglądu kodu

Przy przeglądzie zmian zwracaj szczególną uwagę na:

- niezamierzone uzależnienie aktywności od Moodle;
- bezpośrednie użycie `localStorage` poza `BrowserProgressStore`;
- logikę postępu zaszytą w komponentach UI;
- wiązania oparte na numerze linii lub pozycji elementu DOM oraz `section_id` z sufiksem deduplikacji (`_1`, `_2`…); wiązanie z identyfikatorem nagłówka generowanym przez MkDocs jest zamierzone;
- jakiekolwiek znaczniki ćwiczeń dodane do Markdown książki;
- zmianę lub usunięcie pliku książki na gałęzi ćwiczeń (zasada wyłącznego dodawania, etap G1 bramki);
- wycieki sekretów lub danych osobowych;
- pogorszenie działania statycznego MkDocs;
- ciężkie zależności dodane dla funkcji możliwej do wykonania prostym kodem;
- traktowanie wyniku klientowego jako wiarygodnej formalnej oceny;
- automatyczny import lokalnego postępu do konta LTI;
- mieszanie mikroaktywności podręcznika z formalnymi zestawami zadań i kolokwiami.
