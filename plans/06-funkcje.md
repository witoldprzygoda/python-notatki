# Rozdział 6. Funkcje — plan implementacyjny

Skondensowany projekt rozdziału zaakceptowany przez autora 5 września 2026 (z korektami). Mapa całej książki: `PLAN_ROZWOJU.md`. Katalog `docs/06-funkcje/`, osiem plików; kolejność implementacji: `definiowanie-funkcji.md`, `argumenty-i-parametry.md`, `zasieg-nazw-i-domkniecia.md`, `funkcje-jako-obiekty.md`, `rekurencja.md`, `funkcje-generatorowe.md`, `dekoratory.md`, `index.md`. Stan odniesienia: Python 3.14.7.

## Zasady obowiązujące w całym rozdziale

- Żaden przykład nie wymaga mechanizmu wprowadzanego później: bez `try/except` (rozdz. 8), plików i `open()` (rozdz. 9), klas (rozdz. 10), modułów użytkownika i pakietów (rozdz. 7).
- Bez importów w rdzeniu: `functools` (`cache`, `wraps`, `reduce`, `partial`), `itertools`, `operator`, `annotationlib`, `sys.getrecursionlimit()`, `sys.getsizeof()` i `time` nie pojawiają się w kodzie rozdziału; wracają w rozdziale 7 lub później i są tylko zapowiadane.
- `map()` i `filter()` są dozwolone jako funkcje wbudowane; opisujemy je jako iteratory klasy `map`/`filter`, nigdy jako generatory.
- W przykładach diagnostycznych (liczniki wywołań, wartownik dla `iter()`) nie używamy `global`; stan przechowujemy w domknięciu z `nonlocal` (wprowadzonym na stronie 3). `global` pojawia się wyłącznie tam, gdzie jest nauczanym mechanizmem.
- Adnotacje opisujemy według Pythona 3.14: składnia adnotacji parametrów i wartości zwracanej, brak sprawdzania typów w czasie wykonania, domyślnie leniwa ewaluacja (PEP 649/749) pokazana zachowaniem programu. Bez kodu z `annotationlib`, bez `__annotate__` jako wiedzy podstawowej; introspekcja adnotacji odłożona.
- Terminologia: „funkcja opakowująca (ang. *wrapper*)” przy pierwszym użyciu, w kodzie nazwa `opakowana`; „parametr” w definicji, „argument” w wywołaniu; „funkcja generatorowa”, „obiekt generatora”, „wyrażenie generatorowe”; „domknięcie”, „zmienna wolna”, „późne wiązanie”.
- Docstringi w polskich przykładach konsekwentnie w stylu `"""Zwraca ..."""`, `"""Oblicza ..."""`, `"""Sprawdza ..."""` (świadoma polska konwencja redakcyjna; PEP 257 przywołany jako źródło reguł formalnych).
- Każdy przykład o deterministycznym wyniku uruchomiony na interpreterze projektu przed wpisaniem wyniku; tracebacki, `repr` i komunikaty w brzmieniu 3.14.7. Adresy obiektów, nazwy klas iteratorów i wartości liczbowe zależne od implementacji oznaczamy jako szczegół CPythona.
- Konwencje redakcyjne z `CLAUDE.md`: nagłówki H2 rzeczownikowe, najwyżej sześć H2 na stronę, bloki kodu `python title="plik.py"` / `{ .python .no-copy }` dla sesji REPL / `{ .text .no-copy }` dla wyników i schematów, admonitions z polskimi tytułami, cudzysłowy „…”.
- `index.md` w układzie istniejących rozdziałów: wstęp prozą, `---`, `## W tym rozdziale`. Bez nowych konwencji („Powiązane laboratorium”, „Ściąga”).

## Strony

### 1. `definiowanie-funkcji.md` — Definiowanie funkcji

**Cel.** Czytelnik definiuje funkcję instrukcją `def`, rozumie, że definicja jest instrukcją wykonywalną wiążącą nazwę z obiektem funkcji, a ciało wykonuje się dopiero przy wywołaniu; opanowuje `return`, dokumentuje funkcję docstringiem i czyta `help()`; zapisuje adnotacje ze świadomością semantyki 3.14; poznaje funkcję jako obiekt w zakresie potrzebnym dalszym stronom.

**Kolejność H2.**
1. Anatomia definicji i wywołania
2. Instrukcja return
3. Docstring i funkcja help()
4. Adnotacje w sygnaturze
5. Funkcja jako obiekt
6. Konwencje zapisu funkcji (krótkie zakończenie, bez dygresji)

**Zależności pojęciowe.** Wprowadza: `def`, nagłówek, parametry, ciało, wywołanie, `pass`; `return`, `None` jako wynik domyślny, wczesny `return`, wiele wartości jako pakowanie krotki; docstring, `__doc__`, `help()`; adnotacje parametrów i wartości zwracanej, leniwa ewaluacja; obiekt funkcji, typ `function`, `__name__`. Korzysta z: wcięcia i docstring modułu (`02-konsola/pierwszy-skrypt.md`); słowa kluczowe, `snake_case`, nazwa jako referencja (`03-nazwy-typy/nazwy-i-slowa-kluczowe.md`); `type()`, `id()` (`03-nazwy-typy/obiekty-i-pamiec.md`); adnotacje zmiennych, Pylance i mypy (`03-nazwy-typy/konwersje-i-adnotacje.md`); pakowanie krotki (`05-typy-zlozone/krotka.md`); `help(print)` (`02-konsola/konsola-w-praktyce.md`).

