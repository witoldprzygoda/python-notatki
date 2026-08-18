# Interaktywny podręcznik Python — specyfikacja architektury i plan MVP

## 1. Kontekst

Projekt `python-notatki` jest rozwijanym podręcznikiem do kursu języka Python. Źródłowa treść pozostaje w Markdown i jest publikowana przez MkDocs Material. Rozbudowujemy serwis o lekką warstwę interaktywną, która ma zwiększać aktywność studenta podczas pracy z tekstem, ale nie ma zastępować Moodle ani formalnego systemu oceniania kursu.

System powinien działać w dwóch sytuacjach:

1. **tryb kursowy** — dostęp przez Moodle/LTI, trwały postęp przypisany do studenta;
2. **tryb publiczny** — okresowo udostępniony pełny podręcznik, bez kont, z lokalnym postępem w przeglądarce.

Formalne zestawy zadań, kolokwia, większe quizy oceniane i repozytoria studentów są równoległą częścią kursu i pozostają poza zakresem tej aplikacji.

---

## 2. Najważniejsza decyzja: nie tworzyć nowego repozytorium frontendowego na początku

Na etapie MVP rekomendowana jest praca bezpośrednio w `python-notatki`, na osobnej gałęzi utworzonej od aktualnego `dev`, np.:

```text
feature/interactive-poc
```

Powód: mikroaktywności są ściśle związane z konkretnymi fragmentami podręcznika. Umieszczenie treści i definicji aktywności w tym samym repozytorium pozwala w jednym PR:

- zmienić tekst,
- dodać lub zmienić punkt osadzenia,
- zaktualizować aktywność,
- uruchomić wspólną walidację.

Oddzielenie oznacza tutaj **oddzielne pliki i odpowiedzialności**, a nie koniecznie oddzielne repozytoria.

Nowe repozytorium powinno powstać dopiero dla backendu LTI/postępu, ponieważ jest to osobno wdrażana usługa o innym profilu bezpieczeństwa i cyklu życia. Robocza nazwa:

```text
python-notatki-service
```

---

## 3. Zakres interaktywnego podręcznika

### W zakresie

- statyczna treść MkDocs;
- interaktywne przykłady;
- wykonywanie krótkiego kodu Python w przeglądarce;
- krótkie wprawki;
- poprawianie fragmentów kodu;
- pytania typu „co się stanie?”;
- małe quizy towarzyszące sekcjom;
- aktywności typu „zapoznałem się z materiałem”;
- podpowiedzi;
- lokalny postęp anonimowego użytkownika;
- trwały postęp użytkownika Moodle;
- zbiorczy stan ukończenia fragmentu/modułu;
- opcjonalne raportowanie lekkiego postępu do Moodle.

### Poza zakresem

- rejestracja i logowanie użytkowników niezależne od Moodle;
- hasła, resetowanie haseł, aktywacja kont;
- formalne zestawy zadań;
- duże quizy oceniane;
- kolokwia;
- projekty GitHub studentów;
- wiarygodne serwerowe uruchamianie kodu na ocenę;
- pełny LMS;
- automatyczne przenoszenie anonimowego postępu do konta kursowego.

---

## 4. Architektura logiczna

```text
                           ┌──────────────────────┐
                           │  Markdown / MkDocs   │
                           │  treść podręcznika   │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │ Activity Engine      │
                           │ JS + definicje YAML  │
                           └──────────┬───────────┘
                                      │
                              ProgressStore
                               /            \
                              /              \
                             ▼                ▼
                 BrowserProgressStore   RemoteProgressStore
                    localStorage          HTTP API
                                              │
                                              ▼
                                      python-notatki-service
                                              │
                                       LTI + baza danych
                                              │
                                              ▼
                                            Moodle
```

Warstwa aktywności działa niezależnie od źródła tożsamości. Moodle nie jest wywoływany bezpośrednio z komponentów quizu lub ćwiczenia.

---

