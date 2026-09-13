# Rozdział 10. Klasy i obiekty — plan implementacyjny

Skondensowany projekt stron rozdziału 10 według `PLAN_ROZWOJU.md` (sekcja 4, „10. Klasy i obiekty”) i `DEVELOPMENT_WORKFLOW.md`. Branch: `content/10-klasy` (z `dev` po integracji rozdziału 9, commit `b70288a`). Stan odniesienia: Python 3.14.7 w `.venv` projektu (Windows), MkDocs Material; na komputerze autora dostępna także kompilacja wolnowątkowa `py -V:3.14t` (do jednego zdania na stronie 5).

## Decyzje autora (13 IX 2026)

Plan zaakceptowany 13 IX 2026 w całości. Autor apeluje o szczególną staranność w kontroli materiału — rozdział należy do najważniejszych w książce; każda strona przechodzi pełny cykl weryfikacji z checklisty i niezależną recenzję przed odbiorem.

1. **Struktura:** index + 5 podrozdziałów w kolejności: definicja klasy → atrybuty klasy, metody klasowe i statyczne → reprezentacja, właściwości i hermetyzacja → dziedziczenie → cykl życia obiektu. Etykieta nav i H1 ostatniej strony „Cykl życia obiektu” bez dopisku „(dla dociekliwych)” — charakter uzupełniający zaznaczony w pierwszym akapicie i w `index.md` (konwencja z rozdziałów 7 i 9; tabela w `PLAN_ROZWOJU.md` ma jeszcze dopisek).
2. **Zakres rozdziału:** wyłącznie dziedziczenie pojedyncze i metody specjalne `__init__`, `__repr__`, `__str__`, `__new__`, `__del__`. Bez przeciążania operatorów, `__eq__`/`__hash__`, `__len__`, `__call__` na instancji, iteratorów i menedżerów kontekstu jako klas, deskryptorów (→ rozdział o modelu danych); bez dziedziczenia wielokrotnego, MRO jako mechanizmu, klas abstrakcyjnych, `@dataclass`, wzorców projektowych poza Singletonem (→ rozdział o zaawansowanych mechanizmach obiektowych); `__slots__` w rdzeniu krótko, pomiar pamięci → rozdział o wydajności.
3. **Przykłady i nazwy:** klasy z materiałów źródłowych pod ich nazwami (`Czlowiek`, `Okrag`, `Konto`, `Student`, `Zwierze`/`Pies`/`Kot`, `Pracownik`, `Grupa`, `Punkt`, `Bug`, `Singleton`); identyfikatory jak w rozdziałach 6–9 (polskie nazwy własne, `self`/`cls` bez zmian); docstring klasy jako fraza rzeczownikowa (`"""Okrąg o promieniu r."""`), docstringi metod w konwencji rozdziału 6 (`"""Zwraca ..."""`). Klasa `Bug` z laboratorium 5 służy za przykład licznika instancji (strona 2) i `__del__` (strona 5) bez żadnej noty o laboratorium.
4. **Terminologia:** `__init__` to „metoda inicjalizująca (ang. *initializer*)”; słowa „konstruktor” używamy wyłącznie dla wywołania klasy `Klasa(...)` z wyjaśnieniem, że składa się z `__new__` i `__init__`; „instancja (ang. *instance*)” = obiekt klasy; „atrybut instancji / atrybut klasy”; „metoda instancji / metoda klasy / metoda statyczna”; „właściwość (ang. *property*)”; „hermetyzacja (ang. *encapsulation*)”; „przekształcanie nazw (ang. *name mangling*)”; „klasa bazowa / klasa pochodna” z synonimami „nadklasa / podklasa” przy pierwszym użyciu (rozdział 7 użył już „podklasy”); „nadpisywanie metody (ang. *override*)”; „polimorfizm”; „kompozycja”; „licznik referencji” (rozdział 3); „słaba referencja (ang. *weak reference*)”.
5. **Własne klasy wyjątków** na stronie 4 jako pierwsze zastosowanie dziedziczenia — domykają notę „Zapowiedź — własne typy wyjątków” z rozdziału 8; przykład z jednym łańcuchem dziedziczenia (`BladWieku(ValueError)` → `ZakresBledny(BladWieku)` z atrybutem i `super().__init__(komunikat)`).
6. **Strona 5 jako uzupełniająca:** `__new__` a `__init__`, Singleton, `sys.getrefcount()` z obiektami nieśmiertelnymi (PEP 683), `__del__`, `weakref`, cykle referencji i `gc`, `__slots__` a dziedziczenie. Jedno zdanie o kompilacji wolnowątkowej (inne wartości `getrefcount()`) z zapowiedzią rozdziału o współbieżności.
7. **Ślady wywołań** z komunikatami „Did you mean” i sygnaturą `missing 1 required positional argument: 'self'` jako bloki `.text .no-copy` z uruchomienia; domyślne `repr` z adresem maskowane w harnessie (`--mask=0x[0-9A-Fa-f]+`).
8. **Szacunek rozmiaru** z `PLAN_ROZWOJU.md` (850–950 linii) orientacyjny; przy gęstości rozdziałów 6–9 spodziewane ok. 1500–1800 linii.
9. **Zapowiedzi w przód** prozą po temacie z `TODO` i wpisem w `PLAN_ROZWOJU.md` (lista na końcu planu); zarejestrowane 13 IX 2026 w sekcjach 11, 12, 13, 15 i 16 (wraz z zaległymi zapowiedziami z rozdziału 9).

## Zasady obowiązujące w całym rozdziale

