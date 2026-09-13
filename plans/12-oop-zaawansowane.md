# Rozdział 12. Programowanie obiektowe — mechanizmy zaawansowane — plan implementacyjny

Skondensowany projekt stron rozdziału 12 według `PLAN_ROZWOJU.md` (sekcja 4, „12. Programowanie obiektowe — mechanizmy zaawansowane”) i `DEVELOPMENT_WORKFLOW.md`. Branch: `content/12-oop-zaawansowane` (z `dev` po integracji rozdziału 11, commit `5502692`). Stan odniesienia: Python 3.14.7 w `.venv` projektu (Windows), MkDocs Material. Rozdział realizowany autonomicznie na polecenie autora z 14 IX 2026 („Kontynuuj z rozdziałem 12. Autonomicznie. Proszę zwrócić uwagę na moje materiały źródłowe, gdzie np. szczegółowo rozpisano MRO z przykładami. Oczywiście wszystko ma być zweryfikowane.”).

## Decyzje redakcyjne (14 IX 2026)

1. **Struktura:** index + 5 podrozdziałów: dziedziczenie wielokrotne i MRO → mixiny, kompozycja i klasy abstrakcyjne → klasy danych (`dataclass`, `NamedTuple`, `Enum`) z `match`/`case` → wzorce projektowe → metaprogramowanie. Etykiety dwóch ostatnich stron bez dopisku „(dla dociekliwych)” (konwencja rozdziałów 7–11); charakter uzupełniający zaznaczony w pierwszych akapitach i w `index.md`.
2. **MRO według materiałów autora** (notatki s. 101–108, wykład 7 sl. 4–9, laboratorium 7): pełny rozpisany przykład algorytmu C3 na siedmiu klasach `O`, `F`, `E`, `D`, `C`, `B`, `A` z krokami `merge` (L[C], L[B], L[A]) oraz wariant `B(E, D)` dający `A B E C D F O`; `__mro__` i `mro()`; `super()` jako „następna klasa w MRO” (łańcuch `Baza`/`A`/`C`/`D` z wykładu); kooperatywne `__init__` z `**kwargs`; niespójne MRO `D(B, C)` z rozpisanym `merge` i quiz `X`/`Y`; sekcja uzupełniająca: śledzenie `__new__` i `__init__` w hierarchii `D(A, C, B, Baza)` z laboratorium 7 — przerwanie łańcucha przez `object.__new__(cls)`, `A(1)` samodzielnie kończące się `TypeError`, jawne `A.id(d)`, wariant `D(C, A)`. Nazwy klas z materiałów zachowane (jednoliterowe), bo o nie chodzi w przykładach.
3. **Korekta notatek (s. 106–107):** teza, że `object.__init__(self, x)` wywołane wprost „akceptuje i ignoruje dodatkowe argumenty”, jest nieprawdziwa — w Pythonie 3.14 (sonda) `object.__init__()` z nadmiarowym argumentem zgłasza `TypeError: object.__init__() takes exactly one argument (the instance to initialize)`, gdy klasa nadpisuje `__init__`; książka opisuje to zgodnie ze stanem faktycznym, bez wzmianki o dawnym zachowaniu. Terminy „unbound method call”, „rzutowanie” z notatek → „wywołanie metody przez klasę”, „wywołanie klasy z obiektem innej klasy jako argumentem”.
4. **Klasy abstrakcyjne:** `abc.ABC` z `@abstractmethod`, komunikat 3.12+ (`Can't instantiate abstract class X without an implementation for abstract method 'y'`), abstrakcyjna właściwość przez `@property` nad `@abstractmethod`, `super()` w metodzie abstrakcyjnej z implementacją (notatki s. 119), bez `abstractproperty` (przestarzałe od 3.3). Fabryka pojazdów z wykładu (sl. 38) uproszczona do jednej klasy abstrakcyjnej z właściwością, metodą klasy i statyczną.
5. **Klasy danych:** `@dataclass` z `field(default_factory=...)`, `__post_init__`, opcjami `frozen`, `order`, `slots`, `kw_only` (3.10) i regułami `__hash__` z dokumentacji; pułapka modyfikowalnej wartości domyślnej (`ValueError`); dziedziczenie klas danych (quiz z wykładu sl. 43 i `TypeError` przy polu bez wartości domyślnej po polu z domyślną); `asdict()`/`replace()`; zapis do JSON przez `asdict()` (domyka zapowiedź z rozdziału 9); `typing.NamedTuple` a `namedtuple` z rozdziału 7; `Enum`, `auto`, `IntEnum`, `StrEnum` (3.11); `match`/`case` z wzorcami klasowymi (`__match_args__`), strażnikami, sekwencjami i słownikami — rozszerzenie sekcji z rozdziału 4. Adnotacje typów zapisywane współcześnie (`list[float]`, nie `typing.List`).
6. **Protocol:** `typing.Protocol` z `@runtime_checkable` (3.8) jako sformalizowane typowanie kacze — krótka sekcja uzupełniająca na stronie 2 z uwagą, że sprawdzana jest obecność metod, nie sygnatury (3.12: `inspect.getattr_static`).
7. **Wzorce projektowe:** Fabryka z rejestrem (`@classmethod`), Strategia (klasy a funkcje pierwszej klasy), Obserwator (zapowiedź `bind` w tkinter), Singleton przez dekorator klasy (wariant przez `__new__` z rozdziału 10); wzorce jako idiomy, nie dogmat.
8. **Metaprogramowanie:** klasa jako instancja `type` (`__name__`, `__qualname__`, `__module__`, `__bases__`), `type(nazwa, bazy, słownik)` jako odpowiednik `class`, łańcuch `type.__call__` → `__new__` → `__init__` (metaklasa `Verbose` z wykładu), dekoratory klas, `__init_subclass__` (3.6) jako lekka alternatywa (rejestr fabryki), własna metaklasa z `__new__`/`__init__` (parametr `mcs`/`cls`), sztuczka z notatek: metaklasa z `__repr__` zwracającym `cls.__name__` do czytelnego wydruku MRO; tabela „kiedy nie metaklasa”; `eval()`/`exec()` jako przestroga z `ast.literal_eval()`. Listingi notatek o `inspect.getmembers()` i zmianie `__name__` (s. 111–114) pominięte jako dygresja bez wartości dydaktycznej — jedno zdanie, że `__name__` nie jest w `__dict__` klasy.
9. **Nazwy i przykłady:** klasy z materiałów pod ich nazwami (`Kaczka`, `Latajace`, `Plywajace`, `Figura`, `Kolo`, `Prostokat`, `Pojazd`, `Student`, `Punkt`, `Wersja`, `Kolor`, `Status`, `FabrykaPojazdow`, `Sortowanie`, `Wydarzenie`, `Sklep`, `Plugin`, `Meta`, `Verbose`); jednoliterowe klasy tylko w przykładach MRO. Bez not o laboratorium. Klasy główne z `__repr__` (`@dataclass` generuje własne).
10. **Ślady wywołań** z uruchomienia jako `.text .no-copy`; wydruki MRO jako listy nazw (`[k.__name__ for k in K.__mro__]`) zamiast `<class '__main__.A'>`.
11. **Szacunek rozmiaru** z `PLAN_ROZWOJU.md` (ok. 1100–1300 linii) orientacyjny; spodziewane ok. 1700–2000 linii.
12. **Zapowiedzi w przód** prozą z `TODO` i wpisem w `PLAN_ROZWOJU.md` (sekcje 13, 16, 18); rejestrowane przy commicie planu.