## 5. Architektura wdrożenia

Docelowo rekomendowany jest jeden origin dla użytkownika, np.:

```text
https://python.example.edu/
```

Za reverse proxy:

```text
/           -> statyczny build MkDocs
/api/       -> backend postępu
/lti/       -> endpointy LTI 1.3
```

Pozwala to uniknąć zbędnej konfiguracji CORS i upraszcza sesję użytkownika.

### Tryb MOODLE_ONLY

```text
Moodle -> LTI launch -> nowa karta -> sesja kursowa -> podręcznik
```

Anonimowe żądanie treści powinno zostać zatrzymane przez warstwę dostępu.

### Tryb PUBLIC_FULL

```text
Internet -> podręcznik -> aktywności -> BrowserProgressStore
```

Backend może w tym trybie w ogóle nie być potrzebny do zwykłego korzystania z materiału.

Przełączenie trybu dostępu powinno odbywać się konfiguracją wdrożenia, nie edycją zawartości rozdziałów.

---

## 6. Kontrakt między tekstem a aktywnością

Treść Markdown nie powinna zawierać właściwej definicji quizu lub rozwiązania. Powinna jedynie zapewnić stabilne miejsce osadzenia.

Przykład:

```html
<div data-activity-slot="flow-for-basics"></div>
```

Alternatywnie można użyć stabilnych identyfikatorów sekcji, jeśli MkDocs/Markdown pozwala zagwarantować ich trwałość.

Nie wolno wiązać aktywności z:

- numerem linii;
- wygenerowanym automatycznie slugiem nagłówka, który zmieni się po korekcie tytułu;
- pozycją typu „trzeci blok kodu na stronie”.

Definicja aktywności znajduje się w osobnym pliku:

```text
activities/04-sterowanie/petle-i-iteratory.yaml
```

Przykład schematu roboczego:

```yaml
schema_version: 1
page: 04-sterowanie/petle-i-iteratory

activities:
  - id: flow-for-read-001
    version: 1
    slot: flow-for-basics
    type: acknowledgement
    required: true
    label: "Zapoznałem się z opisem pętli for"

  - id: flow-for-quiz-001
    version: 1
    slot: flow-for-basics
    type: single_choice
    required: false
    prompt: "Ile razy wykona się ciało pętli?"
    options:
      - id: a
        text: "2"
      - id: b
        text: "3"
      - id: c
        text: "4"
    answer: b
    feedback:
      correct: "Tak. range(3) dostarcza wartości 0, 1, 2."
      incorrect: "Sprawdź, jakie wartości dostarcza range(3)."

  - id: flow-for-code-001
    version: 1
    slot: flow-for-practice
    type: code
    required: true
    starter_code: |
      for i in range(3):
          # uzupełnij
          pass
    checks:
      - type: stdout_contains
        value: "0\n1\n2"
```

Schemat jest punktem startowym, nie zamkniętym standardem. Przed rozszerzeniem należy najpierw wdrożyć trzy podstawowe typy.

---

## 7. Typy aktywności

### 7.1 `acknowledgement`

Najprostsza aktywność. Jej celem jest zarejestrowanie, że użytkownik świadomie oznaczył fragment jako przeczytany/obejrzany.

Przykładowe zastosowania:

- „Przeczytaj uwagę o mutowalności i zaznacz jako wykonane.”
- „Obejrzyj krótką animację i przejdź dalej.”
- „Zapoznaj się z zasadą PEP 8.”

Nie wymuszamy pytania kontrolnego, jeżeli autor materiału nie uważa go za potrzebne.

### 7.2 `single_choice`

Małe pytanie osadzone przy treści. Nie jest formalnym quizem Moodle.

Powinno wspierać:

- natychmiastową informację zwrotną;
- możliwość ponownej próby, jeśli autor na to pozwala;
- zapis wyniku i liczby prób;
- opcjonalne oznaczenie jako wymagane do postępu w podręczniku.