- Żaden przykład nie wymaga mechanizmu wprowadzanego później: bez operatorów na obiektach (`==` na instancjach tylko jako tożsamość domyślna — jedno zdanie), bez `__eq__`, bez dziedziczenia wielokrotnego, bez `dataclass`, bez `abc`, bez wątków. Wyjątki zgodnie z rozdziałem 8 (`raise ValueError(...)` w setterach, `try`/`except ... as e`). Pliki i `print(file=)` zgodnie z rozdziałem 9 tylko tam, gdzie potrzebne (nie planuje się).
- Moduły biblioteki standardowej użyte w kodzie: `sys` (`getrefcount()`), `weakref` (`ref()`), `gc` (`collect()`), `math` (`pi`), `types` (`MethodType` jednym przykładem na stronie 1 lub 2 — zamiast odsyłacza do StackOverflow z notatek). Żaden inny moduł; `functools.total_ordering`, `dataclasses`, `abc`, `copy` co najwyżej prozą.
- Kolejność wewnątrz rozdziału: strona 1 korzysta z rozdziałów 1–9 (funkcje, `def`, wartości domyślne, `id()`, `type()`, f-stringi, `!r`); strona 2 po 1 (`self`, atrybuty instancji); strona 3 po 1–2 (`_nazwa` wymaga atrybutów, `@property` — składni `@` z rozdziału 6); strona 4 po 1–3 (`super().__init__()`, `__str__` rozszerzany, walidacja w wyjątkach); strona 5 po 1–4 (`super().__new__()`, `__slots__`, dziedziczenie). Strona 5 jest uzupełniająca — dalsze rozdziały odwołują się do niej tylko przy Singletonie i `__new__`.
- Pojęcia wprowadzane jawnie w miejscu pierwszego użycia: „klasa” i „instancja”; „metoda inicjalizująca”; „`self`”; „atrybut instancji” (strona 1) a „atrybut klasy” (strona 2); „przestrzeń nazw klasy” i „zasięg klasy” (strona 2 — domyka zapowiedź LEGB z rozdziału 6); „metoda klasy”, „metoda statyczna”, „konstruktor alternatywny”; „reprezentacja”; „właściwość”; „hermetyzacja”; „przekształcanie nazw”; „klasa bazowa / pochodna”; „nadpisywanie”; „polimorfizm”; „kompozycja”; „obiekt nieśmiertelny (ang. *immortal object*)”; „słaba referencja”; „cykl referencji”.
- Nagłówki w formie rzeczownikowej z nazwami w kodzie (np. „Tworzenie obiektu i metoda `__init__`”, „Funkcja `super()`”).
- Konwencje `CLAUDE.md`: bloki `python title="plik.py"`, `{ .python .no-copy }` dla REPL, `{ .text .no-copy }` dla wyników i śladów wywołań; admonitions z polskimi tytułami; cudzysłowy „…”; terminy angielskie z „ang.” przy pierwszym użyciu; nazwy plików przykładowych bez kolizji z biblioteką standardową (nie: `types.py`, `weakref.py`, `gc.py`, `abc.py`, `property.py`).
- Weryfikacja: `scripts/verify_page.py` na `.venv` (3.14.7) dla skryptów; `--mask` dla adresów w domyślnym `repr` i `id()`; sesje REPL osobno; `python -i` dla bloków REPL; wartości `getrefcount()` wpisane z uruchomienia na 3.14.7 z zaznaczeniem, że zależą od wersji i kompilacji.
- `index.md` w układzie rozdziałów 6–9. Odsyłacze do rozdziałów 1–9 wewnątrz nowych stron od razu; zmiany w rozdziałach 1–9 (tabela na końcu) zbiorczo po ukończeniu rozdziału. Strony rozdziału 4 z markerami aktywności nie są dotykane.

## Strony

### 1. `definicja-klasy.md` — Definicja klasy

**Cel.** Czytelnik definiuje klasę instrukcją `class`, tworzy obiekty, rozumie rolę `__init__` i `self`, przypisuje atrybuty instancji, pisze metody instancji i wie, że klasa sama jest obiektem (w tym obiektem wywoływalnym).

**Kolejność H2/H3.**
1. Instrukcja `class` (nazwa CapWords, pusta klasa z `pass`, docstring, `help()`; klasa jako przepis na obiekty, obiekt jako instancja)
2. Tworzenie obiektu i metoda `__init__` (wywołanie klasy; `__init__` jako metoda inicjalizująca, nie konstruktor; parametry z wartościami domyślnymi; `return` z wartością → `TypeError`; dwa obiekty — dwa niezależne stany)
3. Parametr `self` (`obiekt.metoda()` ≡ `Klasa.metoda(obiekt)`; `id(self)` równe `id(obiekt)`; ślad wywołania `missing 1 required positional argument: 'self'`; nazwa konwencjonalna, `this` w C++ jednym zdaniem)
4. Atrybuty instancji (przypisanie w `__init__`; dodawanie poza `__init__` i dlaczego nie; `AttributeError` z „Did you mean”; `__dict__` instancji jako słownik atrybutów — H3)
5. Metody instancji (metoda zmieniająca stan, metoda zwracająca wartość, metoda wywołująca inną metodę przez `self`; `return self` i łańcuch wywołań — `Konto`)
6. Klasa jako obiekt (`type(obiekt)`, `obiekt.__class__`, `type(Klasa)` → `type`; `Klasa.__name__`, `__doc__`; klasa w zmiennej i w liście; klasa jako obiekt wywoływalny — `callable(Klasa)` — domyka zapowiedź z rozdziału 6; obiekty z własnym `__call__` → model danych)

**Pojęcia wprowadzane.** Klasa, instancja, metoda inicjalizująca, `self`, atrybut instancji, metoda instancji, `__dict__`, klasa jako obiekt typu `type`.

**Zależności.** `def`, parametry i wartości domyślne (6); `id()`, `type()`, `del`, licznik referencji (3); f-stringi (3, 9); `callable()` i obiekty wywoływalne (6/funkcje-jako-obiekty); `help()` (2); `ValueError` z komunikatem (8).

**Główne przykłady.** `czlowiek.py` (`Czlowiek` z `imie`, `nazwisko`, `wiek=20`; dwa obiekty); `self-id.py` (`id(self)` w `__init__` a `id(k1)` — maskowane); `bez-self.py` (ślad wywołania); `atrybuty.py` (dodanie `pesel` do jednego obiektu, `AttributeError` na drugim z „Did you mean”, `__dict__`); `konto.py` (`Konto` z `wplata()`, `wyplata()` z `raise ValueError`, `historia`, `return self`); `klasa-jako-obiekt.py` (`type()`, `__name__`, `callable()`, lista klas).

**Wymagane zachowania do weryfikacji na 3.14.7.** `TypeError: __init__() should return None, not 'int'`; `TypeError: Okrag.pole() missing 1 required positional argument: 'self'` (z `~~~^^` pod wywołaniem); `AttributeError: 'Czlowiek' object has no attribute 'pesel'` i wariant z `Did you mean: 'imie'?` dla literówki; `type(Czlowiek)` → `<class 'type'>`; `callable(Czlowiek)` → `True`; `c1.__dict__` → `{'imie': 'Jan', 'nazwisko': 'Kowalski', 'wiek': 20}`; `help(Czlowiek)` — fragment z `Methods defined here` (blok `.text`).