## Zasady obowiązujące w całym rozdziale

- Żaden przykład nie wymaga mechanizmu wprowadzanego później: bez wątków, NumPy, tkinter (Obserwator z funkcjami), narzędzi analizy typów (adnotacje tylko jako składnia `dataclass`/`NamedTuple`/`Protocol`). Klasy zgodnie z rozdziałami 10–11 (`__repr__`, `super()`, `@property`, `NotImplemented`).
- Moduły biblioteki standardowej w kodzie: `abc`, `dataclasses`, `typing` (`NamedTuple`, `Protocol`, `runtime_checkable`), `enum`, `json` (mixin i `asdict()`), `collections` (`namedtuple` w porównaniu), `ast` (`literal_eval`), `inspect` co najwyżej prozą.
- Kolejność wewnątrz rozdziału: strona 1 korzysta z 10 (dziedziczenie, `super()`, `__new__`); strona 2 po 1 (mixiny w hierarchii, MRO); strona 3 po 2 (`frozen` a `__hash__` z 11, `Enum` po klasach abstrakcyjnych nie wymaga); strona 4 po 2–3 (ABC w Fabryce i Strategii, `Enum` opcjonalnie); strona 5 po 1–4 (`__init_subclass__` z rejestrem z 4, metaklasa `Verbose` po `__new__`/`__init__` z 10). Strony 4–5 uzupełniające.
- Pojęcia wprowadzane jawnie: „dziedziczenie wielokrotne (ang. *multiple inheritance*)”, „problem diamentu (ang. *diamond problem*)”, „kolejność rozstrzygania metod (ang. *method resolution order*, MRO)” — nazwa z rozdziału 10, tu algorytm, „linearyzacja (ang. *linearization*)”, „algorytm C3”, „kooperatywne dziedziczenie (ang. *cooperative inheritance*)”, „mixin (ang. *mixin*)”, „klasa abstrakcyjna (ang. *abstract base class*, ABC)”, „metoda abstrakcyjna”, „typowanie kacze” (rozdział 11), „podtypowanie strukturalne (ang. *structural subtyping*)”, „klasa danych (ang. *data class*)”, „wyliczenie (ang. *enumeration*)”, „wzorzec klasowy (ang. *class pattern*)”, „strażnik (ang. *guard*)”, „wzorzec projektowy” (rozdział 10 — nazwa), „metaklasa (ang. *metaclass*)”, „metaprogramowanie (ang. *metaprogramming*)”.
- Nagłówki rzeczownikowe z nazwami w kodzie; konwencje `CLAUDE.md`; nazwy plików bez kolizji (nie: `abc.py`, `enum.py`, `typing.py`, `dataclasses.py`, `json.py`, `inspect.py`, `ast.py`).
- Weryfikacja: `scripts/verify_page.py` na `.venv` (3.14.7); adresy maskowane; `mkdocs build` (oba pliki); trzy recenzje; naniesienie; commit; domknięcie tabeli; status; integracja do `dev` i push (tryb autonomiczny).

