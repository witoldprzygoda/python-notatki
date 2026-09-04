# Interaktywny podręcznik Python — specyfikacja architektury i plan MVP

## 1. Kontekst

Projekt `python-notatki` jest rozwijanym podręcznikiem do kursu języka Python. Źródłowa treść pozostaje w Markdown i jest publikowana przez MkDocs Material. Rozbudowujemy serwis o lekką warstwę interaktywną, która ma zwiększać aktywność studenta podczas pracy z tekstem, ale nie ma zastępować Moodle ani formalnego systemu oceniania kursu.

System ma dwie niezależne osie konfiguracji:

1. **prezentacja** — `clean` publikuje czysty podręcznik, a `interactive` dodaje warstwę ćwiczeń;
2. **dostęp i tożsamość** — `MOODLE_ONLY` używa Moodle/LTI, a `PUBLIC_FULL` udostępnia podręcznik bez kont.

Wariant prezentacji nie wybiera trybu dostępu i odwrotnie. Te same źródła Markdown służą do wszystkich wariantów wdrożenia.

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
- jeden zwijany blok ćwiczeń i pytań na końcu strony;
- podpowiedzi;
- lokalny postęp anonimowego użytkownika;
- trwały postęp użytkownika Moodle;
- wskaźniki postępu ćwiczeń dla stron i sekcji w nawigacji wariantu `interactive`;
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

Diagram opisuje wariant `interactive`. Wariant `clean` publikuje ten sam Markdown bez uruchamiania Activity Engine i ProgressStore. Warstwa aktywności działa niezależnie od źródła tożsamości. Moodle nie jest wywoływany bezpośrednio z komponentów quizu lub ćwiczenia.

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

### Wariant prezentacji `clean` / `interactive`

Domyślny `mkdocs.yml` buduje wariant `interactive`. Nakładka `mkdocs.clean.yml` dziedziczy wspólną konfigurację, ale nie publikuje manifestu, JavaScriptu ani CSS warstwy interaktywnej:

```text
mkdocs build                         # interactive
mkdocs build -f mkdocs.clean.yml     # clean
```

Oba buildy walidują wspólne definicje YAML, sloty i stabilne anchory. `clean` nie jest synonimem `PUBLIC_FULL`, a `interactive` nie implikuje `MOODLE_ONLY`.

Przy przełączaniu wariantu trzeba zrestartować `mkdocs serve`. Buildów clean i interactive nie należy mieszać przez `--dirty` w tym samym `site_dir`; CI powinno używać pełnego builda albo osobnych katalogów wynikowych, aby nie pozostawić starych assetów.

### Tryb MOODLE_ONLY

```text
Moodle -> LTI launch -> nowa karta -> sesja kursowa -> podręcznik
```

Anonimowe żądanie treści powinno zostać zatrzymane przez warstwę dostępu.

### Tryb PUBLIC_FULL

```text
PUBLIC_FULL + interactive:
Internet -> podręcznik -> aktywności -> BrowserProgressStore
```

Backend może w tym trybie w ogóle nie być potrzebny do zwykłego korzystania z materiału.

Przełączenie trybu dostępu powinno odbywać się konfiguracją wdrożenia, nie edycją zawartości rozdziałów.

---

## 6. Kontrakt między tekstem a aktywnością

Treść Markdown nie zawiera definicji quizu ani rozwiązania. Strona z aktywnościami zapewnia wyłącznie:

1. jawne, stabilne identyfikatory sekcji, których dotyczą ćwiczenia;
2. dokładnie jeden globalnie unikalny slot na końcu strony.

Przykład:

```markdown
## Pętla for {#petla-for data-activity-section="true"}

<!-- treść podrozdziału -->

<div data-activity-slot="petle-i-iteratory-activities"></div>
```

