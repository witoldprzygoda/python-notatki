# Rozdział 11. Model danych — metody specjalne i protokoły — plan implementacyjny

Skondensowany projekt stron rozdziału 11 według `PLAN_ROZWOJU.md` (sekcja 4, „11. Model danych — metody specjalne i protokoły”) i `DEVELOPMENT_WORKFLOW.md`. Branch: `content/11-model-danych` (z `dev` po integracji rozdziału 10, commit `4a36e05`). Stan odniesienia: Python 3.14.7 w `.venv` projektu (Windows), MkDocs Material. Rozdział realizowany autonomicznie na polecenie autora z 14 IX 2026 („bez mojego potwierdzania, rób całkowicie autonomicznie”) — decyzje poniżej są decyzjami redakcyjnymi zgodnymi z dotychczasowymi ustaleniami autora (rozdziały 6–10).

## Decyzje redakcyjne (14 IX 2026)

1. **Struktura:** index + 5 podrozdziałów w kolejności: przeciążanie operatorów → protokoły kolekcji i wywołania → protokół iteracji → menedżery kontekstu i obiekty plikopodobne → deskryptory. Etykieta nav i H1 ostatniej strony „Deskryptory” bez dopisku „(dla dociekliwych)” (konwencja z rozdziałów 7, 9 i 10); charakter uzupełniający zaznaczony w pierwszym akapicie i w `index.md`.
2. **Zakres:** metody specjalne obsługujące operatory (arytmetyka, odbite, złożone, jednoargumentowe, porównania z `NotImplemented`, `__hash__`), kolekcje (`__len__`, `__bool__`, `__getitem__`/`__setitem__`/`__delitem__`, `__contains__`), wywołanie (`__call__`), iterację (`__iter__`/`__next__`, `__iter__` jako generator, protokół sekwencji), kontekst (`__enter__`/`__exit__`), formatowanie (`__format__`), obiekt plikopodobny (`write()`, `flush()`), deskryptory (`__get__`/`__set__`/`__delete__`/`__set_name__`, dane a niedane, kolejność wyszukiwania, `__getattr__` jako ostatni etap wyszukiwania, funkcje i `property` jako deskryptory). Bez metaklas, `__init_subclass__`, `__class_getitem__`, `__getattribute__` (poza wzmianką), `__slots__` (rozdział 10), klas abstrakcyjnych i `collections.abc` poza krótką wzmianką (→ zaawansowane mechanizmy), bez `__eq__` dla klas modyfikowalnych używanych jako klucze (ostrzeżenie prozą).
3. **Przykłady i nazwy:** klasy ze źródeł pod polskimi nazwami zgodnie z konwencją książki: `Wektor2D`, `Zespolona`, `Liczba`, `Zamowienie`, `Plansza` (kółko i krzyżyk z laboratorium 5, zamiast `TicTacToeBoard`), `Odliczanie`, `Stoper` (jak `stoper()` z rozdziału 8), `Pisarz`, `Nieujemna`/`TylkoDoOdczytu` (deskryptory), `Mnoznik` (`__call__`). Żadnych not o laboratorium. Docstringi klas jako frazy rzeczownikowe, metod — w konwencji rozdziału 6.
4. **`NotImplemented`** jako obowiązkowy element każdej metody dwuargumentowej: zwracany dla nieobsługiwanego typu, z opisem mechanizmu odbicia (`__radd__`) i faktu, że od Pythona 3.14 użycie `NotImplemented` w kontekście logicznym zgłasza `TypeError` (bez etykiety „nowość”); `NotImplemented` ≠ `NotImplementedError`.
5. **`__eq__` i `__hash__`:** reguła „`__eq__` bez `__hash__` ustawia `__hash__ = None`” pokazana wykonywalnie (`TypeError: unhashable type`), `__hash__` z krotki atrybutów biorących udział w porównaniu; `functools.total_ordering` jako skrót po jawnym `__lt__` (`TypeError` dla `<=` bez `total_ordering` pokazany).
6. **Domyślne zachowania klasy `object`** wymienione jawnie tam, gdzie mają znaczenie: `__eq__` przez tożsamość, `__ne__` odwraca `__eq__`, `__bool__` → `__len__` → `True`, `__contains__` → `__iter__` → `__getitem__`, `__format__` przyjmuje tylko pustą specyfikację (`TypeError` dla `{obj:>6}`), `__iadd__` → `__add__`.
7. **Iteracja:** pętla `for` rozpisana na `iter()`/`next()`/`StopIteration` (rozdział 4 wprowadził iterator i `StopIteration`, rozdział 6 — generatory); iterator jako klasa (`Odliczanie`) → oddzielenie kolekcji od iteratora (nowy iterator z każdego `__iter__`) → `__iter__` jako funkcja generatorowa (zalecane) → protokół sekwencji przez `__getitem__` z `IndexError` (dla dociekliwych, krótko) → `iter(obiekt_wywoływalny, wartownik)` z instancją mającą `__call__` (domyka wątek z rozdziału 6).
8. **Menedżer kontekstu jako klasa:** `Stoper` z `__enter__` zwracającym `self` i `__exit__(typ, wartość, ślad)`, porównanie z `@contextmanager` z rozdziału 8 (ten sam efekt, klasa gdy potrzebny stan lub wielokrotne użycie), tłumienie wyjątku przez `return True` z ostrzeżeniem, `pytest.raises()` z rozdziału 8 jako przykład tłumienia. Obiekt plikopodobny `Pisarz` z `write()` (i `flush()`, bo `print(flush=True)` go wymaga) domyka zapowiedź z rozdziału 9; porównanie z `io.StringIO`. Zapowiedź `Lock` z `with` → współbieżność.
9. **Deskryptory** wyłącznie jako wyjaśnienie mechanizmu znanego z rozdziału 10: protokół, `__set_name__`, deskryptor danych a niedanych, kolejność wyszukiwania atrybutu (deskryptor danych → `__dict__` instancji → deskryptor niedanych → `__dict__` klas w `__mro__` → `__getattr__` → `AttributeError`), walidator `Nieujemna` (z rozdziału 7 wykładów), `TylkoDoOdczytu` z notatek, mini-`property` napisane własną klasą, funkcje jako deskryptory niedanych (wiązanie metod, `types.MethodType` z rozdziału 10). Bez `__getattribute__` poza jednym zdaniem.
10. **`singledispatchmethod`** zamiast `multipledispatch` z wykładu (pakiet spoza biblioteki standardowej) — krótka sekcja „dla dociekliwych” na stronie 1 z rejestracją przez adnotacje (3.7) i uwagą, że Python nie ma przeciążania metod po typach argumentów.
11. **Ślady wywołań** z uruchomienia jako `.text .no-copy`; wartości zależne od komputera (adresy, czasy stopera) maskowane albo opisane; `dir(42)` wypisany w skróconej postaci REPL z zaznaczeniem, że lista jest dłuższa.
12. **Szacunek rozmiaru** z `PLAN_ROZWOJU.md` (750–850 linii) orientacyjny; spodziewane ok. 1400–1700 linii.
13. **Zapowiedzi w przód** prozą po temacie z `TODO` i wpisem w `PLAN_ROZWOJU.md` (lista na końcu planu); rejestrowane w sekcjach 12, 13, 15 i 16 przy commicie planu.