**Źródła repozytorium.** `PythonNotatki.txt` 3186–3260 (s. 83–85: definicja, `__init__`, `self`, `id(self)`, atrybuty dynamiczne, `setattr` — introspekcja przeniesiona na stronę 2); `Wyklad_06.txt` sl. 4–6, 9, 11; `Wyklad_01.txt` sl. 19 (CapWords); `06-funkcje/funkcje-jako-obiekty.md:140` (zapowiedź obiektów wywoływalnych).

**Źródła zewnętrzne.** Tutorial *Classes* (9.1–9.4: scopes, class objects, instance objects, method objects); *Data model* (3.3.1 `__init__`, `__new__` tylko wzmianka); *Built-in Functions* (`type()`, `callable()`, `help()`); PEP 8 (Class Names).

**TODO/zapowiedzi do domknięcia.** `06-funkcje/funkcje-jako-obiekty.md:140` (`TODO` o innych obiektach wywoływalnych) → sekcja 6.

**Odłożone.** `__call__` na instancjach (→ model danych); `types.MethodType` — jeden przykład na stronie 2 przy introspekcji; adnotacje typów w klasach (→ narzędzia analizy typów); `__init__` a `__new__` (→ strona 5).

**Ryzyka kolejności pojęć.** Nie używać słowa „konstruktor” dla `__init__`; nie wprowadzać atrybutów klasy przed stroną 2 (docstring i `__name__` opisujemy jako atrybuty klasy dopiero tam — na stronie 1 „informacje o klasie”); `help()` pokazać krótkim fragmentem, bo pełny wydruk zawiera `Data descriptors` (deskryptory → model danych).

**Orientacyjny rozmiar.** ok. 280–330 linii.

### 2. `atrybuty-i-metody.md` — Atrybuty klasy, metody klasowe i statyczne

**Cel.** Czytelnik odróżnia atrybut klasy od atrybutu instancji, zna kolejność wyszukiwania atrybutów i pułapkę modyfikowalnego atrybutu klasy, rozumie przestrzeń nazw klasy (w tym zasięg ciała klasy), używa introspekcji i `__slots__` oraz pisze metody klasy i metody statyczne.

**Kolejność H2/H3.**
1. Atrybut klasy a atrybut instancji (`Bug.licznik` rosnący w `__init__`, `self.id = Bug.licznik`; odczyt przez klasę i instancję; przypisanie przez instancję tworzy atrybut instancji i przesłania atrybut klasy; `type(x).atrybut`; kolejność wyszukiwania: instancja → klasa)
2. Pułapka: modyfikowalny atrybut klasy (`Grupa.studenci = []` a `self.studenci = []`)
3. Przestrzeń nazw klasy (H3: Słownik `__dict__` klasy — wybrane klucze, w tym `__doc__`, metody, `__static_attributes__` i `__firstlineno__` od 3.13 jednym zdaniem; H3: Zasięg ciała klasy — nazwa z ciała klasy niewidoczna w metodzie bez `self.`/`Klasa.`, `NameError`; domyka zapowiedź LEGB z rozdziału 6; H3: Introspekcja — `getattr()` z wartością domyślną, `setattr()`, `hasattr()`, `delattr()`, `vars()`; metoda dodana do obiektu przez `types.MethodType` jednym przykładem jako ciekawostka)
4. Atrybut `__slots__` (krotka dozwolonych nazw, brak `__dict__`, `AttributeError` przy literówce, oszczędność pamięci — pomiar w rozdziale o wydajności; `__slots__` a dziedziczenie → strona 5)
5. Metody klasy — `@classmethod` (parametr `cls`; konstruktory alternatywne `from_string()`, `from_dict()`; `cls(...)` zamiast nazwy klasy — działa z dziedziczeniem, pokaz na stronie 4)
6. Metody statyczne — `@staticmethod` (funkcja w przestrzeni nazw klasy bez `self` i `cls`; wywołanie przez klasę i przez instancję — korekta notatek)
7. Porównanie trzech rodzajów metod (tabela: pierwszy parametr, dostęp do stanu, sposób wywołania, typowe zastosowanie; przykład `Kolo` z metodą instancji, klasy i statyczną)

**Pojęcia wprowadzane.** Atrybut klasy, przesłanianie, przestrzeń nazw klasy, zasięg klasy, introspekcja, `__slots__`, metoda klasy, `cls`, konstruktor alternatywny, metoda statyczna.

**Zależności.** Strona 1; LEGB i `NameError` (6/zasieg-nazw); listy i słowniki (5); `@` (6/dekoratory); `math.pi` (7); `getattr` nie pojawiał się wcześniej (nowe).

**Główne przykłady.** `licznik.py` (`Bug` bez `__del__`); `przeslanianie.py` (`x.gatunek = ...`, `type(x).gatunek`); `grupa.py` (pułapka i poprawka); `przestrzen-nazw.py` (`Czlowiek.__dict__` wybrane klucze przez `sorted()`, `NameError` w metodzie — jako ślad w bloku `.text`); `introspekcja.py` (`getattr`/`setattr`/`hasattr`/`delattr`, `vars()`, `MethodType`); `slots.py` (`Punkt` z `__slots__`, `AttributeError`); `student.py` (`from_string()`, `from_dict()`, `is_full_name()` przez klasę i instancję); `kolo.py` (trzy rodzaje metod).

**Wymagane zachowania do weryfikacji na 3.14.7.** `Czlowiek.__dict__` zawiera `'__firstlineno__'` i `'__static_attributes__'` (kolejność kluczy: `__module__`, `__firstlineno__`, `__doc__`, atrybuty i metody w kolejności definicji, `__static_attributes__`, `__dict__`, `__weakref__`); `NameError: name 'licznik' is not defined` w metodzie; komunikat `AttributeError` dla `__slots__` (brzmienie sprawdzić przy pisaniu — w 3.14 zawiera „and no __dict__ for setting new attributes”); `s.is_full_name('Nowak')` → `False` na instancji; `getattr(c1, 'x', None)` → `None`.

**Źródła repozytorium.** `PythonNotatki.txt` 3260–3330 (s. 85–86: `setattr`/`hasattr`/`delattr`/`getattr`, atrybut klasy `narodowosc`, `@classmethod kraj()`), 4937–4941 (atrybut klasy a instancji — z metaprogramowania), 5109–5186 (s. 119–120: `from_string`, `is_full_name`, błędna teza o metodzie statycznej); `Wyklad_06.txt` sl. 7–9, 12–13, 19, 41 (quiz → strona 4); `lab5.txt` sl. 1 (`Bug`); `Wyklad_07.txt` sl. 40 (tylko wzmianka o `__slots__` w hierarchii → strona 5); `06-funkcje/zasieg-nazw-i-domkniecia.md:18` (zapowiedź zasięgu klasy).