## Strony

### 1. `dziedziczenie-wielokrotne.md` — Dziedziczenie wielokrotne i MRO

**Kolejność H2/H3.** 1. Wiele klas bazowych (składnia, kolejność w nawiasie, `isinstance()`); 2. Problem diamentu i kolejność rozstrzygania metod (`Zwierze`/`Latajace`/`Plywajace`/`Kaczka` z `super().__init__()` wywołanym raz; `__mro__`, `mro()`); 3. Algorytm C3 (definicja L[C] = C + merge(...); reguła czoła i ogona; rozpisane L[C], L[B], L[A] dla siedmiu klas; wariant `B(E, D)`); 4. Funkcja `super()` a MRO (łańcuch `Baza`/`A`/`C`/`D`: `super()` w `A` prowadzi do `C`; H3: Kooperatywne `__init__` z `**kwargs` — `Kaczka(zasieg=5, glebokosc=2)`); 5. Niespójne MRO (`D(B, C)` z rozpisanym `merge`, `TypeError: Cannot create a consistent method resolution order (MRO) for bases B, C`; quiz `A(X, Y)`, `B(Y, X)`, `C(A, B)`; zasada: klasy bardziej szczegółowe przed ogólnymi); 6. Śledzenie `__new__` i `__init__` w hierarchii (dla dociekliwych) (`Baza`, `A`, `B(Baza)`, `C(B)`, `D(A, C, B, Baza)` z laboratorium 7; wydruk `D(789)`; `object.__new__(cls)` w `Baza` kończy łańcuch `__new__`; `A(1)` samodzielnie → `TypeError` z `object.__init__()` — korekta notatek; `A.id(d)`, `Baza.id(d)`; `D2(C, A)` → `TypeError: A.__init__() missing 1 required positional argument: 'x'`).

**Główne przykłady.** `wiele-baz.py`, `diament.py`, `c3-siedem-klas.py` (wydruk `__mro__` obu wariantów), `super-mro.py`, `kaczka-kwargs.py`, `niespojne-mro.py` (dwa `try`/`except TypeError`), `sledzenie-new-init.py`.