### 7.3 `code`

Mała wprawka wykonywana w przeglądarce.

Powinna wspierać:

- kod początkowy;
- uruchomienie;
- stdout/stderr;
- reset;
- proste sprawdzenie;
- zapis stanu ukończenia;
- możliwość późniejszego dodania stopniowanych podpowiedzi.

---

## 8. Wykonywanie Pythona w przeglądarce

Rekomendowany runtime dla POC: **Pyodide**.

Wymagania implementacyjne:

- ładowanie dopiero po pierwszej próbie uruchomienia kodu;
- cache jednej instancji runtime na stronę lub worker;
- wykonanie w Web Workerze;
- przechwycenie stdout/stderr;
- możliwość terminacji workera w przypadku pętli nieskończonej;
- brak dostępu komponentu ćwiczenia do wewnętrznych danych innych aktywności;
- jasne komunikaty o ograniczeniach środowiska przeglądarkowego.

MVP nie potrzebuje pełnego IDE. Pole tekstowe/edytor kodu może być początkowo prosty. Zaawansowany edytor (np. Monaco/CodeMirror) można rozważyć dopiero po ocenie POC.

---

## 9. ProgressStore

### 9.1 Interfejs

Wszystkie komponenty używają wspólnego interfejsu:

```javascript
class ProgressStore {
  async get(activityId) {}
  async save(activityId, state) {}
  async getSummary(scope) {}
  async reset(scope) {}
}
```

Dokładna składnia może być inna, ale semantyka ma pozostać wspólna.

### 9.2 BrowserProgressStore

Pierwsza implementacja oparta o `localStorage`.

Przykładowy klucz:

```text
python-notatki.progress.v1
```

Przykładowy stan:

```json
{
  "schemaVersion": 1,
  "activities": {
    "flow-for-read-001": {
      "version": 1,
      "status": "completed",
      "updatedAt": "2026-08-19T12:00:00Z"
    },
    "flow-for-quiz-001": {
      "version": 1,
      "status": "completed",
      "score": 1,
      "attempts": 2,
      "updatedAt": "2026-08-19T12:05:00Z"
    }
  }
}
```

Nie zapisujemy imienia, nazwiska, e-maila ani innych danych identyfikujących.

### 9.3 RemoteProgressStore

Późniejsza implementacja komunikuje się z backendem. UI nie powinno wymagać zmian przy zamianie magazynu.

---

## 10. Wersjonowanie aktywności

Każda aktywność ma:

```text
id       — trwała tożsamość logiczna
version  — wersja semantyczna aktywności
```

Zmiana kosmetyczna nie musi zwiększać `version`.

Zmiana poprawnej odpowiedzi, kryterium zaliczenia lub istotnej treści zadania powinna zwiększać `version`.

Polityka dotycząca starego ukończenia zostanie zaprojektowana później. MVP ma jedynie przechowywać wersję, aby nie zamknąć drogi do migracji.

---

## 11. Reagowanie na zmiany podręcznika

Mechanizm zależności i hashy jest wartościowy, ale **nie należy go implementować w pierwszym kroku**.

Najpierw potrzebujemy działającego kontraktu `slot_id` + `activity_id`.

Etap późniejszy może dodać:

- walidację, czy wszystkie sloty istnieją;
- wykrywanie osieroconych aktywności;
- zapisywanie hasha fragmentu treści przy ostatnim przeglądzie aktywności;
- raport `REVIEW`, gdy powiązana treść uległa zmianie.

Automat nie powinien sam unieważniać zaliczenia studenta po zwykłej zmianie tekstu.

---

## 12. Proponowana struktura katalogów w `python-notatki`