Anchor oznaczony `data-activity-section="true"` jest decyzją autora i nie może być automatycznym slugiem zależnym od tekstu nagłówka. `slot_id` identyfikuje fizyczne miejsce renderowania; może wystąpić tylko na jednej stronie. W wariancie `interactive` Activity Engine umieszcza w nim jedno domyślnie zamknięte `<details>` z nagłówkiem „Ćwiczenia i pytania” i renderuje aktywności w kolejności YAML. W wariancie `clean` pusty slot pozostaje niewidoczny.

Nie wolno wiązać aktywności z numerem linii, tekstem nagłówka ani pozycją elementu DOM. Aktywność dotycząca całej strony używa jawnego `section_id: null`.

Definicja schema v3 znajduje się poza `docs/`, na przykład w `activities/04-sterowanie/petle-i-iteratory.yaml`:

```yaml
schema_version: 3
page: 04-sterowanie/petle-i-iteratory.md
slot_id: petle-i-iteratory-activities

activities:
  - activity_id: flow-for-quiz-001
    version: 1
    section_id: petla-for
    type: single_choice
    label: "Sprawdzenie zrozumienia pętli for"
    prompt: "Ile razy wykona się ciało pętli po łańcuchu abc?"
    options:
      - option_id: a
        label: "Dwa razy"
      - option_id: b
        label: "Trzy razy"
    correct_option_id: b
    feedback:
      correct: "Pętla wykona się raz dla każdego z trzech znaków."
      incorrect: "Łańcuch abc zawiera trzy znaki."
    solution:
      discussion: >-
        Pętla pobiera kolejno każdy element iterowalnego obiektu. Dla
        trzyznakowego łańcucha jej ciało wykona się zatem trzy razy.

  - activity_id: flow-for-code-001
    version: 1
    section_id: petla-for
    type: code
    label: "Ćwiczenie: iteracja po łańcuchu"
    prompt: "Wypisz każdy znak w osobnym wierszu."
    starter_code: |
      for znak in "abc":
          print(znak)
    checker:
      type: stdout_lines_exact
      expected_lines: ["a", "b", "c"]
    feedback:
      correct: "Program wypisał znaki w oczekiwanej kolejności."
      incorrect: "Sprawdź kolejność wypisanych wierszy."
    solution:
      code: |
        for znak in "abc":
            print(znak)
      discussion: >-
        Zmienna znak otrzymuje w kolejnych iteracjach poszczególne znaki
        łańcucha, dlatego każde wywołanie print wypisuje jeden z nich.
```

Pola `feedback.correct` i `feedback.incorrect` zawierają wyłącznie wyjaśnienie dydaktyczne, a nie etykietę wyniku. Jednolitą etykietę „✓ Poprawnie” albo „! Niepoprawnie” dodaje renderer. Pola te nie powinny rozpoczynać się od „Poprawnie.” ani „Niepoprawnie.”; komunikaty błędów technicznych pozostają odrębną kategorią.

Build waliduje schema v3 przed renderowaniem, a po konwersji Markdown sprawdza dokładnie jeden właściwy slot oraz istnienie wszystkich oznaczonych `section_id`.

Autor podaje wyłącznie źródłową ścieżkę `page`. Podczas pełnego buildu hook
MkDocs odczytuje rzeczywiste `page.url` dla wyrenderowanej strony i dodaje do
publikowanego manifestu pochodne pole `page_url`. Pole uwzględnia konfigurację
URL-i MkDocs, nie należy do źródłowego schema YAML i nie może być wpisywane
ręcznie. Frontend używa go do powiązania aktywności z linkiem strony w
nawigacji bez odtwarzania reguł Markdown → URL.

---

## 7. Typy aktywności

### 7.1 `acknowledgement`

Typ został zweryfikowany w historycznym POC. Bieżące definicje treści schema v3 nie używają aktywności polegających wyłącznie na potwierdzeniu przeczytania; renderer może pozostać do osobnego etapu porządkowania kodu.

