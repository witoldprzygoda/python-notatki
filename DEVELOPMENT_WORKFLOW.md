# Workflow rozwoju repozytorium

Ten dokument jest autorytatywnym źródłem zasad organizacji pracy nad książką,
aktywnościami, ich integracją, infrastrukturą i publikacją. Obowiązuje zarówno
ludzi, jak i modele AI. Szczegółowe zasady redakcyjne pozostają w `CLAUDE.md`,
a kontrakt warstwy interaktywnej w `INTERACTIVE_SYSTEM_SPEC.md`.

Przed rozpoczęciem pracy należy:

1. sprawdzić bieżący branch;
2. jeżeli praca nie odbywa się już na właściwym branchu roboczym, utworzyć go
   z aktualnego `origin/dev` albo ze zsynchronizowanego lokalnego `dev`;
3. zastosować tryb pracy wynikający z prefiksu brancha;
4. nie rozszerzać odpowiedzialności brancha bez jawnej decyzji użytkownika.

## Podział prac

| Obszar | Odpowiedzialność | Typowy branch |
| --- | --- | --- |
| Treść książki | Strony, rozdziały, struktura materiału i redakcja | `content/<temat>` |
| Aktywności | Definicje ćwiczeń, feedback, rozwiązania i omówienia | `activities/<temat>` |
| Integracja | Ponowne związanie zmienionej treści z aktywnościami | `integration/<temat>` |
| Infrastruktura | Renderery, checkery, postęp, runtime, walidacja i buildy | `infra/<temat>` |
| Publikacja | Świadoma promocja zaakceptowanego `dev` | `dev → master` |

## Hierarchia odpowiedzialności

```text
TREŚĆ KSIĄŻKI
    ↓
nadrzędne źródło prawdy merytorycznej

AKTYWNOŚCI
    ↓
są dostosowywane do aktualnej treści

INFRASTRUKTURA
    ↓
służy książce i aktywnościom,
nie może wymuszać struktury książki
```

Istnienie ćwiczenia nigdy nie może blokować sensownej przebudowy książki.
Tekstu książki nie wolno pogarszać tylko po to, aby zachować istniejący
checker. Jeśli aktualna treść i istniejąca aktywność są sprzeczne,
dostosowujemy aktywność do treści. Infrastruktura jest narzędziem, nie źródłem
struktury kursu.

## Role branchy

### `master`

`master` jest stabilnym lub publikowanym snapshotem całego projektu. Może
celowo pozostawać za `dev` i nie jest bazą codziennej pracy. Nie oznacza
„wersji bez interaktywności”: może zawierać zarówno książkę, jak i kod warstwy
interaktywnej.

Promocja `dev → master` następuje wyłącznie jako świadoma decyzja wydawnicza.
Zwykła praca nad treścią, aktywnościami ani infrastrukturą nie może
automatycznie aktualizować `master`.

### `dev`

`dev` jest centralnym branchem integracyjnym. Zawiera aktualną zaakceptowaną
treść książki, zaakceptowaną infrastrukturę interaktywną i zaakceptowane
aktywności. Jest punktem bazowym wszystkich nowych prac roboczych.

Nowe branche należy domyślnie tworzyć z aktualnego `origin/dev` albo ze
zsynchronizowanego lokalnego `dev`. Bezpośrednia praca na `dev` służy tylko
integracji lub zadaniom jawnie zleconym na tym branchu.

### `content/<temat>`

Branch służy do rozwoju samej książki, w szczególności do:

- dodawania nowych rozdziałów;
- przepisywania istniejących rozdziałów;
- reorganizacji struktury tekstu;
- korekt merytorycznych;
- pracy redakcyjnej.

Model pracujący na `content/*` nie projektuje ani nie poprawia aktywności i nie
rozwija infrastruktury interaktywnej, chyba że użytkownik jawnie zmieni zakres
zadania.

### `activities/<temat>`

Branch służy do:

- projektowania ćwiczeń dla aktualnej treści;
- zmiany definicji YAML;
- dostosowywania feedbacku;
- opracowywania rozwiązań i omówień;
- minimalnego dodawania wymaganych markerów integracyjnych do Markdown.

Nie służy do przepisywania książki tylko po to, aby istniejący checker lub
renderer był wygodniejszy.

### `integration/<temat>`

Jest to branch tymczasowy używany wtedy, gdy zaakceptowana zmiana treści:

- zmieniła strukturę strony;
- usunęła, podzieliła albo połączyła sekcję;
- zmieniła semantykę istniejącego `section_id`;
- przeniosła lub usunęła stronę z aktywnościami;
- spowodowała, że istniejące aktywności wymagają dostosowania.

Branch służy do ponownego związania aktualnej treści z aktywnościami. Powstaje
z zaakceptowanego HEAD brancha treściowego, a nie z wcześniejszej wersji
`dev`.

### `infra/<temat>`

Branch służy wyłącznie zmianom infrastrukturalnym, takim jak:

- renderery i checkery;
- `ProgressStore`;
- Pyodide i runtime;
- schemat YAML oraz walidator;
- centralny model postępu i raile;
- system buildów;
- przyszły backend i LTI.