```text
python-notatki/
├── activities/
│   ├── schema/
│   │   └── activity.schema.json        # później
│   └── 04-sterowanie/
│       └── petle-i-iteratory.yaml
│
├── docs/
│   ├── javascripts/
│   │   └── interactive/
│   │       ├── bootstrap.js
│   │       ├── activity-engine.js
│   │       ├── progress-store.js
│   │       ├── browser-progress-store.js
│   │       ├── pyodide-runtime.js
│   │       ├── pyodide-worker.js
│   │       └── activities/
│   │           ├── acknowledgement.js
│   │           ├── single-choice.js
│   │           └── code.js
│   └── stylesheets/
│       ├── extra.css
│       └── interactive.css
│
├── scripts/
│   ├── build_activities.py
│   └── validate_activities.py
│
├── AGENTS.md
├── INTERACTIVE_SYSTEM_SPEC.md
├── CLAUDE.md
└── mkdocs.yml
```

### Uwaga o generowanym manifeście

Pliki YAML nie powinny być parsowane w przeglądarce. `build_activities.py` powinien walidować definicje i generować JSON umieszczany w katalogu publikowanym przez MkDocs, np.:

```text
docs/assets/generated/activities.json
```

Plik generowany nie powinien być ręcznie edytowany.

---

## 13. Pierwszy pionowy wycinek (MVP-0)

### Cel

Udowodnić, że obecny statyczny podręcznik może bezpiecznie przyjąć warstwę aktywności bez Moodle i bez backendu.

### Strona pilotażowa

Preferencja:

```text
docs/04-sterowanie/petle-i-iteratory.md
```

Alternatywnie można użyć strony z rozdziału 2, jeśli prostsze przykłady okażą się lepsze do testu technicznego.

### Zakres

Na jednej stronie umieścić:

- 1 aktywność `acknowledgement`;
- 1 aktywność `single_choice`;
- 1 aktywność `code`;
- 1 podsumowanie postępu strony.

Po przeładowaniu strony wszystko ma zostać odtworzone z `localStorage`.

### Kryteria akceptacji

- `mkdocs build` przechodzi;
- bez JavaScript treść pozostaje czytelna;
- warstwa interaktywna nie zmienia istniejącej nawigacji;
- trzy aktywności są renderowane z osobnych definicji;
- żadna aktywność nie zapisuje bezpośrednio do `localStorage`;
- Pyodide ładuje się dopiero po kliknięciu „Uruchom”;
- kod działa w Workerze;
- można zresetować zawieszone wykonanie;
- tryb jasny i ciemny pozostają spójne z Material;
- interfejs jest używalny na wąskim ekranie;
- stan postępu wraca po odświeżeniu;
- brak Moodle, backendu i kont użytkowników.

---

## 14. Kolejność implementacji MVP-0

### Krok A — przygotowanie repozytorium

1. utworzyć `feature/interactive-poc` od `dev`;
2. dodać `AGENTS.md` i niniejszą specyfikację;
3. dodać puste katalogi docelowe;
4. upewnić się, że istniejący `mkdocs build` nadal przechodzi.

### Krok B — kontrakt aktywności

1. zdefiniować minimalny format YAML;
2. utworzyć `validate_activities.py`;
3. utworzyć `build_activities.py` generujący JSON;
4. dodać jeden stabilny slot do strony pilotażowej;
5. wyświetlić w przeglądarce placeholder aktywności.

### Krok C — postęp lokalny

1. stworzyć `ProgressStore`;
2. stworzyć `BrowserProgressStore`;
3. zaimplementować `acknowledgement`;
4. odtworzyć stan po reloadzie;
5. dodać podsumowanie postępu strony.

### Krok D — mini-quiz

1. zaimplementować `single_choice`;
2. dodać feedback;
3. zapisać status, wynik i próby;
4. sprawdzić ponowne uruchomienie po reloadzie.

### Krok E — Python

1. utworzyć warstwę `pyodide-runtime`;
2. uruchamiać Pyodide leniwie;
3. przenieść wykonanie do Web Workera;
4. przechwycić stdout/stderr;
5. zaimplementować reset/stop;
6. zaimplementować jedno proste sprawdzenie wyniku;
7. zapisać stan ukończenia przez `ProgressStore`.