## Zasady obowiązujące w całym rozdziale

- Żaden przykład nie wymaga mechanizmu wprowadzanego później: bez dziedziczenia wielokrotnego, `abc`, `dataclass`, metaklas, wątków, NumPy (`__matmul__` własną klasą, NumPy tylko prozą jako zapowiedź). Klasy zgodnie z rozdziałem 10 (`__init__`, `__repr__` w każdej klasie przykładowej, `@property`, `super()`); wyjątki zgodnie z rozdziałem 8.
- Moduły biblioteki standardowej użyte w kodzie: `math` (`hypot`, `atan2`), `functools` (`total_ordering`, `singledispatchmethod`), `time` (`perf_counter`), `io` (`StringIO` w porównaniu), `contextlib` (`contextmanager` w porównaniu), `types` (`MethodType` jednym zdaniem), `operator` co najwyżej prozą. `collections.abc` jednym akapitem prozą.
- Kolejność wewnątrz rozdziału: strona 1 korzysta z rozdziałów 3 (operatory, `==`/`is`, `hash()` z rozdziału 5), 10; strona 2 po 1 (`NotImplemented`, `__add__` w `Zamowienie`); strona 3 po 2 (`__getitem__` w protokole sekwencji, `__call__` w `iter()`); strona 4 po 1–3 (`__format__` po `__str__` z 10, `Pisarz` po `__call__`); strona 5 po 1–4 (funkcje jako deskryptory po metodach związanych z 10; `property`). Strona 5 jest uzupełniająca.
- Pojęcia wprowadzane jawnie w miejscu pierwszego użycia: „metoda specjalna” (rozdział 10 — tu rozszerzenie), „przeciążanie operatorów (ang. *operator overloading*)”, „operacja odbita (ang. *reflected*)”, „operacja złożona / w miejscu (ang. *in-place*)”, „porównania bogate (ang. *rich comparison*)” — w książce „metody porównań”, „obiekt wywoływalny” (rozdział 6), „protokół” (rozdział 8 wprowadził „protokół menedżera kontekstu”; tu definicja ogólna: umowa co do nazw metod), „obiekt iterowalny (ang. *iterable*)” a „iterator” (rozdział 4), „protokół sekwencji”, „obiekt plikopodobny (ang. *file-like object*)”, „deskryptor” (rozdział 10 — nazwa; tu definicja), „deskryptor danych / niedanych (ang. *data / non-data descriptor*)”, „wiązanie (ang. *binding*)”.
- Terminologia: „metoda specjalna” (nie „magiczna”; „dunder” raz, w nawiasie); „przeciążanie operatorów”; „metoda odbita”; „metoda złożona”; „obiekt iterowalny” / „iterator”; „menedżer kontekstu”; „deskryptor”; „podrozdział” dla części książki.
- Nagłówki w formie rzeczownikowej z nazwami w kodzie (np. „Operacje odbite — `__radd__`”, „Metody `__enter__` i `__exit__`”).
- Konwencje `CLAUDE.md`: bloki `python title="plik.py"`, `{ .python .no-copy }` dla REPL, `{ .text .no-copy }` dla wyników; admonitions z polskimi tytułami; cudzysłowy „…”; terminy angielskie z „ang.” przy pierwszym użyciu; nazwy plików bez kolizji z biblioteką standardową (nie: `operator.py`, `types.py`, `io.py`, `time.py`, `functools.py`, `contextlib.py`, `abc.py`).
- Weryfikacja: `scripts/verify_page.py` na `.venv` (3.14.7); `--mask` dla adresów i czasów (`\d+\.\d{3} s`); sesje REPL osobno.
- `index.md` w układzie rozdziałów 6–10. Odsyłacze do rozdziałów 1–10 od razu; zmiany w rozdziałach 1–10 (tabela na końcu) zbiorczo po ukończeniu rozdziału. Strony rozdziału 4 z markerami aktywności nie są dotykane.