**Źródła zewnętrzne.** Tutorial *Classes* (9.3.5 class and instance variables, 9.4 random remarks); *Data model* (`__slots__` — notes on using slots; `__dict__`; `__static_attributes__`, `__firstlineno__` — „Added in version 3.13”); *Built-in Functions* (`classmethod`, `staticmethod`, `getattr`, `setattr`, `hasattr`, `delattr`, `vars`); *Execution model* (class scope); `types.MethodType`.

**TODO/zapowiedzi do domknięcia.** `06-funkcje/zasieg-nazw-i-domkniecia.md:18` (zasięg klasy) → sekcja 3; `06-funkcje/dekoratory.md:540` (`@classmethod`, `@staticmethod`) → sekcje 5–6.

**Odłożone.** `__slots__` z `__dict__` w krotce, `__weakref__`; `classmethod` jako deskryptor (→ model danych); `__init_subclass__`, `__class_getitem__` (→ zaawansowane mechanizmy); pomiar `sys.getsizeof()` z `__slots__` (→ wydajność).

**Ryzyka kolejności pojęć.** `type(x).gatunek` wymaga zrozumienia „klasa jako obiekt” ze strony 1; `MethodType` pokazać jako ciekawostkę bez „wiązania metod” (deskryptory); tabela trzech rodzajów metod przed dziedziczeniem — argument „działa z dziedziczeniem” zapowiedziany, pokazany na stronie 4.

**Orientacyjny rozmiar.** ok. 300–350 linii.

### 3. `reprezentacja-i-wlasciwosci.md` — Reprezentacja, właściwości i hermetyzacja

**Cel.** Czytelnik definiuje `__repr__` i `__str__` i wie, kto je wywołuje, zamienia atrybut we właściwość z walidacją bez zmiany interfejsu, unika rekurencji we właściwości i stosuje konwencje `_nazwa` i `__nazwa` ze zrozumieniem, że hermetyzacja jest umową.

**Kolejność H2/H3.**
1. Metody `__repr__` i `__str__` (domyślna reprezentacja `<__main__.Czlowiek object at 0x...>`; `__repr__` jednoznaczna — `Czlowiek('Jan', 'Kowalski', 20)` z `!r`; `__str__` dla użytkownika; `print()`, `str()` i f-string → `__str__`; REPL, kontenery, `repr()`, `!r` → `__repr__`; brak `__str__` → `__repr__`; zasada „zawsze definiuj `__repr__`”)
2. Właściwości — `@property` (`Okrag` z `_promien`; getter; H3: Setter z walidacją — `raise ValueError`; H3: Właściwość wyliczana tylko do odczytu — `pole` z `math.pi`, `AttributeError: property 'pole' of 'Okrag' object has no setter`; H3: Deleter krótko; kiedy nie używać właściwości — zwykły atrybut wystarcza, właściwość dodajemy bez zmiany interfejsu, gdy pojawia się walidacja lub obliczenie)
3. Pułapka: rekurencja we właściwości (getter odwołujący się do własnej nazwy → `RecursionError` z rozdziału 6; pole zapasowe `_wartosc`)
4. Konwencje hermetyzacji — `_nazwa` i `__nazwa` (publiczne, „wewnętrzne” z pojedynczym podkreśleniem — dostępne, umowa; podwójne podkreślenie — przekształcanie nazw do `_Klasa__nazwa` widoczne w `__dict__`, `AttributeError` przy `obiekt.__pin`; hermetyzacja jako umowa, nie blokada; nazwy `__x__` zarezerwowane dla języka)
5. Klasa `property` (dla dociekliwych) (`property(fget, fset, fdel, doc)` z klasą `Okrag` z notatek; `type(Okrag.promien)` → `<class 'property'>`; `Okrag.promien.__doc__`; fragment `help(Okrag)` z „Readonly properties” / „Data descriptors”; mechanizm — deskryptor — w rozdziale o modelu danych)

**Pojęcia wprowadzane.** Reprezentacja, właściwość, getter/setter/deleter (po polsku: metoda odczytu, zapisu, usuwania — z angielskimi nazwami), pole zapasowe, hermetyzacja, przekształcanie nazw.

**Zależności.** `repr()` a `str()` (3/typy-proste); `!r` (9/formatowanie); `raise ValueError` (8); `RecursionError` (6/rekurencja); `@` (6); `__dict__` (strona 1–2); `math.pi` (7).

**Główne przykłady.** `repr-str.py` (`Czlowiek` bez i z metodami; `print()`, `repr()`, lista obiektów); `okrag.py` (`promien` z walidacją, `pole` tylko do odczytu, próba `o.pole = 1` w `try/except AttributeError as e`); `rekurencja-wlasciwosci.py` (ślad w bloku `.text` — ostatnie wiersze z `[Previous line repeated ... more times]`); `hermetyzacja.py` (`Konto` z `_saldo` i `__pin`, `__dict__`, `_Konto__pin`); `property-klasa.py` (`Okrag` z `property(...)`, `type()`, `__doc__`).

**Wymagane zachowania do weryfikacji na 3.14.7.** Domyślne `repr` maskowane; `AttributeError: property 'pole' of 'Okrag' object has no setter`; `AttributeError: 'Konto' object has no attribute '__pin'`; `k.__dict__` → `{'_saldo': 100, '_Konto__pin': 1234}`; `type(Okrag.promien)` → `<class 'property'>`; `Okrag.promien.__name__` → `'promien'` (od 3.13); ślad `RecursionError: maximum recursion depth exceeded` z wierszem `[Previous line repeated 996 more times]` (liczbę wpisać z uruchomienia).

**Źródła repozytorium.** `PythonNotatki.txt` 3330–3420 (s. 86–88: `_a`, `__secret`, `__dict__`, `__class__`, `__str__` z `.format(self=self)` → f-string, `__repr__`), 3943–4136 (s. 98–101: `property()` jako klasa, `Okrag`, `help(Okrag)`, `dir(Okrag.r)` — pominąć listę `dir`); `Wyklad_06.txt` sl. 14, 16–18, 40.

**Źródła zewnętrzne.** *Data model* (`__repr__`, `__str__`); *Built-in Functions* (`property` — w tym „Changed in version 3.13: attributes `__name__`”); tutorial *Classes* (9.6 private variables, name mangling); PEP 8 (naming: `_single_leading_underscore`, `__double_leading_underscore`).

**TODO/zapowiedzi do domknięcia.** `06-funkcje/dekoratory.md:540` (`@property`) → sekcja 2.