Historyczne przykłady zastosowania:

- „Przeczytaj uwagę o mutowalności i zaznacz jako wykonane.”
- „Obejrzyj krótką animację i przejdź dalej.”
- „Zapoznaj się z zasadą PEP 8.”

Nie wymuszamy pytania kontrolnego, jeżeli autor materiału nie uważa go za potrzebne.

### 7.2 `single_choice`

Małe pytanie powiązane z sekcją treści przez `section_id` i renderowane w końcowym bloku ćwiczeń strony. Nie jest formalnym quizem Moodle.

Powinno wspierać:

- natychmiastową informację zwrotną;
- możliwość ponownej próby, jeśli autor na to pozwala;
- zapis wyniku i liczby prób;
- opcjonalne oznaczenie jako wymagane do postępu w podręczniku.

Status `completed` pozostaje monotoniczny podczas zwykłych prób. Jedynym
świadomym wyjątkiem jest akcja użytkownika „Zacznij od nowa”, która dla
zapisanego stanu wywołuje `reset([activityId])` i przywraca aktywność do stanu
początkowego bez rekordu, wyniku i liczby prób. Jeżeli użytkownik jedynie
wybrał odpowiedź, ale jeszcze jej nie sprawdził, renderer czyści wybór lokalnie
bez wywoływania magazynu i bez powiadomienia centralnego modelu postępu.

Poprawna odpowiedź pokazywana przez akcję „Pokaż rozwiązanie” jest wyznaczana
wyłącznie przez `correct_option_id`; definicja nie powiela jej w polu
`solution`. Ujawnienie odpowiedzi nie zmienia zaznaczonego przycisku radio i
nie jest próbą automatycznego sprawdzenia.

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

„Resetuj interpreter” jest operacją techniczną: kończy bieżący Worker, ale
zachowuje kod i postęp ćwiczenia. Akcja jest dostępna tylko wtedy, gdy renderer
utworzył Worker w swoim bieżącym cyklu życia; sam odtworzony zapis `completed`
nie oznacza istnienia interpretera. Osobna akcja „Zacznij od nowa” kończy
ewentualne wykonanie, resetuje interpreter, przywraca dokładny `starter_code`,
czyści wyjście i informację zwrotną oraz wywołuje `reset([activityId])`, jeśli
aktywność miała zapisany stan. Bez zapisanego stanu reset pozostaje lokalny.
Poza tą jawną akcją status `completed` pozostaje monotoniczny.

Rozwiązanie referencyjne pochodzi z YAML i jest prezentowane w osobnym,
nieedytowalnym bloku kodu. Jego ujawnienie nie zastępuje kodu użytkownika, nie
uruchamia interpretera i nie wykonuje checkera. Po ujawnieniu użytkownik może
nadal edytować, uruchamiać i sprawdzać własny kod.

Pole `solution` typu `code` zawiera wymagane `code` i `discussion` oraz może
zawierać listę `alternatives`. Każdy wariant alternatywny ma prostą strukturę
`label`, `code`, `discussion`. Typ `single_choice` nie powiela poprawnej
odpowiedzi w `solution`; przechowuje tam wyłącznie szersze `discussion`.

### 7.4 Zakres automatycznej weryfikacji aktywności `code`

Pozytywny wynik mechanizmu sprawdzającego (ang. *checker*) oznacza wyłącznie,
że sprawdzane wykonanie spełniło jawne kryterium zapisane w definicji
aktywności. Nie stanowi on pełnej oceny poprawności, jakości, stylu, wydajności
ani ogólności rozwiązania. Status `completed` nie jest synonimem pozytywnego
wyniku checkera: oznacza świadomą decyzję użytkownika o zakończeniu pracy z
aktywnością i pozostaje postępem w podręczniku, nie formalną oceną kursową.

