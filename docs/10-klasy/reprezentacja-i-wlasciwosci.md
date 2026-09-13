# Reprezentacja, właściwości i hermetyzacja

Obiekty naszych klas wypisują się dotąd jako `<__main__.Czlowiek object at 0x...>` — zapis, z którego nie wynika nic o ich stanie. W tym podrozdziale nadajemy obiektom czytelną reprezentację metodami `__repr__` i `__str__`, zamieniamy zwykły atrybut we **właściwość** z walidacją bez zmiany sposobu użycia klasy, poznajemy pułapkę rekurencji we właściwości oraz konwencje nazw z podkreśleniami, którymi Python zastępuje modyfikatory dostępu znane z innych języków. Na koniec, dla dociekliwych, zaglądamy do klasy `property`.

## Metody `__repr__` i `__str__`

Python zna dwie tekstowe reprezentacje obiektu: **oficjalną** (ang. *official*), jednoznaczną, przeznaczoną dla programisty — zwraca ją funkcja `repr()`, którą poznaliśmy w rozdziale [7. Moduły, pakiety i biblioteka standardowa](../07-moduly/moduly-i-import.md) i przy obiekcie wyjątku w rozdziale 8, a w f-stringach konwersja `!r` z rozdziału 9 — oraz **nieformalną** (ang. *informal*), czytelną dla użytkownika programu, zwracaną przez `str()`. Dla własnej klasy definiujemy je metodami specjalnymi `__repr__` i `__str__`. Domyślna reprezentacja z klasy `object` pokazuje tylko nazwę modułu, nazwę klasy i adres:

```python title="domyslna-reprezentacja.py"
class Czlowiek:
    def __init__(self, imie, nazwisko, wiek=20):
        self.imie = imie
        self.nazwisko = nazwisko
        self.wiek = wiek


c1 = Czlowiek("Jan", "Kowalski")
c2 = Czlowiek("Anna", "Nowak", 34)
print(c1)
print([c1, c2])
```

```{ .text .no-copy }
<__main__.Czlowiek object at 0x000001E7C2B4F5F0>
[<__main__.Czlowiek object at 0x000001E7C2B4F5F0>, <__main__.Czlowiek object at 0x000001E7C2B4F650>]
```

