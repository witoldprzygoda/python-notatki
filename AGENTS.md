# AGENTS.md — python-notatki: interaktywna warstwa podręcznika

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
2. **Treść i aktywności są rozdzielone.** Nie wpisuj definicji quizów, odpowiedzi, testów i logiki postępu bezpośrednio do właściwego tekstu Markdown poza minimalnymi, stabilnymi punktami osadzenia.
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

- Źródła treści: `docs/`.
- Konfiguracja i nawigacja: `mkdocs.yml`.
- Podstawowy build: `mkdocs build`.
- Podgląd lokalny: `mkdocs serve`.
- Istniejące zasady redakcyjne i konwencje bloków kodu znajdują się w `CLAUDE.md`; przed modyfikacją treści **przeczytaj ten plik i stosuj jego reguły**.
- Nie wykonuj reorganizacji nawigacji ani większych zmian treści tylko po to, aby ułatwić implementację interaktywności.

## Kontrakt treść ↔ aktywność

Aktywność ma stabilny `activity_id`. Miejsce osadzenia w treści ma stabilny `slot_id`.

Do Markdown wolno dodawać minimalne, niewidoczne lub neutralne semantycznie punkty osadzenia, np. element z `data-activity-slot` albo jawny identyfikator sekcji. Punkt osadzenia nie może zależeć od tekstu nagłówka ani numeru linii.

Przykład ideowy:

```html
<div data-activity-slot="flow-for-basics"></div>
```

Definicja aktywności ma pozostać poza właściwym tekstem, np. w `activities/04-sterowanie/petle-i-iteratory.yaml`.

## Typy aktywności w zakresie MVP

MVP musi wspierać dokładnie trzy reprezentatywne typy:

- `acknowledgement` — użytkownik potwierdza zapoznanie się ze wskazanym fragmentem;
- `single_choice` — jedno krótkie pytanie jednokrotnego wyboru z informacją zwrotną;
- `code` — mała wprawka wykonywana lokalnie w Pyodide, opcjonalnie sprawdzana prostymi testami.

Nie implementuj kolejnych typów, dopóki powyższe trzy nie działają w jednym spójnym przepływie i nie mają wspólnego API postępu.

## Activity Engine

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

Na etapie POC **nie twórz osobnego repozytorium frontendowego**. Interaktywna warstwa to część sposobu publikacji podręcznika i powinna być rozwijana razem z treścią, ale w osobnych katalogach/plikach.

Nowe repozytorium tworzymy dla usługi serwerowej, roboczo `python-notatki-service`, gdy rozpocznie się etap LTI i zdalnego postępu.

Usługa serwerowa nie przechowuje kopii treści podręcznika. Jej odpowiedzialności to wyłącznie:

- LTI 1.3,
- sesja użytkownika kursowego,
- API postępu,
- baza postępu,
- opcjonalne raportowanie do Moodle,
- kontrola trybu `MOODLE_ONLY` / `PUBLIC_FULL` na poziomie wdrożenia.

## Proponowana struktura POC w tym repozytorium

```text
activities/
  04-sterowanie/
    petle-i-iteratory.yaml

docs/
  javascripts/
    interactive/
      bootstrap.js
      activity-engine.js
      progress-store.js
      activities/
        acknowledgement.js
        single-choice.js
        code.js
      pyodide-worker.js
  stylesheets/
    interactive.css

scripts/
  build_activities.py
  validate_activities.py

AGENTS.md
INTERACTIVE_SYSTEM_SPEC.md
```

Nazwy mogą zostać skorygowane, ale nie zmieniaj podziału odpowiedzialności bez uzasadnienia.

## Walidacja i jakość

Po zmianie treści lub konfiguracji zawsze uruchom:

```bash
mkdocs build
```

Jeśli w repozytorium istnieją już walidatory aktywności lub testy związane ze zmienianym kodem, uruchom je również.

Każda nowa aktywność musi mieć:

- unikalny `activity_id`,
- jawny `version`,
- istniejący `slot_id`,
- poprawną definicję zgodną ze schematem,
- zachowanie po odświeżeniu strony,
- sensowny stan początkowy i zakończony.

Każda zmiana JavaScript powinna zostać sprawdzona przynajmniej w trybie jasnym i ciemnym oraz przy wąskim viewportcie.

## Bezpieczeństwo i prywatność

- Nigdy nie commituj sekretów LTI, kluczy prywatnych, tokenów ani danych studentów.
- Nie umieszczaj sekretów w JavaScript dostarczanym do przeglądarki.
- Nie ufaj identyfikatorom użytkownika ani wynikom przesłanym przez klienta w zastosowaniach formalnie ocenianych.
- Nie dodawaj analityki śledzącej ani zewnętrznych usług telemetrycznych bez jawnej decyzji autora.
- Minimalizuj zbieranie danych. Postęp kursowy powinien używać technicznego identyfikatora LTI; e-mail nie jest kluczem użytkownika.

## Zasady pracy z Codex

- Najpierw przeczytaj `CLAUDE.md` oraz `INTERACTIVE_SYSTEM_SPEC.md`, jeśli zadanie dotyczy interaktywnej warstwy.
- Przy zadaniu obejmującym architekturę przedstaw najpierw minimalny plan i wskaż pliki, które zamierzasz zmienić.
- Nie dodawaj frameworka frontendowego, bundlera, bazy danych ani nowej usługi bez wyraźnej potrzeby i uzasadnienia.
- Preferuj małe, odwracalne kroki oraz działający pionowy wycinek zamiast dużej jednorazowej przebudowy.
- Nie zmieniaj istniejącego tekstu dydaktycznego tylko po to, aby uprościć kod.
- Nie rozszerzaj zakresu na formalny system oceniania.
- Po implementacji podsumuj: zmienione pliki, zachowanie, testy, znane ograniczenia i proponowany następny krok.

## Code Review Rules

Przy przeglądzie zmian zwracaj szczególną uwagę na:

- niezamierzone uzależnienie aktywności od Moodle;
- bezpośrednie użycie `localStorage` poza `BrowserProgressStore`;
- logikę postępu zaszytą w komponentach UI;
- identyfikatory oparte na tekście nagłówka lub numerze linii;
- wycieki sekretów lub danych osobowych;
- pogorszenie działania statycznego MkDocs;
- ciężkie zależności dodane dla funkcji możliwej do wykonania prostym kodem;
- traktowanie wyniku klientowego jako wiarygodnej formalnej oceny;
- automatyczny import lokalnego postępu do konta LTI;
- mieszanie mikroaktywności podręcznika z formalnymi zestawami zadań i kolokwiami.
