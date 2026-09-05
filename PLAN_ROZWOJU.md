# Plan rozwoju podręcznika „Python Notatki” — mapa rozdziałów 6–18

Dokument jest mapą dalszej książki, nie zadaniem do jednorazowej realizacji. Zaakceptowany przez autora 5 września 2026 (branch `content/book-expansion`). Stan odniesienia: Python 3.14.7 z Python Install Managerem.

## 0. Zasady realizacji

1. **Pracujemy rozdział po rozdziale.** Każdy rozdział przechodzi trzy etapy: szczegółowy projekt stron (do akceptacji; skondensowany zapis w `plans/NN-slug.md`), implementacja, osobny odbiór. Kolejny rozdział zaczynamy dopiero po odbiorze poprzedniego.
2. **Aktualnie w realizacji: rozdział 6. Funkcje.** Rozdziały 7–18 są zaplanowane, ale nie rozpoczęte.
3. **Nawigacja (`mkdocs.yml`) i spis na stronie głównej** zawierają wyłącznie rozdziały, które istnieją. Pozycje 7–18 dodajemy dopiero wraz z ich treścią.
4. **Kolejność pojęć jest bezwzględna.** Żaden przykład nie może wymagać mechanizmu formalnie wprowadzanego dopiero w późniejszym rozdziale. Funkcje wbudowane są dostępne zawsze; moduły biblioteki standardowej użyte już w rozdziałach 1–5 (`math`, `sys`, `copy`, `decimal`, `fractions`, `keyword`) można przywoływać ostrożnie; importowane dekoratory, `functools` i pakiety użytkownika dopiero od rozdziału 7.
5. **Hierarchia źródeł merytorycznych:** aktualna dokumentacja Pythona 3.14 (Language Reference, Standard Library Reference), właściwe PEP-y, oficjalne HOWTO i FAQ, dopiero potem wysokiej jakości źródła zewnętrzne jako pomocnicze. Materiały z `sources/` (PDF autora, wykłady, laboratoria) są źródłem programu kursu i przykładów, ale ich nieaktualności i błędy korygujemy. Blog, tutorial ani Stack Overflow nie mogą być jedynym źródłem twierdzenia o semantyce języka.
6. **Każdy przykład o deterministycznym wyniku uruchamiamy na referencyjnym interpreterze projektu.** Nie przepisujemy bez sprawdzenia wyjątków, `repr`, kodu bajtowego, introspekcji, adnotacji, generatorów i domknięć. Szczegóły CPythona oznaczamy jako szczegół implementacyjny, nie właściwość języka.
7. **Rozdziałów 1–5 nie remontujemy przy okazji.** Podczas pisania nowego rozdziału zmieniamy wcześniejsze strony tylko wtedy, gdy jest to bezpośrednio potrzebne do domknięcia zapowiedzi (np. zamiana komentarza `TODO: link` na odsyłacz). Pozostałe uzupełnienia z sekcji 6 to osobne etapy.
8. **Strony rozdziału 4 z aktywnościami** zmieniamy wyłącznie w tekście odsyłaczy: bez zmiany `section_id`, `data-activity-slot` i `activities/**`; po zmianie obowiązkowy interactive build (`mkdocs build`) oraz clean build (`mkdocs build -f mkdocs.clean.yml`).
9. **Git, GitHub i GitHub Classroom nie są rozdziałem podręcznika.** Materiały laboratoryjne na ten temat pozostają materiałem organizacyjnym kursu poza książką. Strony planu, które ich dotykają (struktura projektu, automatyzacja jakości), muszą obyć się bez założenia znajomości Gita albo odsyłać do materiałów kursu.
10. **Trwałym źródłem planu jest ten plik w repozytorium.** Pamięć narzędzi ani notatki sesji nie są źródłem projektu.

## 1. Punkt wyjścia (stan na 5 IX 2026)

- Książka kończy się na rozdziale 5 „Typy złożone” (ostatnia strona *Złożenia*, ostatnie pojęcie: wyrażenie generatorowe jako jednorazowy iterator). 30 plików Markdown, 3624 linie.
- W książce nie ma: definicji funkcji (jedna pomocnicza w `operatory.md`), klas, `try/except`, `with`, `open()`, systematycznego omówienia `import`, formatowania `%`/`str.format`.
- 20 zapowiedzi do domknięcia; dziesięć wskazuje „rozdział o funkcjach” (siedem komentarzy `TODO: link` w `lista.md`, `krotka.md`, `slownik.md`, `zlozenia.md`), pozostałe: debugger w VSC, `collections.deque`, NumPy, rozbudowa strony o narzędziach AI.
- Rozdziały 1–4 PDF autora są zintegrowane niemal w całości. Rozdziały 5–9 PDF (Funkcje, Przestrzenie nazw, Moduły i pakiety, Klasy, Dodatki: Print i Tkinter) to materiał na kolejne rozdziały; wykłady W04–W12 i laboratoria uzupełniają wyjątki, pliki, testy, collections, NumPy/pandas, wątki.

## 2. Strategia układu

Kręgosłupem pozostaje porządek topologiczny planu zbiorczego: 6 Funkcje → 7 Moduły → 8 Wyjątki → 9 Wejście/wyjście → 10–12 blok obiektowy → 13 Wydajność → 14 NumPy (Git i GitHub poza książką jako materiał organizacyjny kursu). Jedna zmiana strukturalna: rozdziały bez laboratorium idą na koniec — 15 Współbieżność (lab11), 16 Warsztat programisty (z posłowiem „Co dalej”), 17 Pandas, 18 tkinter — więc kolejność tworzenia pokrywa się z numeracją, a ewentualne odłożenie 17–18 nie zostawia luk ani nie łamie odsyłaczy z rozdziałów 1–5. Podział rdzeń/„dla dociekliwych” utrzymany (itertools, animacje, cykl życia obiektu, deskryptory, wzorce, metaprogramowanie, przyspieszanie). Aparat redakcyjny: sources z podziałem PDF/DOPISANE, modernization jako checklista, 90–220 linii i ≤6 H2 na stronę (dalsze pozycje contents to H3; wyjątek: projekt tkinter ≤300 linii), index „wstęp, ---, ## W tym rozdziale”, etykiety nav z półpauzą (bez dwukropka), admonition „Powiązane laboratorium N”, sekcja „Ściąga” (tabela składnia → znaczenie) w index rozdziałów 6, 7, 8. Wykluczenia: quizy i zadania → CONTENT HANDOFF (treść jako warningi); listy modeli Copilot → docs.github.com; pakiet decorator, multipledispatch, deepreload, triki W04 s. 45, threading._shutdown, eval w wielomianie, testy z requests, narzędzia historyczne (jedno zdanie), TIOBE, W12 s. 27–28 i 33 (s. 29–32 → co-dalej.md), lab8 duplikat MRO; W05 pip/venv/match → uzupełnienia 1 i 4. Nowe wykluczenie: moduł re jako osobny temat (brak wykładu źródłowego; lab1 używa regexu tylko jako materiału dla Copilota) — wiersz w tabeli stdlib i admonition w 7; pełna strona do rozważenia w następnym wydaniu. Liczby pomiarowe wyłącznie z 3.14.7.

Zmiany po weryfikacji: limit rekurencji w rozdz. 6 opisany prozą, odczyt i zmiana przez moduł sys odłożone do rozdz. 7; korekty PDF: map/filter jako iteratory, wrapper bez return, property jako klasa-deskryptor, __new__ bez return, sys.__dict__/import builtins; lambda z pełną gramatyką argumentów; pakiety bez klas i importy z „.”; assert przeniesiony do 7; własne wyjątki w 8 tylko jako zapowiedź; redirect_stdout wyłącznie w 9; benchmark NumPy w 14; __init_subclass__ tylko w metaprogramowaniu; __slots__ w rdzeniu 10; usunięto duplikaty Singleton/timer/tabela PEP/annotationlib/.gitignore/sekwencje ucieczki; Warsztat ma 5 podstron; Matplotlib i okna tkinter podzielone na dwie strony; wzorce projektowe jako „dla dociekliwych”; uzupełnienia z wykładów (match z klasami danych, praktyki OOP, __slots__ z dziedziczeniem, wartość yield from, filterfalse/receptury, mock, triki NumPy, Decimal/Fraction, eksperyment lab3, sortowanie importów, callback bez try/except); aktualność: Tk 9.0 od 3.14.6, tearoff (TIP 161), ChainedAssignmentError jako ostrzeżenie, forkserver bez macOS, runtime_checkable 3.8, singledispatch 3.7/3.8, „Did you mean” tylko w tracebacku, seaborn 0.13.2, konkretne wersje bibliotek, identyfikatory rozszerzeń VSC, pomiary __slots__/getrefcount/dis.

## 3. Spis rozdziałów 6–18

| Nr | Rozdział | Katalog | Priorytet | Podstron | Rozmiar | Powiązane laboratorium | Status |
|---|---|---|---|---|---|---|---|
| 6 | 6. Funkcje | `docs/06-funkcje/` | wysoki | 7 | index + 7 stron, ok. 1150–1250 linii | lab4, lab6, lab8 | w realizacji |
| 7 | 7. Moduły, pakiety i biblioteka standardowa | `docs/07-moduly/` | wysoki | 6 | index + 6 stron, ok. 900–1000 linii | lab3 | zaplanowany |
| 8 | 8. Wyjątki i zarządzanie zasobami | `docs/08-wyjatki/` | wysoki | 6 | index + 6 stron, ok. 800–900 linii | — | zaplanowany |
| 9 | 9. Wejście, wyjście i pliki | `docs/09-wejscie-wyjscie/` | wysoki | 7 | index + 7 stron, ok. 1000–1100 linii | lab2 | zaplanowany |
| 10 | 10. Klasy i obiekty | `docs/10-klasy/` | wysoki | 5 | index + 5 stron, ok. 850–950 linii | lab5 | zaplanowany |
| 11 | 11. Model danych — metody specjalne i protokoły | `docs/11-model-danych/` | średni | 5 | index + 5 stron, ok. 750–850 linii | lab5 | zaplanowany |
| 12 | 12. Programowanie obiektowe — mechanizmy zaawansowane | `docs/12-oop-zaawansowane/` | średni | 5 | index + 5 stron, ok. 850–950 linii | lab7, lab8 | zaplanowany |
| 13 | 13. Wydajność i optymalizacja | `docs/13-wydajnosc/` | średni | 3 | index + 3 strony, ok. 450–520 linii | zapowiedź lab6 | zaplanowany |
| 14 | 14. NumPy i Matplotlib | `docs/14-numpy-matplotlib/` | średni | 5 | index + 5 stron, ok. 800–900 linii | lab9–10 | zaplanowany |
| 15 | 15. Współbieżność — wątki, procesy i GIL | `docs/15-wspolbieznosc/` | średni | 4 | index + 4 strony, ok. 600–700 linii | lab11 | zaplanowany |
| 16 | 16. Warsztat programisty i dalsza droga | `docs/16-warsztat/` | średni | 5 | index + 5 stron, ok. 800–900 linii | — | zaplanowany |
| 17 | 17. Pandas i analiza danych | `docs/17-pandas/` | niski | 5 | index + 5 stron, ok. 800–900 linii | — (dodatek) | zaplanowany |
| 18 | 18. Interfejs graficzny tkinter | `docs/18-tkinter/` | niski | 7 | index + 7 stron, ok. 1050–1150 linii | — (dodatek) | zaplanowany |

Poza książką: **Git, GitHub i GitHub Classroom** (materiał organizacyjny kursu; źródła: `sources/github_classroom.pdf`, W12 sl. 15–19, lab3). Rozdziały 17–18 to dodatki bez laboratorium i stoją na końcu.

## 4. Rozdziały

### 6. Funkcje (`docs/06-funkcje/`)

**Cel dydaktyczny.** Czytelnik definiuje i dokumentuje funkcje, opanowuje gramatykę argumentów, zasięg nazw i przekazywanie referencji, traktuje funkcje jako obiekty (wywołania zwrotne, wyrażenie lambda, funkcja klucza, `map()`/`filter()` jako iteratory), stosuje rekurencję ze świadomością limitu, pisze funkcje generatorowe oraz dekoratory zbudowane wyłącznie z własnych funkcji. Zakres lab4, lab6, lab8. Rozdział obywa się bez nowych modułów: `functools`, `itertools`, `operator` oraz odczyt i zmiana limitu rekurencji przez `sys` są odłożone do rozdziału 7 (decyzja autora z 5 IX 2026).

**Główne tematy.**
- def, return (None, wczesny return, wiele wartości jako pakowanie krotki), docstring i help() (PEP 257), funkcja jako obiekt
- adnotacje parametrów i wartości zwracanej według Pythona 3.14: brak sprawdzania typów w czasie wykonania, domyślnie leniwa ewaluacja (PEP 649/749) pokazana zachowaniem programu; introspekcja adnotacji (`annotationlib`, `__annotate__`) odłożona
- parametr a argument; argumenty pozycyjne i nazwane; wartości domyślne i moment ich ewaluacji, pułapka modyfikowalnej wartości domyślnej i idiom None; przekazywanie referencji (modyfikacja w miejscu a ponowne przypisanie)
- `*args`/`**kwargs` jako pakowanie, rozpakowanie `*` i `**` w wywołaniu, parametry tylko pozycyjne `/` i tylko nazwane `*` (PEP 570, PEP 3102), pełna kolejność parametrów, typowe komunikaty TypeError
- przestrzenie nazw i zasięgi (skrót LEGB jako zwyczajowy), UnboundLocalError, funkcje zagnieżdżone i zmienne wolne, global i nonlocal, domknięcia, późne wiązanie (przykłady wyłącznie przez def)
- funkcje pierwszej klasy, wywołania zwrotne, tablica rozdzielcza, callable() i iter(obiekt_wywoływalny, wartownik), wyrażenie lambda jako wyrażenie (PEP 8, E731), funkcja klucza w sorted/min/max, `map()` i `filter()` jako iteratory klasy map/filter (nie generatory), `map(strict=True)` (3.14)
- rekurencja: przypadek bazowy i krok rekurencyjny, silnia, Fibonacci a iteracja (zliczanie wywołań), struktury zagnieżdżone, RecursionError i limit rekurencji prozą (kod z `sys` w rozdz. 7), eliminacja rekurencji ogonowej „dla dociekliwych”
- generatory (rdzeń): funkcja generatorowa → obiekt generatora → yield → next() → zawieszenie i wznowienie → jednorazowość → leniwość (pokazana zachowaniem programu, bez pomiarów pamięci) → generator nieskończony → potoki → yield from; rozróżnienie od wyrażenia generatorowego i od iteratorów map/filter; StopIteration.value, send(), throw(), close() poza rdzeniem
- dekoratory bez `functools`: funkcja jako obiekt → funkcja przyjmująca funkcję → funkcja zwracająca funkcję → domknięcie → ręczne przypisanie wrappera → składnia `@`; funkcja opakowująca (ang. *wrapper*, w kodzie `opakowana`) z `*args`/`**kwargs` i return; rejestrowanie, zliczanie (nonlocal), memoizacja słownikiem w domknięciu; utrata `__name__`/`__doc__` pokazana prostą funkcją opakowującą (`functools.wraps` tylko jako zapowiedź, bez ręcznego kopiowania atrybutów); składanie dekoratorów; fabryka dekoratorów „dla dociekliwych”; bez dekoratora mierzącego czas i bez walidacji przez raise