**Wymagane zachowania (3.14.7, sonda).** `A.__mro__` → `A B C D E F O object`; wariant → `A2 B2 E C D F O object`; `TypeError: Cannot create a consistent method resolution order (MRO) for bases X, Y`; `Kaczka` z `**kwargs`: kolejność `Latajacy`, `Plywajacy`, `Zwierze`; `D(789)` wydruk: `-> A __new__ 789`, `-> Baza __new__`, `<- Baza __new__`, `<- A __new__`, `-> A __init__ 789`, `-> Baza __init__ 789`, `-- Baza __init__`, `<- Baza __init__`, `-- A __init__`, `<- A __init__`; `A(1)` → `TypeError: object.__init__() takes exactly one argument (the instance to initialize)`; `super().__new__(cls, *args)` w klasie bez własnego `__init__`... → w książce tylko `super().__new__(cls)`.

**Źródła.** `PythonNotatki.txt` 4138–4452 (s. 101–108); `Wyklad_07.txt` sl. 4–9, 44; `lab7.txt` sl. 1; docs: *Data model* (`__mro__`, `mro()`, `__init__`), *The Python 2.3 Method Resolution Order* (dokument historyczny, cytowany w notatkach), tutorial 9.5.1.

**Domyka.** `10 dziedziczenie.md:48` (`TODO` o zaawansowanych mechanizmach — MRO), `10 cykl-zycia-obiektu.md` (łańcuch `__new__` w hierarchii — bez `TODO`).

**Rozmiar.** ok. 420–500 linii.

### 2. `mixiny-i-abstrakcja.md` — Mixiny, kompozycja i klasy abstrakcyjne

**Kolejność H2/H3.** 1. Mixiny (`ReprMixin`, `JsonMixin` z `json.dumps(vars(self))` i `from_json()` — `json` z rozdziału 9; konwencja nazwy, brak `__init__`, kolejność w nawiasie); 2. Dziedziczenie, mixin czy kompozycja (tabela relacji is-a / acts-as / has-a; zasada z rozdziału 10); 3. Klasy abstrakcyjne — `abc.ABC` i `@abstractmethod` (`Figura` z `pole()`/`obwod()` abstrakcyjnymi i `opis()` zwykłą; `Kolo`, `Prostokat`; `TypeError` przy `Figura()` i przy niepełnej implementacji; H3: Abstrakcyjna właściwość — `@property` nad `@abstractmethod`; H3: Implementacja w metodzie abstrakcyjnej i `super()`); 4. Fabryka pojazdów (`Pojazd(ABC)` z właściwością `predkosc` z walidacją, `@classmethod utworz()` wybierający klasę pochodną ze słownika, `@staticmethod sprawdz_rok()`); 5. Typowanie kacze i `typing.Protocol` (dla dociekliwych) (`Czytelne` z `read()`, `@runtime_checkable`, `isinstance()`, obecność metod bez sygnatur, statyczna analiza → zapowiedź); 6. Zasady projektowania (SOLID jednym akapitem — pojedyncza odpowiedzialność, otwarte-zamknięte, podstawienie Liskov; DRY; tabela „Kompas OOP” z wykładu: potrzeba → mechanizm).

**Główne przykłady.** `mixiny.py`, `figury.py`, `figura-niepelna.py` (ślad), `wlasciwosc-abstrakcyjna.py`, `super-w-abstrakcyjnej.py`, `fabryka-pojazdow.py`, `protokol-czytelne.py`.

**Wymagane zachowania.** `TypeError: Can't instantiate abstract class Figura without an implementation for abstract methods 'obwod', 'pole'`; `... Prostokat without an implementation for abstract method 'obwod'`; `Figura.__abstractmethods__` → `frozenset({...})`; `isinstance(Plik(), Czytelne)` → `True`, `isinstance(3, Czytelne)` → `False`.

**Źródła.** `PythonNotatki.txt` 5008–5108 (s. 117–119); `Wyklad_07.txt` sl. 11–12, 14–16, 24–25, 38, 42, 45; docs: `abc`, `typing.Protocol`, `runtime_checkable`.