### Krok F — walidacja UX

1. tryb jasny;
2. tryb ciemny;
3. desktop;
4. wąski viewport;
5. klawiatura;
6. rozsądne komunikaty błędów;
7. brak regresji statycznego tekstu.

---

## 15. Dopiero później: `python-notatki-service`

Po zatwierdzeniu MVP-0 tworzymy osobne repozytorium backendowe.

Zakres pierwszej wersji serwisu:

```text
/lti/login
/lti/launch
/lti/jwks
/api/me
/api/progress
/api/progress/{activity_id}
```

Dokładne endpointy mogą zostać zmienione po spike'u LTI.

### Minimalny model danych

```text
Platform
CourseContext
UserIdentity
Enrollment
ActivityProgress
```

Nie ma modelu `Password`, `PasswordReset`, `EmailVerification` ani lokalnej rejestracji.

### Proponowana technologia

Backend powinien pozostać w Pythonie. Przed wyborem frameworka należy zrobić mały spike kompatybilności z aktualną biblioteką LTI 1.3. Preferuj rozwiązanie z dojrzałym adapterem LTI zamiast pisać protokół OIDC/JWT ręcznie.

Na etapie spike'u nie budujemy jeszcze panelu administracyjnego.

---

## 16. Integracja LTI — MVP-1

Po zaakceptowaniu statycznego POC:

1. zarejestrować testowe narzędzie LTI 1.3 w środowisku Moodle;
2. uruchomić launch do nowej karty;
3. zweryfikować podpis i claims po stronie backendu;
4. utworzyć sesję aplikacji;
5. przekazać frontendowi tylko minimalną informację o trybie kursowym;
6. przełączyć `ProgressStore` z Browser na Remote;
7. sprawdzić ciągłość postępu na dwóch przeglądarkach/urządzeniach;
8. nie implementować jeszcze AGS/ocen, jeśli nie jest potrzebne do proof-of-concept.

Dopiero w następnym kroku rozważyć raportowanie zbiorczego ukończenia modułu do Moodle.

---

## 17. Tryb dostępu publicznego

Mechanizm powinien umożliwiać zmianę konfiguracji bez przebudowy aktywności:

```text
ACCESS_MODE=MOODLE_ONLY
```

lub:

```text
ACCESS_MODE=PUBLIC_FULL
```

W `PUBLIC_FULL`:

- brak kont;
- brak LTI;
- pełny tekst;
- pełne mikroaktywności;
- postęp w `localStorage`;
- jasna informacja, że postęp jest lokalny dla tej przeglądarki.

W `MOODLE_ONLY`:

- serwer/reverse proxy nie udostępnia materiału bez poprawnej sesji kursowej;
- frontend korzysta z `RemoteProgressStore`;
- żadnego formularza logowania lokalnego.

---

## 18. Zasada „publiczny i kursowy frontend to ten sam produkt”

Nie tworzymy dwóch paczek JavaScript i dwóch wersji strony.

Uruchomienie powinno wyglądać ideowo tak:

```javascript
const store = runtimeMode === "course"
  ? new RemoteProgressStore(apiClient)
  : new BrowserProgressStore(window.localStorage);

const engine = new ActivityEngine({ store });
engine.start();
```

Różnica jest w konfiguracji i magazynie postępu, nie w treści aktywności.

---

## 19. Czego nie robić w MVP

Nie implementować teraz:

- React/Vue/Svelte tylko dlatego, że projekt staje się interaktywny;
- pełnego SPA;
- własnych kont;
- profilu użytkownika;
- importu postępu z publicznego trybu do Moodle;
- synchronizacji offline;
- rankingów;
- odznak;
- adaptacyjnego AI;
- formalnego oceniania;
- sandboxa serwerowego;
- JupyterLite;
- zaawansowanego edytora kodu;
- automatycznych hashy treści;
- panelu prowadzącego;
- rozbudowanej analityki.