**Kluczowe przykłady.** `pole_prostokata(a, b)` (12; 5.0 typu float); `NameError` przy wywołaniu przed definicją, `IndentationError` bez ciała, `TypeError: ... missing 1 required positional argument: 'b'`; `powitanie()` z `print` zwraca `None`; `dziel()` z wczesnym `return`; `min_max()` zwracające krotkę i rozpakowanie; `srednia()` z docstringiem, `help(srednia)` i `repr(srednia.__doc__)` bez wcięć (od 3.13 kompilator usuwa wspólne wcięcie); docstring nie na początku ciała → `__doc__` równe `None`; `kwadrat(x: int) -> int` wywołane z `2.5` i `"ab"` — błąd zgłasza mnożenie, nie adnotacja; `def f(x: Nieistniejacy) -> Wynik: pass` definiuje się bez błędu (leniwa ewaluacja pokazana zachowaniem); `type(pole_prostokata)`, druga nazwa, `pole_prostokata + 1` → `TypeError`; `type(len)`, `abs.__doc__`.

**Źródła.** Repozytorium: `PythonNotatki.txt` 1988–2062 (s. 59; przykład `__annotations__` nieaktualny — pominięty; `sys.argv` → rozdz. 7), `Wyklad_04.txt` sl. 4–6, 39–41 (import w ciele funkcji → na górę pliku), `Wyklad_02.txt` sl. 21, `Wyklad_01.txt` sl. 24. Zewnętrzne: Language Reference *Function definitions* (definicja jako instrukcja; od 3.14 adnotacje ewaluowane leniwie w zasięgu adnotacji), *The return statement*, datamodel *User-defined functions*; HOWTO *Annotations Best Practices*; What's New 3.14 (PEP 649/749); tutorial *Documentation Strings* (usuwanie wcięcia od 3.13); PEP 257; PEP 8; glosariusz (*parameter*, *argument*, *function annotation*, *docstring*).

**Odsyłacze do domknięcia.** `01-instalacja/konfiguracja.md:102` i `02-konsola/pierwszy-skrypt.md:62` (docstring) → sekcja 3; `04-sterowanie/wyrazenia-warunkowe.md:86` (`return`) → sekcja 2, wyłącznie tekst odsyłacza (strona z markerami aktywności); `03-nazwy-typy/nazwy-i-slowa-kluczowe.md:14` → jeden uzgodniony tekst dla całego rozdziału: „Ich znaczenie poznajemy stopniowo — m.in. `def` i `return` w podrozdziale [Definiowanie funkcji](../06-funkcje/definiowanie-funkcji.md), `lambda` w [Funkcje jako obiekty](../06-funkcje/funkcje-jako-obiekty.md), `yield` w [Funkcje generatorowe](../06-funkcje/funkcje-generatorowe.md), `global` i `nonlocal` w [Zasięg nazw i domknięcia](../06-funkcje/zasieg-nazw-i-domkniecia.md).”

**Odłożone.** `sys.argv` i `__doc__` skryptu przy `--help` → rozdz. 7; introspekcja adnotacji (`annotationlib`, `__annotate__`, `__annotations__`) → późniejszy rozdział o narzędziach typów; `from __future__ import annotations`, `inspect`, PEP 695 → poza programem; `__defaults__` → strona 2; `__closure__`, przekazywanie funkcji, `callable()`, `lambda` → strony 3–4; „funkcja czysta” → krótka wzmianka przy stylu funkcyjnym na stronie 4.

### 2. `argumenty-i-parametry.md` — Argumenty i parametry

**Cel.** Czytelnik rozróżnia parametr od argumentu, łączy argumenty pozycyjne i nazwane z wartościami domyślnymi, rozumie jednorazową ewaluację wartości domyślnej przy wykonaniu `def` (pułapka listy, idiom `None`), wie, że funkcja otrzymuje referencje do obiektów, opanowuje `*args`/`**kwargs`, rozpakowanie `*` i `**` w wywołaniu oraz separatory `/` i `*`; czyta komunikaty `TypeError` i `SyntaxError` związane z wywołaniem.

**Kolejność H2.**
1. Parametr a argument
2. Wartości domyślne (H3: Pułapka modyfikowalnej wartości domyślnej)
3. Przekazywanie referencji
4. Zmienna liczba argumentów (H3: `*args` i `**kwargs`; H3: Rozpakowanie w wywołaniu)
5. Parametry tylko pozycyjne i tylko nazwane — na końcu kompaktowa tabela typowych komunikatów błędów (admonition, nie osobny H2)

**Zależności pojęciowe.** Wprowadza: parametr i argument (za glosariuszem), argument pozycyjny i nazwany; wartość domyślna ewaluowana raz przy `def`, `__defaults__` (udokumentowany atrybut funkcji — jedno zdanie); współdzielenie obiektu domyślnego, idiom `None`; przekazywanie referencji do obiektu, modyfikacja w miejscu a ponowne przypisanie parametru; pakowanie do krotki (`*args`) i słownika (`**kwargs`), rozpakowanie w wywołaniu; parametr tylko pozycyjny i tylko nazwany, pełna kolejność pięciu rodzajów. Korzysta z: strona 1; modyfikowalność i `is` (rozdz. 3); referencje i kopiowanie, pakowanie, `zip(*pary)`, `print(*…)`, `dict(a=1)`, operator `|` (rozdz. 5); obiekt iterowalny (rozdz. 4).