**Zależności od wcześniejszych rozdziałów.**
- 3 (nazwa jako referencja, adnotacje zmiennych, id/del, type/isinstance)
- 4 (iteratory iter/next/StopIteration → generatory; for/while/break)
- 5 (pakowanie/rozpakowywanie → `*args`; słownik → `**kwargs`; key w sorted; wyrażenie generatorowe; kopie i referencje → pułapka wartości domyślnej)

**Zapowiedzi i luki, które rozdział domyka.**
- 1, 5 docstring/PEP 257 (definiowanie-funkcji)
- 6 def/return/lambda/yield/global/nonlocal (odpowiednie strony; jeden uzgodniony tekst odsyłacza)
- 9 return w funkcji (definiowanie-funkcji)
- 10, 20 yield, map(), filter() (funkcje-generatorowe, funkcje-jako-obiekty)
- 12 rekurencja, limit rekurencji, eliminacja rekurencji ogonowej (rekurencja; kod `sys` świadomie odłożony do rozdz. 7)
- 13 iter(obiekt_wywoływalny, wartownik), callable (funkcje-jako-obiekty)
- 14 własne funkcje klucza, lambda (funkcje-jako-obiekty)
- 16, 17, 18 `*args`, rozpakowanie `*`, `**kwargs` (argumenty-i-parametry)

**Podział na strony.**

| Plik | Etykieta nav / H1 | Zawartość |
|---|---|---|
| `06-funkcje/index.md` | Wprowadzenie | Funkcja jako jednostka kodu i obiekt; odsyłacze do rozdz. 3–5; zapowiedź rozdz. 7; ---; ## W tym rozdziale (7 podstron). |
| `06-funkcje/definiowanie-funkcji.md` | Definiowanie funkcji | Anatomia definicji i wywołania; Instrukcja return; Docstring i funkcja help(); Adnotacje w sygnaturze (semantyka 3.14 prozą i zachowaniem, bez introspekcji); Funkcja jako obiekt; Konwencje zapisu funkcji (krótkie zakończenie). |
| `06-funkcje/argumenty-i-parametry.md` | Argumenty i parametry | Parametr a argument; Wartości domyślne (H3: pułapka modyfikowalnej wartości domyślnej); Przekazywanie referencji; Zmienna liczba argumentów (H3: `*args` i `**kwargs`, rozpakowanie w wywołaniu); Parametry tylko pozycyjne i tylko nazwane (na końcu kompaktowa tabela komunikatów błędów). |
| `06-funkcje/zasieg-nazw-i-domkniecia.md` | Zasięg nazw i domknięcia | Przestrzenie nazw i zasięgi (H3: przestrzeń wbudowana i przesłanianie nazw; krótka nota o globals()/locals()); Nazwy lokalne i UnboundLocalError; Funkcje zagnieżdżone i zmienne wolne; Deklaracje global i nonlocal; Domknięcia (krótka nota o `__closure__`); Pułapka późnego wiązania. |
| `06-funkcje/funkcje-jako-obiekty.md` | Funkcje jako obiekty | Funkcje pierwszej klasy; Obiekty wywoływalne (wartownik z licznikiem w domknięciu); Wyrażenie lambda; Funkcja klucza w sorted, min i max; Funkcje map() i filter() (`map(strict=True)` jako nota 3.14). |
| `06-funkcje/rekurencja.md` | Rekurencja | Przypadek bazowy i krok rekurencyjny (H3: funkcja pomocnicza w funkcji zewnętrznej); Rekurencja a iteracja — ciąg Fibonacciego (zliczanie wywołań w domknięciu); Rekurencja na strukturach zagnieżdżonych; Limit rekurencji i RecursionError; Dla dociekliwych: eliminacja rekurencji ogonowej. |
| `06-funkcje/funkcje-generatorowe.md` | Funkcje generatorowe | Funkcja generatorowa a obiekt generatora; yield i next(): zawieszenie i wznowienie wykonania; Jednorazowość i leniwość (zachowanie programu, bez pomiarów pamięci); Generatory nieskończone; Potoki generatorów (H3: delegacja yield from). |
| `06-funkcje/dekoratory.md` | Dekoratory | Od funkcji do dekoratora (pięć kroków progresji); Anatomia dekoratora; Przykłady zastosowań (rejestrowanie, zliczanie, memoizacja); Tożsamość funkcji opakowanej; Wiele dekoratorów i kolejność; Dla dociekliwych: dekorator z argumentami. |

Szczegółowy projekt stron (kolejność sekcji, zależności pojęciowe, kluczowe przykłady, źródła, odsyłacze do domknięcia, elementy odłożone, checklista weryfikacyjna): `plans/06-funkcje.md`.

**Istotne materiały źródłowe.**
- PDF: PythonNotatki.txt 1988–2258 (s. 59–63: def, docstring, adnotacje, fib, domyślne, domknięcia, `*args`/`**kwargs`, / i *); 2260–2372 (dekorator, wraps — wraps tylko zapowiedź); 2374–2681 (lambda, dis, map/filter/reduce — dis i reduce odłożone); 2683–2839 (s. 70–76: LEGB, builtins, global/nonlocal — kod w zrzutach, odtworzony i uruchomiony)
- DOPISANE: Wyklad_04.txt sl. 3–44, 46–48 (sl. 45 wykluczony; sl. 49 „ściąga” i sl. 50 „Fibonacci sześcioma technikami” pominięte)
- DOPISANE: lab4.txt sl. 1–7, lab6.txt sl. 1–2, lab8.txt sl. 1 (fib, `__defaults__`, memoizacja, / i *, LEGB; lru_cache/wraps → rozdz. 7)
- DOPISANE: Wyklad_08.txt sl. 18–24 (yield, potoki, yield from; send/throw/close i return w generatorze poza rdzeniem); Wyklad_03.txt sl. 15, 35, 37, 42; Wyklad_02.txt sl. 21; Wyklad_01.txt sl. 24

**Modernizacje i korekty względem źródeł (Python 3.14).**
- PEP 649/749: adnotacje ewaluowane leniwie (opis prozą i zachowaniem; introspekcja przez `annotationlib` odłożona); PEP 667: locals() jako migawka (3.13); SyntaxError o domyślnych w brzmieniu od 3.12; limit rekurencji od 3.12 dotyczy tylko ramek Pythona; tracebacki w stylu 3.14 (w tym prefiks `__main__.` przy błędnym rozpakowaniu `**`)
- BŁĘDY PDF: map/filter to iteratory klasy map/filter, nie generatory; wrapper bez `return f(...)` zwraca None; komentarz „dla lambda” przy identycznych tracebackach; sys.__dict__ z 3.8 pominięty; `__builtins__.list` → del list; locals() „kopiuje obiekty” → migawka słownika
- W04: „+= dla list tworzy nowy obiekt” — nieprawda (działa w miejscu); czas fib(40) zawyżony — nie cytujemy; callback ze sl. 42 bez try/except; bytecode ze sl. 46 (dis) odłożony do rozdz. 13
- Decyzja autora: `functools` (cache, wraps, reduce, partial), `itertools`, `operator` i kod `sys.getrecursionlimit()` poza rozdziałem 6 — rozdz. 7; `map(strict=True)` (3.14) jako krótka nota; liczby (zliczanie wywołań, granica rekurencji) zmierzone na 3.14.7 i oznaczone jako szczegóły CPythona; bez pomiarów pamięci `sys.getsizeof()`; liczniki diagnostyczne przez domknięcie z nonlocal, nie przez global
- Nazwy plików bez kolizji ze stdlib (test.py); pliki i open() poza rozdziałem (rozdz. 9)

**Priorytet:** wysoki. **Szacunek rozmiaru:** index + 7 stron, ok. 1200–1500 linii (150–225 linii na stronę). **Status:** w realizacji — projekt stron zaakceptowany 5 IX 2026 (`plans/06-funkcje.md`), implementacja strona po stronie.

### 7. Moduły, pakiety i biblioteka standardowa (`docs/07-moduly/`)

**Cel dydaktyczny.** Czytelnik rozumie mechanizm importu, zamienia skrypt w program z main() i argumentami wiersza poleceń, organizuje kod w pakiety i projekt src/tests z pierwszymi testami pytest oraz instrukcją assert (lab3), poznaje collections i — dla dociekliwych — itertools.

**Główne tematy.**
- moduł, formy import/from/as, __all__, PEP 8 i sortowanie importów (ruff I), import w funkcji
- sys.path, -P/PYTHONSAFEPATH, PYTHONPATH (separator ; i :), site-packages ↔ venv, sys.modules, reload, __pycache__
- __name__ == '__main__', main(), sys.argv, argparse 3.14, sys.exit, python -m
- pakiety, __init__.py (zawsze w pakiecie regularnym), subpakiety, importy względne . i .., PEP 420
- src layout, pyproject.toml, pytest podstawy, assert (AssertionError), float a Decimal
- collections: deque, Counter, defaultdict, namedtuple; mapa stdlib (w tym re jako wzmianka)
- itertools (dla dociekliwych): nieskończone, chain/islice, filterfalse, groupby, kombinatoryka, pairwise/batched, receptury

**Zależności od wcześniejszych rozdziałów.**
- 1 (pip, venv, site-packages, sys.path)
- 2 (opcja -m, uruchamianie skryptu)
- 6 (main(), lambda dla groupby, generatory, callable dla defaultdict, dekorator w osobnym module)

**Zapowiedzi i luki, które rozdział domyka.**
- 15 collections.deque
- 6 import/from/as/assert
- luka: import bez omówienia, if __name__, sys.argv/argparse (PDF 2007–2020), pytest lab3, Counter/defaultdict/namedtuple, itertools (W03 s. 43)

**Podział na strony.**

| Plik | Etykieta nav / H1 | Zawartość |
|---|---|---|
| `07-moduly/index.md` | Wprowadzenie | Od pliku do projektu; odsyłacze do 1 i 6; ---; ## W tym rozdziale (6 podstron); nota „Powiązane laboratorium 3”; ## Ściąga (tabela z W05 sl. 42, część modułowa). |
| `07-moduly/import.md` | Moduły i instrukcja import | Czym jest moduł (rozszerzenia: _sqlite3); Formy import (H3: kolejność PEP 8, ruff --select I → 16); Gdzie interpreter szuka modułów (sys.path Windows/3.14, -P, PYTHONPATH); Moduł jako przestrzeń nazw (dir, __file__, docstring); Dla dociekliwych: sys.modules, reload, __pycache__; Pułapki (test.py, import cykliczny). |
| `07-moduly/skrypt-jako-program.md` | Skrypt jako program | __name__ i "__main__" (dwa pliki, nie samoimport); Konwencja main(); sys.argv i --help z __doc__; argparse (suggest_on_error, kolor 3.14); python -m i __main__.py; Kody wyjścia (sys.exit). |
| `07-moduly/pakiety.md` | Pakiety | Katalog jako pakiet, __init__.py zawsze (pkg/md1..md3 z PDF z funkcjami zamiast K1..K3, drzewo .text); __all__ pakietu i import *; Subpakiety i nazwa kropkowa; Importy względne (from . import x, from .m import f, ..; błąd „attempted relative import”, python -m); Dla dociekliwych: PEP 420 i trzy wyniki importu. |
| `07-moduly/struktura-projektu.md` | Struktura projektu i pierwsze testy | Układ src/<pakiet>/, tests/, pyproject.toml (.gitignore jednym zdaniem — zakłada Git — do rozstrzygnięcia przy projekcie rozdziału; Git nie jest tematem książki); python -m pip install -e .; Instrukcja assert (AssertionError, dlaczego pytest z niej korzysta; -O w 8); pytest (instalacja, test_*, -q -v -s); Refaktoryzacja do funkcji testowalnej (lab2 → lab3); Porównania float (0.1+0.2+0.3: float a Decimal, round, isclose, approx; NumPy → 14); zapowiedź raises (8), fixtures (16). |
| `07-moduly/biblioteka-standardowa.md` | Biblioteka standardowa i collections | Mapa modułów (tabela moduł → przeznaczenie → rozdział; wiersz re z admonition „dla dociekliwych”: re.search/sub, r'' → typy-proste); deque (domyka lista.md:490, O(1)); Counter (most_common); defaultdict (a setdefault); namedtuple (zapowiedź NamedTuple/dataclass w 12); functools/operator przypomnienie. |
| `07-moduly/itertools.md` | Moduł itertools (dla dociekliwych) | count/cycle/repeat i islice; chain/compress/takewhile/dropwhile/filterfalse; groupby (wymaga sortowania); product/permutations/combinations; accumulate/starmap/tee, pairwise, batched(strict) 3.13 z recepturą chunked (iter+islice+walrus), zip_longest; Receptury z dokumentacji i more-itertools; Kompas itertools; potok na danych w pamięci (wersja plikowa w 9). |

**Istotne materiały źródłowe.**
- PDF: PythonNotatki.txt 2841–3185 (s. 76–84: moduły, sys.path, import, __all__, __name__, reload, pakiety, importy względne, PEP 420); 2007–2020 (sys.argv)
- DOPISANE: Wyklad_05.txt sl. 3–13, 31–36, 40, 42–43, 46; lab3.txt sl. 1–3, 5–6; lab2.txt sl. 6–8 (baza refaktoryzacji)
- DOPISANE: Wyklad_08.txt sl. 25–31, 40 (itertools, chunked, receptury); Wyklad_03.txt sl. 14–15, 22–23, 31, 43; Wyklad_01.txt sl. 32

**Modernizacje i korekty względem źródeł (Python 3.14).**
- test.py → narzedzia.py; re „w C” → _sqlite3; timeit.timeit() jako zegar → perf_counter; ścieżki C:\tmp → neutralne z venv i Install Managerem
- moduł imp usunięty (3.12); deepreload pominięte; URL PEP 420 na peps.python.org; wszystkie wydruki dir() odtworzyć na 3.14 ze skryptu w terminalu (zestaw dunder zależy od środowiska i PEP 649/749), nie kopiować z PDF
- SyntaxError „import * only allowed at module level”; „from pkg import * bez __all__ → nic” uściślić (moduły już zaimportowane w __init__ są widoczne)
- src layout + pyproject (PEP 621); python -m pytest; pytest 9.1.1 na 3.14; goły pip → python -m pip
- argparse 3.14 (suggest_on_error, kolor); python -m json; batched(strict=True) 3.13