## Strony

### 1. `operatory.md` — Przeciążanie operatorów

**Cel.** Czytelnik wie, że operatory i funkcje wbudowane są realizowane przez metody specjalne, definiuje arytmetykę (z operacjami odbitymi i złożonymi), porównania z `NotImplemented`, `__hash__` spójny z `__eq__` i zna `total_ordering`.

**Kolejność H2/H3.**
1. Operator jako metoda specjalna (`(3).__add__(4)`, `"abc".__len__()`, `dir(42)` skrócone, `3.__add__` → `SyntaxError: invalid decimal literal`; tabela kategorii metod specjalnych z odsyłaczami do sekcji rozdziału; Python nie ma przeciążania metod po typach argumentów — druga definicja nadpisuje pierwszą)
2. Arytmetyka — `__add__`, `__sub__`, `__mul__` (`Wektor2D` z `__repr__`, `__add__`, `__sub__`, `__mul__` przez skalar, `__neg__`, `__abs__` z `math.hypot`; tabela operator → metoda)
3. Wartość `NotImplemented` i operacje odbite — `__radd__`, `__rmul__` (`Liczba` z notatek: `Liczba + int`, `int + Liczba`; mechanizm: lewy operand zwraca `NotImplemented` → Python próbuje metody odbitej prawego; `TypeError: unsupported operand type(s)`, gdy obie zwrócą `NotImplemented`; od 3.14 `bool(NotImplemented)` → `TypeError`; `NotImplemented` a `NotImplementedError`)
4. Operacje złożone — `__iadd__` (`Zamowienie` z notatek: `__add__` zwraca nowy obiekt, `__iadd__` zmienia i zwraca `self`; pułapka braku `return` → `None`; bez `__iadd__` Python używa `__add__` i przypisuje)
5. Porównania — `__eq__`, `__lt__` i `functools.total_ordering` (`Student` z ocenami; `__ne__` z `__eq__` automatycznie; `TypeError: '<=' not supported` bez `total_ordering`; `Zespolona` z `__eq__`, `__add__` i `NotImplemented`)
6. Metoda `__hash__` (domyślne `__eq__`/`__hash__` z `object` przez tożsamość; `__eq__` bez `__hash__` → `__hash__ = None`, `TypeError: unhashable type`; `__hash__` z krotki atrybutów; obiekty modyfikowalne z `__eq__` bez `__hash__`; `Wektor2D` w zbiorze)
7. Operator `@` i `singledispatchmethod` (dla dociekliwych) (`__matmul__` iloczyn skalarny; NumPy prozą; `singledispatchmethod` z rejestracją przez adnotacje)

**Główne przykłady.** `dunder-na-literalach.py`; `wektor2d.py`; `liczba.py` (odbicie); `zamowienie-iadd.py`; `bez-return-iadd.py`; `student-porownania.py`; `zespolona.py`; `hash-demo.py`; `matmul.py`; `dispatch.py`.