**Kluczowe przykłady.** `przedstaw(imie, wiek, miasto="Kraków")` pozycyjnie, przez nazwę i `SyntaxError: positional argument follows keyword argument`; `i = 5; def f(arg=i)` po zmianie `i` daje 5, `f.__defaults__` → `(5,)`; `SyntaxError: parameter without a default follows parameter with a default`; `dodaj(x, lista=[])` daje `[1, 2]` dwukrotnie, wersja z `None` daje `[1]` i `[2]`; `dopisz`/`zastap`/`dolacz`/`nowa` (append, przypisanie, `+=` w miejscu, konkatenacja tworzy nowy obiekt); `zwieksz(n)` na `int`; `fun(par1, *par, **keypar)`; `przedstaw(*dane)`, `przedstaw(**opis)`, `list(range(*[3, 6]))`, `TypeError: __main__.przedstaw() argument after ** must be a mapping, not list`; `help(len)` → `len(obj, /)`, `help(sorted)`; `podziel(a, b, /)` i `polacz(*, sep)` z komunikatami; kolizja `fun(nazwa, **kwds)` i naprawa przez `/`; `g(a, b=0, /, c=1, *args, d, e=2, **kwargs)`.

**Źródła.** Repozytorium: `PythonNotatki.txt` 2072–2126, 2166–2258 (s. 60–63; stary komunikat SyntaxError zastąpiony); `Wyklad_04.txt` sl. 7–12, 17 (błędna teza „`+=` dla list tworzy nowy obiekt”); `Wyklad_03.txt` sl. 35; `lab4.txt` sl. 1–2, 5. Zewnętrzne: Language Reference *Function definitions* (domyślne ewaluowane raz; gramatyka `/` i `*`), *Calls*; tutorial *More on Defining Functions*; glosariusz; FAQ (*Why are default values shared between objects?*, *How do I write a function with output parameters?*); datamodel (`__defaults__`, `__kwdefaults__`); PEP 570; PEP 3102; PEP 8 (odstępy przy `=`).

**Odsyłacze do domknięcia.** `05-typy-zlozone/krotka.md:20` (`*args`) i `:128` (rozpakowanie w wywołaniu) → sekcja 4; `05-typy-zlozone/slownik.md:56` (`**kwargs`) → sekcja 4. Teksty: „…omawia strona [Argumenty i parametry](../06-funkcje/argumenty-i-parametry.md)”.

**Odłożone.** Słownik domyślny jako pamięć podręczna → nota przy memoizacji na stronie 7; `inspect.signature`, `argparse`, `sys.argv` → rozdz. 7; `lab4` sl. 7 (`py -0p`) → osobny etap rozdz. 1; `lambda` z pełną gramatyką parametrów → strona 4.

### 3. `zasieg-nazw-i-domkniecia.md` — Zasięg nazw i domknięcia

**Cel.** Czytelnik rozumie, gdzie Python szuka nazwy (zasięg lokalny, otaczający, globalny, wbudowany) i dlaczego przypisanie w funkcji czyni nazwę lokalną w całym jej ciele; poznaje funkcje zagnieżdżone i zmienne wolne, deklaracje `global` i `nonlocal` jako wyjątek od reguły, buduje pojęcie domknięcia i rozpoznaje pułapkę późnego wiązania.

**Kolejność H2.**
1. Przestrzenie nazw i zasięgi (H3: Przestrzeń wbudowana i przesłanianie nazw; na końcu bardzo krótka nota „Dla dociekliwych” o `globals()` i `locals()` — dwa–trzy zdania, bez rozbudowanego przykładu)
2. Nazwy lokalne i UnboundLocalError
3. Funkcje zagnieżdżone i zmienne wolne
4. Deklaracje global i nonlocal
5. Domknięcia (krótka nota „Dla dociekliwych” o `__closure__` jako szczególe implementacyjnym)
6. Pułapka późnego wiązania

**Zależności pojęciowe.** Wprowadza: przestrzeń nazw, zasięg, reguła LEGB jako skrót zwyczajowy, przesłanianie; wiązanie ustalane w czasie kompilacji, `UnboundLocalError`; funkcja zagnieżdżona, zmienna wolna, zmienna domknięcia, zwracanie funkcji (minimalnie); `global`, `nonlocal`; domknięcie, fabryka funkcji; późne wiązanie i obejście wartością domyślną. Korzysta z: nazwa jako referencja, `del`, `+=` na `int` (rozdz. 3); słownik, kopia płytka, złożenia (rozdz. 5); funkcja jako obiekt (strona 1); wartość domyślna, modyfikacja w miejscu a przypisanie (strona 2). Przykłady wyłącznie przez `def` — `lambda` dopiero na stronie 4.

**Kluczowe przykłady.** Cztery poziomy nazwy `x` z `print(len)`; przesłonięcie `list` i naprawa przez `del`; `licznik += 1` bez deklaracji → `UnboundLocalError: cannot access local variable 'licznik' where it is not associated with a value`; `print(x)` przed lokalnym przypisaniem; `dane.append(3)` bez `global` działa; niewidoczność funkcji wewnętrznej (`NameError`, nazwy dobrane bez podpowiedzi „Did you mean”); `global` na liczniku modułu; `nonlocal` w funkcji otaczającej; `test_zasiegu()` z tutoriala (trzy rodzaje przypisania); `mnoznik(k)` jako fabryka; `licznik()` ze stanem przez `nonlocal` (dwa niezależne liczniki); `zrob_fib()` ze słownikiem modyfikowanym w miejscu bez `nonlocal`; `zew()()` widzi bieżące wiązanie; pętla tworząca trzy funkcje `def` → `[2, 2, 2]`, obejścia `f(i=i)` i fabryka → `[0, 1, 2]`.