**Domyka.** `10 dziedziczenie.md:348` (kompozycja i wzorce — część o mechanizmach), `11 kolekcje-i-wywolania.md:311` (ABC), `10 index.md:5`, `11 index.md:5` (klasy abstrakcyjne).

**Rozmiar.** ok. 380–440 linii.

### 3. `klasy-danych.md` — Klasy danych — dataclass, NamedTuple i Enum

**Kolejność H2/H3.** 1. Dekorator `@dataclass` (zakładki: klasa ręczna z `__init__`/`__repr__`/`__eq__` a `@dataclass`; co generuje; `__match_args__`); 2. Funkcja `field()` i `__post_init__` (`default_factory`, `init=False`, `repr=False`, walidacja w `__post_init__`; `ValueError` dla `lista: list = []`); 3. Opcje `frozen`, `order`, `slots` i `kw_only` (`Wersja` z `order=True`; `frozen=True` → `FrozenInstanceError` i `__hash__`; tabela reguł `__hash__`; `slots=True` → rozdział 10; `kw_only`); 4. Klasy danych a dziedziczenie (quiz `A`/`B(A)`/`C(A)`; kolejność pól; `TypeError: non-default argument 'y' follows default argument 'x'`); 5. Funkcje `asdict()`, `replace()` i zapis do JSON (`json.dumps(asdict(obj))`, odczyt `Klasa(**dane)` — domyka rozdział 9); 6. `typing.NamedTuple` (a `namedtuple` z rozdziału 7; tabela `dataclass` / `NamedTuple` / zwykła klasa); 7. Wyliczenia — `Enum`, `auto`, `IntEnum`, `StrEnum` (`name`/`value`, `Kolor(1)`, `Kolor["ZIELONY"]`, iteracja, tożsamość, brak `<` dla `Enum`, `IntEnum` jako `int`, `StrEnum` jako `str` z `auto()` → nazwa małymi literami; `TypeError` dla powtórzonej nazwy; aliasy jednym zdaniem); 8. Dopasowanie `match`/`case` z klasami danych i wyliczeniami (wzorce klasowe `Punkt(x=0, y=0)`, pozycyjne przez `__match_args__`, strażnik `if`, wzorce sekwencji `[a, b, *reszta]` i odwzorowania `{"typ": t, **inne}`, `case Kolor.CZERWONY`, `case str() as s`, `case _` — rozszerzenie rozdziału 4).

**Główne przykłady.** `punkt-dataclass.py`, `student-field.py`, `mutable-default.py`, `wersja-opcje.py`, `dziedziczenie-dataclass.py`, `asdict-json.py`, `punkt-namedtuple.py`, `kolory-enum.py`, `match-klasy.py`.

**Wymagane zachowania (sonda).** `Punkt.__match_args__` → `('x', 'y', 'tagi')`; `hash(p)` dla zwykłej klasy danych → `TypeError: unhashable type`; `frozen`: `FrozenInstanceError: cannot assign to field 'major'`; `ValueError: mutable default <class 'list'> for field lista is not allowed: use default_factory`; `TypeError: non-default argument 'y' follows default argument 'x'`; `kw_only`: `TypeError: Konf.__init__() takes 1 positional argument but 2 were given`; `Kolor.CZERWONY == 1` → `False`, `Kolor.CZERWONY < Kolor.ZIELONY` → `TypeError: '<' not supported between instances of 'Kolor' and 'Kolor'`; `Tryb.JASNY == "jasny"` → `True`; `Enum` z powtórzoną nazwą → `TypeError: 'A' already defined as 1`.

**Źródła.** `Wyklad_07.txt` sl. 18–22, 27, 43; `Wyklad_05.txt` sl. 44; `07-moduly/biblioteka-standardowa.md` (`namedtuple`); `04-sterowanie/wyrazenia-warunkowe.md#pola-wyboru-match`; docs: `dataclasses` (parametry, reguły `__hash__`, dziedziczenie, „Changed in version 3.11: unhashable defaults”), `enum` (`StrEnum` 3.11, `auto`), `typing.NamedTuple` („Changed in version 3.14: super() unsupported”), PEP 634/636.