**Wymagane zachowania (3.14.7, sprawdzone sondą).** `(3).__add__(4.5)` → `NotImplemented`; `bool(NotImplemented)` → `TypeError: NotImplemented should not be used in a boolean context`; `L(1) + "a"` → `TypeError: unsupported operand type(s) for +: 'L' and 'str'`; `"a" + L(1)` → `TypeError: can only concatenate str (not "L") to str`; `C(1) <= C(2)` bez `__le__` → `TypeError: '<=' not supported between instances of 'C' and 'C'`; klasa z `__eq__` → `__hash__` is `None`, `hash()` → `TypeError: unhashable type: 'P'`; `v += w` przy `__iadd__` bez `return` → `v` jest `None`; `__iadd__` nieobecne → `__add__` i przypisanie.

**Źródła.** `PythonNotatki.txt` 3485–3745 (s. 89–95); `Wyklad_06.txt` sl. 27–29, 31–37, 39; `lab5.txt` sl. 3; docs: *Data model* (emulating numeric types, rich comparison, `__hash__`), *Built-in Constants* (`NotImplemented`, „Changed in version 3.14”), `functools` (`total_ordering`, `singledispatchmethod`).

**Domyka.** `10 reprezentacja-i-wlasciwosci.md` i `dziedziczenie.md` (`__eq__`/`__hash__`); `07-moduly/functools.md:224` (`total_ordering`, `singledispatch` — wzmianka).

**Rozmiar.** ok. 380–440 linii.

### 2. `kolekcje-i-wywolania.md` — Protokoły kolekcji i wywołania

**Cel.** Czytelnik implementuje `len()`, `bool()`, indeksowanie z wycinkami i indeksem krotkowym, `in` oraz `__call__`, i rozumie protokół jako umowę co do nazw metod.

**Kolejność H2/H3.**
1. Protokół jako umowa (definicja; rozdział 8 wprowadził protokół menedżera kontekstu; `len()`/`bool()`/`[]`/`in`/wywołanie jako protokoły; typowanie kacze jednym zdaniem — ang. *duck typing*)
2. Metody `__len__` i `__bool__` (`Zamowienie`; `__len__` musi zwrócić `int` ≥ 0 — `TypeError`, `ValueError`; `bool()` → `__bool__` → `__len__` → `True`)
3. Metody `__getitem__`, `__setitem__` i `__delitem__` (`Zamowienie` delegujące do listy: indeks ujemny, wycinek jako obiekt `slice`, `IndexError`, `TypeError` dla złego typu; H3: Indeks krotkowy — `Plansza` 3×3 `plansza[1, 1] = "O"`; H3: Protokół sekwencji jako efekt uboczny — iteracja i `in` przez `__getitem__` z `IndexError`, jedno zdanie z odesłaniem do strony 3)
4. Metoda `__contains__` (`in` bez `__contains__` → `__iter__` → `__getitem__`; własna implementacja dla szybkości lub innej semantyki)
5. Metoda `__call__` (`Mnoznik(3)(10)`; obiekt wywoływalny z pamięcią stanu a domknięcie z rozdziału 6; `callable()`; `iter(obiekt, wartownik)` z instancją mającą `__call__` — domyka zapowiedź z rozdziału 6; dekorator jako klasa jednym przykładem)
6. Klasy abstrakcyjne kolekcji — `collections.abc` (dla dociekliwych) (jeden akapit prozą + `isinstance(obj, Sized)`; szczegóły → zaawansowane mechanizmy)

**Główne przykłady.** `zamowienie.py` (`__len__`, `__bool__`, `__getitem__`, `__contains__`, `__add__`, `__iadd__`), `plansza.py`, `bledy-len.py`, `mnoznik.py`, `licznik-call.py` (`iter(Licznik(), 4)`), `dekorator-klasa.py`.

**Wymagane zachowania.** `len()` z `__len__` zwracającym `str` → `TypeError: 'str' object cannot be interpreted as an integer`; `-1` → `ValueError: __len__() should return >= 0`; `z[1::-1]` → `['pilka', 'rower']`; `z["x"]` → `TypeError: list indices must be integers or slices, not str`; `2 in Tylko()` przez `__iter__`; `list(iter(Licznik(), 4))` → `[1, 2, 3]`.

**Źródła.** `PythonNotatki.txt` 3538–3620 (s. 91–92); `Wyklad_06.txt` sl. 30–31; `lab5.txt` sl. 4; `06-funkcje/funkcje-jako-obiekty.md` (obiekty wywoływalne, `iter(callable, sentinel)`); docs: *Emulating container types*, `__call__`, `collections.abc`.

**Domyka.** `10 definicja-klasy.md` (`__call__` na instancji); wątek `iter(callable, sentinel)` z rozdziału 6 (bez `TODO`).

**Rozmiar.** ok. 300–350 linii.