**Odłożone.** `__format__` i `__str__` w f-stringach ze specyfikacją (→ model danych); `__eq__`/`__hash__` (→ model danych); `functools.cached_property` (wzmianka prozą); deskryptory.

**Ryzyka kolejności pojęć.** Nie tłumaczyć `@property` przez deskryptory; `property` jako klasa tylko w sekcji dla dociekliwych; rekurencja we właściwości — ślad skrócony do końcówki z zaznaczeniem, że pełny ma ok. tysiąca wierszy.

**Orientacyjny rozmiar.** ok. 300–350 linii.

### 4. `dziedziczenie.md` — Dziedziczenie

**Cel.** Czytelnik buduje hierarchię klas z dziedziczeniem pojedynczym, nadpisuje i rozszerza metody przez `super()`, sprawdza typy przez `isinstance()`/`issubclass()`, definiuje własne klasy wyjątków oraz zna alternatywę kompozycji i podstawowe zasady projektowania klas.

**Kolejność H2/H3.**
1. Klasa bazowa i klasa pochodna (`Zwierze` → `Pies`, `Kot`; składnia `class Pies(Zwierze)`; przejęcie metod i `__init__`; `object` jako korzeń każdej hierarchii; `__bases__`; `__mro__` pokazana jako krotka dla łańcucha pojedynczego z nazwą „kolejność rozstrzygania metod” i odesłaniem szczegółów do rozdziału o zaawansowanych mechanizmach)
2. Nadpisywanie metod i polimorfizm (`odglos()` w każdej klasie; pętla po liście zwierząt wywołująca tę samą metodę; wspólny interfejs)
3. Funkcja `super()` (rozszerzanie `__init__` i `__str__`; postać pełna `super(Pies, self)` jako równoważna, nie „z Pythona 2”; H3: Pułapka pominiętego `super().__init__()` — `AttributeError`; H3: Pułapka atrybutu klasy dzielonego z klasą pochodną — quiz `A.x = []`, `B(A)`, `a.x is b.x` → `True`)
4. Funkcje `isinstance()` i `issubclass()` (zamiast `type(x) == Klasa`; krotka typów; `bool` jako podklasa `int`; `Counter` jako podklasa `dict` — domyka rozdział 7; hierarchia wyjątków z rozdziału 8 jako dziedziczenie — `issubclass(KeyError, LookupError)`)
5. Własne klasy wyjątków (`BladWieku(ValueError)` z docstringiem, `ZakresBledny(BladWieku)` z atrybutem `wiek` i `super().__init__(komunikat)`; `except BladWieku` obsługuje oba; konwencje: przyrostek `Error`/`Blad`, dziedziczenie po `Exception` lub odmianie, hierarchia programu; użycie w funkcji `sprawdz_wiek()` i obsługa z `e.wiek`)
6. Kompozycja a dziedziczenie („ma” zamiast „jest”: `Samochod` z atrybutem `silnik` typu `Silnik`; kiedy dziedziczyć, kiedy składać; wzorce i mechanizmy zaawansowane → zapowiedź)
7. Admonition „Zasady projektowania klas” (zawsze `__repr__`; atrybuty w `__init__`; `isinstance()` zamiast `type()`; walidacja we właściwościach; kompozycja przed dziedziczeniem; docstring klasy; `__eq__` i `__hash__` — zapowiedź modelu danych)

**Pojęcia wprowadzane.** Klasa bazowa/pochodna (nadklasa/podklasa), dziedziczenie, nadpisywanie, polimorfizm, `super()`, kolejność rozstrzygania metod (nazwa), kompozycja.

**Zależności.** Strony 1–3; hierarchia wyjątków, `raise`, `except ... as e` (8); `Counter` (7); `bool`/`int` (3); listy (5); `issubclass` nowe.

**Główne przykłady.** `zwierzeta.py` (hierarchia, polimorfizm w pętli, `__bases__`, `__mro__`); `pracownik.py` (`Pracownik(Czlowiek)` z `super().__init__()` i `super().__str__()`); `bez-super.py` (ślad `AttributeError`); `wspolna-lista.py` (quiz); `typy.py` (`isinstance`, `issubclass`, `bool`, `Counter`, `KeyError`/`LookupError`); `wyjatki-wlasne.py` (`BladWieku`, `ZakresBledny`, `sprawdz_wiek()`); `kompozycja.py` (`Silnik`, `Samochod`).

**Wymagane zachowania do weryfikacji na 3.14.7.** `Pies.__mro__` → `(<class '__main__.Pies'>, <class '__main__.Zwierze'>, <class 'object'>)`; `Pies.__bases__` → `(<class '__main__.Zwierze'>,)`; `AttributeError: 'Pracownik' object has no attribute 'imie'`; quiz: `[1, 2]`, `[1, 2]`, `[1, 2]`, `True`; `issubclass(bool, int)` → `True`, `isinstance(True, int)` → `True`, `type(True) is int` → `False`; `issubclass(KeyError, LookupError)` → `True`; `str(ZakresBledny(-5))` → `'Zły wiek: -5'`.

**Źródła repozytorium.** `PythonNotatki.txt` 4216–4322 (s. 103–105: `Baza`/`A`/`B`/`C` z `super().__init__()` — w książce bez łańcucha `__new__`, ten fragment → zaawansowane mechanizmy); `Wyklad_06.txt` sl. 21–24, 40–41; `Wyklad_05.txt` sl. 24 (własne wyjątki); `07-moduly/biblioteka-standardowa.md:186` (`Counter` podklasą); `08-wyjatki/zglaszanie-wyjatkow.md:125` i nota 440–449.

**Źródła zewnętrzne.** Tutorial *Classes* (9.5 inheritance — „Python has two built-in functions that work with inheritance”), *Errors and Exceptions* (8.6 user-defined exceptions), *Built-in Functions* (`super()`, `isinstance()`, `issubclass()`), *Built-in Exceptions* (hierarchia), PEP 8 (exception names).

**TODO/zapowiedzi do domknięcia.** `08-wyjatki/zglaszanie-wyjatkow.md:125` (dziedziczenie) → sekcja 1 lub 4; `08-wyjatki/zglaszanie-wyjatkow.md:440–449` (nota o własnych typach wyjątków) → sekcja 5; `07-moduly/biblioteka-standardowa.md:186` (`Counter` podklasą) → sekcja 4.

**Odłożone.** Dziedziczenie wielokrotne, algorytm C3, `super()` w rombie, klasy abstrakcyjne i `abc`, `__init_subclass__`, `NotImplemented` (→ zaawansowane mechanizmy); `__eq__` (→ model danych); `ExceptionGroup` z własnymi wyjątkami (rozdział 8 wystarcza).