Te elementy mogą być wartościowe później, ale utrudniają ocenę podstawowej architektury.

---

## 20. CI i kontrola jakości — po działającym POC

Po MVP-0 warto dodać GitHub Actions, które wykonują:

```text
1. walidację YAML aktywności
2. generowanie manifestu
3. mkdocs build
4. testy JavaScript / testy przeglądarkowe
5. kontrolę, czy wszystkie sloty wskazane przez aktywności istnieją
```

W późniejszym etapie CI może raportować aktywności wymagające przeglądu po zmianie powiązanej treści.

---

## 21. Sugerowany sposób pracy z Codex w VS Code

Codex powinien być używany do małych, dobrze ograniczonych etapów. Nie należy zaczynać od polecenia „zbuduj cały system”.

Przykładowa sekwencja zadań:

### Zadanie 1

> Przeczytaj `AGENTS.md`, `CLAUDE.md` i `INTERACTIVE_SYSTEM_SPEC.md`. Nie zmieniaj jeszcze kodu. Przejrzyj repozytorium i zaproponuj minimalny patch dla MVP-0: katalogi, jeden slot na stronie pilotażowej i sposób podłączenia jednego pliku JavaScript do MkDocs. Wskaż ryzyka i pliki do zmiany.

### Zadanie 2

> Zaimplementuj tylko minimalny Activity Engine, który znajduje `data-activity-slot` i renderuje placeholder na podstawie statycznej definicji. Bez Pyodide, quizów i backendu. Uruchom `mkdocs build`.

### Zadanie 3

> Dodaj `BrowserProgressStore` i aktywność `acknowledgement`. Komponent nie może używać `localStorage` bezpośrednio. Dodaj test/mały mechanizm walidacji i sprawdź reload strony.

### Zadanie 4

> Dodaj `single_choice` używające tego samego Activity Engine i ProgressStore. Nie rozszerzaj schematu poza to, co jest potrzebne.

### Zadanie 5

> Dodaj Pyodide dla jednej aktywności `code`. Runtime ma ładować się leniwie i działać w Web Workerze. Dodaj możliwość przerwania/resetu. Nie dodawaj zaawansowanego edytora.

Taki sposób pracy ogranicza ryzyko dużego, trudnego do oceny patcha.

---

## 22. Definicja zakończenia etapu MVP-0

Etap jest zakończony, kiedy można pokazać jedną stronę istniejącego podręcznika, która:

- nadal jest zwykłą stroną MkDocs;
- zawiera trzy różne mikroaktywności;
- uruchamia prawdziwy Python 3.14 w przeglądarce;
- zapisuje anonimowy postęp lokalnie;
- po odświeżeniu odtwarza stan;
- nie potrzebuje Moodle ani serwera;
- ma kod przygotowany do podmiany `BrowserProgressStore` na `RemoteProgressStore`;
- przechodzi build i podstawową walidację;
- nie miesza się z formalnymi zadaniami/kolokwiami kursu.

Dopiero po tym etapie rozpoczynamy osobny spike LTI i tworzenie `python-notatki-service`.

---

## 23. Decyzje do podjęcia po MVP-0

Po obejrzeniu działającego prototypu należy świadomie zdecydować:

- czy YAML jest wygodnym formatem autorskim;
- czy aktywności powinny być ładowane per strona czy z jednego manifestu;
- czy prosty edytor kodu wystarcza;
- jaki poziom postępu ma trafiać do Moodle;
- czy backend ma korzystać z Flask/Django/innego frameworka na podstawie aktualnej kompatybilności LTI;
- czy potrzebny jest osobny panel prowadzącego;
- jak dokładnie działa sezonowe `PUBLIC_FULL`;
- kiedy wdrożyć wykrywanie zmian treści zależnych od aktywności.

Te decyzje nie powinny blokować pierwszego pionowego wycinka.