**Priorytet:** wysoki. **Szacunek rozmiaru:** index + 6 stron, ok. 900–1000 linii.

### 8. Wyjątki i zarządzanie zasobami (`docs/08-wyjatki/`)

**Cel dydaktyczny.** Czytelnik obsługuje i zgłasza wyjątki widoczne od rozdziału 3 tylko w tracebackach, dobiera styl EAFP/LBYL, testuje wyjątki w pytest, stosuje with i contextlib.contextmanager (bez klas) oraz zyskuje warsztat diagnostyczny: traceback, debugger VSC (zapowiedź z rozdz. 1) i logging.

**Główne tematy.**
- anatomia tracebacku 3.14 (podpowiedzi „Did you mean” tylko w tracebacku, nie w str(e)), tabela najczęstszych wyjątków
- try/except/else/finally, PEP 758, PEP 765, as e, kolejność
- raise, raise from/from None, add_note, hierarchia BaseException; assert a -O i zakaz walidacji danych
- własne wyjątki — wyłącznie zapowiedź (admonition, pełnia w 10)
- EAFP a LBYL, antywzorce gołego except, pytest.raises
- with, składnia nawiasowa 3.10, protokół pojęciowo, @contextmanager, suppress/nullcontext/ExitStack
- traceback, debugger VSC (ms-python.debugpy, F5, pułapki, Variables/Call Stack), breakpoint()/pdb
- logging: poziomy, basicConfig(encoding), log.exception, leniwe %s (odsyłacz do 9)

**Zależności od wcześniejszych rozdziałów.**
- 3–5 (ValueError przy int(input()), KeyError/get, IndexError, StopIteration)
- 6 (propagacja przez stos; generatory + dekoratory → @contextmanager; timer)
- 7 (pytest i assert → raises; import contextlib/logging/traceback)

**Zapowiedzi i luki, które rozdział domyka.**
- 2 debugowanie w VSC (diagnostyka.md)
- 6 try/except/finally/raise/with/as
- 4 Zen: „Errors should never pass silently”
- luka: try/except nieomówione; EAFP/LBYL (W03 s. 19); with; logging

**Podział na strony.**

| Plik | Etykieta nav / H1 | Zawartość |
|---|---|---|
| `08-wyjatki/index.md` | Wprowadzenie | Błędy jako obiekty; retrospekcja tracebacków z 3–6; ---; ## W tym rozdziale (6 podstron); ## Ściąga (tabela z W05 sl. 42, część o wyjątkach i with). |
| `08-wyjatki/obsluga-wyjatkow.md` | Obsługa wyjątków | Program z obsługą i bez; Anatomia tracebacku 3.14 (pełny blok .no-copy; str(e) bez sugestii); Tabela wyjątków z odsyłaczami; try/except (krotka typów, PEP 758 z zaleceniem nawiasów, as e); else i finally (PEP 765); Walidacja wejścia (while z try, walrus, isdigit jako LBYL). |
| `08-wyjatki/zglaszanie-wyjatkow.md` | Zgłaszanie wyjątków | raise i propagacja; Hierarchia (drzewo .text z docs 3.14, ExceptionGroup, KeyboardInterrupt); Ponowne zgłoszenie i łańcuchy (from, from None, add_note); assert (-O, nie do walidacji; wprowadzony w 7); Przykład: liczby rzymskie z walidacją przez ValueError; nota „Zapowiedź: własne typy wyjątków” → ../10-klasy/dziedziczenie.md. |
| `08-wyjatki/styl-i-testowanie.md` | Styl obsługi błędów i testy wyjątków | EAFP a LBYL (słownik, zero-cost 3.11); Antywzorce (gołe except, pass, szeroki try); Zasięg bloku try; pytest.raises z match; Dla dociekliwych: ExceptionGroup i except*. |
| `08-wyjatki/with-i-contextlib.md` | Instrukcja with i menedżery kontekstu | Problem zasobów (try/finally); with (open() jako czarna skrzynka z encoding — szczegóły w 9; wiele zasobów, nawiasy 3.10); Protokół pojęciowo (klasa w 11); contextlib.contextmanager (timer z try/finally, TemporaryDirectory); Dla dociekliwych: suppress, chdir, nullcontext, ExitStack (redirect_stdout → 9). |
| `08-wyjatki/diagnostyka.md` | Diagnostyka — traceback i debugger | Czytanie tracebacku od dołu, moduł traceback; Debugger w VSC (rozszerzenie Python Debugger ms-python.debugpy, F5, pułapki warunkowe, Variables/Watch/Call Stack — stos rekurencji z 6, launch.json) — domyka konfiguracja.md:136; breakpoint() i pdb; nota sys.remote_exec (PEP 768); <!-- TODO: screenshot ×3 --> + ZRZUTY.md. |
| `08-wyjatki/logging.md` | Logowanie zamiast print | Dlaczego nie print; getLogger, basicConfig (level, format, encoding); poziomy DEBUG–CRITICAL; log.exception w except; leniwe formatowanie %s (nota: wieloznacznik % → 9/formatowanie.md); logowanie do pliku (odsyłacz 9) i z wątków (15). |

**Istotne materiały źródłowe.**
- DOPISANE: Wyklad_05.txt sl. 18–30, 36–37, 41–42, 45 (wyjątki, raise, hierarchia, walidacja, with, EAFP, logging, ExceptionGroup, ściąga)
- DOPISANE: Wyklad_08.txt sl. 7, 33–36 (with, contextlib); Wyklad_12.txt sl. 5 (raises); Wyklad_03.txt sl. 19, 33; Wyklad_07.txt sl. 23–24 (EAFP)
- DOPISANE: python_thread.txt sl. 10–11, 18 (logging, with); docs.python.org exceptions 3.14, PEP 758/765; docs VSC debugging (materiał własny)
- PDF: brak (tylko tracebacki 728, 1541–1547, 1594–1596, 1868–1870; fib z -1 w 2050–2070 jako kontrprzykład)

**Modernizacje i korekty względem źródeł (Python 3.14).**
- PEP 758 (except A, B bez nawiasów; z as nadal nawiasy — SyntaxError), PEP 765 (SyntaxWarning w finally), add_note 3.11, zero-cost 3.11, drzewo z ExceptionGroup
- open() zawsze z encoding; usunąć gołe except z W05 s. 45; timer W08 z try/finally; /tmp → tempfile
- logging.basicConfig(encoding=) 3.9; %s zamiast f-stringów; nazwa rozszerzenia: Python Debugger (ms-python.debugpy)
- tracebacki i podpowiedzi „Did you mean” odtworzyć na 3.14.7 jako pełne bloki; przykłady 8 zgłaszają wyłącznie wyjątki wbudowane

**Priorytet:** wysoki. **Szacunek rozmiaru:** index + 6 stron, ok. 800–900 linii.

### 9. Wejście, wyjście i pliki (`docs/09-wejscie-wyjscie/`)

**Cel dydaktyczny.** Rozdział przekrojowy: pełne formatowanie tekstu, funkcja print i strumienie z buforowaniem (PDF Dodatki, lab2), pliki tekstowe z jawnym kodowaniem na Windows, typ bytes, pathlib oraz CSV i JSON; animacje w terminalu jako strona projektowa dla dociekliwych.

**Główne tematy.**
- mini-język formatu, !r/!s/=, zagnieżdżone pola, str.format, %, pprint; t-stringi PEP 750
- pełna sygnatura print, sep/end/file/flush, znaki sterujące \r \b \a \t, stdin/stdout/stderr, buforowanie, -u, redirect_stdout, input()
- animacje: \r, \b, ANSI, os.system, znaki blokowe Unicode
- open(): tryby, read/readline/iteracja, write, newline; kodowanie cp1250 a UTF-8, utf-8-sig, errors, EncodingWarning, PEP 686
- bytes/bytearray/memoryview, encode/decode, rb/wb, struct, io.StringIO/BytesIO
- pathlib: Path, /, glob/rglob, mkdir, read_text, copy/move/info 3.14; os/shutil/tempfile
- csv (newline='', ';', utf-8-sig), json (ensure_ascii=False, mapowanie typów, python -m json)

**Zależności od wcześniejszych rozdziałów.**
- 2–3 (print/input, f-stringi, metody str, sekwencje ucieczki \n i r'', ord/chr, katalog typów z bytes)
- 6–7 (generatory — plik jako iterator, iter(f.readline, ''); import os/sys/pathlib/csv/json; itertools w potoku)
- 8 (with, FileNotFoundError/UnicodeDecodeError, ExitStack)

**Zapowiedzi i luki, które rozdział domyka.**
- 7 f-stringi z pełnym mini-językiem
- luka: pełna sygnatura print (W01 s. 23, PDF PRINT, lab2); formatowanie %/str.format (PDF 788–789); pliki/open; bytes; pathlib/json (W05 s. 38–39)

**Podział na strony.**