W szczególności kryterium oparte na oczekiwanym wyjściu potwierdza zgodność wyniku tylko w sprawdzanym przypadku. Nie dowodzi użycia oczekiwanej konstrukcji ani poprawności dla innych danych. Polecenie i informacja zwrotna powinny precyzyjnie opisywać zakres faktycznie sprawdzany przez checker.

### 7.5 Ukończenie, rozwiązanie i omówienie

Aktywne typy `single_choice` i `code` mogą przejść do `completed` trzema
równorzędnymi drogami:

```text
poprawny Check      -> checked
Pokaż rozwiązanie   -> solution_shown
Oznacz jako wykonane -> self_marked
```

Otwarcie „Omów rozwiązanie” również ujawnia rozwiązanie i używa metody
`solution_shown`. Interfejs nie pokazuje metody ukończenia i nie różnicuje na
jej podstawie statusu ani wskaźników postępu. Nagłówek we wszystkich
przypadkach pokazuje wyłącznie „✓ Wykonano”.

Metoda pierwszego przejścia do `completed` jest zapisywana jednokrotnie w
`payload.completion_method`. Późniejsze próby, ujawnienie rozwiązania i dalsza
praca nie mogą jej nadpisać. `payload.solution_revealed` oraz
`payload.discussion_revealed` przechowują trwały stan ujawnienia; omówienie
implikuje ujawnienie rozwiązania. Wszystkie te pola usuwa dopiero istniejąca
akcja „Zacznij od nowa”.

Historyczny rekord `completed` z `score: 1`, lecz bez `completion_method`, jest
interpretowany jako ukończony metodą `checked`. Samo renderowanie nie zapisuje
migracji; pole trafia do rekordu dopiero przy jego następnej jawnej aktualizacji.

`attempts` zwiększa się wyłącznie przy Check. `score` opisuje najlepszy
dotychczasowy wynik automatycznej weryfikacji: poprawny Check ustawia `1`, a
błędny `0`, o ile wcześniej nie osiągnięto `1`. Run, ujawnienie rozwiązania i
samoocena nie tworzą ani nie zmieniają `score`. Status oraz wynik są odrębnymi
pojęciami.

„Pokaż rozwiązanie” oraz „Omów rozwiązanie” ujawniają treść lokalnie przed
próbą zapisu. Błąd `ProgressStore.save()` nie może odebrać użytkownikowi już
pokazanej pomocy, ale nie powoduje wtedy zmiany nagłówka ani wskaźników; po
przeładowaniu niezapisane ujawnienie może zniknąć. „Oznacz jako wykonane”
zmienia interfejs dopiero po udanym zapisie.

