# Organizacja pracy w repozytorium

Dokument jest autorytatywnym źródłem zasad organizacji pracy nad książką
i obowiązuje zarówno ludzi, jak i narzędzia AI. Zasady redakcyjne i konwencje
zapisu treści zawiera `CLAUDE.md`.

Książkę rozwijamy niezależnie od ćwiczeń: gałęzie książki zawierają wyłącznie
książkę i narzędzia służące jej przygotowaniu, a ćwiczenia interaktywne
powstają w osobnym projekcie na gałęzi `cwiczenia`, który przyjmuje książkę
jednokierunkowo i niczego do niej nie wnosi.

Przed rozpoczęciem pracy należy:

1. sprawdzić bieżącą gałąź i katalog roboczy (ang. *worktree*);
2. utworzyć gałąź roboczą `content/<temat>` albo `infra/<temat>` z aktualnego
   `dev` (`origin/dev` albo zsynchronizowanego lokalnego `dev`), chyba że autor
   wskazał inną gałąź; prace nad ćwiczeniami prowadzimy na gałęziach `fala/*`
   i `platform/*` utworzonych z `cwiczenia` (zasady w `kurs/README.md` na tej
   gałęzi);
3. nie rozszerzać zakresu zadania bez jawnej decyzji autora;
4. traktować `sources/**` jako materiał źródłowy autora: korzystamy z niego
   jako z odniesienia, ale go nie zmieniamy.

## Gałęzie i ich role

| Gałąź | Zawartość i rola | Przyjmuje zmiany z | Przekazuje zmiany do |
| --- | --- | --- | --- |
| `master` | wydania książki; przesuwana wyłącznie decyzją autora | `dev` | — |
| `dev` | książka i narzędzia jej przygotowania; punkt wyjścia codziennej pracy | `content/*`, `infra/*` | `master`, `sync/*` |
| `content/<temat>` | treść książki: strony, rozdziały, redakcja, nawigacja | `dev` | `dev` |
| `infra/<temat>` | narzędzia książki: skrypty w `scripts/`, konfiguracja budowania, zrzuty ekranu | `dev` | `dev` |
| `cwiczenia` | projekt ćwiczeń: książka z `dev` i warstwa ćwiczeń | `sync/*`, `fala/*`, `platform/*` | — |

Projekt ćwiczeń ma własny katalog roboczy `../python-notatki-cwiczenia`
i gałęzie robocze `fala/<NN-rozdzial>` (partie ćwiczeń), `platform/<temat>`
(hook, JavaScript, CSS, bramka kontrolna, CI, wydania) oraz `sync/<RRRR-MM-DD>`
— jedyne gałęzie, do których scalamy (ang. *merge*) `dev`. Jego zasady opisuje
plik `kurs/README.md` na gałęzi `cwiczenia`.

Slajdy wykładowe powstaną na osobnej gałęzi `slajdy` (katalog `slajdy/`), której
zmiany nie trafiają do `dev` ani `master`; tryb pracy na niej zostanie ustalony
osobno (zob. `DO_OMOWIENIA.md`).

## Kierunki przepływu

```text
content/*, infra/*  →  dev  →  master
dev  →  sync/*  →  cwiczenia  ←  fala/*, platform/*
```

- Gałęzie `content/*` i `infra/*` włączamy do `dev` po odbiorze przez autora,
  wyłącznie przez przewinięcie (ang. *fast-forward*, `git merge --ff-only`).
- `master` przesuwamy tylko na polecenie autora, również przez przewinięcie:
  `git push origin dev:master`.
- Historia `dev` i `master` jest liniowa: nie trafiają do nich commity
  scalające, dlatego `dev` nie scalamy do gałęzi roboczych książki.
- Książka trafia do projektu ćwiczeń wyłącznie przez gałąź `sync/*`, która
  scala `dev` z gałęzią `cwiczenia`.
- Zmian z gałęzi `cwiczenia`, `fala/*`, `platform/*` ani `sync/*` nigdy nie
  scalamy, nie przenosimy pojedynczymi commitami (ang. *cherry-pick*) ani nie
  kopiujemy do `dev` lub `master`.
- Nie przepisujemy historii gałęzi wypchniętych na `origin`: bez
  `git push --force`, bez przebudowy historii (ang. *rebase*) i bez poprawiania
  wypchniętych commitów (`--amend`). Gałąź `content/*` lub `infra/*`, której
  jeszcze nie wypchnięto, można przed włączeniem przebudować na aktualny `dev`;
  gałąź już wypchniętą, której nie da się przewinąć, odtwarzamy na aktualnym
  `dev` pod nową nazwą (np. `content/<temat>-2`).
- Błąd w treści książki zauważony podczas pracy nad ćwiczeniami poprawiamy na
  gałęzi `content/*` utworzonej z `dev`; do projektu ćwiczeń poprawka trafia
  przy kolejnej synchronizacji.

## Elementy niedozwolone na `dev` i `master`

- pliki warstwy ćwiczeń: `activities/**`, `scripts/build_activities.py`,
  `docs/javascripts/interactive/**`, `docs/stylesheets/interactive.css`,
  `tests/interactive/**`, `tests/test_build_activities.py`, `mkdocs.kurs.yml`,
  `kurs/**`, `.github/workflows/kurs.yml`;
- pliki dawnej warstwy ćwiczeń: `mkdocs.clean.yml`,
  `INTERACTIVE_SYSTEM_SPEC.md`;
- slajdy wykładowe: `slajdy/**`;
- atrybuty `data-activity-*` w plikach Markdown, w tym sloty aktywności;
- hook ćwiczeń (`build_activities`), obserwowanie katalogu `activities`
  (`watch`), CSS i JavaScript warstwy interaktywnej oraz klucz
  `presentation_mode` w `mkdocs.yml`.