Nowy `infra/*` powinien powstawać dopiero wtedy, gdy realna potrzeba treści lub
systemu uzasadnia zmianę infrastruktury. Nie tworzymy nowych mechanizmów „na
zapas”.

Skrót trybów pracy:

```text
content/*      → CONTENT AUTHORING
activities/*   → ACTIVITY AUTHORING
integration/*  → CONTENT/ACTIVITY INTEGRATION
infra/*        → INTERACTIVE INFRASTRUCTURE
dev            → tylko integracja lub jawnie zlecona praca
master         → branch wydawniczy; bez zmian bez jawnej decyzji
```

## Tryb CONTENT AUTHORING

Model pracujący na `content/*` ma przede wszystkim rozwijać książkę.

Może modyfikować w szczególności:

- `docs/**`, z zastrzeżeniem poniższej listy ścieżek tylko do odczytu;
- `mkdocs.yml`, jeżeli zadanie wymaga dodania strony lub zmiany nawigacji;
- `ZRZUTY.md`;
- pliki redakcyjne i dokumentacyjne bezpośrednio związane z treścią książki.

Jeżeli użytkownik jawnie nie poleci inaczej, model traktuje jako tylko do
odczytu:

- `activities/**`;
- `docs/javascripts/interactive/**`;
- `docs/stylesheets/interactive.css`;
- `scripts/build_activities.py`;
- testy systemu interaktywnego;
- `INTERACTIVE_SYSTEM_SPEC.md`;
- `mkdocs.clean.yml`.

`sources/**` jest materiałem źródłowym. Model może czytać znajdujące się tam
pliki PDF i TXT oraz wykłady i korzystać z nich jako referencji, ale nie
powinien modyfikować `sources/**`.

### Nadrzędność jakości książki

Jeśli wynika to z jakości merytorycznej i dydaktycznej, model CONTENT może:

- dodawać i usuwać strony;
- dzielić i łączyć strony;
- zmieniać kolejność sekcji;
- przepisywać całe rozdziały;
- zmieniać nagłówki;
- reorganizować strukturę materiału.

Nie wolno ograniczać takich zmian tylko dlatego, że istnieją powiązane
ćwiczenia.

## Markery integracyjne w Markdown

Zapis:

```markdown
{#stable-id data-activity-section="true"}
```

oznacza stabilny anchor pojęcia, do którego aktywności odwołują się przez
`section_id`.

Zapis:

```html
<div data-activity-slot="..."></div>
```

oznacza końcowe miejsce renderowania aktywności strony.

Jeżeli sekcja nadal opisuje to samo pojęcie, należy zachować jej stabilny
identyfikator nawet wtedy, gdy zmieni się tytuł, cały tekst, przykłady albo
sekcja zostanie gruntownie przepisana. Jeżeli strona nadal posiada aktywności,
końcowy slot powinien zostać zachowany. Markera nie wolno przesuwać wyłącznie
dla wygody renderera.

Jeżeli zmiana merytoryczna naprawdę usuwa pojęcie, dzieli je na nowe pojęcia,
łączy z innym albo zmienia jego sens, model CONTENT może usunąć, zastąpić lub
przenieść marker. Nie należy zachowywać starego `section_id` tylko po to, aby
build był zielony. Każdą taką zmianę trzeba jawnie wskazać w końcowym raporcie
jako wpływającą na aktywności.

## Zmiany stron posiadających aktywności

Jeżeli `content/*` modyfikuje stronę, dla której istnieje definicja w
`activities/**`, obowiązuje następujący workflow:

1. treść można zmieniać normalnie;
2. model CONTENT nie poprawia aktywności na własną rękę;
3. po zmianach wykonuje interactive build jako kontrolę kontraktu;
4. jeśli build nadal przechodzi, branch content może zostać normalnie
   zintegrowany;
5. jeśli build przestaje przechodzić wskutek świadomej zmiany struktury lub
   semantyki, nie należy sztucznie przywracać starych markerów;
6. model CONTENT kończy swoją pracę i raportuje zerwany kontrakt;
7. z jego zaakceptowanego HEAD powstaje `integration/<temat>`;
8. integrator dostosowuje YAML, `section_id`, `slot_id` — jeśli jest to
   konieczne — anchory, treść ćwiczeń, rozwiązania, checkery w ramach
   istniejących możliwości oraz `activity.version`, gdy zmieniła się semantyka
   ćwiczenia;
9. po ponownym przejściu interactive i clean buildów branch integracyjny
   trafia do `dev`.

Do `dev` nie integrujemy stanu z celowo zepsutym kontraktem Markdown ↔
activities.

### Dwa scenariusze content branch

```text
A. Zmiana nie łamie aktywności

dev
 ↓
content/<temat>
 ↓
testy/buildy PASS
 ↓
dev

B. Zmiana wymaga dostosowania aktywności

dev
 ↓
content/<temat>
 ↓
CONTENT zakończony
 ↓
integration/<temat> utworzony z zaakceptowanego HEAD treści
 ↓
dostosowanie activities
 ↓
testy/buildy PASS
 ↓
dev
```