### 3. `iteracja.md` — Protokół iteracji

**Cel.** Czytelnik rozumie, jak pętla `for` korzysta z `__iter__` i `__next__`, pisze iterator jako klasę, oddziela kolekcję od iteratora, korzysta z `__iter__` jako funkcji generatorowej i zna typowe błędy.

**Kolejność H2/H3.**
1. Obiekt iterowalny a iterator (definicje od strony metod: iterowalny ma `__iter__` zwracające iterator; iterator ma `__next__` i `__iter__` zwracające `self`; `iter()`/`next()` wywołują te metody; rozdział 4 i 6 jako punkt wyjścia)
2. Pętla `for` od środka (rozpisanie na `iter()`, `while True`, `next()`, `except StopIteration`; `next(it, wartość_domyślna)`)
3. Iterator jako klasa — `Odliczanie` (`__iter__` zwraca `self`, `__next__` z `StopIteration`; stan w atrybutach; jednorazowość — drugie `list()` puste)
4. Oddzielenie kolekcji od iteratora (`Kolejka`/`Talia` z `__iter__` zwracającym nowy obiekt iteratora — wielokrotne przejście, dwie pętle zagnieżdżone po tej samej kolekcji)
5. Metoda `__iter__` jako funkcja generatorowa (najkrótsza poprawna implementacja — `yield` z rozdziału 6; `type(iter(obj))` → `generator`; kiedy klasa iteratora jest jednak potrzebna)
6. Protokół sekwencji przez `__getitem__` (dla dociekliwych) (klasa tylko z `__getitem__` i `IndexError`; `iter()` tworzy iterator sekwencji; starszy mechanizm, w nowym kodzie `__iter__`)
7. Typowe błędy (zużyty iterator — generator wyrażeniowy z rozdziału 6, `list()` na nieskończonym iteratorze — `itertools.islice` z rozdziału 7, `__iter__` zwracające listę zamiast iteratora → `TypeError: iter() returned non-iterator of type 'list'`)

**Główne przykłady.** `for-od-srodka.py`, `odliczanie.py`, `talia.py` (kolekcja + osobny iterator), `talia-generator.py`, `sekwencja-getitem.py`, `bledy-iteracji.py`.

**Wymagane zachowania.** `list(Odl(3))` → `[3, 2, 1]`, drugie → `[]`, `iter(it) is it` → `True`; `type(iter(Gen(3))).__name__` → `'generator'`; `list(Seq())` → `[0, 10, 20]`; `__iter__` zwracające listę → `TypeError: iter() returned non-iterator of type 'list'` (sprawdzić brzmienie przy pisaniu).

**Źródła.** `Wyklad_08.txt` sl. 14–17, 41; `04-sterowanie/petle-i-iteratory.md#iteratory`; `06-funkcje/funkcje-generatorowe.md`; docs: *Iterator Types* (stdtypes), `__iter__`, `__reversed__`.

**Domyka.** `10 index.md` (iteratory jako klasy); wątek iteratora z rozdziału 4 (bez `TODO`).

**Rozmiar.** ok. 280–330 linii.

### 4. `menedzery-kontekstu.md` — Menedżery kontekstu i obiekty plikopodobne

**Cel.** Czytelnik pisze menedżer kontekstu jako klasę, wie, kiedy wybrać klasę, a kiedy `@contextmanager`, tworzy obiekt plikopodobny dla `print(file=)` i definiuje `__format__`.

**Kolejność H2/H3.**
1. Metody `__enter__` i `__exit__` (protokół z rozdziału 8 od strony klasy; sygnatura `__exit__(self, typ, wartosc, slad)` — trzy `None` bez wyjątku; `Stoper` z `time.perf_counter()` i atrybutem `czas` odczytywanym po bloku; `__enter__` zwraca `self`)
2. Tłumienie wyjątku — wartość zwracana przez `__exit__` (`return True` tłumi; `Ignoruj(TypeError)` jako własny `contextlib.suppress`; ostrzeżenie: tłumić wyłącznie oczekiwane wyjątki; `pytest.raises()` z rozdziału 8 jako menedżer tłumiący)
3. Klasa a dekorator `contextlib.contextmanager` (ten sam `Stoper` w obu postaciach; klasa, gdy menedżer ma stan po bloku lub jest używany wielokrotnie; `@contextmanager`, gdy wystarczy prosty przebieg)
4. Obiekt plikopodobny — metoda `write()` (`Pisarz` z notatek: `write()` gromadzi tekst, `getvalue()`; `print(file=pisarz)`; `flush()` wymagane przy `print(flush=True)` — `AttributeError` bez niej; porównanie z `io.StringIO` z rozdziału 9; obiekt plikopodobny jako protokół, nie typ)
5. Metoda `__format__` (f-string `{obj:spec}` → `format(obj, spec)` → `__format__`; domyślne `object.__format__` tylko z pustą specyfikacją — `TypeError: unsupported format string passed to ...__format__`; `Wektor2D.__format__` delegujące specyfikację do składowych `float`; `__str__` a `__format__` w f-stringach — domyka zapowiedź z rozdziału 10)
6. Zapowiedź blokad — jedno zdanie (`with blokada:` w programach wielowątkowych → współbieżność)