**Domyka.** `06 dekoratory.md:540` (`@dataclass`), `09 csv-i-json.md:226` (klasy danych do JSON), `07 biblioteka-standardowa.md:266` (zapowiedź klas danych — prozą), `11 operatory.md` (klasy danych z automatycznym `__eq__`/`__hash__` — bez `TODO`).

**Rozmiar.** ok. 450–520 linii.

### 4. `wzorce-projektowe.md` — Wzorce projektowe

**Kolejność H2/H3.** 1. Wzorce a idiomy Pythona (co to wzorzec projektowy — rozdział 10 nazwał Singleton; funkcje pierwszej klasy zastępują część wzorców); 2. Fabryka z rejestrem (`Pojazd(ABC)`, `Samochod`, `Rower`; `FabrykaPojazdow` ze słownikiem `_rejestr`, `@classmethod utworz()` i `zarejestruj()`; `ValueError` dla nieznanego typu); 3. Strategia (`Sortowanie(ABC)`, `SortowanieBabelkowe`, `SortowanieWbudowane`, `Sorter` z wymianą strategii; wersja z funkcjami zamiast klas); 4. Obserwator (`Wydarzenie` z `subskrybuj()`/`powiadom()`, `Sklep`; funkcje jako obserwatorzy; zapowiedź `bind` w tkinter); 5. Singleton przez dekorator klasy (`@singleton` z pamięcią instancji; porównanie z `__new__` z rozdziału 10; zastrzeżenia: stan globalny, testowalność, moduł jako alternatywa).

**Główne przykłady.** `fabryka-rejestr.py`, `strategia.py`, `strategia-funkcje.py`, `obserwator.py`, `singleton-dekorator.py`.

**Źródła.** `Wyklad_07.txt` sl. 32–34, 41, 42; `10 cykl-zycia-obiektu.md` (Singleton przez `__new__`); `06 funkcje-jako-obiekty.md`.

**Domyka.** `10 cykl-zycia-obiektu.md:83` (Singleton przez dekorator klasy), `10 dziedziczenie.md:348` (wzorce).

**Rozmiar.** ok. 300–360 linii.

### 5. `metaprogramowanie.md` — Metaprogramowanie

**Kolejność H2/H3.** 1. Klasa jako obiekt typu `type` (`type(Foo)`, `type(type)`, `__name__`, `__qualname__` dla klas zagnieżdżonych, `__module__`, `__bases__`; `__name__` poza `__dict__` klasy); 2. Funkcja `type()` z trzema argumentami (`type("Punkt", (), {...})` ≡ `class`; funkcja z zewnątrz jako metoda; klasa pochodna przez `type()`); 3. Łańcuch tworzenia obiektu — `type.__call__`, `__new__`, `__init__` (metaklasa `Verbose` z wykładu; `Foo(42)` z wydrukiem trzech kroków; nawiązanie do rozdziału 10); 4. Dekoratory klas (`@dodaj_repr` generujący `__repr__` z `vars()`; kolejność: klasa utworzona, potem zmieniona; `@total_ordering` i `@dataclass` jako dekoratory klas); 5. Metoda `__init_subclass__` (rejestr podklas `Plugin`; argumenty słowa kluczowego w nagłówku klasy; fabryka z rozdziału o wzorcach bez ręcznej rejestracji); 6. Własna metaklasa (`Meta(type)` z `__new__`/`__init__` dodającym atrybut; sztuczka z notatek: `__repr__` metaklasy → nazwy klas w wydruku `__mro__`; tabela „kiedy nie metaklasa”: `__init_subclass__`, dekorator klasy, `@dataclass`); 7. Funkcje `eval()` i `exec()` — przestroga (`ast.literal_eval()`; nigdy dla danych z zewnątrz).

**Główne przykłady.** `klasa-jako-obiekt-type.py`, `type-trzy-argumenty.py`, `verbose.py`, `dekorator-klasy.py`, `init-subclass.py`, `metaklasa.py`, `mro-czytelnie.py`, `literal-eval.py`.

**Wymagane zachowania (sonda).** `type(type)` → `<class 'type'>`; `"__name__" in Dyn.__dict__` → `False`; kolejność wydruków `Meta.__new__`, `Meta.__init__` przy definicji, `Meta.__call__`, `M.__new__`, `M.__init__` przy wywołaniu; `ast.literal_eval("__import__('os')")` → `ValueError: malformed node or string`.