Pola `solution.discussion` są zwykłym tekstem i zawierają szersze omówienie,
a nie powtórzenie `feedback.correct`. Rozwiązania są publikowane w jawnym
manifeście wariantu `interactive` i nie są zabezpieczeniem formalnej oceny.
Frontend wstawia tekst przez `textContent`, a kod przez `textContent` elementu
`<code>`; nie interpretuje HTML ani Markdown.

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
  async getSummary() {}
  async reset(activityIds = null) {}
}
```

`reset(null)` usuwa cały postęp należący do magazynu, natomiast
`reset([activityId, ...])` usuwa wyłącznie stan wskazanych aktywności. Pusta
lista nie zmienia magazynu. Implementacja nie może interpretować braku
argumentu inaczej niż jawnego `null`.

### 9.2 BrowserProgressStore

Pierwsza implementacja oparta o `localStorage`.

Przykładowy klucz:

```text
python-notatki.progress.v1
```

Przykładowy stan:

```json
{
  "schema_version": 1,
  "activities": {
    "flow-for-quiz-001": {
      "activity_id": "flow-for-quiz-001",
      "version": 1,
      "status": "completed",
      "score": 1,
      "attempts": 2,
      "updated_at": "2026-08-19T12:05:00Z",
      "payload": {
        "selected_option_id": "b",
        "last_result": "correct",
        "completion_method": "checked",
        "solution_revealed": true
      }
    }
  }
}
```

Nie zapisujemy imienia, nazwiska, e-maila ani innych danych identyfikujących.

Wersja dokumentu `localStorage` jest niezależna od wersji schematu definicji aktywności. Usunięcie definicji z manifestu nie usuwa automatycznie jej starego, osieroconego wpisu z magazynu i nie powoduje jego renderowania.

### 9.3 RemoteProgressStore

Późniejsza implementacja komunikuje się z backendem. UI nie powinno wymagać zmian przy zamianie magazynu.

### 9.4 Centralny model postępu ćwiczeń

W wariancie `interactive` moduł `global-progress.js` działa jako bezgłowy
centralny model statusów aktywności z aktualnego manifestu. Utrzymuje jedyną
mapę `activity_id → completed`, gdzie wartość `completed` jest prawdziwa
wyłącznie wtedy, gdy `ProgressStore.get(activityId)` zwraca stan o
`status === "completed"`. Model nie tworzy żadnego widocznego komponentu,
procentu ani elementu `<progress>`. Jego dane służą wyłącznie wskaźnikom stron
i sekcji opisanym w sekcji 9.5.

Do modelu nie wchodzą `score`, `attempts`, odwiedzone strony, stan rozwinięcia
bloku ćwiczeń ani osierocone rekordy nieobecne w manifeście.
Nie wchodzą do niego również `completion_method` ani flagi ujawnienia pomocy:
wszystkie drogi świadomego ukończenia dają ten sam stan raila.

Aktualizacje zapewnia neutralny względem DOM dekorator `NotifyingProgressStore`.
Zachowuje on pełny interfejs magazynu i dodaje subskrypcję zmian. Po udanym
`save(activityId, state)` emituje `{ type: "save", activityId }`; odbiorca
odczytuje kanoniczny stan przez `get(activityId)`. Po udanym resecie emituje
`{ type: "reset", activityIds }`, gdzie `null` oznacza reset całego magazynu,
a tablica — reset częściowy. Nieudana operacja nie emituje powiadomienia.
Dekorator przekazuje wywołującemu niezmieniony wynik właściwego magazynu, ale
nie interpretuje go i nie umieszcza go w zdarzeniu.
Dekorator nie korzysta z `window`, `document`, `EventTarget` ani zdarzeń DOM,
dzięki czemu może opakować zarówno `BrowserProgressStore`, jak i przyszły
`RemoteProgressStore`.

Manifest jest pobierany raz w ramach życia dokumentu i współdzielony między
nawigacjami `navigation.instant`. Model jest hydratowany raz, a po `save` oraz
resecie aktualizuje cache przed powiadomieniem subskrybentów. Wariant `clean`
nie publikuje modelu ani kodu wskaźników.

### 9.5 Wskaźniki stron i sekcji w nawigacji

W wariancie `interactive` rzeczywiste linki stron w lewej nawigacji kursu oraz
jawnie oznaczone sekcje w obu kopiach lokalnego spisu treści mogą mieć
dyskretny pionowy rail postępu. Rail jest osobnym elementem DOM umieszczonym w
własnej kolumnie po lewej stronie nazwy. Nie przejmuje ani nie modyfikuje
istniejącego niebieskiego markera aktywnej pozycji Material/`extra.css`: marker
aktywny oznacza bieżące położenie, a rail wyłącznie stan ćwiczeń.

Lewy rail agreguje wszystkie aktywności o danym `page`, korzystając z
generowanego `page_url`. Otrzymują go wyłącznie rzeczywiste linki `<a>` do stron;
organizacyjne etykiety i grupy nawigacji pozostają bez statusu. Prawy rail
używa `slot_id` bieżącej strony oraz `section_id`; aktywność z
`section_id: null` nie zasila wskaźnika sekcji. Wskaźników nie umieszcza się
przy nagłówkach artykułu.

Dla strony lub sekcji oblicza się liczbę przypisanych aktywności `N` oraz liczbę
stanów `status === "completed"` równą `C`. Stany to: `none` dla `N == 0`,
`none_completed` dla `N > 0` i `C == 0`, `partial` dla `0 < C < N` oraz
`completed` dla `C == N`. Oprócz szarego, czerwonego, pomarańczowego i
zielonego koloru stany rozróżnia kształt: subtelne szare wypełnienie z
przerywanym obrysem, ciągły pusty obrys, częściowe wypełnienie albo pełne
wypełnienie. Pełny tekst dostępny w obrębie linku przekazuje znaczenie
niezależnie od koloru, a rail nie tworzy osobnego punktu Tab.

Jedynym cache'em statusów pozostaje mapa należąca do centralnego modelu
postępu. Udostępnia on wyłącznie odczyt pojedynczego statusu i subskrypcję
identyfikatorów zmienionych po zaktualizowaniu cache'u. Dekoratory lewej
nawigacji i lokalnego ToC nie czytają bezpośrednio `ProgressStore` i nie
przechowują własnych map ukończeń. Mogą przechowywać jedynie statyczne indeksy
manifestu oraz referencje do markerów aktualnego dokumentu. Po `save`, resecie
częściowym lub pełnym przeliczają tylko odpowiednie strony i sekcje.

Brak slotu oznacza pusty zbiór aktywności bieżącej strony, dlatego jawnie
oznaczone sekcje mogą otrzymać stan `none`. Brak spisu treści albo oznaczonych
sekcji jest bezpiecznym brakiem działania. Niedostępny manifest lub nieudana
hydratacja postępu nie są żadnym ze stanów strony ani sekcji: w takim przypadku
markerów nie tworzy się albo usuwa się markery utworzone wcześniej. Wariant
`clean` nie publikuje modułów ani stylów wskaźników.

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

`schema_version` opisuje strukturę dokumentu YAML i manifestu, natomiast `version` opisuje semantykę konkretnej aktywności. Przeniesienie niezmienionej aktywności do nowego slotu lub zmiana wspólnego schematu definicji nie zmienia jej `activity_id`, `version` ani zapisanego postępu.

Analogicznie przejście wspólnego kontraktu YAML z schema v2 na schema v3 oraz
dodanie systemowych dróg ukończenia nie zwiększa automatycznie `version`
każdej aktywności. Wersję aktywności podnosimy dopiero wtedy, gdy zmienia się
jej indywidualne polecenie, poprawna odpowiedź, checker albo inny element
semantyczny uzasadniający ponowne rozpatrzenie wcześniejszego postępu.

---

## 11. Reagowanie na zmiany podręcznika

Obowiązujący kontrakt to `page` + top-level `slot_id` + per-activity `section_id` + `activity_id`. Build sprawdza globalną unikalność slotu, jego pojedyncze wystąpienie na właściwej stronie oraz istnienie jawnie oznaczonego anchora dla każdego niepustego `section_id`.

Mechanizm hashy treści jest wartościowy, ale nie należy go jeszcze implementować.

Etap późniejszy może dodać:

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
│   │       ├── page-activities.js
│   │       ├── progress-store.js
│   │       ├── browser-progress-store.js
│   │       ├── notifying-progress-store.js
│   │       ├── global-progress.js       # bezgłowy centralny model statusów
│   │       ├── page-progress.js
│   │       ├── section-progress.js
│   │       ├── progress-rail.js
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
├── mkdocs.yml
└── mkdocs.clean.yml
```