**Główne przykłady.** `stoper-klasa.py`, `ignoruj.py`, `stoper-dwie-postacie.py`, `pisarz.py`, `format-wektor.py`.

**Wymagane zachowania.** `__exit__` bez wyjątku otrzymuje `None None None`; `return True` tłumi — „po with” wypisane; `print("x", file=object())` → `AttributeError: 'object' object has no attribute 'write'`; `print(..., file=p, flush=True)` bez `flush()` → `AttributeError: 'Pisarz' object has no attribute 'flush'`; `f"{F():>6}"` → `TypeError: unsupported format string passed to F.__format__`; czasy stopera maskowane.

**Źródła.** `Wyklad_05.txt` sl. 29; `Wyklad_07.txt` sl. 35; `PythonNotatki.txt` 5423–5488 (s. 125–126, `Pisarz`); `08-wyjatki/with-i-contextlib.md` (protokół, `stoper()`); `09-wejscie-wyjscie/print-i-strumienie.md:204`, `bytes-i-pliki-binarne.md#pliki-w-pamieci`; docs: `__exit__`, `__format__` („Changed in version 3.4”), `contextlib.suppress`.

**Domyka.** `08-wyjatki/with-i-contextlib.md:114` (`TODO`), `09-wejscie-wyjscie/print-i-strumienie.md:204` (`TODO`), `10 reprezentacja-i-wlasciwosci.md` (`__format__`).

**Rozmiar.** ok. 280–330 linii.

### 5. `deskryptory.md` — Deskryptory

**Cel (strona uzupełniająca).** Czytelnik rozumie protokół deskryptorów i kolejność wyszukiwania atrybutów, pisze walidator wielokrotnego użytku i wie, że `property`, metody klasy i zwykłe metody działają dzięki deskryptorom.

**Kolejność H2/H3.**
1. Protokół deskryptorów (`__get__(self, obiekt, wlasciciel=None)`, `__set__`, `__delete__`, `__set_name__`; deskryptor jako atrybut klasy, nie instancji; `Sledzacy` z notatek wypisujący wywołania)
2. Walidator wielokrotnego użytku — `Nieujemna` (`__set_name__` zapamiętuje nazwę, wartość w `__dict__` instancji pod nazwą z podkreśleniem; `Produkt` z `cena` i `ilosc`; porównanie z `@property` — jedna klasa zamiast powtarzania metod zapisu)
3. Deskryptor tylko do odczytu — `TylkoDoOdczytu` (z notatek; `AttributeError` w `__set__`)
4. Deskryptory danych i niedanych — kolejność wyszukiwania atrybutu (definicje; przykład z wpisem w `__dict__` instancji przesłaniającym deskryptor niedanych, ale nie danych; pełna kolejność: deskryptor danych z klas w `__mro__` → `__dict__` instancji → deskryptor niedanych / atrybut klasy → `__getattr__` → `AttributeError`; `__getattr__` jednym przykładem; `__getattribute__` jednym zdaniem)
5. Klasa `property` jako deskryptor (mini-`Wlasciwosc` z `__get__`/`__set__` i `fget`/`fset` odtwarzająca `@property` z rozdziału 10; `__set_name__` zamiast `doc`)
6. Funkcje jako deskryptory — metody związane (funkcja ma `__get__`; `Klasa.__dict__["metoda"]` to funkcja, `obiekt.metoda` to metoda związana — `types.MethodType` z rozdziału 10; `classmethod`/`staticmethod` jako deskryptory jednym akapitem)

**Główne przykłady.** `sledzacy.py`, `nieujemna.py`, `tylko-do-odczytu.py`, `kolejnosc-wyszukiwania.py`, `getattr-demo.py`, `wlasciwosc.py`, `metody-zwiazane.py`.

**Wymagane zachowania.** `__set_name__` wywołane przy tworzeniu klasy (wydruk przed utworzeniem instancji); `x.__dict__["d"] = ...` przesłania deskryptor niedanych, nie danych; `property` ma `__get__` i `__set__`, `classmethod`/`staticmethod` tylko `__get__`, funkcja tylko `__get__`; `f.__get__(x)` → `method`.