**Ryzyka kolejności pojęć.** `__mro__` tylko jako krotka do odczytania, bez algorytmu; nie sugerować, że `super()` „wywołuje rodzica” — „następną klasę w kolejności rozstrzygania”, w łańcuchu pojedynczym to klasa bazowa; własne wyjątki bez `__str__` (wystarczy `super().__init__(komunikat)`); kompozycja jako jedna sekcja bez wzorców.

**Orientacyjny rozmiar.** ok. 320–380 linii.

### 5. `cykl-zycia-obiektu.md` — Cykl życia obiektu

**Cel (strona uzupełniająca).** Czytelnik wie, co dzieje się między wywołaniem klasy a gotowym obiektem (`__new__` i `__init__`), potrafi napisać Singleton, rozumie licznik referencji i obiekty nieśmiertelne, zna ograniczenia `__del__`, użycie `weakref.ref()`, cykle referencji z modułem `gc` oraz zachowanie `__slots__` w dziedziczeniu.

**Kolejność H2/H3.**
1. Metody `__new__` i `__init__` (`__new__(cls, *args, **kwargs)` jako metoda statyczna wywoływana przed `__init__`; `super().__new__(cls)`; kolejność wydruków; H3: Pułapka `__new__` bez `return` — wynik `None`, `__init__` pominięte; `Foo.__new__(Bar)` jednym zdaniem; kiedy `__new__`: typy niemodyfikowalne, Singleton)
2. Wzorzec Singleton (`_instancja = None`, `cls._instancja = super().__new__(cls)`; `s1 is s2` → `True`; pułapka ponownego `__init__` — `s1.wartosc` → `'druga'`; wariant przez dekorator klasy → zaawansowane mechanizmy)
3. Licznik referencji i `sys.getrefcount()` (odwołanie do rozdziału 3; `+1` za argument; `del`; obiekty nieśmiertelne (PEP 683): `getrefcount(1)` i `getrefcount(None)` → `3221225472` na 3.14; jedno zdanie o kompilacji wolnowątkowej — inne wartości, zapowiedź rozdziału o współbieżności)
4. Metoda `__del__` (`Bug` z licznikiem malejącym i komunikatem; wywołanie przy spadku licznika do zera — w CPythonie natychmiast; bez gwarancji przy cyklach i przy zamykaniu interpretera; nie do zwalniania zasobów — `with` z rozdziału 8)
5. Słabe referencje — `weakref.ref()` (obserwator nieutrzymujący obiektu; `w()` → obiekt albo `None`; nie dla `list`, `dict`, `int`, `str`, `tuple` — `TypeError`; `WeakValueDictionary` jednym zdaniem)
6. Cykle referencji i moduł `gc` (`a.inny = b; b.inny = a`; `del a, b` bez `__del__`; `gc.collect()` zwraca liczbę zebranych obiektów, `__del__` wywołane; odśmiecanie automatyczne — krótko; łączy się z rozdziałem 3 „licznik referencji spadnie do zera”)
7. Atrybut `__slots__` a dziedziczenie (klasa pochodna bez `__slots__` odzyskuje `__dict__`; klasa pochodna z `__slots__` wymienia tylko nowe nazwy; `AttributeError` dla nazwy spoza obu krotek)

**Pojęcia wprowadzane.** `__new__`, Singleton, obiekt nieśmiertelny, `__del__` (finalizator), słaba referencja, cykl referencji, odśmiecanie (ang. *garbage collection*, rozdział 3 użył „odśmiecacz”/„licznik referencji” — ujednolicić przy pisaniu).

**Zależności.** Strony 1–4; rozdział 3 (`id()`, licznik referencji, `del`, `getsizeof`); `with` (8); `super()` (strona 4).

**Główne przykłady.** `new-init.py` (`Foo` z wydrukami); `new-bez-return.py`; `singleton.py`; `refcount.py` (`getrefcount` listy, `1`, `None`); `bug.py` (lab 5: trzy obiekty w liście, `del bugs[0]`, komunikaty z `__del__`); `slaba-referencja.py`; `cykl.py` (`gc.collect()`); `slots-dziedziczenie.py`.

**Wymagane zachowania do weryfikacji na 3.14.7.** `Bez()` → `None` przy `__new__` bez `return`, bez wydruku z `__init__`; `sys.getrefcount(1)` → `3221225472`; `sys.getrefcount(lista)` → `2` po utworzeniu; `weakref.ref([])` → `TypeError: cannot create weak reference to 'list' object`; `w()` → `None` po `del`; `gc.collect()` → liczba > 0 dla cyklu (wartość wpisać z uruchomienia, zaznaczyć, że może się różnić); `Pod().__dict__` istnieje dla klasy pochodnej bez `__slots__`; na `py -V:3.14t`: `getrefcount([])` → `1` (tylko zdanie prozą).

**Źródła repozytorium.** `PythonNotatki.txt` 3420–3483 (s. 88–89: `__del__`, `__new__` z `*args`/`**kwargs`, `object.__new__(cls)`, `Foo.__new__(Bar)`); `Wyklad_06.txt` sl. 5, 25, 38; `lab5.txt` sl. 1–2 (`Bug`, `getrefcount`, `weakref`); `Wyklad_04.txt` sl. 48 (błąd o listach i słownikach); `Wyklad_07.txt` sl. 40; `03-nazwy-typy/obiekty-i-pamiec.md` (licznik referencji, `del`).

**Źródła zewnętrzne.** *Data model* (`__new__`, `__init__`, `__del__` — „It is not guaranteed that `__del__()` methods are called for objects that still exist when the interpreter exits”, `__slots__` — notes on inheritance); `sys.getrefcount()` (uwaga o obiektach nieśmiertelnych, „Changed in version 3.12”); PEP 683; `weakref` (typy obsługujące słabe referencje — „Several built-in types such as list and dict do not directly support weak references”); `gc.collect()`; PEP 703 tylko jako odsyłacz przy zdaniu o kompilacji wolnowątkowej.

**TODO/zapowiedzi do domknięcia.** `03-nazwy-typy/obiekty-i-pamiec.md:90` („definicje klas”, licznik referencji) → `index.md` rozdziału i sekcja 3.

**Odłożone.** `__new__` w typach niemodyfikowalnych (podklasa `tuple`), metaklasy, `type.__call__` (→ zaawansowane mechanizmy); `weakref.finalize`, `WeakKeyDictionary`; `gc.get_referrers()`, `gc.disable()`; `tracemalloc` (→ wydajność); `__slots__` z `__dict__`.