## CONTENT HANDOFF

Każda większa sesja CONTENT powinna zakończyć się raportem w odpowiedzi
modelu, PR albo opisie przekazania pracy. Nie trzeba tworzyć osobnego pliku dla
każdej sesji.

```text
CONTENT HANDOFF

Zmienione strony:
...

Nowe strony:
...

Usunięte/przeniesione strony:
...

Zmienione stabilne section_id:
...

Usunięte section_id:
...

Nowe section_id:
...

Strony z istniejącymi aktywnościami, których dotyczyła zmiana:
...

Zmiany mogące wymagać aktualizacji activities:
...

Interactive build:
PASS / FAIL

Clean build:
PASS / FAIL

Jeśli interactive FAIL:
dokładny powód i oczekiwany wpływ na activities
```

Jeżeli model CONTENT przenosi stronę, zmienia nazwę pliku, dzieli lub łączy
strony albo usuwa stronę posiadającą aktywności, raport musi dodatkowo podać:

- starą ścieżkę;
- nową ścieżkę lub nowe ścieżki;
- usunięte `section_id`;
- nowe `section_id`;
- potencjalnie nieaktualne `activity_id`.

Sam model CONTENT nie zmienia wtedy `activities/**`.

## Reguły `activity.version`

- zmiana tekstu książki sama w sobie nie podnosi `activity.version`;
- zmiana tytułu sekcji sama w sobie nie podnosi `activity.version`;
- korekta literówki w feedbacku nie musi podnosić wersji;
- zmiana rozwiązania alternatywnego nie musi automatycznie podnosić wersji.

`activity.version` powinno wzrosnąć, gdy semantycznie zmienia się:

- polecenie ćwiczenia;
- poprawna odpowiedź;
- wymagany wynik;
- checker;
- sens ukończenia;
- cel dydaktyczny;
- zakres tego, co oznacza wcześniejsze `completed`.

Decyzję o zmianie wersji podejmuje etap `activities/*` albo `integration/*`.
Model CONTENT nie powinien samodzielnie zmieniać `activity.version`.

## Konflikty treści z aktywnościami

Przy konflikcie merytorycznej treści książki z istniejącą aktywnością bazą
jest zaakceptowana nowa treść. Aktywność należy ponownie dostosować do książki;
nie przywracamy starszego tekstu tylko dlatego, że istniejący YAML był do niego
dopasowany. Stabilny anchor zachowujemy wyłącznie wtedy, gdy nadal oznacza tę
samą koncepcję. Nie wolno używać istniejącego checkera jako argumentu za
pozostawieniem gorszej struktury merytorycznej.

## Niezależny rozwój aktywności

```text
dev
 ↓
activities/<temat>
 ↓
dev
```

Branch aktywności zawsze powinien rozpoczynać się z aktualnego `dev`. Jeżeli w
trakcie jego pracy `dev` otrzyma nowe zmiany treści dotyczące tych samych
stron, branch aktywności powinien przed integracją zsynchronizować się z
aktualnym `dev` i ponownie zweryfikować:

- ścieżki;
- `section_id`;
- treść poleceń;
- zgodność rozwiązania;
- checker.

## Rozwój infrastruktury

```text
dev
 ↓
infra/<temat>
 ↓
dev
```

Nie tworzymy nowych rendererów, checkerów ani mechanizmów „na zapas”. Zmiana
infrastruktury powinna wynikać z realnego przypadku użycia.

W szczególności obecne elementy backlogu:

- mismatch `activity.version`;
- ścisła walidacja nieznanych pól YAML;
- legacy `acknowledgement`;
- współdzielony `PyodideRuntime` dla wielu kart;
- `python_cases`;

nie są automatycznie częścią następnych etapów.

## Buildy w trybie CONTENT

Po większych zmianach model CONTENT powinien wykonać co najmniej:

```bash
mkdocs build
mkdocs build -f mkdocs.clean.yml
```

Jeżeli modyfikowana była strona posiadająca aktywności, interactive build jest
obowiązkowym testem kontraktu.

Clean build ma pozostać całkowicie pozbawiony:

- manifestu aktywności;
- `javascripts/interactive/`;
- `stylesheets/interactive.css`.

Po zmianie kodu hooków w `scripts/` należy całkowicie zrestartować
`mkdocs serve`, ponieważ długo działający proces może nadal używać wcześniej
zaimportowanego kodu hooka.

## Publikacja i warianty prezentacji

`master` nie oznacza „czystej książki”. Repozytorium posiada jeden zestaw
źródeł, a wariant prezentacji wybiera konfiguracja buildu:

```text
mkdocs.yml        → interactive
mkdocs.clean.yml  → clean
```

Kod infrastruktury interaktywnej może znajdować się również na `master`.
`master` oznacza stabilność wydania, a nie tryb prezentacji. Aktualizacja
`master` zostanie wykonana osobno po świadomej decyzji wydawniczej.