**Źródła.** `PythonNotatki.txt` 3747–3941 (s. 95–98); `Wyklad_07.txt` sl. 28–30; `10 reprezentacja-i-wlasciwosci.md#klasa-property-dla-dociekliwych`; docs: *Implementing Descriptors*, *Invoking Descriptors*, `__set_name__`, *Descriptor HowTo Guide*.

**Domyka.** `10 atrybuty-i-metody.md` i `reprezentacja-i-wlasciwosci.md` (mechanizm deskryptora za `property` i `classmethod`).

**Rozmiar.** ok. 280–330 linii.

### 6. `index.md` — Wprowadzenie

Wstęp (dwa–trzy akapity): metody specjalne z rozdziału 10 (`__init__`, `__repr__`, `__str__`) jako początek większej całości — **modelu danych** (ang. *data model*) Pythona, czyli zbioru metod specjalnych, przez które język realizuje operatory, funkcje wbudowane i instrukcje; `(3).__add__(4)` jako dowód, że typy wbudowane grają w tę samą grę; „protokół” jako umowa co do nazw; co rozdział domyka (iteratory z 4, `iter(callable, wartownik)` z 6, menedżer z 8, `Pisarz` z 9, `__eq__`/`__hash__`/`__format__`/`__call__`/deskryptory z 10); podrozdział „Deskryptory” jako uzupełniający. Następnie `---` i `## W tym rozdziale` z pięcioma pozycjami.

## Nawigacja

```yaml
  - 11. Model danych — metody specjalne i protokoły:
      - Wprowadzenie: 11-model-danych/index.md
      - Przeciążanie operatorów: 11-model-danych/operatory.md
      - Protokoły kolekcji i wywołania: 11-model-danych/kolekcje-i-wywolania.md
      - Protokół iteracji: 11-model-danych/iteracja.md
      - Menedżery kontekstu i obiekty plikopodobne: 11-model-danych/menedzery-kontekstu.md
      - Deskryptory: 11-model-danych/deskryptory.md
```

Pozycja w `docs/index.md`: „11. [Model danych — metody specjalne i protokoły](11-model-danych/index.md) — przeciążanie operatorów, protokoły kolekcji i wywołania, iteracja, menedżery kontekstu i obiekty plikopodobne, deskryptory”.

## Kolejność tworzenia stron i odbiór

Cykl jak w rozdziale 10: research w dokumentacji 3.14 → napisanie → `scripts/verify_page.py` → `mkdocs build` (oba pliki konfiguracyjne) → trzy niezależne recenzje (styl stron 1–3, styl stron 4–5 i index, adwersarialna kontrola faktów) → naniesienie → commit. Kolejność: 1 `operatory.md`, 2 `kolekcje-i-wywolania.md`, 3 `iteracja.md`, 4 `menedzery-kontekstu.md`, 5 `deskryptory.md`, 6 `index.md`. Klasy `Wektor2D` i `Zamowienie` wracają na kilku stronach — definicje spójne (`Wektor2D(x, y)` z `float`, `Zamowienie(koszyk, klient)`).

## Zapowiedzi w przód (do zarejestrowania w `PLAN_ROZWOJU.md`)

- Rozdział 12: klasy abstrakcyjne i `collections.abc` (strona 2), dekoratory klas i `__init_subclass__` (strona 5 — jeśli padnie), klasy danych z automatycznym `__eq__`/`__hash__`/`__repr__` (strona 1), metaklasy i `__getattribute__` (strona 5).
- Rozdział 13: koszt `total_ordering` i deskryptorów (strona 1, 5 — jedno zdanie).
- Rozdział 14: `__matmul__` w NumPy, `__getitem__` z krotką indeksów w tablicach (strony 1–2).
- Rozdział 15: `with blokada:` (strona 4).
- Rozdział 16: adnotacje w `singledispatchmethod`, `typing.Protocol` (strony 1–2 — jedno zdanie).

## Zmiany w rozdziałach 1–10 (wyłącznie domknięcie zapowiedzi, zbiorczo po ukończeniu rozdziału 11)

| Plik:linia | Zmiana | Uwagi |
|---|---|---|
| `08-wyjatki/with-i-contextlib.md:114` | `TODO` (menedżer jako klasa) → odsyłacz do `menedzery-kontekstu.md#metody-__enter__-i-__exit__` | slug sprawdzić |
| `09-wejscie-wyjscie/print-i-strumienie.md:204` | `TODO` (obiekt z `write()`) → odsyłacz do `menedzery-kontekstu.md#obiekt-plikopodobny-metoda-write` | |
| `10-klasy/definicja-klasy.md:297` | `TODO` (`__call__`) → odsyłacz do `kolekcje-i-wywolania.md#metoda-__call__` | |
| `10-klasy/reprezentacja-i-wlasciwosci.md:72` i `:272` | zdanie o `__format__` → odsyłacz do `menedzery-kontekstu.md#metoda-__format__`; `TODO` (deskryptor) → odsyłacz do `deskryptory.md` | |
| `10-klasy/dziedziczenie.md:358` | `TODO` (`__eq__`/`__hash__`) → odsyłacz do `operatory.md#metoda-__hash__` | |
| `10-klasy/index.md:5` | `TODO` (model danych) → odsyłacz do `../11-model-danych/index.md`; `TODO` o zaawansowanych mechanizmach pozostaje | |
| `07-moduly/functools.md:224` | wzmianka o `total_ordering`/`singledispatch` → odsyłacz do `operatory.md` | brzmienie dopasować |
| `docs/index.md`, `mkdocs.yml` | pozycja „11. Model danych — metody specjalne i protokoły” | |