**Ryzyka kolejności pojęć.** `__del__` przy zamykaniu interpretera — kolejność komunikatów niegwarantowana, przykład kończy się jawnymi `del` przed końcem programu; wartości `getrefcount()` zależne od wersji — podać z 3.14.7 i zaznaczyć; nie obiecywać determinizmu `gc`.

**Orientacyjny rozmiar.** ok. 280–340 linii.

### 6. `index.md` — Wprowadzenie

Wstęp (dwa–trzy akapity): od „wszystko jest obiektem” (rozdział 3) do własnych typów — klasa jako przepis, obiekt jako instancja; co czytelnik już zna (funkcje i `@` z 6, wyjątki i `with` z 8, `repr` i f-stringi z 3 i 9) i co rozdział wnosi (definicja klasy, atrybuty i metody, właściwości, dziedziczenie z własnymi wyjątkami, cykl życia); podział materiału obiektowego na trzy rozdziały: ten, model danych (metody specjalne i protokoły) oraz mechanizmy zaawansowane — prozą, z `TODO`; podrozdział „Cykl życia obiektu” oznaczony jako uzupełniający. Następnie `---` i `## W tym rozdziale` z pięcioma pozycjami „Tytuł — tematy”. Bez „Powiązanego laboratorium” i bez „Ściągi”. Orientacyjny rozmiar: ok. 20 linii.

## Nawigacja (dodawana wraz z powstającymi stronami, za zgodą autora)

```yaml
  - 10. Klasy i obiekty:
      - Wprowadzenie: 10-klasy/index.md
      - Definicja klasy: 10-klasy/definicja-klasy.md
      - Atrybuty klasy, metody klasowe i statyczne: 10-klasy/atrybuty-i-metody.md
      - Reprezentacja, właściwości i hermetyzacja: 10-klasy/reprezentacja-i-wlasciwosci.md
      - Dziedziczenie: 10-klasy/dziedziczenie.md
      - Cykl życia obiektu: 10-klasy/cykl-zycia-obiektu.md
```

Pozycja w `docs/index.md` (dodawana wraz z `index.md` rozdziału): „10. [Klasy i obiekty](10-klasy/index.md) — definicja klasy, atrybuty i metody, właściwości, dziedziczenie i własne wyjątki, cykl życia obiektu”.

## Kolejność tworzenia stron i odbiór

Każda strona przechodzi cykl: research w dokumentacji 3.14 → napisanie → uruchomienie wszystkich przykładów (`scripts/verify_page.py`, `--mask` dla adresów; sesje REPL osobno) → `mkdocs build` i `mkdocs build -f mkdocs.clean.yml` → niezależna recenzja (styl, fakty, kolejność pojęć, aktualność 3.14) → naniesienie ustaleń → raport → akceptacja autora → commit. Kolejność: 1 `definicja-klasy.md`, 2 `atrybuty-i-metody.md`, 3 `reprezentacja-i-wlasciwosci.md`, 4 `dziedziczenie.md`, 5 `cykl-zycia-obiektu.md`, 6 `index.md`. Klasy `Czlowiek` i `Okrag` wracają na kilku stronach — ich definicje mają pozostać spójne (te same nazwy parametrów: `imie`, `nazwisko`, `wiek=20`; `promien`).

## Zapowiedzi w przód (do zarejestrowania w `PLAN_ROZWOJU.md` przy akceptacji planu)

- Rozdział 11 (model danych): `__call__` na instancji (strona 1), mechanizm deskryptora za `property` i `classmethod` (strony 2–3), `__eq__`/`__hash__` i `__format__` (strony 3–4), iteratory i menedżery kontekstu jako klasy (index).
- Rozdział 12 (mechanizmy zaawansowane): kolejność rozstrzygania metod i dziedziczenie wielokrotne, klasy abstrakcyjne, `__init_subclass__` (strony 2, 4), klasy danych (index — zapowiedź z 7 pozostaje), kompozycja i wzorce, Singleton przez dekorator klasy, łańcuch `__new__` w hierarchii (strony 4–5).
- Rozdział 13 (wydajność): pomiar pamięci `__slots__` (strona 2), `tracemalloc` (strona 5 — jeśli padnie).
- Rozdział 15 (współbieżność): kompilacja wolnowątkowa a licznik referencji (strona 5).
- Rozdział 16 (narzędzia analizy typów): adnotacje w klasach (strona 1 — jedno zdanie, jeśli padnie).

## Zmiany w rozdziałach 1–9 (wyłącznie domknięcie zapowiedzi, zbiorczo po ukończeniu rozdziału 10)

| Plik:linia | Zmiana | Uwagi |
|---|---|---|
| `03-nazwy-typy/obiekty-i-pamiec.md:90` | „czy nawet definicje klas” → odsyłacz do `../10-klasy/index.md`; zdanie o liczniku referencji → dodatkowo odsyłacz do `cykl-zycia-obiektu.md#licznik-referencji-i-sysgetrefcount` | sekcja 6 `PLAN_ROZWOJU.md`; slug sprawdzić |
| `06-funkcje/funkcje-jako-obiekty.md:140` | `TODO` (inne obiekty wywoływalne) → odsyłacz do `definicja-klasy.md#klasa-jako-obiekt` | |
| `06-funkcje/zasieg-nazw-i-domkniecia.md:18` | `TODO` (dwa linki) → zasięg klasy do `atrybuty-i-metody.md#przestrzen-nazw-klasy`; część o narzędziach analizy typów pozostaje z `TODO` | |
| `06-funkcje/dekoratory.md:540` | `TODO` (linki) → `@property` do `reprezentacja-i-wlasciwosci.md#wasciwosci-property`, `@classmethod`/`@staticmethod` do `atrybuty-i-metody.md#metody-klasy-classmethod`; `@dataclass` pozostaje z `TODO` | slugi bez „ł” |
| `07-moduly/biblioteka-standardowa.md:186` | „mechanizm tworzenia takich typów poznamy w rozdziale o klasach” → odsyłacz do `dziedziczenie.md#funkcje-isinstance-i-issubclass` | |
| `08-wyjatki/zglaszanie-wyjatkow.md:125` | `TODO` (dziedziczenie) → odsyłacz do `dziedziczenie.md#klasa-bazowa-i-klasa-pochodna` | |
| `08-wyjatki/zglaszanie-wyjatkow.md:440–449` | nota „Zapowiedź — własne typy wyjątków” → odsyłacz do `dziedziczenie.md#wasne-klasy-wyjatkow`; usunięcie `TODO` | treść noty zachowana |
| `docs/index.md`, `mkdocs.yml` | pozycja „10. Klasy i obiekty” w spisie i w nav (blok wyżej) | nav rośnie wraz z powstającymi stronami |