Metoda `__repr__` powinna zwracać łańcuch, który jednoznacznie opisuje obiekt — najlepiej w postaci wyrażenia tworzącego taki sam obiekt, z wartościami atrybutów zapisanymi przez konwersję `!r` z rozdziału [9. Wejście, wyjście i pliki](../09-wejscie-wyjscie/formatowanie.md#f-stringi-wyrazenia-konwersje-i-pola-zagniezdzone), aby łańcuchy miały cudzysłowy. Metoda `__str__` zwraca opis dla człowieka:

```python title="repr-str.py"
class Czlowiek:
    def __init__(self, imie, nazwisko, wiek=20):
        self.imie = imie
        self.nazwisko = nazwisko
        self.wiek = wiek

    def __repr__(self):
        return f"Czlowiek({self.imie!r}, {self.nazwisko!r}, {self.wiek})"

    def __str__(self):
        return f"{self.imie} {self.nazwisko} (lat {self.wiek})"


class Punkt:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Punkt({self.x}, {self.y})"


c = Czlowiek("Jan", "Kowalski")
print(c)
print(str(c), "|", repr(c))
print(f"{c} / {c!r}")
print([c])
print({"prezes": c})
p = Punkt(1, 2)
print(p, str(p), [p])
```

```{ .text .no-copy }
Jan Kowalski (lat 20)
Jan Kowalski (lat 20) | Czlowiek('Jan', 'Kowalski', 20)
Jan Kowalski (lat 20) / Czlowiek('Jan', 'Kowalski', 20)
[Czlowiek('Jan', 'Kowalski', 20)]
{'prezes': Czlowiek('Jan', 'Kowalski', 20)}
Punkt(1, 2) Punkt(1, 2) [Punkt(1, 2)]
```

Kto wywołuje którą metodę? Funkcje `print()` i `str()` używają `__str__`; f-string bez konwersji wywołuje `format()`, a więc metodę specjalną `__format__`, która w wersji odziedziczonej po `object` sprowadza się do `__str__` (do `__format__` wracamy w rozdziale o modelu danych). Funkcja `repr()`, konwersja `!r`, konsola wypisująca wynik wyrażenia oraz kontenery — lista, słownik, krotka — wypisujące swoje elementy używają `__repr__`. Dlatego w liście `[c]` widzimy zapis oficjalny, mimo że sam `print(c)` daje nieformalny. Gdy klasa definiuje tylko `__repr__`, jak `Punkt`, `str()` i `print()` korzystają z niego — odwrotnie to nie działa, więc jeśli definiujemy jedną z tych metod, powinna to być `__repr__`. Dobra reprezentacja oficjalna ułatwia diagnostykę: w konsoli, pod debuggerem i w dzienniku z rozdziału 8 zamiast adresu widzimy stan obiektu.

## Właściwości — `@property`

Atrybuty instancji są w Pythonie dostępne wprost: `o.promien` odczytuje, `o.promien = 5` zapisuje. To wygodne, ale nie pozwala sprawdzić przypisywanej wartości — okrąg o ujemnym promieniu powstanie bez żadnego błędu. W innych językach odpowiedzią są metody dostępowe `get_promien()` i `set_promien()`, które zmieniają sposób użycia klasy. Python oferuje **właściwość** (ang. *property*): parę metod, do których obiekt sięga przy odczycie i zapisie atrybutu, podczas gdy kod korzystający z klasy nadal pisze `o.promien`. Właściwość definiujemy dekoratorem `@property` nad metodą odczytu (ang. *getter*), a metodę zapisu (ang. *setter*) dekoratorem `@nazwa.setter`:

```python title="okrag.py"
import math


class Okrag:
    """Okrąg o nieujemnym promieniu."""

    def __init__(self, promien):
        self.promien = promien

    @property
    def promien(self):
        """Promień okręgu."""
        return self._promien

    @promien.setter
    def promien(self, wartosc):
        if wartosc < 0:
            raise ValueError(f"promień nie może być ujemny: {wartosc}")
        self._promien = wartosc

    @property
    def pole(self):
        """Pole okręgu, wyliczane z promienia."""
        return math.pi * self._promien**2


o = Okrag(2)
print(o.promien, round(o.pole, 2))
o.promien = 3
print(o.promien, round(o.pole, 2), vars(o))
try:
    o.promien = -1
except ValueError as e:
    print("ValueError:", e)
try:
    o.pole = 100
except AttributeError as e:
    print("AttributeError:", e)
try:
    Okrag(-5)
except ValueError as e:
    print("ValueError:", e)
```

```{ .text .no-copy }
2 12.57
3 28.27 {'_promien': 3}
ValueError: promień nie może być ujemny: -1
AttributeError: property 'pole' of 'Okrag' object has no setter
ValueError: promień nie może być ujemny: -5
```

Z zewnątrz `promien` wygląda jak zwykły atrybut, ale odczyt `o.promien` wywołuje metodę odczytu, a przypisanie `o.promien = 3` — metodę zapisu, która sprawdza wartość i dopiero wtedy zapisuje ją w atrybucie `_promien`. Sama wartość jest przechowywana pod inną nazwą niż właściwość — w **polu zapasowym** (ang. *backing field*) `_promien`, jedynym wpisie w `vars(o)`. Metoda zapisu działa również w `__init__`: przypisanie `self.promien = promien` przechodzi przez tę samą walidację, więc `Okrag(-5)` zgłasza wyjątek, a obiekt z niepoprawnym stanem nigdy nie powstaje. Właściwość `pole` ma tylko metodę odczytu, więc jest **tylko do odczytu**: wartość jest wyliczana przy każdym odczycie z bieżącego promienia, a próba przypisania kończy się `AttributeError` z komunikatem wskazującym brak metody zapisu. Trzecią, rzadko potrzebną metodą właściwości jest metoda usuwania (ang. *deleter*), definiowana dekoratorem `@nazwa.deleter` i wywoływana przez `del o.nazwa`.

Właściwość jest narzędziem, po które sięgamy z konkretnego powodu — walidacji, obliczenia, zachowania zgodności po zmianie wewnętrznej reprezentacji — a nie zamiennikiem każdego atrybutu. Zwykły atrybut wystarcza, dopóki nie ma nic do sprawdzenia; ponieważ sposób użycia klasy się nie zmienia, właściwość można dodać później, gdy potrzeba się pojawi, bez poprawiania kodu, który z klasy korzysta.

## Pułapka: rekurencja we właściwości

Nazwa właściwości i nazwa pola zapasowego muszą się różnić. Jeśli metoda odczytu albo zapisu właściwości `wartosc` odwoła się do `self.wartosc`, wywoła samą siebie:

```python title="rekurencja-wlasciwosci.py"
class Zle:
    def __init__(self, x):
        self.wartosc = x

    @property
    def wartosc(self):
        return self.wartosc

    @wartosc.setter
    def wartosc(self, v):
        self.wartosc = v


try:
    Zle(1)
except RecursionError as e:
    print("RecursionError:", e)
```

```{ .text .no-copy }
RecursionError: maximum recursion depth exceeded
```

Już w `__init__` przypisanie `self.wartosc = x` wywołuje metodę zapisu, a ta przypisuje `self.wartosc = v`, czyli ponownie wywołuje metodę zapisu — bez końca, aż do wyczerpania limitu rekurencji z rozdziału [6. Funkcje](../06-funkcje/rekurencja.md#limit-rekurencji). Bez `try` interpreter wypisałby ślad, w którym powtarzające się ramki metody zapisu są zwinięte do jednego wiersza `[Previous line repeated 995 more times]` (liczba zależy od wersji interpretera i sposobu uruchomienia skryptu). Poprawna wersja przechowuje wartość w polu `_wartosc`, jak `_promien` w klasie `Okrag`.

## Konwencje hermetyzacji — `_nazwa` i `__nazwa`

**Hermetyzacja** (ang. *encapsulation*) to zasada, według której szczegóły wewnętrzne obiektu — pola zapasowe, metody pomocnicze — nie należą do jego interfejsu i kod zewnętrzny nie powinien na nich polegać. Python nie ma słów kluczowych `private` i `protected`; zamiast blokady stosuje umowę zapisaną w nazwach. Nazwa z jednym podkreśleniem na początku, jak `_promien` czy `_saldo`, oznacza element wewnętrzny: technicznie dostępny, ale nieprzeznaczony do użycia spoza klasy. Nazwa z dwoma podkreśleniami na początku (i najwyżej jednym na końcu) uruchamia dodatkowo mechanizm **przekształcania nazw** (ang. *name mangling*): kompilator zamienia `__pin` wewnątrz klasy `Konto` na `_Konto__pin`:

```python title="hermetyzacja.py"
class Konto:
    def __init__(self, wlasciciel, pin):
        self.wlasciciel = wlasciciel
        self._saldo = 0
        self.__pin = pin

    def _zapisz(self, kwota):
        self._saldo += kwota

    def wplata(self, kwota):
        self._zapisz(kwota)

    def sprawdz_pin(self, pin):
        return pin == self.__pin


k = Konto("Jan", 1234)
k.wplata(100)
print(k._saldo, k.sprawdz_pin(1234))
print(vars(k))
try:
    print(k.__pin)
except AttributeError as e:
    print("AttributeError:", e)
print(k._Konto__pin)
k.__pin = 0
print(vars(k), k.sprawdz_pin(1234))
```

```{ .text .no-copy }
100 True
{'wlasciciel': 'Jan', '_saldo': 100, '_Konto__pin': 1234}
AttributeError: 'Konto' object has no attribute '__pin'
1234
{'wlasciciel': 'Jan', '_saldo': 100, '_Konto__pin': 1234, '__pin': 0} True
```

Odczyt `k._saldo` działa — podkreślenie jest tylko sygnałem dla czytelnika kodu. Odczyt `k.__pin` kończy się `AttributeError`, bo w słowniku obiektu nie ma nazwy `__pin`, lecz `_Konto__pin`; kto zna ten mechanizm, może odczytać atrybut również tą drogą. Ostatnie wiersze pokazują, że przekształcanie dotyczy wyłącznie kodu wewnątrz definicji klasy: przypisanie `k.__pin = 0` na zewnątrz tworzy nowy, niezależny atrybut o dosłownej nazwie `__pin`, a metoda `sprawdz_pin()` nadal używa `_Konto__pin`. Podwójne podkreślenie służy więc nie ukrywaniu, lecz ochronie przed przypadkowym zderzeniem nazw: klasa dziedzicząca po `Konto` (dziedziczenie omawiamy w następnym podrozdziale) może zdefiniować własny atrybut `__pin`, który po przekształceniu otrzyma inną nazwę i nie nadpisze `_Konto__pin`. Na co dzień wystarcza pojedyncze podkreślenie. Nazw z podkreśleniami po obu stronach, jak `__init__`, nie tworzymy sami — są zarezerwowane dla metod specjalnych języka.

## Klasa `property` (dla dociekliwych)

Zapis `@property` sugeruje funkcję-dekorator, ale `property` jest klasą, a właściwość — jej instancją przechowywaną jako atrybut klasy. Pełna sygnatura `property(fget=None, fset=None, fdel=None, doc=None)` przyjmuje trzy metody i docstring; klasa `Okrag` bez dekoratorów wygląda tak:

```python title="property-klasa.py"
class Okrag:
    """Okrąg o nieujemnym promieniu."""

    def __init__(self, promien):
        self.promien = promien

    def _czytaj_promien(self):
        print("odczyt promienia")
        return self._promien

    def _ustaw_promien(self, wartosc):
        print("zapis promienia")
        if wartosc < 0:
            raise ValueError(f"promień nie może być ujemny: {wartosc}")
        self._promien = wartosc

    def _usun_promien(self):
        print("usunięcie promienia")
        del self._promien

    promien = property(_czytaj_promien, _ustaw_promien, _usun_promien, "Promień okręgu.")


o = Okrag(2)
print(o.promien)
del o.promien
print(vars(o))
print(type(Okrag.promien).__name__, Okrag.promien.__doc__)
print(Okrag.promien.fget.__name__, Okrag.promien.fset.__name__)
```

```{ .text .no-copy }
zapis promienia
odczyt promienia
2
usunięcie promienia
{}
property Promień okręgu.
_czytaj_promien _ustaw_promien
```

Atrybut klasy `Okrag.promien` jest obiektem typu `property`, który pamięta trzy funkcje pod nazwami `fget`, `fset` i `fdel` oraz docstring. Dekorator `@property` to skrót dla `promien = property(promien)`, a `@promien.setter` zwraca nowy obiekt `property` z dodaną metodą zapisu — stąd w wersji z dekoratorami wszystkie trzy metody noszą tę samą nazwę, `promien`. Funkcja `help(Okrag)` wymienia właściwość wśród deskryptorów danych (`Data descriptors`), obok technicznych wpisów `__dict__` i `__weakref__`, wraz z jej docstringiem; właściwości tylko do odczytu, jak `pole` z `okrag.py`, trafiają do osobnej sekcji `Readonly properties`:

```{ .python .no-copy }
>>> help(Okrag)
Help on class Okrag in module __main__:

class Okrag(builtins.object)
 |  Okrag(promien)
 |
 |  Okrąg o nieujemnym promieniu.
 ...
 |  Data descriptors defined here:
 ...
 |  promien
 |      Promień okręgu.
```

Nagłówek `Data descriptors` wskazuje mechanizm: obiekt `property` jest **deskryptorem** (ang. *descriptor*) — obiektem, któremu Python oddaje kontrolę nad odczytem i zapisem atrybutu klasy, w której go umieszczono. Ten sam mechanizm stoi za metodami klasy i statycznymi z poprzedniego podrozdziału oraz za wiązaniem zwykłych funkcji z instancją; omawiamy go w rozdziale o modelu danych. <!-- TODO: link po powstaniu rozdziału o modelu danych -->