Ćwiczenia wiążą się z nagłówkami przez identyfikatory, które MkDocs generuje
automatycznie; znaczniki dodaje dopiero budowanie projektu ćwiczeń. Nagłówki,
strony i odsyłacze zmieniamy wyłącznie ze względu na jakość książki; jeśli
zmiana zerwie powiązanie ćwiczenia z nagłówkiem, dostosowuje się projekt
ćwiczeń podczas synchronizacji. Jawny identyfikator `{#…}` pozostaje zwykłym
elementem książki, służącym jej własnym odsyłaczom.

## Zabezpieczenia

- `python scripts/check_book_only.py [<commit>]` sprawdza commit (domyślnie
  `HEAD`), a `python scripts/check_book_only.py --robocze` — katalog roboczy
  łącznie ze zmianami niezatwierdzonymi: kod 0 oznacza wyłącznie książkę,
  1 — naruszenia, 2 — błąd.
- `python scripts/install_git_hooks.py`, uruchamiany raz w głównym katalogu
  repozytorium, instaluje hooki Git wspólne dla wszystkich katalogów roboczych.
  `pre-push` przy wypychaniu do `dev` i `master` odrzuca commit scalający
  w wypychanym zakresie, nadpisanie historii oraz commit odrzucony przez
  strażnika w wersji z wypychanego commitu albo w wersji obecnej na gałęzi
  zdalnej. `pre-rebase` odmawia przebudowy historii gałęzi `cwiczenia`
  i `sync/*`. Opcja `--sprawdz` pokazuje stan hooków, `--usun` je usuwa.
  Hooków nie pomijamy (`--no-verify`).
- Reguły repozytorium na GitHubie uzupełnią je po stronie serwera, także dla
  zmian wprowadzanych w przeglądarce: zakaz nadpisywania historii i usuwania
  gałęzi `dev`, `master` i `cwiczenia`; wymóg liniowej historii `dev`
  i `master` jako reguła GitHuba czeka na potwierdzenie autora.

## Naprawa po przedostaniu się warstwy ćwiczeń na `dev`

Jeśli elementy warstwy ćwiczeń trafią na `dev` mimo zabezpieczeń, historii nie
przepisujemy, a warstwę usuwamy commitami naprzód:

1. Znaczniki w treści, wpisy w `mkdocs.yml` i pliki dawnej warstwy, jeśli
   się pojawiły, usuwa najpierw zwykły commit książki, tak aby każdy kolejny
   commit dawał się zbudować.
2. Osobny commit usuwa pliki warstwy ćwiczeń (pierwsza pozycja listy
   „Elementy niedozwolone na `dev` i `master`”) i nie zawiera żadnej innej
   zmiany. Nie cofamy (`git revert`) commitów, które obok warstwy wprowadziły
   zmiany książki.
3. Projekt ćwiczeń przyjmuje commit usuwający według procedury z
   `kurs/README.md`: najpierw scala commit go poprzedzający, a następnie
   rejestruje sam commit usuwający bez jego skutków (`git merge -s ours`),
   dzięki czemu pliki ćwiczeń na gałęzi `cwiczenia` pozostają nienaruszone.

## Odbiór prac

- Wynik każdej pracy (strony, rozdziału, narzędzia) odbiera autor. Commity
  tworzymy po akceptacji wyniku albo na polecenie autora, a do `dev` włączamy
  wyłącznie zaakceptowane zmiany.
- Do commitu dodajemy jawnie wskazane ścieżki (`git add <ścieżki>`), nigdy
  `git add -A` ani `git add .`: katalog roboczy może zawierać nieśledzone pliki
  innych gałęzi.
- Każda większa sesja kończy się raportem: zmienione i nowe pliki, wykonane
  kontrole z wynikami oraz sprawy otwarte. Sprawy odłożone zapisujemy
  w `DO_OMOWIENIA.md`.

## Budowanie, kontrola i podgląd

- `mkdocs build --strict` musi kończyć się bez ostrzeżeń; ostrzeżenie
  o brakującym pliku z nawigacji jest błędem do zgłoszenia. Przykłady
  wykonywalne sprawdzają `scripts/verify_page.py` i `scripts/verify_cells.py`.
- Przed oddaniem pracy uruchamiamy `scripts/check_book_only.py --robocze`,
  a przed włączeniem gałęzi do `dev` — `scripts/check_book_only.py` dla jej
  ostatniego commitu.
- Port 8000: podgląd książki autora (`mkdocs serve` w głównym katalogu, gałąź
  `dev`); narzędzia AI go nie uruchamiają ani nie zatrzymują.
- Port 8002: podgląd projektu ćwiczeń (katalog `../python-notatki-cwiczenia`),
  uruchamiany na czas odbioru i zatrzymywany po nim.
- Port 8001 zajmuje inny projekt; do kontroli doraźnych używamy portów od 8003
  i zatrzymujemy serwer po kontroli.

## Historia

Od 4 IX do 3 X 2026 warstwa ćwiczeń znajdowała się na `dev` (tag
`interactive-poc-v1`), a książkę i ćwiczenia rozdzielała konfiguracja budowania
(`mkdocs.clean.yml`); ostatni stan łączony zachowuje tag
`przed-rozdzieleniem-cwiczen`. Kroki w `plans/*.md` i `PLAN_ROZWOJU.md`
dotyczące `mkdocs.clean.yml`, testów warstwy interaktywnej i ograniczeń zmian
stron rozdziału 4 są nieaktualne.