### Uwaga o generowanym manifeście

Pliki YAML nie są parsowane w przeglądarce. `build_activities.py` waliduje definicje w obu wariantach prezentacji, a w wariancie `interactive` zapisuje JSON bezpośrednio do katalogu wynikowego MkDocs:

```text
<site_dir>/assets/generated/activities.json
```

Manifest nie powstaje w `docs/`, nie powinien być ręcznie edytowany i nie jest publikowany w wariancie `clean`. Clean build wyklucza również `docs/javascripts/interactive/**` oraz `docs/stylesheets/interactive.css`.

Każdy wpis publikowanego manifestu zawiera pochodne `page_url` odczytane z
`Page.url` MkDocs. Pole służy wyłącznie frontendowi i nie jest częścią
autorskiego pliku YAML.

---

## 13. Pierwszy pionowy wycinek (MVP-0)

Ta sekcja dokumentuje historyczny zakres POC. Bieżący kontrakt autorski znajduje się w sekcji 6 i używa schema v3, jednego końcowego slotu na stronę oraz dwóch aktywnych typów treści: `single_choice` i `code`.

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
- w prezentacji `interactive`: pełne mikroaktywności i postęp w `localStorage`;
- w prezentacji `clean`: statyczny tekst bez warstwy postępu;
- przy lokalnym postępie: jasna informacja, że jest właściwy dla tej przeglądarki.