**Źródła.** Repozytorium: `PythonNotatki.txt` 2683–2839 (s. 70–75; kod ze zrzutów odtworzony; `sys.__dict__` z 3.8 pominięty; `__builtins__.list` → `del list`; „`locals()` kopiuje obiekty” → migawka słownika), 2131–2175; `Wyklad_04.txt` sl. 13–16, 22–23, 37 (korekta: `+=` wiąże nazwę lokalnie), 39–40; `lab4.txt` sl. 4; `lab8.txt` sl. 1. Zewnętrzne: Language Reference *Naming and binding* (executionmodel), *The global statement*, *The nonlocal statement*; tutorial *Python Scopes and Namespaces* (źródło właściwe dla „LEGB”); PEP 227; PEP 3104; FAQ (*Why am I getting an UnboundLocalError…*, *Why do lambdas defined in a loop…*); datamodel (`__closure__`); glosariusz (*namespace*, *nested scope*, *free variable*, *closure variable*); dokumentacja `builtins`, `globals()`, `locals()` (PEP 667).

**Odsyłacze do domknięcia.** `03-nazwy-typy/nazwy-i-slowa-kluczowe.md:14` (`global`, `nonlocal`) — tekst uzgodniony jak na stronie 1.

**Odłożone.** `import builtins` → rozdz. 7; przestrzeń modułu i `__main__` → rozdz. 7; zasięg klasy → rozdz. 10; silnia z funkcją pomocniczą → strona 5; `functools.partial` → rozdz. 7; `dis` → rozdz. 13.

### 4. `funkcje-jako-obiekty.md` — Funkcje jako obiekty

**Cel.** Czytelnik traktuje funkcję jako pełnoprawny obiekt: przekazuje ją jako argument (wywołanie zwrotne), przechowuje w kolekcjach, rozpoznaje obiekty wywoływalne; poznaje `lambda` jako wyrażenie tworzące anonimowy obiekt funkcji (nie jako „lepszą krótką funkcję”), stosuje funkcje klucza w `sorted`/`min`/`max` i rozumie, że `map()` i `filter()` zwracają jednorazowe iteratory, zwykle mniej czytelne niż złożenia.

**Kolejność H2.**
1. Funkcje pierwszej klasy
2. Obiekty wywoływalne
3. Wyrażenie lambda
4. Funkcja klucza w sorted, min i max
5. Funkcje map() i filter() (`map(strict=True)` jako krótka nota 3.14; jedno zdanie o stylu funkcyjnym i funkcji czystej)

**Zależności pojęciowe.** Wprowadza: funkcja pierwszej klasy, funkcja wyższego rzędu, wywołanie zwrotne, tablica rozdzielcza; `callable()`, `iter(obiekt_wywoływalny, wartownik)`; wyrażenie `lambda`, nazwa `<lambda>`; funkcja klucza; `map()`/`filter()` jako iteratory klasy `map`/`filter`, `filter(None, …)`. Korzysta z: obiekt funkcji, `__name__` (strona 1); gramatyka parametrów (strona 2); domknięcie, `nonlocal`, późne wiązanie (strona 3); iterator, `next`, `StopIteration` (rozdz. 4); `sorted` z `key`, `items()`, `get`, porównywanie krotek, złożenia, wartości fałszywe (rozdz. 5); `input()` (rozdz. 2).

**Kluczowe przykłady.** `zastosuj(abs, [-1, -2])`, `zastosuj(str.upper, …)`; `przetwarzaj(dane, print)`; lista funkcji i słownik akcji; `callable(kwadrat), callable(len), callable(str), callable(42)`; `TypeError: 'int' object is not callable`; wartownik: licznik zbudowany jako domknięcie z `nonlocal` (bez `global`) oraz `iter(input, "koniec")`; `lambda x: x + 1` jako obiekt, wywołanie natychmiastowe, pełna gramatyka parametrów, `[(lambda: i) for i in range(3)][0]()` → 2 (potwierdzenie późnego wiązania); traceback z `in <lambda>` (`ZeroDivisionError: division by zero`); `sorted(slowa, key=ostatnia_litera)` i z `lambda`, klucz krotkowy `(len(s), s)`; słownik po wartościach, `max(oceny, key=oceny.get)`; obiekt `map`, `type(m)`, wyczerpanie po `list(m)`, `map(round, …, range(1, 4))`, `ValueError` przy `strict=True`; `filter(None, …)`; to samo zadanie przez `map`+`filter` i przez złożenie.

**Źródła.** Repozytorium: `PythonNotatki.txt` 2374–2482 (s. 65–66; komunikat „division by zero”; `dis` odłożone), 2566–2681 (s. 67–68; „obiekt mapy – generatora” → iterator; `reduce` → zdanie); `Wyklad_04.txt` sl. 19–21, 36, 42 (wywołanie zwrotne bez `try/except`), 47. Zewnętrzne: glosariusz (*callable*, *lambda*, *key function*); Language Reference *Lambdas*, *Calls*; dokumentacja `callable()`, `iter()`, `map()`, `filter()`, `sorted()`; Sorting HOWTO; tutorial *Lambda Expressions*; PEP 8 (przypisanie lambdy do nazwy; E731); FAQ (lambdy w pętli); przegląd *Functional Programming Modules*.