**Źródła.** `PythonNotatki.txt` 4454–5006 (s. 108–117); `Wyklad_07.txt` sl. 26, 36–37, 41; `Wyklad_09.txt` sl. 29–30 (eval); docs: *Data model* (metaclasses, `__init_subclass__`, `type.mro`), `type()`, `ast.literal_eval`.

**Domyka.** `11 deskryptory.md:236` (`__getattribute__` — wzmianka przy metaklasach; metaklasy), `10 atrybuty-i-metody.md` (`__init_subclass__` — bez `TODO`), `10 index.md:5`, `11 index.md:5`.

**Rozmiar.** ok. 380–440 linii.

### 6. `index.md` — Wprowadzenie

Wstęp: od pojedynczej hierarchii z rozdziału 10 i protokołów z rozdziału 11 do projektowania — dziedziczenie wielokrotne z jego regułami, mixiny i klasy abstrakcyjne jako narzędzia kształtowania hierarchii, klasy danych jako codzienne narzędzie, wzorce i metaprogramowanie jako mechanizmy rzadkie; co rozdział domyka; strony 4–5 uzupełniające; zapowiedź narzędzi analizy typów (adnotacje w klasach danych i `Protocol`). `---`, `## W tym rozdziale` (5 pozycji).

## Nawigacja

```yaml
  - 12. Programowanie obiektowe — mechanizmy zaawansowane:
      - Wprowadzenie: 12-oop-zaawansowane/index.md
      - Dziedziczenie wielokrotne i MRO: 12-oop-zaawansowane/dziedziczenie-wielokrotne.md
      - Mixiny, kompozycja i klasy abstrakcyjne: 12-oop-zaawansowane/mixiny-i-abstrakcja.md
      - Klasy danych — dataclass, NamedTuple i Enum: 12-oop-zaawansowane/klasy-danych.md
      - Wzorce projektowe: 12-oop-zaawansowane/wzorce-projektowe.md
      - Metaprogramowanie: 12-oop-zaawansowane/metaprogramowanie.md
```

Pozycja w `docs/index.md`: „12. [Programowanie obiektowe — mechanizmy zaawansowane](12-oop-zaawansowane/index.md) — dziedziczenie wielokrotne i MRO, mixiny i klasy abstrakcyjne, klasy danych, wzorce projektowe, metaprogramowanie”.

## Zapowiedzi w przód (do zarejestrowania w `PLAN_ROZWOJU.md`)

- Rozdział 13: `slots=True` w klasach danych i koszt `__slots__` (strona 3); koszt `isinstance()` z `Protocol` (strona 2).
- Rozdział 16: `Protocol` i `mypy`, adnotacje w klasach danych jako informacja dla narzędzi (strony 2–3).
- Rozdział 18: Obserwator a `bind`/`trace_add` w tkinter (strona 4).

## Zmiany w rozdziałach 1–11 (zbiorczo po ukończeniu rozdziału 12)

| Plik:linia | Zmiana |
|---|---|
| `06-funkcje/dekoratory.md:540` | `TODO` (klasy danych) → odsyłacz do `klasy-danych.md#dekorator-dataclass` |
| `07-moduly/biblioteka-standardowa.md:266` | „poznamy je po wprowadzeniu klas” → odsyłacz do `klasy-danych.md` |
| `09-wejscie-wyjscie/csv-i-json.md:226` | `TODO` (klasy danych do JSON) → odsyłacz do `klasy-danych.md#funkcje-asdict-replace-i-zapis-do-json` |
| `10-klasy/dziedziczenie.md:48` | `TODO` (MRO) → odsyłacz do `dziedziczenie-wielokrotne.md` |
| `10-klasy/dziedziczenie.md:348` | `TODO` (kompozycja i wzorce) → odsyłacze do `mixiny-i-abstrakcja.md#dziedziczenie-mixin-czy-kompozycja` i `wzorce-projektowe.md` |
| `10-klasy/cykl-zycia-obiektu.md:83` | `TODO` (Singleton przez dekorator) → odsyłacz do `wzorce-projektowe.md#singleton-przez-dekorator-klasy` |
| `10-klasy/index.md:5` | `TODO` → odsyłacz do `../12-oop-zaawansowane/index.md` |
| `11-model-danych/index.md:5` | `TODO` → odsyłacz do `../12-oop-zaawansowane/index.md` |
| `11-model-danych/kolekcje-i-wywolania.md:311` | `TODO` (klasy abstrakcyjne) → odsyłacz do `mixiny-i-abstrakcja.md#klasy-abstrakcyjne-abcabc-i-abstractmethod` |
| `11-model-danych/deskryptory.md:236` | `TODO` (`__getattribute__`, metaklasy) → odsyłacz do `metaprogramowanie.md#wasna-metaklasa` |
| `docs/index.md`, `mkdocs.yml` | pozycja „12. …” |