Reguła: powyższe zmiany wykonujemy jednym zbiorczym etapem po zaakceptowaniu wszystkich stron rozdziału 10, z kontrolą semantyczną każdego zdania i sprawdzeniem kotwic w zbudowanym HTML. Pozostają bez zmian komentarze `TODO` wskazujące na model danych (`08-wyjatki/with-i-contextlib.md:114`, `09-wejscie-wyjscie/print-i-strumienie.md:204`), klasy danych (`07-moduly/biblioteka-standardowa.md:266`, `09-wejscie-wyjscie/csv-i-json.md:226`), narzędzia analizy typów, wydajność, współbieżność, pandas i tkinter.

## CONTENT HANDOFF (rozbieżności ze źródłami)

Książka ma rację, materiały kursu do poprawki: (a) notatki s. 120: metoda statyczna „nie może być wywołana również dla obiektu” — może, `s.is_full_name('Nowak')` działa (W06 sl. 13 ma to poprawnie); (b) W04 sl. 48 i lab5 sl. 2: `weakref` „działa z listami, słownikami” — nie działa, `weakref.ref([])` zgłasza `TypeError`; słabe referencje obsługują instancje klas, funkcje, zbiory, `frozenset`, a `list`/`dict` tylko przez podklasę; (c) W06 sl. 22: postać `super(Klasa, self)` przedstawiona jako Python 2 — w Pythonie 3 pozostaje poprawną pełną postacią, `super()` bez argumentów jest skrótem; (d) notatki s. 88: `'{self.imie}'.format(self=self)` → f-string; `class Foo(object)` → `class Foo:`; (e) notatki s. 85: odsyłacze do StackOverflow i quantifiedcode → `types.MethodType` i tabela trzech rodzajów metod; (f) W06 sl. 16: `3.14159` → `math.pi`; (g) lab5 sl. 1: komunikaty z `__del__` przy zamykaniu interpretera — kolejność niegwarantowana, w książce jawne `del` przed końcem programu; (h) W06 sl. 42 i 40: `NotImplemented`, `__eq__`/`__hash__`, przeciążanie operatorów — w książce dopiero w rozdziale o modelu danych; (i) notatki s. 86: „nazwy widzialne w wewnętrznym zakresie klasy są poprzedzone podwójnym podkreśleniem” — przekształcanie nazw nie ogranicza widoczności, tylko zmienia nazwę; (j) notatki s. 88: `__new__` „jest to metoda statyczna” — poprawnie, ale przyjmuje `cls` jawnie (zachowujemy); (k) notatki s. 100: `help(Okrag)` z `__init__(self, r)` przy klasie zdefiniowanej z parametrem `value` — w książce jeden parametr `promien`. Bez konfliktu: `__init__` jako inicjalizator, pułapka modyfikowalnego atrybutu klasy, `isinstance()` zamiast `type()`, Singleton z pułapką `__init__`.

## Checklista weryfikacyjna strony (przed odbiorem)

1. Wszystkie deterministyczne przykłady uruchomione na `.venv` (3.14.7) przez `scripts/verify_page.py` (`--mask` dla adresów i `id()`); wartości `getrefcount()` i `gc.collect()` wpisane z uruchomienia z zaznaczeniem zależności od wersji.
2. Brak mechanizmów z późniejszych rozdziałów: operatory na obiektach, `__eq__`, dziedziczenie wielokrotne, `abc`, `dataclass`, wątki; MRO tylko jako nazwa krotki `__mro__`.
3. Kolejność wewnątrz rozdziału (1 → 2 → 3 → 4 → 5; strona 5 uzupełniająca); pojęcia z listy „do wprowadzenia jawnie” wprowadzone w miejscu pierwszego użycia; słowo „konstruktor” tylko w ustalonym znaczeniu.
4. Spójne definicje `Czlowiek` i `Okrag` na wszystkich stronach; nazwy plików bez kolizji z biblioteką standardową; każdy `raise` z komunikatem; ślady wywołań z uruchomienia (wiersze, znaczniki `~~~^^^`, „Did you mean”).
5. Konwencje `CLAUDE.md`: bloki z `title=` albo `.no-copy`, admonitions z polskimi tytułami, cudzysłowy „…”, terminy angielskie z „ang.”; nagłówki rzeczownikowe.
6. `mkdocs build` bez ostrzeżeń oraz `mkdocs build -f mkdocs.clean.yml`; testy warstwy interaktywnej bez regresji.
7. Każdy odsyłacz względny prowadzi do istniejącego pliku i sekcji (`id` w HTML); zapowiedzi w przód prozą z `TODO` i wpisem w `PLAN_ROZWOJU.md`.
8. Struktura: do około 6–7 H2; sekcja „(dla dociekliwych)” tylko na stronie 3; długość według treści.

## Checklista finalnego odbioru rozdziału

1. Wszystkie sześć plików zaakceptowanych; nav i `docs/index.md` zawierają komplet pozycji; H1 = etykieta nav (index: „Wprowadzenie” / H1 „10. Klasy i obiekty”).
2. Zbiorcza redakcja: ujednolicona terminologia (instancja, metoda inicjalizująca, atrybut klasy/instancji, właściwość, klasa bazowa/pochodna, licznik referencji), spójne klasy przykładowe, brak powtórzeń między stronami 1 i 2 (`__dict__`) oraz 2 i 5 (`__slots__`).
3. Tabela „Zmiany w rozdziałach 1–9” wykonana w całości; w `docs/` nie pozostał żaden komentarz `TODO` wskazujący na rozdział o klasach.
4. Pełny przebieg weryfikacji: harness dla wszystkich stron, sesje REPL, audyt kotwic, oba buildy, testy warstwy interaktywnej, `git diff --check`.
5. Ponowna kontrola faktów zależnych od wersji: `__static_attributes__`/`__firstlineno__` (3.13), `property.__name__` (3.13), komunikat właściwości bez settera (3.11), „Did you mean” dla atrybutów (3.10), obiekty nieśmiertelne (3.12, PEP 683), kompilacja wolnowątkowa (3.13, PEP 703).
6. `PLAN_ROZWOJU.md`: status rozdziału 10 „ukończony” z rzeczywistą liczbą linii; zapowiedzi w przód zarejestrowane; CONTENT HANDOFF przekazany autorowi w raporcie końcowym.
7. Commit końcowy; bez integracji do `dev` bez osobnego polecenia.