W `MOODLE_ONLY`:

- serwer/reverse proxy nie udostępnia materiału bez poprawnej sesji kursowej;
- frontend wariantu `interactive` korzysta z `RemoteProgressStore`;
- żadnego formularza logowania lokalnego.

---

## 18. Zasada „publiczny i kursowy frontend interactive to ten sam produkt”

Nie tworzymy osobnych paczek JavaScript dla dostępu publicznego i kursowego. Wariant `interactive` używa tego samego Activity Engine, a źródło postępu wynika z trybu dostępu. Osobny statyczny wariant `clean` powstaje z tych samych źródeł Markdown przez konfigurację builda.

Uruchomienie powinno wyglądać ideowo tak:

```javascript
const store = runtimeMode === "course"
  ? new RemoteProgressStore(apiClient)
  : new BrowserProgressStore(window.localStorage);

const engine = new ActivityEngine({ store });
engine.start();
```

Różnica publiczny/kursowy jest w konfiguracji i magazynie postępu, nie w treści aktywności. Jest to oś niezależna od wyboru `clean`/`interactive`.

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
2. walidację pojedynczych slotów i jawnych section_id w bieżącym schemacie
3. osobne buildy MkDocs clean oraz interactive
4. testy JavaScript / testy przeglądarkowe
5. kontrolę, że tylko interactive publikuje manifest i zasoby interaktywne
```

W późniejszym etapie CI może raportować aktywności wymagające przeglądu po zmianie powiązanej treści.

---

## 21. Historyczna sekwencja prac MVP-0 (archiwum)

Poniższa sekwencja dokumentuje sposób, w jaki powstał pierwszy POC. Nie jest bieżącą instrukcją autorską; aktualny kontrakt znajduje się w sekcji 6.

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

## 22. Historyczna definicja zakończenia etapu MVP-0 (archiwum)

Pierwotny etap uznawaliśmy za zakończony, kiedy można było pokazać jedną stronę istniejącego podręcznika, która:

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
- czy prosty edytor kodu wystarcza;
- jaki poziom postępu ma trafiać do Moodle;
- czy backend ma korzystać z Flask/Django/innego frameworka na podstawie aktualnej kompatybilności LTI;
- czy potrzebny jest osobny panel prowadzącego;
- jak dokładnie działa sezonowe `PUBLIC_FULL`;
- kiedy wdrożyć wykrywanie zmian treści zależnych od aktywności.
- jak odizolować cykl życia runtime'u wielu aktywności `code`: obecna
  implementacja współdzieli jedną instancję `PyodideRuntime`, więc reset Workera
  z jednej aktywności może przerwać wykonanie uruchomione w innej; MVP nie
  rozwiązuje jeszcze tego przypadku.

Te decyzje nie powinny blokować pierwszego pionowego wycinka.