Pozostają bez zmian `TODO` wskazujące na klasy danych, zaawansowane mechanizmy obiektowe, narzędzia analizy typów, wydajność, współbieżność, pandas i tkinter.

## CONTENT HANDOFF (rozbieżności ze źródłami)

(a) W06 sl. 29 i notatki s. 95: „Python wywoła `bool()` na wyniku” — od 3.14 wynik `NotImplemented` w kontekście logicznym zgłasza `TypeError`, więc metody porównań muszą zwracać `NotImplemented` tylko tam, gdzie interpreter je odbierze; (b) W06 sl. 39 i notatki s. 91: `multipledispatch` (pakiet zewnętrzny) → `functools.singledispatchmethod`; (c) W06 sl. 32: `total_ordering` bez `__repr__` i bez `NotImplemented`; (d) W07 sl. 35 i W05 sl. 29: `time.time()` / `import time` wewnątrz metod → `time.perf_counter()` i import na poziomie modułu; (e) notatki s. 125: ręczna podmiana `sys.stdout` — rozdział 9 pokazał `redirect_stdout()`; (f) notatki s. 126: klasa `Pisarz` bez `flush()` — `print(flush=True)` zgłasza `AttributeError`; (g) notatki s. 97: kolejność wyszukiwania pomija `__getattr__`; (h) W06 sl. 31: `__hash__` zdefiniowane bez `NotImplemented` w `__eq__`; (i) W06 sl. 34: `__sub__` przez `self + (-other)` — w książce bezpośrednio; (j) notatki s. 92: `zamowienie[1::-1]` opisane jako „slicing” bez wyjaśnienia obiektu `slice`.

## Checklista weryfikacyjna strony

1. Wszystkie deterministyczne przykłady przez `scripts/verify_page.py` (3.14.7); czasy i adresy maskowane.
2. Brak mechanizmów z późniejszych rozdziałów: `abc` (poza wzmianką), `dataclass`, metaklasy, wątki, NumPy w kodzie.
3. Kolejność wewnątrz rozdziału (1 → 2 → 3 → 4 → 5; strona 5 uzupełniająca); pojęcia wprowadzone w miejscu pierwszego użycia; każda metoda dwuargumentowa zwraca `NotImplemented` dla obcego typu.
4. Spójne definicje `Wektor2D` i `Zamowienie`; `__repr__` w każdej klasie, której instancje są wypisywane (ustalenie recenzji: krótkie klasy demonstracyjne bez `__repr__`); nazwy plików bez kolizji z biblioteką standardową.
5. Konwencje `CLAUDE.md`; nagłówki rzeczownikowe; cudzysłowy „…”; „ang.” przy pierwszym użyciu.
6. `mkdocs build` bez ostrzeżeń oraz `mkdocs build -f mkdocs.clean.yml`.
7. Każdy odsyłacz względny prowadzi do istniejącego pliku i sekcji; zapowiedzi w przód z `TODO` i wpisem w `PLAN_ROZWOJU.md`.

## Checklista finalnego odbioru rozdziału

1. Sześć plików ukończonych; nav i `docs/index.md` kompletne; H1 = etykieta nav.
2. Zbiorcza redakcja terminologii (metoda specjalna, protokół, obiekt iterowalny/iterator, deskryptor danych/niedanych).
3. Tabela „Zmiany w rozdziałach 1–10” wykonana; w `docs/` nie pozostał `TODO` wskazujący na model danych.
4. Pełny przebieg weryfikacji: harness, sesje REPL, audyt kotwic, oba buildy, `git diff --check`.
5. Kontrola faktów zależnych od wersji: `NotImplemented` w kontekście logicznym (3.14), `singledispatchmethod` (3.8), rejestracja przez adnotacje (3.7), `__set_name__` (3.6), `object.__format__` (3.4).
6. `PLAN_ROZWOJU.md`: status „ukończony” z liczbą linii; CONTENT HANDOFF w raporcie końcowym.
7. Commit końcowy, integracja do `dev` i push — zgodnie z poleceniem autora o pełnej autonomii.