**Odsyłacze do domknięcia.** `05-typy-zlozone/lista.md:398` (własne `key`, `lambda`) → sekcja 4; `05-typy-zlozone/lista.md:117` (`iter(callable, sentinel)`) → sekcja 2; `05-typy-zlozone/zlozenia.md:45` → tekst uzgodniony ze stroną 6: „Drugim sposobem tworzenia generatorów są [funkcje generatorowe](../06-funkcje/funkcje-generatorowe.md) ze słowem kluczowym `yield`; funkcje `map()` i `filter()` omawiamy na stronie [Funkcje jako obiekty](../06-funkcje/funkcje-jako-obiekty.md).”; `03-nazwy-typy/nazwy-i-slowa-kluczowe.md:14` (`lambda`) — tekst uzgodniony.

**Odłożone.** `functools.reduce`/`partial`, `operator`, `itertools` → rozdz. 7 (jedno zdanie zapowiedzi); `dis` → rozdz. 13; `__call__` i klasy wywoływalne → rozdz. 10–11; wywołanie zwrotne z `try/except` → rozdz. 8; `sys.getrefcount`, `weakref` → rozdz. 10/13; `iter(partial(f.read, 64), b'')` → rozdz. 9.

### 5. `rekurencja.md` — Rekurencja

**Cel.** Czytelnik rozumie rekurencję jako wywołanie funkcji przez samą siebie, w którym każde wywołanie ma własną przestrzeń lokalną; wskazuje przypadek bazowy i krok rekurencyjny; porównuje wersję rekurencyjną z iteracyjną (Fibonacci — koszt wykładniczy pokazany zliczaniem wywołań); stosuje rekurencję do struktur zagnieżdżonych; rozpoznaje `RecursionError` i wie, że limit (w CPythonie domyślnie 1000 ramek) można odczytać i zmienić przez moduł `sys` — kod w rozdz. 7.

**Kolejność H2.**
1. Przypadek bazowy i krok rekurencyjny (H3: Funkcja pomocnicza w funkcji zewnętrznej)
2. Rekurencja a iteracja — ciąg Fibonacciego
3. Rekurencja na strukturach zagnieżdżonych (bez wieży Hanoi)
4. Limit rekurencji i RecursionError
5. Dla dociekliwych: eliminacja rekurencji ogonowej (krótko)

**Zależności pojęciowe.** Wprowadza: funkcja rekurencyjna, przypadek bazowy, krok rekurencyjny, ramka wywołania (prozą); koszt wykładniczy (jedno zdanie); spłaszczanie listy; `RecursionError`, limit rekurencji, skrót „[Previous line repeated N more times]”; rekurencja ogonowa, akumulator. Korzysta z: `def`/`return` (strona 1); wartości domyślne niemodyfikowalne (strona 2); przestrzeń lokalna, funkcje zagnieżdżone, domknięcie z `nonlocal` (strona 3); `isinstance()` (rozdz. 3); listy zagnieżdżone, `[1, 2, [...]]` (rozdz. 5); `for`, `a, b = b, a + b` (rozdz. 4); traceback (rozdz. 2).

**Kluczowe przykłady.** `silnia(n)` z komentarzami „przypadek bazowy”/„krok rekurencyjny”; `silnia_slad(n, glebokosc=0)` z wcięciem śladu (osobna nazwa, `silnia` nienaruszona); `silnia_bezpieczna(n)` z zagnieżdżoną `pomocnicza(k)` (PDF s. 60; błąd sygnalizowany przez `None` — wyjątki w rozdz. 8); `fib(n)` i `fib_iter(n)`; zliczanie wywołań przez domknięcie `fib_z_licznikiem()` zwracające parę funkcji (`nonlocal`, bez `global`): 177, 21 891, 2 692 537 dla n = 10, 20, 30; `splaszcz(lista)` z `isinstance` i `extend`; `odliczaj(n)` bez przypadku bazowego jako skrypt `odliczaj.py` z tracebackiem i skrótem powtórzeń; granica silni wyłącznie w formie skryptu (997 i 998 działają, 999 i 1000 zgłaszają `RecursionError` — ramka modułu liczy się do limitu; w konsoli interaktywnej granica jest niższa, bo ramki konsoli również się liczą — szczegół implementacyjny); lista zagnieżdżona w sobie `L.append(L)` i `splaszcz(L)`; `silnia_ogon(n, akumulator=1)` nadal wyczerpuje limit.

**Źródła.** Repozytorium: `PythonNotatki.txt` 2063–2070 (fib z wartownikiem −1 → `n < 2`), 1424–1438, 2133–2142; `Wyklad_04.txt` sl. 28 (czas fib(40) — nie cytujemy), 30, 31 (Hanoi i quicksort pominięte); `lab4.txt` 62–112 („O(2n)” → 2ⁿ); `lab6.txt`. Zewnętrzne: dokumentacja `RecursionError`, `sys.getrecursionlimit()` (wartość domyślna nieudokumentowana — 1000 to wartość CPythona), What's New 3.12 (limit dotyczy wyłącznie ramek Pythona), moduł `traceback` (skracanie powtórzeń), tutorial *Defining Functions* (lokalna tablica symboli przy każdym wywołaniu), executionmodel; wpis Guido van Rossuma *Tail Recursion Elimination* (2009) jako źródło pomocnicze.

**Odsyłacze do domknięcia.** `05-typy-zlozone/lista.md:49` → wyłącznie zamiana komentarza `TODO` na odsyłacz z zachowaniem zdania o odczycie i zmianie limitu w module `sys`: „…omawiamy w rozdziale [6. Funkcje](../06-funkcje/rekurencja.md)”; dygresja o eliminacji rekurencji ogonowej pokryta sekcją 5.