| Plik | Etykieta nav / H1 | Zawartość |
|---|---|---|
| `09-wejscie-wyjscie/index.md` | Wprowadzenie | Od napisu do pliku; strumienie jako wspólny model; skąd sekcja PRINT (Dodatki PDF); ---; ## W tym rozdziale (7 podstron); nota „Powiązane laboratorium 2”. |
| `09-wejscie-wyjscie/formatowanie.md` | Formatowanie tekstu | F-stringi przypomnienie; Mini-język (schemat .text; H3: wyrównanie, znak, separatory, precyzja, typy, zagnieżdżone pola); Wypisywanie tabel; format() i str.format(); Operator % (kod zastany, logging z 8); Dla dociekliwych: t-stringi (string.templatelib), pprint. |
| `09-wejscie-wyjscie/print-i-strumienie.md` | Funkcja print i strumienie | Pełna sygnatura print (.text; domyka konsola-w-praktyce.md); Znaki sterujące terminala (\r \b \a \t; \n, r'' i \u → typy-proste); Strumienie standardowe i przekierowanie (zakładki PowerShell / Git Bash); Buforowanie (flush, -u, PYTHONUNBUFFERED w zakładkach, stderr od 3.9; testy w skrypcie z terminala, nie w REPL); Argument file i contextlib.redirect_stdout (obiekt z write() → 11); input() (EOFError). |
| `09-wejscie-wyjscie/animacje-w-terminalu.md` | Animacje w terminalu (dla dociekliwych) | Zasada (\r, end='', flush, sleep); Spinner i maszyna do pisania; Odbijająca się piłeczka; Czyszczenie ekranu (os.system a ANSI \033[2J\033[H — korekta tezy PDF); Animacje wieloliniowe (U+2588/2580/2584/2593); ograniczenia terminala/REPL. |
| `09-wejscie-wyjscie/pliki-tekstowe.md` | Pliki tekstowe | open() (sygnatura .text, tryby); Odczyt (H3: read/readline/readlines, iteracja, iter(f.readline, '') — czyta do EOF); Zapis (write, writelines, print(file=)); Zawsze with; Kodowanie (encoding='utf-8', cp1250, utf-8-sig, errors, EncodingWarning, PYTHONUTF8, PEP 686 od 3.15; H3: newline); Dla dociekliwych: seek/tell; Typowe błędy. |
| `09-wejscie-wyjscie/bytes-i-pliki-binarne.md` | Typ bytes i pliki binarne | bytes/bytearray/memoryview (domyka katalog typów z 3); encode/decode, len('ż') a bajty; rb/wb, kopiowanie w blokach, nagłówek PNG; Dla dociekliwych: struct z prefiksem '<', io.BytesIO/StringIO. |
| `09-wejscie-wyjscie/pathlib.md` | Ścieżki i system plików | Ścieżki na Windows; Path (home, cwd, /, name/stem/suffix, exists, resolve); iterdir/glob/rglob/walk; mkdir/unlink/rename; read_text/write_text; Nowości 3.14 (copy, move, info); os.path/shutil/tempfile — tabela odpowiedników. |
| `09-wejscie-wyjscie/csv-i-json.md` | Formaty danych — CSV i JSON | csv.reader/writer (newline='', ';' i utf-8-sig z Excela), DictReader/DictWriter; json (dumps/loads/dump/load, indent, ensure_ascii=False, tabela typów, default=); python -m json (3.14); przykład zapisu stanu programu (użyty w 18); Dla dociekliwych: potok logów z itertools + ExitStack; pickle ostrzeżenie, tomllib, compression.zstd. |

**Istotne materiały źródłowe.**
- PDF: PythonNotatki.txt 5191–5488 (s. 121–127: PRINT — sygnatura, sep/end/flush, znaki sterujące, animacje, buforowanie, -u, file=; kod l. 5249, 5346, 5353 uszkodzony — odtworzyć z PDF); 788–789 (formatowanie odłożone)
- DOPISANE: Wyklad_08.txt sl. 4–13, 32, 37–39, 41 (open, zapis, binarne/struct, pathlib, csv, kodowanie/PEP 686, json, buforowanie, seek/tell, błędy)
- DOPISANE: lab2.txt sl. 3–5; Wyklad_01.txt sl. 23; Wyklad_05.txt sl. 38–39; Wyklad_02.txt sl. 17, 39
- DOPISANE: docs.python.org formatspec, PEP 750, pathlib 3.14, json CLI — materiał własny (mini-język nieobecny w źródłach)

**Modernizacje i korekty względem źródeł (Python 3.14).**
- „ASCII 9619” → U+2593; teza PDF „nie da się cofnąć kursora” — dodać ANSI; PYTHONUNBUFFERED dowolny niepusty ciąg; stderr line-buffered 3.9; \a i \b zależne od terminala (Windows Terminal) — zweryfikować
- każde open() z encoding (W08 wielokrotnie bez); PEP 686 jako stan 3.15; EncodingWarning/-X warn_default_encoding
- ręczna podmiana sys.stdout → contextlib.redirect_stdout (jedyne omówienie tu); klasa Pisarz → 11
- python -m json zamiast json.tool; Path.copy/move/info 3.14; Path.walk 3.12; t-stringi zweryfikować na 3.14
- tell() w trybie tekstowym nieprzezroczysty; struct z jawną kolejnością bajtów; komentarz „czyta do pustej linii” poprawić

**Priorytet:** wysoki. **Szacunek rozmiaru:** index + 7 stron, ok. 1000–1100 linii.

### 10. Klasy i obiekty (`docs/10-klasy/`)

**Cel dydaktyczny.** Czytelnik definiuje klasy z __init__ i self, odróżnia atrybuty klasy od instancji, stosuje trzy rodzaje metod i __slots__, __repr__/__str__, property z walidacją i konwencje hermetyzacji, buduje dziedziczenie pojedyncze z super() i własne hierarchie wyjątków; dla dociekliwych — cykl życia obiektu (lab5).

**Główne tematy.**
- class, CapWords, __init__ (inicjalizator), self, atrybuty instancji, docstring klasy
- atrybuty klasy a instancji, licznik instancji, pułapka modyfikowalnego atrybutu klasy (dwie instancje), __dict__, setattr/getattr, __slots__ (rdzeń)
- @classmethod (konstruktory alternatywne), @staticmethod (także na instancji — korekta PDF), tabela
- __repr__ a __str__, !r; @property getter/setter/deleter; _ i __, name mangling; property jako klasa-deskryptor
- dziedziczenie, super(), pominięte super().__init__(), isinstance/issubclass, własne wyjątki, kompozycja (zapowiedź), zasady projektowania klas (W06 s. 40)
- dociekliwi: __new__ (pułapka bez return), Singleton, __del__, getrefcount/PEP 683, weakref, gc, __slots__ a dziedziczenie

**Zależności od wcześniejszych rozdziałów.**
- 3 (obiekty-i-pamiec: id, refcount, del; type/isinstance)
- 6 (def, self, domyślne, składnia @)
- 8 (raise w setterach; hierarchia wyjątków); 9 (f-stringi z !r)

**Zapowiedzi i luki, które rozdział domyka.**
- 8 „definicje klas”
- 6 class
- odłożone z 8: własne klasy wyjątków z atrybutami
- luka: klasy nieobecne; weakref/getrefcount/__del__ (lab5); CapWords (W01 s. 19); __slots__

**Podział na strony.**

| Plik | Etykieta nav / H1 | Zawartość |
|---|---|---|
| `10-klasy/index.md` | Wprowadzenie | Klasa jako przepis; „wszystko jest obiektem”; podział 10–12; strony potrzebne do lab5 (tu i w 11); ---; ## W tym rozdziale (5 podstron). |
| `10-klasy/definicja-klasy.md` | Definicja klasy | Instrukcja class (CapWords, docstring, help); Tworzenie obiektu i __init__ (nie konstruktor); self (obj.m() ≡ K.m(obj), traceback missing self); Atrybuty instancji (pełny traceback AttributeError z „Did you mean”); Metody instancji (return self); Klasa jako obiekt (type, __class__). |
| `10-klasy/atrybuty-i-metody.md` | Atrybuty klasy, metody klasowe i statyczne | Atrybut klasy a instancji (Bug.licznik z lab5, przesłanianie, Klasa.atrybut a x.atrybut — fragment z PDF 4937–4941); Pułapka: modyfikowalny atrybut klasy na dwóch instancjach; Introspekcja (setattr/getattr/hasattr/delattr, vars, __dict__ 3.14); __slots__ (krótko; pomiar w 13); @classmethod (from_string); @staticmethod (korekta PDF); Tabela trzech rodzajów. |
| `10-klasy/reprezentacja-i-wlasciwosci.md` | Reprezentacja, właściwości i hermetyzacja | __repr__ a __str__ (!r, eval(repr), print/kontener); @property (getter, setter z raise ValueError, deleter, pole wyliczane, komunikat 3.11+); Pułapka rekurencji; Konwencje _ i __ (name mangling w __dict__); Dla dociekliwych: property jako klasa — property(fget, fset, fdel, doc), type(Okrag.r) → <class 'property'>; mechanizm w 11/deskryptory.md. |
| `10-klasy/dziedziczenie.md` | Dziedziczenie | Klasa bazowa i pochodna (object, __bases__); Nadpisywanie i polimorfizm w pętli; super() (pełna forma; błąd pominięcia super().__init__(); warning: modyfikowalny atrybut klasy dzielony z klasą pochodną — quiz W06); isinstance/issubclass zamiast type() (bool jako int); Własne klasy wyjątków (hierarchia, atrybuty, super().__init__(msg)) — domyka 8; Kompozycja a dziedziczenie (→ 12); admonition „Zasady projektowania klas” (W06 s. 40). |
| `10-klasy/cykl-zycia-obiektu.md` | Cykl życia obiektu (dla dociekliwych) | __new__ a __init__ (cls, super().__new__; pułapka __new__ bez return → None i brak __init__; Foo.__new__(Bar) jednym zdaniem); Singleton przez __new__ (pułapka ponownego __init__); __del__ bez gwarancji (cykle, gc, 3.14t); sys.getrefcount i PEP 683 (getrefcount(1) = 3221225472); weakref.ref (nie dla list/dict — korekta W04); __slots__ a dziedziczenie (potomna bez __slots__ odzyskuje __dict__). |

**Istotne materiały źródłowe.**
- PDF: PythonNotatki.txt 3186–3427 (s. 84–88: definicja, self, setattr, atrybuty, classmethod, mangling, __str__/__repr__, __del__; zrzuty 3362–3375, 3407–3411 odtworzyć); 3429–3483 (__new__); 3943–4136 (property jako klasa); 5109–5186 (classmethod/staticmethod — błąd o staticmethod); 4216–4322 (super w dziedziczeniu pojedynczym); 4937–4941 (atrybut klasy a instancji — przeniesione z metaprogramowania)
- DOPISANE: Wyklad_06.txt sl. 4–25, 38, 40–41 (klasa, atrybuty, metody, repr/str, property, mangling, __slots__, dziedziczenie, super, isinstance, __new__, Singleton, praktyki, quiz → warning)
- DOPISANE: lab5.txt sl. 1–2 (Bug, getrefcount, weakref); Wyklad_07.txt sl. 40 (__slots__ a dziedziczenie); Wyklad_05.txt sl. 24 (własne wyjątki); Wyklad_04.txt sl. 48 (weakref — korekta); Wyklad_01.txt sl. 19

**Modernizacje i korekty względem źródeł (Python 3.14).**
- class Foo(object) → class Foo:; .format(self=self) → f-stringi; math.pi; adresy/daty w wydrukach jako przykładowe z 3.14
- BŁĄD PDF: staticmethod wywoływalna na instancji; BŁĄD W04: weakref dla list/dict; getrefcount z PEP 683 (nieśmiertelne małe int) i wartości na 3.14t
- property to klasa, nie funkcja; help(Okrag), dir(Okrag.r) odtworzyć na 3.14 (property.__name__ od 3.13); ujednolicić parametr __init__ (value a r) z wydrukiem help()
- __dict__ klasy 3.13+ (__static_attributes__, __firstlineno__); „Did you mean” tylko w pełnym tracebacku; komunikat property bez settera 3.11+
- super(K, self) jako pełna forma, nie „Python 2”; linki StackOverflow/quantifiedcode z PDF — zastąpić (types.MethodType)

**Priorytet:** wysoki. **Szacunek rozmiaru:** index + 5 stron, ok. 850–950 linii.

### 11. Model danych — metody specjalne i protokoły (`docs/11-model-danych/`)

**Cel dydaktyczny.** Czytelnik włącza własne klasy w mechanizmy języka: przeciążanie operatorów i porównań z NotImplemented, protokoły kolekcji i __call__, protokół iteracji od strony klasy (domyka wątek z rozdz. 4), menedżery kontekstu jako klasy i obiekt plikopodobny; deskryptory dla dociekliwych wyjaśniają property i metody związane.

**Główne tematy.**
- dunder na literałach, dir(int), obj.__add__ ≡ +, kategorie metod specjalnych
- __add__/__radd__/__iadd__, __neg__/__abs__, __matmul__; NotImplemented (TypeError w kontekście logicznym 3.14)
- __eq__/__lt__, total_ordering, __hash__ a __eq__; Wektor2D, Zespolona (lab5)
- __len__/__bool__/__getitem__ (indeks krotkowy, TicTacToeBoard)/__contains__/__call__; Zamowienie z PDF
- __iter__/__next__, rozpisanie for, __iter__ jako generator, protokół sekwencji, iter(callable) z __call__
- __enter__/__exit__ jako klasa, tłumienie wyjątków; obiekt z write() (klasa Pisarz)
- deskryptory: __get__/__set__/__set_name__, dane/niedane, kolejność wyszukiwania; singledispatchmethod

**Zależności od wcześniejszych rozdziałów.**
- 10 (klasy, property, dziedziczenie)
- 4–5 (iteratory, hash, wycinki, in); 3 (operatory, is/==)
- 6 i 8 (callable, generatory; with, contextmanager do porównania); 9 (print(file=), redirect_stdout)

**Zapowiedzi i luki, które rozdział domyka.**
- luka: NotImplemented, __getitem__ krotkowy (lab5); własny iterator (W08 s. 16); menedżer kontekstu jako klasa (W05 s. 29); deskryptory (PDF s. 95–98); klasa Pisarz (PDF 5423–5488)
- 13 iter(callable, sentinel) od strony __call__

**Podział na strony.**

| Plik | Etykieta nav / H1 | Zawartość |
|---|---|---|
| `11-model-danych/index.md` | Wprowadzenie | „Wszystko jest obiektem” (dir(42), (3).__add__(4), SyntaxError dla 3.__add__ — od 3.10); tabela kategorii dunder z odsyłaczami; ---; ## W tym rozdziale (5 podstron); nota lab5. |
| `11-model-danych/operatory.md` | Przeciążanie operatorów | Operator jako metoda (brak przeciążania metod); Arytmetyka (Wektor2D: __add__/__sub__/__mul__/__rmul__/__iadd__, tabela numeryczna); NotImplemented (odbicie, TypeError; 3.14 w kontekście logicznym); Porównania (__eq__ kasuje __hash__, total_ordering); Zespolona z lab5; Dla dociekliwych: __matmul__, singledispatchmethod. |
| `11-model-danych/kolekcje-i-wywolania.md` | Protokoły kolekcji i wywołania | __len__ i __bool__; __getitem__/__setitem__ (TicTacToeBoard, slice, IndexError); __contains__; Klasa Zamowienie z PDF (__add__/__iadd__ z pułapką braku return); __call__ (licznik jako klasa a domknięcie; iter(obiekt, wartownik)); Dla dociekliwych: collections.abc. |
| `11-model-danych/iteracja.md` | Protokół iteracji | Iterowalny a iterator od strony klasy (Odliczanie); Jak działa for (while + StopIteration); Oddzielenie kolekcji od iteratora; __iter__ jako generator; Protokół sekwencji przez __getitem__; Typowe błędy (zużyty iterator, list() na nieskończonym). |
| `11-model-danych/menedzery-kontekstu.md` | Menedżery kontekstu i obiekty plikopodobne | __enter__/__exit__ (sygnatura, True tłumi); Timer jako klasa a @contextmanager z 8; Obiekt plikopodobny (klasa Pisarz z PDF, print(file=), flush) — domyka notę z 9; __format__ i __str__ w f-stringach; zapowiedź Lock (15). |
| `11-model-danych/deskryptory.md` | Deskryptory (dla dociekliwych) | Protokół (__get__/__set__/__delete__/__set_name__); Deskryptory danych i niedanych, kolejność wyszukiwania (__getattr__ na końcu); ReadOnly z PDF, walidator z __set_name__; property jako deskryptor (mini-property); Funkcje jako deskryptory — metody związane. |

**Istotne materiały źródłowe.**
- PDF: PythonNotatki.txt 3485–3745 (s. 89–95: dunder, Zamowienie, Liczba, metody numeryczne, NotImplemented; zrzuty 3494–3513 odtworzyć); 3747–3941 (s. 95–98: deskryptory); 5423–5488 (klasa Pisarz)
- DOPISANE: Wyklad_06.txt sl. 26–37, 39 (dunder, arytmetyka, porównania, kolekcje, __call__, total_ordering, Wektor2D, Zespolona, __matmul__, singledispatch)
- DOPISANE: Wyklad_07.txt sl. 28–30, 35, 39; Wyklad_08.txt sl. 14–17, 41 (iteracja, Odliczanie, błędy); lab5.txt sl. 3–4

**Modernizacje i korekty względem źródeł (Python 3.14).**
- NotImplemented w kontekście logicznym → TypeError (3.14); W06 „bool() na wyniku” uściślić; „invalid decimal literal” od 3.10; dir(int) z is_integer (3.12)
- multipledispatch → functools.singledispatchmethod (3.8; register z adnotacji od 3.7, unie typów w adnotacji od 3.11)
- time.perf_counter; import na poziomie modułu; brakujący __repr__ w przykładzie total_ordering
- zrzuty PDF (dir, TypeError dla str) jako sesje REPL 3.14; adresy jako przykładowe

**Priorytet:** średni. **Szacunek rozmiaru:** index + 5 stron, ok. 750–850 linii.

### 12. Programowanie obiektowe — mechanizmy zaawansowane (`docs/12-oop-zaawansowane/`)

**Cel dydaktyczny.** Rozdział rozwija model o dziedziczenie wielokrotne z MRO i kooperatywnym super() (lab7), mixiny i kompozycję, ABC i Protocol, klasy danych (dataclass, NamedTuple, Enum) z dopasowaniem match/case, a dla dociekliwych — wzorce projektowe i metaprogramowanie z PDF.

**Główne tematy.**
- dziedziczenie wielokrotne, diament, __mro__, super() wg MRO, niespójne MRO; C3 i śledzenie __new__/__init__ (dociekliwi)
- mixiny, kompozycja, tabela is-a/has-a, SOLID/DRY, Kompas OOP
- abc.ABC/@abstractmethod, abstrakcyjna property, fabryka pojazdów; duck typing, Protocol/@runtime_checkable (3.8)
- @dataclass (field, default_factory, __post_init__, frozen/order/slots/kw_only), NamedTuple, Enum/IntEnum/StrEnum
- match/case z klasami danych (wzorce klasowe, __match_args__, guard, wzorce sekwencji i słownika)
- dociekliwi: Factory z rejestrem, Strategy, Observer, Singleton przez dekorator; type(name, bases, dct), type.__call__ → __new__ → __init__, dekoratory klas, __init_subclass__, metaklasy

**Zależności od wcześniejszych rozdziałów.**
- 10–11 (dziedziczenie, super, property, __eq__/__hash__/__call__, __new__)
- 3 i 6 (adnotacje typów; dekoratory)
- 7 (namedtuple → NamedTuple); 4 (match — wzorce podstawowe)

**Zapowiedzi i luki, które rozdział domyka.**
- luka: MRO/__new__/super (lab7/lab8, PDF s. 101–108); ABC (PDF s. 117–119); dataclass/NamedTuple/Enum/Protocol/__init_subclass__ (W07); metaklasy (PDF s. 108–117); match zaawansowane (W05 sl. 44)
- zapowiedź z 7 (namedtuple → NamedTuple/dataclass)

**Podział na strony.**

| Plik | Etykieta nav / H1 | Zawartość |
|---|---|---|
| `12-oop-zaawansowane/index.md` | Wprowadzenie | Od hierarchii do projektowania; mechanizmy codzienne (dataclass, ABC) a rzadkie (wzorce, metaklasy); ---; ## W tym rozdziale (5 podstron); nota lab7. |
| `12-oop-zaawansowane/dziedziczenie-wielokrotne.md` | Dziedziczenie wielokrotne i MRO | Wiele baz i kolejność; Diament i MRO (__mro__, mro(), A.id(d) jawnie); super() podąża za MRO (kooperatywne __init__ z **kwargs, korekta PDF o object.__init__); Niespójne MRO → TypeError (warning z quizu X,Y/Y,X); Dla dociekliwych: śledzenie __new__/__init__ w hierarchii D(A, C) z PDF/lab7; algorytm C3 (merge, 7 klas). |
| `12-oop-zaawansowane/mixiny-i-abstrakcja.md` | Mixiny, kompozycja i klasy abstrakcyjne | Mixiny (ReprMixin, JsonMixin — json z 9); Dziedziczenie, mixin czy kompozycja (tabela); ABC i @abstractmethod (komunikat 3.12+, abstrakcyjna property, super() w metodzie abstrakcyjnej — kod PDF zrekonstruowany); Fabryka pojazdów (ABC+property+classmethod+staticmethod); Duck typing i Protocol (dla dociekliwych); SOLID/DRY i Kompas OOP (tabela decyzyjna). |
| `12-oop-zaawansowane/klasy-danych.md` | Klasy danych — dataclass, NamedTuple i Enum | @dataclass (zakładki ręcznie a dataclass; H3: field/default_factory, __post_init__, frozen/order/slots/kw_only); dataclass a dziedziczenie (warning B(x=5) — korekta W07), asdict/replace; typing.NamedTuple a namedtuple (tabela); Enum, auto, IntEnum, StrEnum; match/case z klasami danych i Enum (wzorce klasowe, guard, sekwencje, słowniki — odsyłacz z 4). |
| `12-oop-zaawansowane/wzorce-projektowe.md` | Wzorce projektowe (dla dociekliwych) | Wzorce a idiomy (funkcje pierwszej klasy); Factory z rejestrem przez @classmethod (wariant automatyczny → metaprogramowanie.md); Strategy (klasy a funkcje); Observer (zapowiedź tkinter bind/trace_add, 18); Singleton przez dekorator klasy (wariant __new__ → 10) i zastrzeżenia. |
| `12-oop-zaawansowane/metaprogramowanie.md` | Metaprogramowanie (dla dociekliwych) | Klasy jako obiekty typu type (__name__, __qualname__, __module__); type(name, bases, dct) ≡ class; Łańcuch type.__call__ → __new__ → __init__ (metaklasa Verbose z PDF, parametr mcs); Dekoratory klas (inspect.getmembers skrótowo); __init_subclass__ (rejestr Factory); Własna metaklasa (Meta, fabryka klas) i „kiedy nie” (tabela alternatyw); eval/exec — nota bezpieczeństwa (ast.literal_eval). |

**Istotne materiały źródłowe.**
- PDF: PythonNotatki.txt 4138–4452 (s. 101–108: MRO, C3, __new__/__init__ w hierarchii, D(A, C), niespójne MRO; BŁĄD o object.__init__ w 4322–4393); 4454–5006 (s. 108–117: metaprogramowanie; listingi 4687–4701 zniekształcone; 4937–4941 → 10); 5008–5108 (ABC; kod do odtworzenia)
- DOPISANE: Wyklad_07.txt sl. 3–27, 31–34, 36–38, 41–45 (wielodziedziczenie, mixiny, ABC, dataclass, NamedTuple, Protocol, __init_subclass__, Enum, wzorce, metaklasy, fabryka, dekoratory klas, SOLID, quizy → warningi, Kompas)
- DOPISANE: Wyklad_05.txt sl. 44 (match zaawansowane); lab7.txt sl. 1–2 (lab8 duplikat); Wyklad_09.txt sl. 29–30 (eval — przestroga)

**Modernizacje i korekty względem źródeł (Python 3.14).**
- BŁĄD PDF: object.__init__(self, x) także zgłasza TypeError (3.14); terminy „unbound method”, „rzutowanie”, „klasa nadrzędna” → współczesne; literówka metalcass; parametr metaklasy mcs; adresy w wydrukach jako przykładowe z 3.14
- komunikat ABC 3.12+; abstractproperty pominąć; typing.List → list[...]; StrEnum i str(IntEnum) 3.11; @runtime_checkable od 3.8, od 3.12 isinstance przez inspect.getattr_static
- BŁĄD W07 quiz: B(x=5); identyfikatory ASCII (FabrykaPojazdow), date.today().year, math.pi
- TypeError dla type.__new__ = …: „cannot set '__new__' attribute of immutable type 'type'”; dygresję o Foo.__name__ skrócić; blogi zweryfikować

**Priorytet:** średni. **Szacunek rozmiaru:** index + 5 stron, ok. 850–950 linii.

### 13. Wydajność i optymalizacja (`docs/13-wydajnosc/`)

**Cel dydaktyczny.** Krótki rozdział domykający zapowiedź lab6 przed NumPy: pomiar czasu i profilowanie, praktyczne reguły optymalizacji w CPythonie, pomiar pamięci i __slots__, dis dla dociekliwych oraz przegląd dróg przyspieszania (NumPy, Numba, Cython, mypyc, PyPy, free-threading) bez kodu tablicowego.

**Główne tematy.**
- perf_counter, dekorator timera (z 6), timeit (moduł i -m), cProfile/pstats, snakeviz, tracemalloc
- zasady: mierz, algorytm i struktura przed mikrooptymalizacją; in O(1)/O(n), deque, join, złożenia, generatory, cache
- __slots__ z pomiarem (48 B a 40 B, __dict__ 296 B na 3.14.7); dis — lambda a def (co_code), specjalizacja 3.11+
- NumPy (tabela wyników, kod w 14), Numba na czystych pętlach, Cython, mypyc, PyPy, 3.14t, PEP 799 profiling (3.15)

**Zależności od wcześniejszych rozdziałów.**
- 6 (rekurencja/Fibonacci, dekorator timera, cache)
- 10 (__slots__ w rdzeniu), 12 (dataclass(slots=True))
- 5 (zbiory — złożoność in); 7 (deque, python -m timeit)

**Zapowiedzi i luki, które rozdział domyka.**
- luka: profilowanie/optymalizacja (W12 s. 20–22); zapowiedź lab6 (Cython, mypyc, ndarray, @jit); dis (W04 s. 46, PDF 2411–2466); __slots__ benchmark (W06 s. 19, W07 s. 40)

**Podział na strony.**

| Plik | Etykieta nav / H1 | Zawartość |
|---|---|---|
| `13-wydajnosc/index.md` | Wprowadzenie | „Najpierw działa, potem mierz”; odsyłacze do 6 i 14; ---; ## W tym rozdziale (3 podstrony); nota lab6. |
| `13-wydajnosc/pomiar-i-profilowanie.md` | Pomiar czasu i profilowanie | perf_counter i dekorator timera (import z 6); timeit (number, python -m timeit); cProfile i pstats (kolumny, -o); snakeviz (po weryfikacji); sys.getsizeof i tracemalloc; Fibonacci pod lupą (tabela czasów z 3.14.7). |
| `13-wydajnosc/optymalizacja-kodu.md` | Optymalizacja kodu | Zasady; Struktury danych a złożoność (in na liście a set, pop(0) a deque); Idiomy (join, złożenia a pętla ostrożnie, generatory, wbudowane, nazwy lokalne); Memoizacja (odsyłacz 6); __slots__ — pomiar na milionie obiektów (tracemalloc; getsizeof nie wlicza __dict__); Dla dociekliwych: dis (lambda i def — porównanie co_code, listing 3.14 z RESUME/LOAD_FAST_BORROW/LOAD_SMALL_INT/BINARY_OP). |
| `13-wydajnosc/przyspieszanie-pythona.md` | Drogi przyspieszania (dla dociekliwych) | Idea wektoryzacji — tabela wyników z odsyłaczem do 14/operacje.md (kod tam); Numba @njit na czystych pętlach; Cython i mypyc (adnotacje jako źródło przyspieszenia); PyPy; wiele rdzeni — 3.14t i procesy (zapowiedź 15); Python 3.15: pakiet profiling (PEP 799). |

**Istotne materiały źródłowe.**
- DOPISANE: Wyklad_12.txt sl. 20–22 (timeit, cProfile, snakeviz, wskazówki); lab6.txt sl. 2 (zapowiedź optymalizacji)
- DOPISANE: Wyklad_04.txt sl. 46 (dis); PDF 2411–2466 (lambda a def w dis); Wyklad_06.txt sl. 19, Wyklad_07.txt sl. 40 (__slots__); Wyklad_09.txt sl. 11–12, 35 (benchmark — wyniki, Numba); Wyklad_03.txt sl. 9, 38

**Modernizacje i korekty względem źródeł (Python 3.14).**
- wszystkie liczby (fib(40), __slots__: 48 B → 40 B, __dict__ 296 B, konkatenacja) z 3.14.7; getsizeof nie wlicza __dict__ (leniwy od 3.12) — tracemalloc
- dis: RESUME, BINARY_OP, LOAD_FAST_BORROW i LOAD_SMALL_INT (3.14); porównywać co_code, nie tekst dis; konkatenacja str ma optymalizację in-place
- Numba 0.66 (3.14 od 0.63, 3.14t od 0.65); Cython/mypyc koła 3.14 — zweryfikować; snakeviz — status; PEP 799 (3.15) jako nota; PEP 703/779, sys._is_gil_enabled()

**Priorytet:** średni. **Szacunek rozmiaru:** index + 3 strony, ok. 450–520 linii.

### 14. NumPy i Matplotlib (`docs/14-numpy-matplotlib/`)

**Cel dydaktyczny.** Czytelnik przechodzi od list do ndarray (tworzenie, dtype, indeksowanie i maski, ufunc, broadcasting, agregacje, generator losowy, widok a kopia, benchmark wektoryzacji) oraz tworzy i zapisuje wykresy Matplotlib w stylu obiektowym. Domyka zapowiedzi arange/linspace i ndarray (lab9–10).

**Główne tematy.**
- instalacja w venv (NumPy 2.5.x, Matplotlib 3.11.x), ndarray a lista, array/zeros/ones/arange/linspace/eye, dtype (int64 na Windows), float32/64 i isclose (lab3)
- indeksowanie 1D/2D, fancy indexing, maski & | ~, widok a kopia (kontrast z listami)
- ufunc, np.where, broadcasting, agregacje z axis, reshape/ravel/T, concatenate; default_rng
- wektoryzacja — benchmark pętla a ndarray (kod tu, tabela w 13); tabela funkcji: sort/argsort, unique(return_counts), clip, nanmean; linalg, save/load, meshgrid
- Matplotlib: Figure/Axes, plot/scatter/bar/hist, OO a pyplot, subplots, gridspec (zdanie), adnotacje, savefig, pułapki
- przykłady: wielomian bez eval, histogram+boxplot; FuncAnimation, imshow, SciPy 1.18, Numba — dociekliwi

**Zależności od wcześniejszych rozdziałów.**
- 1 (pip/venv); 5 (wycinki, tablice 2D, kopie); 3 (float, operatory bitowe)
- 6 (funkcje, lambda, timer); 7 (eksperyment Decimal/float); 8–9 (with dla style.context, savefig/pathlib, csv → loadtxt)
- 11 (__getitem__ krotkowy, __matmul__); 13 (tabela wyników wektoryzacji)

**Zapowiedzi i luki, które rozdział domyka.**
- 11 numpy.arange/linspace
- 19 NumPy ndarray, macierze
- luka: np.float32/64 i isclose (lab3); __matmul__ (W06 s. 37); benchmark z 13

**Podział na strony.**

| Plik | Etykieta nav / H1 | Zawartość |
|---|---|---|
| `14-numpy-matplotlib/index.md` | Wprowadzenie | Ekosystem naukowy; python -m pip install numpy matplotlib; NumPy 2.x; pliki danych w docs/14-…/data/; ---; ## W tym rozdziale (5 podstron); nota lab9–10. |
| `14-numpy-matplotlib/ndarray.md` | Tablice ndarray | Od listy do tablicy; Tworzenie (arange/linspace — domyka petle-i-iteratory.md:83); Atrybuty i dtype (int64, float32 — pełny eksperyment lab3 z np.float32/64 i np.isclose, astype); Indeksowanie i wycinki (2D, fancy, maski); Widok a kopia (warning, .copy(), base — domyka referencje-i-kopiowanie.md:62); save/load, loadtxt. |
| `14-numpy-matplotlib/operacje.md` | Operacje na tablicach | Ufunc i np.where (np.sin(np.pi) ≈ 1.22e-16); Broadcasting (reguły); Agregacje i axis (schemat .text); Przekształcanie (reshape -1, ravel a flatten, T, stack); default_rng; Wektoryzacja — pełny benchmark pętla a ndarray (odsyłacz z 13); Tabela przydatnych funkcji (sort/argsort, unique, clip, nan*); Dla dociekliwych: linalg, meshgrid, @. |
| `14-numpy-matplotlib/matplotlib-podstawy.md` | Matplotlib — pierwszy wykres i styl obiektowy | Hierarchia Figure/Axes/Axis; Pierwszy wykres w stylu OO (subplots, set_*, show() w VSC); pyplot stanowy a OO (pułapki: show blokuje, plt.close); Customizacja (kolory, style, markery, style.context, LaTeX w etykietach z r''); Adnotacje (annotate, text). |
| `14-numpy-matplotlib/matplotlib-wykresy.md` | Matplotlib — rodzaje wykresów, układ i zapis | scatter/bar/hist (bins, density); Wiele paneli (subplots, layout='constrained', współdzielone osie; gridspec jednym zdaniem); Legendy i siatki; savefig (formaty, dpi, bbox_inches); wykresy jako obrazy generowane skryptem w img/. |
| `14-numpy-matplotlib/przyklady-i-rozszerzenia.md` | Przykłady i rozszerzenia (dla dociekliwych) | Histogram + boxplot (orientation=); Wielomian ze współczynników z input() bez eval (np.polyval); FuncAnimation (Pillow); imshow/imread/corrcoef; SciPy przegląd (make_interp_spline); Numba — odsyłacz do 13. |

**Istotne materiały źródłowe.**
- DOPISANE: Wyklad_09.txt sl. 3–17 (NumPy), 18–28 (Matplotlib), 29–36 (przykłady, animacja, imshow, SciPy, Numba, triki); ekstrakcja miesza kolumny (s. 6, 12, 14) — weryfikować z PDF
- DOPISANE: lab3.txt sl. 5–6 (float32/64, isclose); lab6.txt sl. 2; Wyklad_06.txt sl. 37 (__matmul__)
- PDF: 1023–1024, 1486–1487 (wzmianki o NumPy)

**Modernizacje i korekty względem źródeł (Python 3.14).**
- python -m pip; NumPy 2.5.2 (3.11–3.14), Matplotlib 3.11.x (koła 3.14/3.14t), SciPy 1.18.0 — potwierdzone; int64 domyślny na Windows 64-bit od NumPy 2.0
- wyłącznie default_rng; np.sin(np.pi) ≈ 1.22e-16; benchmarki z 3.14.7
- boxplot orientation= (3.10; vert przestarzałe), layout='constrained', styl 'seaborn-v0_8' — sprawdzić plt.style.available; interp1d → make_interp_spline
- eval() na wejściu zastąpić; wykresy jako obrazy generowane skryptem, nie zrzuty

**Priorytet:** średni. **Szacunek rozmiaru:** index + 5 stron, ok. 800–900 linii.

### 15. Współbieżność — wątki, procesy i GIL (`docs/15-wspolbieznosc/`)

**Cel dydaktyczny.** Czytelnik rozumie wątki a procesy, rolę GIL i oficjalnie wspierany w 3.14 wariant free-threaded, synchronizuje wątki (Lock, Event, Queue), używa multiprocessing i concurrent.futures oraz dobiera narzędzie do zadań I/O-bound i CPU-bound na podstawie pomiarów (lab11). Domyka async/await zapowiedzią asyncio.

**Główne tematy.**
- threading.Thread, start/join, daemon, current_thread; eksperyment countdown 1 a 2 wątki
- GIL, getswitchinterval; free-threading PEP 703/779, py install 3.14t, sys._is_gil_enabled (sekcja opcjonalna)
- wątek-logger z threading.Event, logging z wątków
- data race, Lock/with, RLock, deadlock, queue.Queue, Tk a wątki (queue + after → 18)
- multiprocessing.Pool (spawn na Windows i macOS, forkserver na Linuksie, strażnik __main__), concurrent.futures, Future, as_completed; InterpreterPoolExecutor (PEP 734)
- studia wydajności: urllib (I/O), pbkdf2/liczby pierwsze (CPU), tabela 3.14 a 3.14t; asyncio zapowiedź

**Zależności od wcześniejszych rozdziałów.**
- 6–7 (funkcje jako target, gotowy dekorator timera importowany z modułu; if __name__ obowiązkowy dla spawn)
- 8 (with dla Lock, wyjątki, logging); 11 (menedżer kontekstu)
- 1 (py install 3.14t, py -0p); 13 (pomiary)

**Zapowiedzi i luki, które rozdział domyka.**
- 6 async, await (zapowiedź; przykład w 16)
- luka: GIL/threading/multiprocessing/concurrent.futures/Lock (lab11, python_thread) nieobecne

**Podział na strony.**

| Plik | Etykieta nav / H1 | Zawartość |
|---|---|---|
| `15-wspolbieznosc/index.md` | Wprowadzenie | Współbieżność a równoległość, I/O-bound a CPU-bound, trzy drogi i asyncio; ---; ## W tym rozdziale (4 podstrony); nota lab11. |
| `15-wspolbieznosc/watki-i-gil.md` | Wątki i GIL | Proces a wątek; threading (Thread, target/args, start/join, daemon, get_ident); Eksperyment countdown (perf_counter); GIL (getswitchinterval, kiedy wątki pomagają); Free-threading 3.14 (opcjonalnie: py install 3.14t, sys._is_gil_enabled, ten sam eksperyment); Wątek-logger i zatrzymanie przez Event; logging z wątków. |
| `15-wspolbieznosc/synchronizacja.md` | Synchronizacja | Wyścig danych (FakeDatabase; na 3.14t częściej); Lock (acquire/release, with), RLock; Zakleszczenie i zasada stałej kolejności; queue.Queue producent–konsument; Tk a wątki (queue + after — odsyłacz 18); Dla dociekliwych: Semaphore, Condition, Barrier. |
| `15-wspolbieznosc/procesy-i-executory.md` | Procesy i pule wykonawców | multiprocessing.Pool (map/apply_async/close/join; metody startu: spawn — Windows i macOS, forkserver — Linux 3.14; strażnik __main__, picklowalność); concurrent.futures (Executor, submit/Future/result, map, as_completed, max_workers z os.process_cpu_count); Dla dociekliwych: InterpreterPoolExecutor i concurrent.interpreters; tabela doboru narzędzia. |
| `15-wspolbieznosc/studia-wydajnosci.md` | Studia wydajności i asyncio | Timer z 6 importowany z modułu pomocniczego (jedno zdanie); I/O-bound: pobieranie plików urllib (sekwencyjnie a ThreadPoolExecutor); CPU-bound: pbkdf2_hmac, liczby pierwsze (wątki a procesy a 3.14t — tabela); Koszt procesów; Zapowiedź asyncio (async/await, run, gather; python -m asyncio ps 3.14) — domyka katalog słów kluczowych. |

**Istotne materiały źródłowe.**
- DOPISANE: lab11.txt sl. 1–5 (GIL, Thread, countdown, logger, Pool)
- DOPISANE: python_thread.txt sl. 1–9, 12–17, 20–32, 33–45 (GIL, cykl życia wątku, ThreadPoolExecutor, data race, Lock/RLock, deadlock, concurrent.futures, studia wydajności — kod w zrzutach, odtworzyć); sl. 36 (_shutdown) wykluczony
- DOPISANE: Wyklad_12.txt sl. 23–24 (asyncio); Wyklad_11.txt sl. 34 (Tk a wątki); docs.python.org 3.14 (PEP 779, 734, multiprocessing)
- PDF: brak

**Modernizacje i korekty względem źródeł (Python 3.14).**
- GIL nie jest bezwarunkowy: 3.13 eksperymentalnie, 3.14 oficjalnie (PEP 779); 3.14t z Install Managera; PYTHON_GIL; wyniki CPU-bound inne
- forkserver domyślny tylko na Linuksie i innych uniksach (3.14); macOS i Windows — spawn; InterpreterPoolExecutor/concurrent.interpreters (PEP 734)
- time.time → perf_counter; threading._shutdown usunąć; pętla nieskończona loggera → Event; max_workers min(32, cpu+4), os.process_cpu_count 3.13
- urllib.request zamiast requests; czasy „ze starego laptopa” zmierzyć na 3.14.7; logging %s; python -m asyncio ps/pstree potwierdzone

**Priorytet:** średni. **Szacunek rozmiaru:** index + 4 strony, ok. 600–700 linii.

### 16. Warsztat programisty i dalsza droga (`docs/16-warsztat/`)

**Cel dydaktyczny.** Rozdział scala narzędzia jakości: pytest z fixtures i parametryzacją, adnotacje typów w praktyce z mypy/pyright, Zen i PEP 8 z Ruff, automatyzację przez pre-commit i GitHub Actions, a na koniec posłowie „Co dalej” (asyncio, web, data science, zasoby, Python 3.15). Domyka zapowiedź konwencji Zen/PEP 8 i narzędzi z rozdziału 1.

**Główne tematy.**
- fixtures (yield, scope, tmp_path/capsys/monkeypatch), parametrize, conftest, markery, -k/-x/--lf, pytest-cov; mock z regułą „patchuj tam, gdzie używane” i side_effect (dociekliwi)
- typy: generyki wbudowane, X | None, Callable z collections.abc, type alias 3.12, TypedDict, PEP 695; mypy 2.3 w pyproject, pyright/Pylance, Pyrefly 1.0, ty (beta)
- Zen i PEP 8 w praktyce (tabela dobrze/źle), tabela PEP (jedyne miejsce); Ruff check/format z regułami I, target-version py314; black jako alternatywa
- pre-commit (ruff-check/ruff-format v0.16.6, mypy), rozszerzenie Ruff w VSC, GitHub Actions — minimalny ci.yml (3.14); pipx/uv tool
- co dalej: asyncio (jeden przykład), Flask/FastAPI, DS/ML, ścieżki, Python 3.15, ściągawka narzędzi, zasoby, projekty, posłowie

**Zależności od wcześniejszych rozdziałów.**
- 7 (pytest podstawy, pyproject); Git/GitHub — materiał organizacyjny kursu (poza książką)
- 6 i 8 (dekoratory → fixture/parametrize; generatory → yield w fixture; raises)
- 1 i 3 (konfiguracja VSC, Pylint/autopep8, mypy/Pylance — odsyłacze); 12 (dataclass/Protocol dla TypedDict); 15 (asyncio)

**Zapowiedzi i luki, które rozdział domyka.**
- 4 konwencje Zen/PEP 8 (styl-kodu.md)
- 3 praktyka z AI — realizowana jako rozbudowa ai-tools.md; tu odsyłacz
- 6 async/await (przykład w co-dalej.md)
- luka: pytest zaawansowany, typy, ruff/pre-commit, Actions (W12 s. 3–14, 19); „co dalej” (W12 s. 20–26, 29–32)

**Podział na strony.**

| Plik | Etykieta nav / H1 | Zawartość |
|---|---|---|
| `16-warsztat/index.md` | Wprowadzenie | Od działającego kodu do utrzymywalnego; mapa narzędzi (cel → narzędzie → rozdział); ---; ## W tym rozdziale (5 podstron). |
| `16-warsztat/testowanie.md` | Testowanie z pytest — techniki zaawansowane | Przypomnienie (7, raises z 8); Fixtures (yield, scope, wbudowane); Parametryzacja (ids, z raises); conftest.py i markery (rejestracja w pyproject, -m, skip/xfail); Uruchamianie (-k, -x, --lf, pytest-cov; H3: panel Testing w VSC); Dla dociekliwych: monkeypatch/unittest.mock (patchować w module użycia → 7/import.md, side_effect); dobre praktyki (bez sieci, approx). |
| `16-warsztat/typy-statyczne.md` | Adnotacje typów w praktyce | Przypomnienie (3, 6 — annotationlib i rozszerzenie mypy tylko odsyłacze); Typy złożone (list[int], X | None, Callable, Iterable, Any; typing.List historycznie); Aliasy i generyki (type, PEP 695 skrót); TypedDict a dataclass a Protocol; mypy (pyproject python_version 3.14, strict, # type: ignore); pyright/Pylance, Pyrefly 1.0, ty (beta) — stan na IX 2026. |
| `16-warsztat/styl-kodu.md` | Styl i formatowanie kodu | Zen w praktyce (domyka konsola-w-praktyce.md:119); PEP 8 tabela dobrze/źle; Tabela PEP (8, 20, 257, 484, 572, 634, 649, 703, 750); Ruff (check, format, --fix, [tool.ruff] target-version py314, lint.select z I — odsyłacz z 7); black/autopep8 jako alternatywy (odsyłacz 1). |
| `16-warsztat/automatyzacja-jakosci.md` | Automatyzacja jakości — pre-commit i CI | pre-commit (.pre-commit-config.yaml: ruff-check, ruff-format, mypy; install, run --all-files); Rozszerzenie Ruff w VSC (charliermarsh.ruff); GitHub Actions — minimalny ci.yml (checkout, setup-python 3.14, ruff/mypy/pytest) (zakłada Git — do rozstrzygnięcia przy projekcie rozdziału; Git nie jest tematem książki); pipx/uv tool jako nota; typowe błędy. |
| `16-warsztat/co-dalej.md` | Co dalej | asyncio (async def, await, run, gather — jeden przykład; kiedy); Flask i FastAPI (fastapi dev, Pydantic) minimalnie; Data science i ML (scikit-learn 1.7.2+, PyTorch 2.10, Jupyter — odsyłacze 1, 14, 17); Python 3.15 (nota: PEP 810, 686, 798, 814, 661, 799; 1 X 2026); Ściągawka narzędzi; Zasoby i projekty na start; posłowie. |

**Istotne materiały źródłowe.**
- DOPISANE: Wyklad_12.txt sl. 3–7 (fixtures, parametrize, mock, conftest, coverage), 8–11 (typy, mypy), 12–14 (black, ruff, pre-commit), 19 (Actions), 20–26, 29–32 (co dalej, praktyki, zasoby, ściągawka); sl. 27–28, 33 wykluczone
- DOPISANE: Wyklad_01.txt sl. 14, 18–19 (ruff, tabela PEP, PEP 8); lab1.txt sl. 1–4 (linter/formater — odsyłacz do 1); Wyklad_05.txt sl. 34–35, 46 (sortowanie importów, workflow)
- DOPISANE: docs.astral.sh/ruff, pre-commit.com, mypy docs, docs.python.org whatsnew 3.15
- PDF: brak

**Modernizacje i korekty względem źródeł (Python 3.14).**
- py312 → py314 w ruff/black/mypy; wersje potwierdzone: pytest 9.1.1, mypy 2.3 (t-stringi od 1.19), ruff-pre-commit v0.16.6 z hookami ruff-check/ruff-format; identyfikatory rozszerzeń ms-python.mypy-type-checker, charliermarsh.ruff
- typing.List/Optional/Union tylko wzmianka; collections.abc.Callable; type alias 3.12; PEP 649/749 — from __future__ zbędne; strict zawiera warn_return_any
- actions/checkout i setup-python z 3.14 — wersje zweryfikować; rejestracja markerów (PytestUnknownMarkWarning); testy bez sieci
- FastAPI: fastapi dev z fastapi[standard]; Flask 3.x, Pydantic 2; pominąć Godot/TensorFlow; książki — aktualne wydania
- instalacja narzędzi: python -m pip w venv (konwencja), pipx/uv tool jako nota; uv a Install Manager komplementarnie

**Priorytet:** średni. **Szacunek rozmiaru:** index + 5 stron, ok. 800–900 linii.

### 17. Pandas i analiza danych (`docs/17-pandas/`)

**Cel dydaktyczny.** Rozdział dodatkowy (bez laboratorium): czytelnik wczytuje dane tabelaryczne do DataFrame, eksploruje i czyści je, selekcjonuje przez loc/iloc i maski, przekształca, grupuje i łączy tabele, wizualizuje wyniki i składa potok od CSV do raportu — pod pandas 3.x z Copy-on-Write.

**Główne tematy.**
- Series i DataFrame, tworzenie, dostęp, read_csv/to_csv, inne formaty z zależnościami
- head/info/describe/value_counts; astype/to_numeric/to_datetime/category; isna/dropna/fillna/ffill
- loc a iloc, maski, isin, query, sort_values/nlargest, nowe kolumny, .str/.dt, apply/map/replace
- Copy-on-Write w pandas 3 (ostrzeżenie ChainedAssignmentError, .loc), inplace odradzane
- groupby/agg (nazwana agregacja), transform/filter/pivot_table/crosstab (dociekliwi), merge, concat + glob
- DataFrame.plot, seaborn 0.13.2 (jedna strona, po testach na pandas 3), potok CSV → raport

**Zależności od wcześniejszych rozdziałów.**
- 14 (ndarray, maski, fig/ax, savefig)
- 9 (csv/json, pathlib, kodowanie, glob)
- 6 (lambda w apply/agg); 5 (słowniki → DataFrame)

**Zapowiedzi i luki, które rozdział domyka.**
- brak zapowiedzi w książce; realizuje W10 i ścieżkę „Data Science” z W12 (odsyłacz z 16/co-dalej.md)

**Podział na strony.**

| Plik | Etykieta nav / H1 | Zawartość |
|---|---|---|
| `17-pandas/index.md` | Wprowadzenie | pandas 3.x jako stan odniesienia; instalacja (pandas seaborn openpyxl); relacja do NumPy; wspólny zbiór danych rozdziału; ---; ## W tym rozdziale (5 podstron). |
| `17-pandas/series-i-dataframe.md` | Series i DataFrame | Series (indeks etykietowy, .iloc); DataFrame (ze słownika, listy słowników, ndarray; dtypes z typem str); Dostęp do kolumn i wierszy (notacja atrybutowa odradzana); read_csv (sep=';', encoding, parse_dates, dtype) i to_csv; Inne formaty (Excel, JSON, SQL/sqlite3, parquet — tabela zależności). |
| `17-pandas/eksploracja-i-czyszczenie.md` | Eksploracja i czyszczenie danych | Pierwszy rzut oka (head/tail/sample, info, describe, nunique, value_counts); Typy i konwersje (astype, to_numeric coerce, to_datetime i .dt, category z pamięcią); Brakujące dane (isna, dropna, fillna, ffill/bfill, interpolate); Zasada: metody zwracają nowy obiekt; przykład CSV z polskiego Excela. |
| `17-pandas/selekcja-i-przeksztalcenia.md` | Selekcja i przekształcenia | loc a iloc (włącznie/wyłącznie — warning); Filtrowanie (maski z nawiasami, isin, str.contains, between, query); Sortowanie i ranking; Operacje na kolumnach (np.where, drop/rename, .str); apply/map/replace (koszt apply); Copy-on-Write w pandas 3 (wycinek jak kopia, ostrzeżenie ChainedAssignmentError, df.loc[maska, 'kol'] = …, .copy()). |
| `17-pandas/grupowanie-i-laczenie.md` | Grupowanie i łączenie tabel | groupby — split-apply-combine (schemat .text, size a count); agg z nazwaną agregacją; Dla dociekliwych: transform, filter, pivot_table, crosstab; merge (typy join, suffixes, analogia SQL); concat (ignore_index, wiele CSV przez Path.glob). |
| `17-pandas/wizualizacja-i-pipeline.md` | Wizualizacja i potok analizy | DataFrame.plot (kind=, ax=, rolling); Seaborn (set_theme, scatterplot z hue/size; histplot/boxplot z hue i legend=False; nota o stanie 0.13.2 na pandas 3); Potok krok po kroku (wczytanie → eksploracja → czyszczenie → groupby/nlargest/pivot → 3 panele i savefig, to_csv raportu) jako plik analiza.py; dobre praktyki. |

**Istotne materiały źródłowe.**
- DOPISANE: Wyklad_10.txt sl. 3–10 (Series, DataFrame, read_csv, formaty), 11–19 (eksploracja, typy, braki, loc/iloc, filtrowanie, kolumny, apply), 20–27 (groupby, pivot, SettingWithCopy → CoW, merge, concat), 28–34 (plot, seaborn, pipeline; ekstrakcja s. 23 pomieszana)
- DOPISANE: pandas.pydata.org 3.0 (CoW, StringDtype, migracja str), seaborn 0.13.2; Wyklad_12.txt sl. 26 (DS/ML — odsyłacz do 16)
- PDF: brak

**Modernizacje i korekty względem źródeł (Python 3.14).**
- pandas 3.0.0 (21 I 2026): CoW domyślnie, brak SettingWithCopyWarning, ChainedAssignmentError jako ostrzeżenie (nie wyjątek), typ str zamiast object — zaktualizować wydruki; fillna(method=) usunięte → ffill()/bfill(); inplace odradzane; s[1:3] → .iloc
- seaborn 0.13.2 (I 2024, brak nowszego wydania): palette bez hue → hue=x, legend=False; przed pisaniem uruchomić przykłady na pandas 3 i 3.14 — ryzyko realne
- requests/pyarrow/openpyxl jako zależności zewnętrzne (python -m pip); przykład API → plik lokalny; wersje 2.2.1 → 3.x
- pliki CSV w docs/17-pandas/data/ (decyzja autora); .dt.to_period zweryfikować

**Priorytet:** niski. **Szacunek rozmiaru:** index + 5 stron, ok. 800–900 linii.

### 18. Interfejs graficzny tkinter (`docs/18-tkinter/`)

**Cel dydaktyczny.** Rozdział dodatkowy (bez laboratorium): czytelnik buduje aplikacje okienkowe w tkinter/ttk — pętla zdarzeń, widżety, menedżery układu, zmienne kontrolne i zdarzenia, styl obiektowy, menu i dialogi, Canvas, mini-projekt z zapisem CSV. Scala PDF Dodatki (TKINTER) i W11 pod Tcl/Tk 9.0.x (Python 3.14.6+ na Windows).

**Główne tematy.**
- Tk(), mainloop, title/geometry/resizable, iconphoto; sprawdzanie TkVersion / info patchlevel
- Label/Button/Entry (focus, state)/Text+Scrollbar, Check/Radio, Listbox/Combobox/Spinbox/Scale, tk a ttk, Notebook, Treeview, Progressbar, Style
- pack/grid/place, Frame/LabelFrame, sticky/weight, winfo_children, pułapka pack+grid
- StringVar…, trace_add (trace → TclError w Tk 9), command a bind, protocol, after zamiast sleep, ToolTip
- klasa po tk.Tk lub z master, Menu (tearoff domyślnie 0 w Tk 9), messagebox (bool)/filedialog/simpledialog, Toplevel
- Canvas: figury, PhotoImage (referencja), tagi, mysz, animacja after, szachownica
- mini-projekt Menedżer kontaktów (dataclass Kontakt, Treeview, live search, DictWriter), praktyki, wątki + queue + after

**Zależności od wcześniejszych rozdziałów.**
- 10–12 (klasy, dziedziczenie po tk.Tk, dataclass, Observer)
- 6 (lambda w command=, późne wiązanie n=i, callback)
- 9 (csv/DictWriter, filedialog + open); 15 (Tk a wątki — odsyłacz)

**Zapowiedzi i luki, które rozdział domyka.**
- brak zapowiedzi; realizuje PDF TKINTER (s. 127–150) i W11; callback command= jako zastosowanie funkcji pierwszej klasy (W04 s. 42)

**Podział na strony.**

| Plik | Etykieta nav / H1 | Zawartość |
|---|---|---|
| `18-tkinter/index.md` | Wprowadzenie | Pętla zdarzeń; tkinter w Install Managerze (python -m tkinter; Tcl/Tk 9.0.x od 3.14.6, sprawdzenie TkVersion i root.tk.call('info','patchlevel'); embeddable bez, python3-tk); alternatywy jednym zdaniem; ---; ## W tym rozdziale (7 podstron). |
| `18-tkinter/okno-i-widzety.md` | Okno i widżety | Pierwsze okno (Tk, title, geometry, mainloop, iconphoto); Label i Button (foreground = kolor tekstu — korekta PDF, command bez nawiasów, configure); Entry (focus(), state='disabled'/'readonly'); Text/ScrolledText ('1.0', 'end-1c', tagi, Scrollbar); Checkbutton/Radiobutton; H3: Listbox/Combobox/Spinbox/Scale; tk a ttk. <!-- TODO: screenshot okna --> |
| `18-tkinter/uklad.md` | Menedżery układu | pack (side/fill/expand, tabela); grid (sticky, columnspan, weight — formularz logowania); place; Frame/LabelFrame, winfo_children i grid_configure (ta sama metoda co grid — korekta PDF; „Mighty Python”); Pułapka: mieszanie pack i grid (zachowanie w Tk 9.0 zweryfikowane); Porównanie menedżerów. |
| `18-tkinter/zdarzenia-i-zmienne.md` | Zdarzenia i zmienne kontrolne | Zmienne Tk (textvariable, get/set; dlaczego zwykła zmienna nie odświeża); trace_add/trace_remove/trace_info (sygnatura, *_; kod PDF przepisany; dokładny TclError „bad option \"variable\"” i DeprecationWarning 3.14.7 dla trace); command a bind (tabela zdarzeń, event, lambda e: root.destroy() — korekta W11); Pułapka lambda w pętli (odsyłacz 6); after zamiast sleep, after_cancel, zegar; protocol; Dla dociekliwych: ToolTip (tip_window = None w __init__). |
| `18-tkinter/aplikacja-obiektowa-i-menu.md` | Aplikacja obiektowa i menu | Klasa aplikacji (po tk.Tk — PDF; z master — W11; super().__init__, stan w atrybutach zamiast global); Podział na _create_menu/_create_widgets/_create_bindings; Menu (cascade/command/separator; tearoff domyślnie wyłączony w Tk 9 — TIP 161, tearoff=0 tylko dla 8.6; akceleratory + bind); Zamykanie (protocol WM_DELETE_WINDOW, destroy zamiast exit). |
| `18-tkinter/dialogi-i-widzety-ttk.md` | Dialogi, Toplevel i widżety ttk | Dialogi (messagebox zwraca bool — korekta PDF; filedialog; simpledialog; anulowanie); Toplevel (transient, grab_set, withdraw); Notebook; Treeview (kolumny, insert, selekcja); Style i motywy Windows 11 (vista domyślny, winnative, clam, alt, default, classic, xpnative); Progressbar z after (nie update w pętli). |
| `18-tkinter/canvas.md` | Canvas — rysowanie i animacja | Figury i tekst (create_*, tagi); Obrazy (PhotoImage PNG/GIF — referencja w atrybucie; JPEG przez Pillow); itemconfig/coords/move/delete; Rysowanie myszą (<B1-Motion>, stan w klasie); Przeciąganie (find_closest()[0]); Animacja przez after (piłka); Szachownica z weight (PDF). |
| `18-tkinter/projekt-menedzer-kontaktow.md` | Mini-projekt — menedżer kontaktów | Założenia i szkielet ContactApp; dataclass Kontakt; Formularz z walidacją (messagebox); Wyszukiwanie na żywo (trace_add); Treeview i pasek stanu; Eksport CSV (DictWriter, newline='', encoding); pełny kod title="kontakty.py" (wyjątek: do ~300 linii); Dobre praktyki i pułapki (wątki + queue + after → 15); rozszerzenia. |

**Istotne materiały źródłowe.**
- PDF: PythonNotatki.txt 5493–6824 (s. 127–150: okno, Label/Button/ttk, pack/grid/place, klasa po tk.Tk, after, zmienne, messagebox, Entry, Combobox, Check/Radio, trace, ScrolledText, LabelFrame, Menu, Notebook, Spinbox, ToolTip, Progressbar, Canvas); listingi 5346, 5526, 5883, 6076–6086, 6147–6159, 6192, 6298, 6347–6352, 6632, 6645–6672, 6715–6723, 6779–6785, 6805–6806 uszkodzone — rekonstrukcja z PDF
- DOPISANE: Wyklad_11.txt sl. 3–34 (anatomia, widżety, układ, pułapka pack/grid, zmienne/trace_add, command/bind, protocol/after, menu, dialogi, Toplevel, Canvas, ttk/Notebook/Treeview/Style, mini-projekt, praktyki; s. 23, 30–33 uszkodzone)
- DOPISANE: Wyklad_04.txt sl. 42 (callback); tcl-lang.org (Tk 9.0 changes, TIP 161); cpython gh-124111, gh-127802; docs.python.org tkinter 3.14

**Modernizacje i korekty względem źródeł (Python 3.14).**
- KRYTYCZNE: Variable.trace('w', …) i trace_variable (PDF 5944–5945, 6189–6190) → trace_add('write', cb); w Tk 9 TclError: bad option \"variable\": must be add, info, or remove; od 3.14.7 DeprecationWarning (usunięcie w 3.17); trace_vdelete/vinfo usunąć
- Tcl/Tk 9.0.4 w instalatorach Windows od 3.14.6 (starsze 3.14.x mogą mieć 8.6) — podać sposób sprawdzenia; nie cytować zdania docs o „bundles Tcl/Tk 8.6”; tearoff domyślnie 0 (TIP 161); mieszanie pack/grid, paski przewijania, DPI — zweryfikować na Windows 11
- BŁĘDY PDF: foreground = kolor tekstu; askyesno/askokcancel → bool; self.close() → destroy(); grid_configure to grid; „ASCII 9619” → Unicode; „rok 2021” usunąć; textvar → textvariable; tk.Spinbox z bd/relief → ttk.Spinbox; ToolTip bez tip_window = None (AttributeError); teksty „Czesc”/„Zegnaj” z polskimi znakami; BŁĄD W11: bind('<Escape>', quit), get('1.0', END) z \n → 'end-1c'
- from tkinter import * → import tkinter as tk; class X(object) → class X:; % i str.format → f-stringi; global w handlerach → stan w klasie; sleep+update → after; iconbitmap → iconphoto; exit() → destroy/sys.exit
- zrzuty okien (kolory, układ) do ZRZUTY.md; brak plików .ico w repozytorium

**Priorytet:** niski. **Szacunek rozmiaru:** index + 7 stron, ok. 1050–1150 linii.

## 5. Kolejność realizacji

Kolejność realizacji pokrywa się z numeracją. Każdy rozdział: projekt → implementacja → odbiór.

1. 06-funkcje — domyka 11 zapowiedzi i 7 TODO; fundament dalszych rozdziałów (lab4).
2. 07-moduly — import używany od rozdz. 3; lab3 (pakiety, pytest, assert); domyka deque.
3. 08-wyjatki — największa luka pojęciowa; with i debugger potrzebne w 9 i dalej.
4. 09-wejscie-wyjscie — formatowanie, print i pliki używane we wszystkich dalszych przykładach; lab2.
5. 10-klasy — rdzeń OOP (lab5); po nim własne wyjątki, iteratory i menedżery jako klasy.
6. 11-model-danych — kontynuacja 10; domyka lab5 (Zespolona, TicTacToeBoard) i wątek iteratora.
7. 12-oop-zaawansowane — lab7/lab8 (MRO), W07; kończy blok obiektowy.
8. 13-wydajnosc — zapowiedź lab6 przed lab9–10; wymaga klas (__slots__) i dekoratorów.
9. 14-numpy-matplotlib — lab9–10; domyka zapowiedzi 11 i 19; kod benchmarku dla 13.
10. 15-wspolbieznosc — lab11 (ostatnie laboratorium); wymaga 13 do pomiarów.
11. 16-warsztat — pytest zaawansowany i narzędzia; posłowie „Co dalej” zamyka rdzeń kursu.
12. 17-pandas — dodatek bez labu; wymaga pandas 3.x, plików danych i testów seaborn.
13. 18-tkinter — dodatek bez labu; największy nakład rekonstrukcji listingów i weryfikacji Tk 9.

## 6. Uzupełnienia rozdziałów 1–5

Podział: **(A)** zmiany dopuszczalne w ramach rozdziału, który domyka daną zapowiedź (zamiana `TODO`/zapowiedzi na odsyłacz, minimalny dopisek); **(B)** osobne etapy redakcyjne, niewykonywane przy okazji pisania nowych rozdziałów.

- **docs/05-typy-zlozone/lista.md:49, :117, :398, :490** — Cztery TODO/zapowiedzi → odsyłacze: rekurencja i limit sys → ../06-funkcje/rekurencja.md (sekcja Limit rekurencji); iter(callable) → ../06-funkcje/funkcje-jako-obiekty.md (wersja klasowa w 11); key/lambda → tamże; deque → ../07-moduly/biblioteka-standardowa.md z dopiskiem pop(0) O(n) a deque O(1). *(Zapowiedzi 12, 13, 14, 15.)*
- **docs/05-typy-zlozone/krotka.md:20 i :128** — Oba TODO → ../06-funkcje/argumenty-i-parametry.md; dopisać _ jako nazwę-wypełniacz, listę „kiedy krotka”, zdanie o zip_longest (7/itertools.md) i namedtuple (7/biblioteka-standardowa.md). *(Zapowiedzi 16, 17; luki W03 s. 12, 14–15, 31.)*
- **docs/05-typy-zlozone/slownik.md:56** — TODO → ../06-funkcje/argumenty-i-parametry.md; dodać {**a, **b} obok |, dict(sorted(d.items())), del d[k] z KeyError, zdanie o EAFP z odsyłaczem do ../08-wyjatki/styl-i-testowanie.md. *(Zapowiedź 18; luki W03 s. 19–22, 37.)*
- **docs/05-typy-zlozone/zlozenia.md:45** — TODO → yield: ../06-funkcje/funkcje-generatorowe.md, map/filter: ../06-funkcje/funkcje-jako-obiekty.md; dodać spłaszczanie listy list, sum(x > 0 for …), idiom '\n'.join(f'{k}: {v}' …), wzorzec [a if w else b for x in s] z przestrogą przed zagnieżdżaniem, nota „kiedy nie złożenie”. *(Zapowiedź 20; luki W02 s. 39, W03 s. 8–9, 21; lab2 sl. 6–8.)*
- **docs/05-typy-zlozone/zbiory.md i index.md** — zbiory.md: złożoność in (O(1) a O(n)), frozenset jako klucz/element, list(dict.fromkeys(x)); index.md: ściąga wyboru kolekcji i tabela funkcji wbudowanych na kolekcjach. *(Luki wysokie W03 s. 27, 38–39, 41, 44.)*
- **docs/05-typy-zlozone/referencje-i-kopiowanie.md:62** — Zapowiedź → ../14-numpy-matplotlib/ndarray.md; zdanie: wycinek listy to kopia, wycinek ndarray to widok. *(Zapowiedź 19.)*
- **docs/04-sterowanie/petle-i-iteratory.md:83 i :97** — Wyłącznie tekst odsyłaczy: yield → ../06-funkcje/funkcje-generatorowe.md; arange/linspace → ../14-numpy-matplotlib/ndarray.md; bez zmiany nagłówków i slotów aktywności. *(Zapowiedzi 10, 11; strona z markerami aktywności.)*
- **docs/04-sterowanie/wyrazenia-warunkowe.md:86** — return → odsyłacz do ../06-funkcje/definiowanie-funkcji.md; przy match numer PEP 634 i zdanie-odsyłacz do wzorców klasowych w ../12-oop-zaawansowane/klasy-danych.md — bez zmiany struktury sekcji. *(Zapowiedź 9; W05 sl. 44; markery aktywności.)*
- **docs/03-nazwy-typy/nazwy-i-slowa-kluczowe.md:14** — Tabela „gdzie omawiamy” dla 35 słów kluczowych (def/return/lambda/yield/global/nonlocal → 6; import/from/as/assert → 7; try/except/finally/raise/with → 8; class → 10; async/await → 15/16); konwencje CapWords, UPPER_CASE, _nazwa. *(Zapowiedź 6; luki W01 s. 19, W02 s. 4; assert wprowadzony w 7.)*
- **docs/03-nazwy-typy/typy-proste.md, operatory.md, obiekty-i-pamiec.md:90, konwersje-i-adnotacje.md** — typy-proste: s[0]='J' → TypeError, isdigit/isalpha/endswith, zakres find(), \u/\U, arytmetyka bool, łańcuch metod str czytany od wewnątrz (lab2), Fraction obok Decimal, odsyłacz do 9/formatowanie.md, zamknięcie TODO:24 — kod odtworzyć z obrazów PDF s. 17–18 (w PythonNotatki.txt brak) jako bloki .python .no-copy; operatory: tabela priorytetów (-2 ** 2), przypisania rozszerzone, PEP 572; obiekty-i-pamiec: „definicje klas” → ../10-klasy/index.md, zdanie o cyklach i gc; konwersje: odsyłacze do 6, 8, 16 (mypy). *(Zapowiedzi 7, 8; luki W01/W02, lab2 i PDF; rekonstrukcja zrzutów.)*
- **docs/02-konsola/konsola-w-praktyce.md:34 i :119; pierwszy-skrypt.md:62** — TODO zrzutu IDLE → sygnatura print jako blok .text z odsyłaczem do 9/print-i-strumienie.md; Zen → odsyłacze do 6 i 16/styl-kodu.md; docstring → 6/definiowanie-funkcji.md; dodać IndentationError obok TabError i zapowiedź if __name__ (7). *(Zapowiedzi 4, 5; luki W01 s. 23, 27, 32; tekst zamiast zrzutu.)*
- **docs/01-instalacja/konfiguracja.md:102 i :136** — Docstring → 6/definiowanie-funkcji.md; debugowanie → ../08-wyjatki/diagnostyka.md; dodać Ruff jako alternatywę dla Pylint/autopep8, rozszerzenie Jupyter, tabelę skrótów VSC, notę o wyłączaniu Pylance ("python.languageServer": "None" — zweryfikować) i pliku .pylintrc; tabela PEP wyłącznie jako odsyłacz do 16/styl-kodu.md. *(Zapowiedzi 1, 2; luki W01 s. 14–15, 18; lab1 sl. 1–4; jedno miejsce dla tabeli PEP.)*
- **docs/01-instalacja/ai-tools.md:20–23** — Rozbudować: trzy kategorie narzędzi (Copilot z trybami inline/Ask/Edit/Agent i prefiksami @ # /; asystenci czatowi; edytory z AI — Cursor/Windsurf), zasada weryfikacji kodu i uczciwości w Classroom, jeden aktywny asystent, wyłączanie podpowiedzi; modele/limity tylko odsyłacz do docs.github.com; usunąć TODO-AKTUALIZACJA; nazwy zweryfikować w sieci. *(Zapowiedź 3; lab1 s. 5–14; W01 s. 17.)*
- **docs/01-instalacja/pip.md, instalacja.md, sciezki-i-utrzymanie.md** — pip: tabela specyfikatorów PEP 440, zdanie o pyproject.toml (→ 7/struktura-projektu.md), py -0p; instalacja: nota o zgodności ekosystemu z 3.14 (potwierdzona IX 2026), zalecenie 3.14.6+ (Tcl/Tk 9) i o 3.15; ścieżki: zakładka Linux/macOS (which/whereis), -P/PYTHONSAFEPATH (→ 7). *(Luki W05 s. 16, lab4 s. 7, PDF 96–98, 368–370; rozstrzygnięcie stanu odniesienia.)*
- **docs/index.md, mkdocs.yml (nav), ZRZUTY.md** — PROPOZYCJA do zatwierdzenia: pozycje 6–18 w „Spisie rozdziałów” i nav (etykiety = H1, index jako „Wprowadzenie”, 17–18 oznaczone jako dodatki), dodawane przyrostowo po mkdocs build bez ostrzeżeń; ZRZUTY.md: debugger VSC (8), panel Testing (16), okna tkinter (18). *(Zmiana nav wymaga zgody; konwencja zrzutów.)*

## 7. Decyzje autora (5 IX 2026)

1. Realizacja rozdział po rozdziale; teraz wyłącznie rozdział 6, po nim osobny odbiór.
2. Rozdział „Git i GitHub” usunięty z planu; numeracja 6–18 bez luki; rozdziały 17–18 pozostają dodatkami na końcu.
3. Rozdział 6 zachowuje siedem podstron: `definiowanie-funkcji.md`, `argumenty-i-parametry.md`, `zasieg-nazw-i-domkniecia.md`, `funkcje-jako-obiekty.md`, `rekurencja.md`, `funkcje-generatorowe.md`, `dekoratory.md` (+ `index.md`). Generatorów i dekoratorów nie wydzielamy.
4. W rozdziale 6: `map()`/`filter()` dozwolone (funkcje wbudowane); `functools.reduce` nie jest elementem podstawowej narracji; `functools.cache`, `functools.wraps` i inne importowane dekoratory nie są wymaganą wiedzą; `sys.getrecursionlimit()` nie jest przykładem; brak założeń o pakietach i modułach użytkownika. Dekorator wyjaśniany wyłącznie własnymi funkcjami: funkcja jako obiekt → funkcja przyjmująca funkcję → funkcja zwracająca funkcję → domknięcie → ręczne przypisanie wrappera → składnia `@`. Dekoratory biblioteczne wracają po modułach.
5. Generatory są rdzeniem rozdziału 6, z rozróżnieniem: zwykła funkcja, funkcja generatorowa, obiekt generatora (iterator), wyrażenie generatorowe. `map()` zwraca iterator, nie generator.
6. Adnotacje opisujemy według Pythona 3.14 (leniwa ewaluacja, PEP 649/749) po weryfikacji w dokumentacji; w rozdziale 6 tylko składnia parametrów i wartości zwracanej, brak wymuszania typów, aktualna semantyka, odsyłacz do rozdziału 3. Narzędzia statycznej analizy później.
7. Przed implementacją każdego rozdziału autor akceptuje szczegółowy projekt stron; skondensowany zapis projektu trafia do `plans/NN-slug.md`.
8. Korekty projektu rozdziału 6 (5 IX 2026): bez kodu z `annotationlib` i bez `__annotate__` jako wiedzy podstawowej (adnotacje: leniwa ewaluacja i brak sprawdzania typów w czasie wykonania, introspekcja odłożona); bez `sys.getsizeof()` i liczb bajtów (leniwość pokazana zachowaniem programu); bez `global` w przykładach diagnostycznych (liczniki przez domknięcie z `nonlocal`); bez dekoratora mierzącego czas, bez dekoratora wymagającego `raise`, bez „Ciągu Fibonacciego w czterech zapisach”, bez wieży Hanoi; `globals()`/`locals()` najwyżej krótka nota; tabela komunikatów TypeError jako element kompaktowy; „Konwencje zapisu funkcji” jako krótkie zakończenie; „funkcja czysta” nie jest pojęciem podstawowym; utrata metadanych pokazana prostą funkcją opakowującą, bez ręcznego kopiowania `__name__`/`__doc__` jako rozwiązania — `functools.wraps` zapowiedziane po modułach; rdzeń generatorów: funkcja generatorowa → obiekt generatora → yield → next() → zawieszenie/wznowienie → jednorazowość → leniwość → generator nieskończony → potoki → yield from (`StopIteration.value`, `send()`, `throw()`, `close()` poza rdzeniem).
9. Konwencje redakcyjne: „funkcja opakowująca (ang. *wrapper*)” przy pierwszym użyciu, w polskim kodzie nazwa `opakowana`; docstringi w polskich przykładach w stylu `"""Zwraca ..."""`, `"""Oblicza ..."""`, `"""Sprawdza ..."""` (świadoma polska konwencja). Bez nowych konwencji „Powiązane laboratorium” (książka niezależna od organizacji laboratoriów) i „Ściąga”; układ index.md jak w istniejących rozdziałach.

## 8. Pytania otwarte

1. Konwencje do rozstrzygnięcia przy kolejnych rozdziałach: „(dla dociekliwych)” w etykietach nav oraz półpauza zamiast dwukropka w etykietach.
2. Moduł re: wykluczony jako osobny temat (wiersz w tabeli stdlib i krótka admonition w 7). Czy w następnym wydaniu planować stronę „Wyrażenia regularne” w rozdziale 9?
3. Zrzuty ekranu: debugger VSC (8, 2–3), panel Testing (16), okna tkinter (18, 6–10) — kto wykonuje, jaki motyw; wykresy w 14 i 17 generowane skryptami do img/?
4. Pliki danych (CSV/JSON dla 9 i 17, obraz dla 14) w docs/<rozdział>/data/ i publikacja w site/ — zgoda?
5. Weryfikacje przed pisaniem (mieszanie pack/grid, paski przewijania i DPI w Tk 9 na Windows 11; przykłady seaborn na pandas 3; snakeviz, Cython/mypyc dla 3.14) — wykonuje autor czy redaktor?
6. Aktywności interaktywne: nowe rozdziały bez markerów; quizy i zadania z wykładów/labów jako CONTENT HANDOFF do activities — które rozdziały mają je docelowo dostać? Zmiany nav w mkdocs.yml i docs/index.md wyłącznie po akceptacji planu.

## 9. Jak powstał plan

Etap 1: 15 agentów przeczytało w całości 30 stron książki, PDF autora (rozdz. 1–9), 12 wykładów, 9 laboratoriów, `python_thread.pdf` i `github_classroom.pdf`, tworząc mapy treści (346 jednostek) i analizę luk. Etap 2: trzy niezależne plany (wierność PDF, progresja kursu, graf zależności), panel trzech sędziów (zwycięzca: graf zależności), synteza, pięciu weryfikatorów (zapowiedzi, pokrycie PDF, pokrycie wykładów i laboratoriów, zależności i struktura, aktualność faktów — 58 ustaleń), korekta. Etap 3: decyzje autora z 5 IX 2026 (sekcja 7) i przenumerowanie.

| Weryfikator | Wynik | Ustalenia |
|---|---|---|
| zapowiedzi | PROBLEMY | 2 |
| pokrycie-pdf | PROBLEMY | 11 |
| pokrycie-wyklady | PROBLEMY | 16 |
| zaleznosci | PROBLEMY | 18 |
| aktualnosc | PROBLEMY | 11 |