Slugi do sprawdzenia w zbudowanym HTML (MkDocs pomija „ł”).

## CONTENT HANDOFF (rozbieżności ze źródłami)

(a) notatki s. 106–107: `object.__init__(self, x)` „akceptuje i ignoruje dodatkowe argumenty” — w 3.14 zgłasza `TypeError`, gdy klasa nadpisuje `__init__` (sonda; dotyczy też wcześniejszych wersji 3.x); wywód o różnicy między `object.__init__(x)` a `super().__init__(x)` do usunięcia; (b) notatki s. 103: literówka `metalcass`; (c) notatki s. 108: „unbound method call” i „rzutowanie” — współcześnie „wywołanie metody przez klasę” i „wywołanie klasy z obiektem jako argumentem”; (d) W07 sl. 15 i notatki s. 118: komunikat `Can't instantiate abstract class ... with abstract method(s) ...` — od 3.12 brzmi `... without an implementation for abstract method(s) ...`; (e) W07 sl. 19: `typing.List` → `list[float]`; (f) W07 sl. 25: nazwa `Readable` — w książce polska; (g) W07 sl. 13: `@abstractproperty` przestarzałe od 3.3; (h) W07 sl. 38: `sprawdz_rok` z rokiem 2025 na stałe; (i) W07 sl. 21: „Slicing/index — NamedTuple ograniczone” — indeksowanie i wycinki `NamedTuple` są pełne (to krotka); (j) notatki s. 111–114: dygresja o `inspect.getmembers()` i `__name__` pominięta.

## Checklista weryfikacyjna strony

1. Wszystkie deterministyczne przykłady przez `scripts/verify_page.py` (3.14.7); adresy maskowane.
2. Brak mechanizmów z późniejszych rozdziałów; adnotacje tylko składniowo.
3. Kolejność wewnątrz rozdziału (1 → 2 → 3 → 4 → 5; 4–5 uzupełniające); pojęcia wprowadzone w miejscu pierwszego użycia; wydruki MRO jako listy nazw.
4. Konwencje `CLAUDE.md`; nagłówki rzeczownikowe; cudzysłowy „…”; „ang.” przy pierwszym użyciu; „podrozdział”.
5. `mkdocs build` bez ostrzeżeń (oba pliki); kotwice sprawdzone w HTML.

## Checklista finalnego odbioru rozdziału

1. Sześć plików; nav i `docs/index.md`; H1 = etykiety.
2. Redakcja terminologii (MRO, linearyzacja, mixin, klasa abstrakcyjna, klasa danych, wyliczenie, metaklasa).
3. Tabela „Zmiany w rozdziałach 1–11” wykonana; brak `TODO` wskazujących na klasy danych i zaawansowane mechanizmy obiektowe.
4. Harness, audyt kotwic, oba buildy, `git diff --check`.
5. Fakty zależne od wersji: komunikat ABC (3.12), `StrEnum` (3.11), `kw_only`/`slots` (3.10), `runtime_checkable` (3.8, zmiana 3.12), `__init_subclass__` (3.6), niehaszowalne wartości domyślne w `dataclass` (3.11), `super()` w `NamedTuple` (3.14 — `TypeError`).
6. `PLAN_ROZWOJU.md`: status „ukończony” z liczbą linii; CONTENT HANDOFF w raporcie.
7. Commit, integracja do `dev`, push.