**Odłożone.** Kod `sys.getrecursionlimit()`/`setrecursionlimit()` → rozdz. 7 (jawna nota na stronie); memoizacja → strona 7; `try/except RecursionError` → rozdz. 8; wieża Hanoi, quicksort, pomiary czasu → rozdz. 13 lub pominięcie; `fib(n, l=None)` (lab4) → pominięte.

### 6. `funkcje-generatorowe.md` — Funkcje generatorowe

**Cel.** Czytelnik odróżnia funkcję generatorową od obiektu generatora oraz od wyrażenia generatorowego i od iteratorów `map()`/`filter()`; rozumie, że `yield` zawiesza wykonanie, a `next()` je wznawia; zna jednorazowość i leniwość pokazane zachowaniem programu; pisze generatory nieskończone, potoki i delegację `yield from`. Domyka model iteratora z rozdziałów 4–5.

**Kolejność H2 (rdzeń).**
1. Funkcja generatorowa a obiekt generatora
2. yield i next(): zawieszenie i wznowienie wykonania
3. Jednorazowość i leniwość — pokazane momentem wykonania kodu (komunikaty „obliczam n” wypisywane dopiero przy pobieraniu), częściową konsumpcją i porównaniem z funkcją budującą całą listę; bez `sys.getsizeof()` i bez liczb bajtów
4. Generatory nieskończone
5. Potoki generatorów (H3: Delegacja yield from)

`return` w funkcji generatorowej wspomniane jednym zdaniem jako zakończenie iteracji; `StopIteration.value`, `send()`, `throw()`, `close()` poza rdzeniem — jedno zdanie zapowiedzi (rozdz. 15).

**Zależności pojęciowe.** Wprowadza: funkcja generatorowa, obiekt generatora, `yield`; zawieszenie i wznowienie, zachowanie stanu lokalnego; jednorazowość; leniwość; generator nieskończony i przerwanie odbioru przez `break`; potok; `yield from`. Korzysta z: `iter()`, `next()`, `StopIteration`, `range`, `while True`, `break` (rozdz. 4); wyrażenie generatorowe, złożenia (rozdz. 5); `def`, `return`, `__name__` (strona 1); `*args` (strona 2); spłaszczanie listy (strona 5); `map()`/`filter()` jako iteratory (strona 4); `split`, `startswith` (rozdz. 3).

**Kluczowe przykłady.** `odliczanie(n)` z `print("start")`/`print("koniec")`: `type(odliczanie)` → `function`, wywołanie nie wypisuje „start”, `type(g)` → `generator`; krokowe `next(g)` aż do `StopIteration`; `kwadraty(it)`: `iter(g) is g`, `list(g)` dwukrotnie (`[0, 1, 4]`, `[]`), dwa niezależne obiekty, `sum()`/`max()`; leniwość: generator z `print(f"obliczam {n}")` a funkcja z listą — kolejność komunikatów przy `next()` i częściowej konsumpcji; typ wyrażenia generatorowego identyczny z typem obiektu z funkcji generatorowej, `type(map(str, [1]))` → `map` (jeden wiersz kontrastu, szczegóły na stronie 4); `naturalne(start=0)` bez końca, po przerwaniu przy 5 kolejne `next()` daje 6; `len(g)` → `TypeError: object of type 'generator' has no len()`; potok `parzyste(kwadraty(naturalne()))` → 0, 4, 16; potok wyrażeń generatorowych na liście wierszy dziennika; `polacz(*iterowalne)` i `splaszcz(zagniezdzona)` z `yield from`.

**Źródła.** Repozytorium: `Wyklad_08.txt` 339–486 (sl. 18–24; `open()` → lista wierszy; `send()` jako kontekst historyczny — poza rdzeniem), `Wyklad_04.txt` 620–682 (sl. 32–34; `list(...)[:5]` materializuje cały potok — nota), `PythonNotatki.txt` 1012–1069, 2579 (błędne „generator” dla `range` i `map`). Zewnętrzne: Language Reference *Yield expressions*, datamodel *Generator functions*; glosariusz (*generator*, *generator iterator*, *generator expression*); stdtypes *Generator Types*; dokumentacja `next()`, `map()`, `filter()`; tutorial *Generators*, *Generator Expressions*; PEP 255; PEP 380; PEP 289.

**Odsyłacze do domknięcia.** `04-sterowanie/petle-i-iteratory.md:97–100` (strona z markerami aktywności — wyłącznie tekst odsyłacza): „…oraz w rozdziale [6. Funkcje](../06-funkcje/funkcje-generatorowe.md)”; `05-typy-zlozone/zlozenia.md:45` — tekst uzgodniony ze stroną 4, komentarz `TODO` usunięty; `03-nazwy-typy/nazwy-i-slowa-kluczowe.md:14` (`yield`) — tekst uzgodniony.

**Odłożone.** `itertools.islice`/`chain`/`count` → rozdz. 7; potok czytający plik → rozdz. 9; `StopIteration.value`, `send()`, `throw()`, `close()`, korutyny → rozdz. 15; `__iter__` jako generator w klasie → rozdz. 11; pomiar pamięci `sys.getsizeof()` → rozdz. 13; `gi_frame`, `yield` w złożeniach → pominięte.

### 7. `dekoratory.md` — Dekoratory

**Cel.** Czytelnik rozumie dekorator jako zwykłą funkcję, która przyjmuje funkcję i zwraca funkcję opakowującą (domknięcie), a składnię `@` jako skrót zapisu `f = deko(f)`; pisze poprawną funkcję opakowującą z `*args`/`**kwargs` i `return`; stosuje dekorator do rejestrowania, zliczania i memoizacji; zna koszt (utrata `__name__`/`__doc__`) i wie, że właściwym rozwiązaniem jest `functools.wraps` z rozdz. 7; zna kolejność składania. Bez importów.

**Kolejność H2.**
1. Od funkcji do dekoratora (H3 w progresji: funkcja jako obiekt; funkcja przyjmująca funkcję; funkcja zwracająca funkcję; domknięcie opakowujące i ręczne przypisanie `powitanie = z_ramka(powitanie)`; składnia `@`)
2. Anatomia dekoratora (wzorzec `opakowana(*args, **kwargs)` z `return`; antyprzykłady: brak `return`, sztywna sygnatura)
3. Przykłady zastosowań (H3: Rejestrowanie wywołań; H3: Zliczanie wywołań — `nonlocal`; H3: Memoizacja ciągu Fibonacciego — słownik w domknięciu; nota o słowniku w wartości domyślnej jako świadomym użyciu jednorazowej ewaluacji)
4. Tożsamość funkcji opakowanej (utrata `__name__`, `__doc__`, `help()` pokazana prostą funkcją opakowującą; bez ręcznego kopiowania atrybutów jako rozwiązania; zapowiedź `functools.wraps` po modułach)
5. Wiele dekoratorów i kolejność
6. Dla dociekliwych: dekorator z argumentami

**Zależności pojęciowe.** Wprowadza: dekorator, funkcja opakowująca (ang. *wrapper*), cukier składniowy `@`; wzorzec `opakowana(*args, **kwargs)` + `return f(*args, **kwargs)`; memoizacja, stan w domknięciu; `!r` w f-stringu (jedno zdanie przy pierwszym użyciu); `__qualname__` (jedno zdanie); składanie dekoratorów; fabryka dekoratorów. Korzysta z: funkcja jako obiekt, `__name__`, `__doc__`, `help()` (strona 1); `*args`/`**kwargs` (strona 2); domknięcie, `nonlocal`, zwracanie funkcji, fabryka (strona 3); przekazywanie funkcji, `lambda` (strona 4); `fib` i koszt wykładniczy (strona 5); haszowalność, krotka jako klucz (rozdz. 5).

**Kluczowe przykłady.** `wykonaj(f, imie)`, `bez_zmian(f)`; `z_ramka(f)` z `opakowana(imie)`, ręczne przypisanie, potem `@z_ramka`; `z_ramka(lambda x: x.upper())("ab")` → `'AB'`; wersja ogólna `opakowana(*args, **kwargs)` z docstringiem; `zly(f)` bez `return` → `None`; `deko_bez(f)` ze sztywną sygnaturą → `TypeError: deko_bez.<locals>.opakowana() takes 0 positional arguments but 2 were given`; `rejestruj(f)` z `{wynik!r}`; `licz_wywolania(f)` z `nonlocal`; `zapamietuj(f)` — `fib(30)`, `fib(100)` natychmiast, 31 wywołań zamiast 2 692 537, `TypeError` dla argumentu-listy (niehaszowalny klucz); `powitanie.__name__` → `'opakowana'`, `__doc__` opakowania, `help(powitanie)` pokazuje `opakowana(*args, **kwargs)`; dekoratory `a` i `b` z komunikatami „stosuję b / stosuję a / a: przed / b: przed / funkcja / b: po / a: po”; `powtorz(3)`.

**Źródła.** Repozytorium: `PythonNotatki.txt` 2260–2372 (s. 63–65; wrapper bez `return` jako antyprzykład; `moje_dekoratory` → rozdz. 7; pakiet `decorator` i `warn_slow` pominięte; `wraps` → zapowiedź), 2478–2482; `Wyklad_04.txt` sl. 25, 26, 28, 37, 44, 45 (trik 1); `lab6.txt` sl. 1–2; `lab4.txt` sl. 3, 6–7. Zewnętrzne: Language Reference *Function definitions* (dekoratory ewaluowane przy definicji; równoważność `@f1(arg) @f2 def func` ≡ `func = f1(arg)(f2(func))`; od 3.9 dowolne wyrażenie); PEP 318; glosariusz (*decorator*); datamodel (atrybuty funkcji); dokumentacja `functools.wraps` i PEP 749 (od 3.14 kopiowany jest `__annotate__`) — wyłącznie do zapowiedzi.

**Odsyłacze do domknięcia.** Brak zapowiedzi z rozdz. 1–5 adresowanych wprost; domyka zapowiedzi wewnętrzne ze stron 2 (nota o wartości domyślnej), 4 (dekorowanie lambdy) i 5 (memoizacja).

**Odłożone.** `functools.wraps`, `__wrapped__`, `functools.cache`/`lru_cache` → rozdz. 7; dekorator pomiaru czasu → rozdz. 13 (bez wariantu w tym rozdziale); dekorator walidujący przez `raise` → rozdz. 8 (bez wariantu zwracającego `None`); dekorator z osobnego modułu, pakiet `decorator` → rozdz. 7 / pominięcie; `property`, `classmethod`, `staticmethod`, `dataclass`, dekoratory klas → rozdz. 10–12; „Ciąg Fibonacciego w czterech zapisach” (W04 sl. 50) → usunięte.

### 8. `index.md` — Wprowadzenie

Wstęp (dwa akapity): funkcja jako jednostka organizacji kodu i jednocześnie obiekt — nazwa funkcji jest referencją jak w rozdziale 3; rozdział rozwija wątki z rozdziałów 4–5 (iteratory → funkcje generatorowe, pakowanie → `*args`/`**kwargs`, funkcje klucza → `lambda`) i obywa się bez nowych modułów, które wracają w rozdziale 7. Następnie `---` i `## W tym rozdziale` z siedmioma pozycjami „Tytuł — tematy” w konwencji istniejących rozdziałów. Bez not „Powiązane laboratorium” i bez sekcji „Ściąga”.

## Zmiany w rozdziałach 1–5 (wyłącznie domknięcie zapowiedzi)

| Plik:linia | Zmiana | Uwagi |
|---|---|---|
| `01-instalacja/konfiguracja.md:102` | odsyłacz do `definiowanie-funkcji.md` (docstring) | tekst zapowiedzi → link |
| `02-konsola/pierwszy-skrypt.md:62` | odsyłacz do `definiowanie-funkcji.md` (docstring) | |
| `03-nazwy-typy/nazwy-i-slowa-kluczowe.md:14` | jeden uzgodniony tekst z czterema odsyłaczami | jedna edycja |
| `04-sterowanie/wyrazenia-warunkowe.md:86` | odsyłacz do `definiowanie-funkcji.md` (`return`) | strona z markerami aktywności: tylko tekst, bez zmian nagłówków i slotu |
| `04-sterowanie/petle-i-iteratory.md:97–100` | odsyłacz do `funkcje-generatorowe.md` (`yield`) | jw. |
| `05-typy-zlozone/lista.md:49` | `TODO` → odsyłacz do `rekurencja.md`, zdanie o `sys` zachowane | |
| `05-typy-zlozone/lista.md:117` | `TODO` → odsyłacz do `funkcje-jako-obiekty.md` | |
| `05-typy-zlozone/lista.md:398` | `TODO` → odsyłacz do `funkcje-jako-obiekty.md` | |
| `05-typy-zlozone/krotka.md:20`, `:128` | `TODO` → odsyłacze do `argumenty-i-parametry.md` | |
| `05-typy-zlozone/slownik.md:56` | `TODO` → odsyłacz do `argumenty-i-parametry.md` | |
| `05-typy-zlozone/zlozenia.md:45` | `TODO` → uzgodniony tekst z dwoma odsyłaczami | |
| `docs/index.md`, `mkdocs.yml` | pozycja „6. Funkcje” w spisie i w nav (etykiety = H1 podstron, index jako „Wprowadzenie”) | nav rośnie wraz z powstającymi stronami |

Nie wykonujemy innych zmian w rozdziałach 1–5 (osobne etapy według `PLAN_ROZWOJU.md`, sekcja 6).

## Checklista weryfikacyjna (każda strona, przed odbiorem)

1. Wszystkie deterministyczne przykłady uruchomione na `.venv` (Python 3.14.7); wyniki, tracebacki i `repr` wpisane z uruchomienia, nie z pamięci ani ze źródeł.
2. Brak mechanizmów z późniejszych rozdziałów: `import` poza modułami znanymi z rozdz. 1–5 (a w tym rozdziale żaden nowy), `try/except`, `open()`, `class`, `functools`, `annotationlib`, `sys.getrecursionlimit()`, `sys.getsizeof()`, `time`.
3. Kolejność wewnątrz rozdziału: strona używa wyłącznie pojęć ze stron wcześniejszych i z rozdziałów 1–5; odsyłacze w przód tylko jako zapowiedzi prozą.
4. Brak `global` w przykładach diagnostycznych; liczniki przez domknięcie z `nonlocal`.
5. `map()`/`filter()` nazywane iteratorami; „generator” tylko dla funkcji generatorowej / obiektu generatora / wyrażenia generatorowego.
6. Adnotacje: bez sprawdzania typów w czasie wykonania, leniwa ewaluacja pokazana zachowaniem, bez `annotationlib`/`__annotate__`.
7. Terminologia i docstringi zgodne z zasadami na początku tego pliku; „funkcja opakowująca (ang. *wrapper*)” przy pierwszym użyciu; nazwa `opakowana` w kodzie.
8. Konwencje `CLAUDE.md`: nagłówki rzeczownikowe, ≤ 6 H2, bloki kodu z `title=` albo `.no-copy`, admonitions z polskimi tytułami, cudzysłowy „…”, terminy angielskie kursywą z „ang.”, `python -m pip` (jeśli w ogóle), klawisze przez `++…++`.
9. Szczegóły CPythona (adresy, nazwy klas iteratorów, wartość domyślna limitu rekurencji, granice zależne od ramek konsoli) oznaczone jako szczegół implementacyjny.
10. `mkdocs build` bez ostrzeżeń oraz `mkdocs build -f mkdocs.clean.yml`; po edycji stron rozdziału 4 z markerami aktywności — interactive build jako test kontraktu, bez zmian `section_id`, `data-activity-slot` i `activities/**`.
11. Każdy odsyłacz względny prowadzi do istniejącego pliku i sekcji; teksty odsyłaczy współdzielonych (`nazwy-i-slowa-kluczowe.md:14`, `zlozenia.md:45`) identyczne z ustalonymi wyżej.
12. Długość strony w granicach ok. 150–225 linii; sekcje opcjonalne oznaczone „Dla dociekliwych” w tytule.
