# Definicja klasy

Od rozdziału 3 wiemy, że każda wartość w Pythonie jest obiektem określonego typu: liczba typu `int`, tekst typu `str`, a od rozdziału 6 — że także funkcja jest obiektem, typu `function`. Typy wbudowane nie wyczerpują jednak potrzeb programów — konto bankowe, punkt na płaszczyźnie czy zadanie z listy zadań mają własne dane i własne operacje. Instrukcja `class` pozwala zdefiniować **własny typ**: klasa opisuje, jakie dane przechowuje każdy obiekt tego typu i co można z nim zrobić. W tym podrozdziale definiujemy pierwsze klasy, tworzymy z nich obiekty, poznajemy metodę `__init__` i parametr `self`, a na końcu przekonujemy się, że klasa sama jest obiektem.

## Instrukcja `class`

**Klasa** (ang. *class*) to przepis na obiekty: określa, z jakich danych składa się obiekt i jakie operacje na nim wykonujemy. Obiekt utworzony według tego przepisu nazywamy **instancją** (ang. *instance*) klasy; słów „obiekt klasy `Czlowiek`” i „instancja klasy `Czlowiek`” używamy zamiennie. Najprostsza definicja klasy składa się ze słowa kluczowego `class`, nazwy, dwukropka i wciętego ciała — tu pustego, z instrukcją `pass` znaną z rozdziału 4:

```{ .python .no-copy }
>>> class Czlowiek:
...     pass
...
>>> Czlowiek
<class '__main__.Czlowiek'>
>>> c = Czlowiek()
>>> c
<__main__.Czlowiek object at 0x000001D5A3B7F5F0>
>>> type(c)
<class '__main__.Czlowiek'>
```

Nazwa klasy jest pisana w konwencji **CapWords** — każdy wyraz od wielkiej litery, bez podkreśleń (`Czlowiek`, `KontoBankowe`), inaczej niż nazwy funkcji i zmiennych z rozdziału [3. Nazwy i typy](../03-nazwy-typy/nazwy-i-slowa-kluczowe.md#zasady-nazywania), które PEP 8 każe pisać małymi literami z podkreśleniami. Po definicji nazwa `Czlowiek` wskazuje na obiekt klasy, a wywołanie `Czlowiek()` tworzy nową instancję. Wypisana reprezentacja instancji zawiera nazwę modułu (`__main__`, bo klasa powstała w uruchomionym skrypcie albo w konsoli), nazwę klasy i adres obiektu w pamięci — ten sam, który zwróciłaby funkcja `id()` z rozdziału 3, tylko w zapisie szesnastkowym. Adres różni się przy każdym uruchomieniu.

Ciało klasy, jak ciało funkcji, może zaczynać się od docstringu opisującego, co klasa reprezentuje. Funkcja `help()` z rozdziału 2 wyświetla go w nagłówku pomocy, a dla klas z metodami — także ich listę:

```{ .python .no-copy }
>>> class Czlowiek:
...     """Osoba o imieniu, nazwisku i wieku."""
...
>>> Czlowiek.__doc__
'Osoba o imieniu, nazwisku i wieku.'
>>> help(Czlowiek)
Help on class Czlowiek in module __main__:

class Czlowiek(builtins.object)
 |  Osoba o imieniu, nazwisku i wieku.
 |
 |  Data descriptors defined here:
 ...
```

Dopisek `builtins.object` w nagłówku pomocy informuje, że nasza klasa pochodzi od wbudowanej klasy `object`, wspólnego przodka wszystkich typów w Pythonie; do tej zależności wracamy w podrozdziale o dziedziczeniu. Pozostałą część wydruku (`Data descriptors`) pomijamy — w tym rozdziale nie będzie nam potrzebna.

## Tworzenie obiektu i metoda `__init__`

Pusta klasa jest mało przydatna: każdy jej obiekt wygląda tak samo. Zwykle chcemy, aby obiekt od razu po utworzeniu miał określony stan — człowiek imię i nazwisko, konto właściciela i saldo. Służy do tego **metoda specjalna** (ang. *special method*) `__init__`. Metody specjalne rozpoznajemy po nazwach z dwoma podkreśleniami po obu stronach (ang. *double underscore*, stąd potoczne określenie „dunder”); zwykle nie wywołujemy ich sami — Python wywołuje je w określonych sytuacjach, a `__init__` po utworzeniu każdego obiektu (wyjątkiem jest wywołanie wersji z klasy bazowej przez `super()`, które poznamy przy dziedziczeniu):

```python title="czlowiek.py"
class Czlowiek:
    """Osoba o imieniu, nazwisku i wieku."""

    def __init__(self, imie, nazwisko, wiek=20):
        self.imie = imie
        self.nazwisko = nazwisko
        self.wiek = wiek


c1 = Czlowiek("Jan", "Kowalski")
c2 = Czlowiek("Anna", "Nowak", 34)
print(c1.imie, c1.nazwisko, c1.wiek)
print(c2.imie, c2.nazwisko, c2.wiek)
```

```{ .text .no-copy }
Jan Kowalski 20
Anna Nowak 34
```

Wywołanie `Czlowiek("Jan", "Kowalski")` wykonuje dwa kroki: Python tworzy nowy, pusty obiekt klasy `Czlowiek`, a następnie wywołuje `__init__` z tym obiektem jako pierwszym argumentem i z argumentami wywołania jako pozostałymi. Metoda `__init__` jest więc **metodą inicjalizującą** (ang. *initializer*): nie tworzy obiektu, lecz nadaje mu stan początkowy. W innych językach podobną rolę pełni konstruktor, ale w Pythonie „konstruktorem” można nazwać najwyżej całe wywołanie klasy — składa się ono z utworzenia obiektu i z jego inicjalizacji, a `__init__` odpowiada tylko za drugi krok. Za pierwszy odpowiada metoda `__new__`, którą omawiamy w podrozdziale o cyklu życia obiektu; w zwykłym kodzie nigdy nie trzeba jej definiować.

Definicja `__init__` to zwykła definicja funkcji wewnątrz ciała klasy, więc obowiązują w niej wszystkie reguły z rozdziału [6. Funkcje](../06-funkcje/argumenty-i-parametry.md#wartosci-domyslne): parametry pozycyjne, nazwane i domyślne (`wiek=20`), także `*args` i `**kwargs`. Dwa obiekty utworzone z tej samej klasy mają niezależne stany — `c1` i `c2` przechowują inne imiona i inny wiek, choć powstały według jednego przepisu.

Metoda `__init__` niczego nie zwraca. Próba zwrócenia z niej wartości innej niż `None` kończy się wyjątkiem, bo wynikiem wywołania klasy ma być nowy obiekt, a nie to, co zwróci `__init__`:

```python title="init-return.py"
class Licznik:
    def __init__(self, start):
        self.wartosc = start
        return start


licznik = Licznik(0)
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "init-return.py", line 7, in <module>
    licznik = Licznik(0)
TypeError: __init__() should return None, not 'int'
```

## Parametr `self`

Pierwszy parametr każdej zwykłej metody wywoływanej na obiekcie wskazuje ten obiekt. Nazwa `self` jest konwencją: składnia języka jej nie wymusza, ale cała społeczność jej używa, a narzędzia diagnostyczne interpretera — jak podpowiedzi w śladzie wywołań, które zobaczymy w następnym podrozdziale — rozpoznają właśnie tę nazwę. Przez `self` metoda odczytuje i ustawia atrybuty obiektu, na którym została wywołana: `self.imie = imie` w `__init__` zapisuje wartość parametru `imie` w tworzonym obiekcie. Skąd `self` bierze wartość? Wywołanie metody na obiekcie jest skrótem: `obiekt.metoda(argumenty)` oznacza `Klasa.metoda(obiekt, argumenty)`. Python wstawia obiekt jako pierwszy argument, a my w definicji odbieramy go pod nazwą `self`:

```python title="self-demo.py"
class Klasa:
    def __init__(self):
        print("w __init__:", id(self))

    def pokaz(self, etykieta):
        print(etykieta, id(self))


k1 = Klasa()
print("obiekt k1:  ", id(k1))
k1.pokaz("k1.pokaz:   ")
Klasa.pokaz(k1, "Klasa.pokaz:")
```

```{ .text .no-copy }
w __init__: 2027213254608
obiekt k1:   2027213254608
k1.pokaz:    2027213254608
Klasa.pokaz: 2027213254608
```

Wszystkie cztery wiersze pokazują ten sam identyfikator: `self` wewnątrz metod to dokładnie ten obiekt, który na zewnątrz nosi nazwę `k1`. Zapis `Klasa.pokaz(k1, ...)` — z jawnym przekazaniem obiektu — jest poprawny i daje ten sam wynik co `k1.pokaz(...)`, choć w praktyce używamy krótszej formy. Programiści C++ znają tę samą ideę pod nazwą `this`, z tą różnicą, że tam wskaźnik na obiekt jest przekazywany niejawnie, a w Pythonie parametr `self` jest zwykłym, jawnie zapisanym parametrem.

Jawny `self` tłumaczy też jeden z najczęstszych komunikatów błędu przy pierwszych klasach. Gdy w definicji metody zapomnimy o pierwszym parametrze, wywołanie `obiekt.metoda()` przekazuje obiekt do metody, która nie ma gdzie go odebrać:

```python title="bez-self.py"
import math


class Okrag:
    def __init__(self, promien):
        self.promien = promien

    def pole():
        return math.pi * promien**2


o = Okrag(2)
print(o.pole())
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "bez-self.py", line 13, in <module>
    print(o.pole())
          ~~~~~~^^
TypeError: Okrag.pole() takes 0 positional arguments but 1 was given
```

Komunikat mówi, że `pole()` nie przyjmuje argumentów, a otrzymała jeden — tym jednym argumentem jest obiekt `o`. Odwrotna pomyłka — wywołanie poprawnie zdefiniowanej metody `pole(self)` przez klasę bez podania obiektu, `Okrag.pole()` — daje komunikat `missing 1 required positional argument: 'self'`. Oba komunikaty należy czytać tak samo: liczba argumentów nie zgadza się z liczbą parametrów, bo Python liczy `self` jak każdy inny parametr.

## Atrybuty instancji

Dane przechowywane w obiekcie nazywamy **atrybutami instancji** (ang. *instance attributes*). Powstają w chwili pierwszego przypisania `self.nazwa = wartość` — zwykle w `__init__`, aby każdy obiekt klasy miał ten sam zestaw atrybutów. Odczytujemy je i zmieniamy zapisem `obiekt.nazwa`:

```python title="atrybuty.py"
class Czlowiek:
    def __init__(self, imie, nazwisko, wiek=20):
        self.imie = imie
        self.nazwisko = nazwisko
        self.wiek = wiek


c1 = Czlowiek("Jan", "Kowalski")
c2 = Czlowiek("Anna", "Nowak", 34)
c1.wiek = 21
c1.pesel = "80010112345"
print(c1.wiek, c1.pesel)
print(c1.__dict__)
print(c2.__dict__)
print(c2.pesel)
```

```{ .text .no-copy }
21 80010112345
{'imie': 'Jan', 'nazwisko': 'Kowalski', 'wiek': 21, 'pesel': '80010112345'}
{'imie': 'Anna', 'nazwisko': 'Nowak', 'wiek': 34}
Traceback (most recent call last):
  File "atrybuty.py", line 15, in <module>
    print(c2.pesel)
          ^^^^^^^^
AttributeError: 'Czlowiek' object has no attribute 'pesel'
```

Przypisanie `c1.wiek = 21` zmienia istniejący atrybut, a `c1.pesel = ...` tworzy nowy — ale wyłącznie w obiekcie `c1`. Obiekt `c2` powstał z tego samego przepisu, lecz nikt nie nadał mu atrybutu `pesel`, więc odczyt kończy się wyjątkiem `AttributeError`. Wydruki pokazują, gdzie ten stan jest przechowywany: każdy obiekt ma słownik `__dict__`, w którym nazwy atrybutów są kluczami, a ich wartości — wartościami. Dodawanie atrybutów spoza `__init__` jest w Pythonie dozwolone, ale utrudnia czytanie kodu: czytelnik klasy powinien znaleźć pełną listę atrybutów w jednym miejscu, w `__init__`. Do dynamicznego dodawania i sprawdzania atrybutów wracamy w następnym podrozdziale przy introspekcji.

Przy literówce w nazwie atrybutu interpreter podpowiada najbliższą istniejącą nazwę, jak przy literówce w nazwie modułu w rozdziale 8:

```python title="literowka.py"
class Okrag:
    def __init__(self, promien):
        self.promien = promien


o = Okrag(2)
print(o.promin)
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "literowka.py", line 7, in <module>
    print(o.promin)
          ^^^^^^^^
AttributeError: 'Okrag' object has no attribute 'promin'. Did you mean: 'promien'?
```

## Metody instancji

Funkcja zdefiniowana w ciele klasy, której pierwszym parametrem jest `self`, to **metoda instancji** (ang. *instance method*): operacja wykonywana na konkretnym obiekcie, z dostępem do jego atrybutów. Klasa `Konto` pokazuje trzy typowe role metod instancji — zmieniającą stan obiektu, zwracającą wartość obliczoną ze stanu oraz wywołującą inną metodę tego samego obiektu:

```python title="konto.py"
class Konto:
    """Konto bankowe z historią operacji."""

    def __init__(self, wlasciciel, saldo=0):
        self.wlasciciel = wlasciciel
        self.saldo = saldo
        self.historia = []

    def wplata(self, kwota):
        """Dopisuje kwotę do salda i zwraca konto."""
        self.saldo += kwota
        self.historia.append(f"+{kwota}")
        return self

    def wyplata(self, kwota):
        """Odejmuje kwotę od salda; brak środków zgłasza ValueError."""
        if kwota > self.saldo:
            raise ValueError(f"brak środków: saldo {self.saldo}, żądano {kwota}")
        self.saldo -= kwota
        self.historia.append(f"-{kwota}")
        return self

    def liczba_operacji(self):
        """Zwraca liczbę zapisanych operacji."""
        return len(self.historia)

    def wyciag(self):
        """Zwraca opis konta z liczbą operacji."""
        return f"{self.wlasciciel}: saldo {self.saldo}, operacji: {self.liczba_operacji()}"


k = Konto("Jan", 1000)
k.wplata(500).wplata(200)
k.wyplata(300)
print(k.wyciag())
print(k.historia)
try:
    k.wyplata(5000)
except ValueError as e:
    print("odmowa:", e)
```

```{ .text .no-copy }
Jan: saldo 1400, operacji: 3
['+500', '+200', '-300']
odmowa: brak środków: saldo 1400, żądano 5000
```

Metody `wplata()` i `wyplata()` zmieniają atrybuty obiektu i zwracają `self`, dzięki czemu wywołania można łączyć w łańcuch: `k.wplata(500).wplata(200)` wywołuje drugą metodę na obiekcie zwróconym przez pierwszą — tym samym koncie. Zwracanie `self` nie jest obowiązkowe; wiele metod zmieniających stan zwraca `None`, jak `list.append()` z rozdziału 5. Metoda `wyciag()` korzysta z `liczba_operacji()` przez `self.` — wewnątrz klasy własne metody wywołujemy zawsze na `self`, a nie po samej nazwie, bo nazwy zdefiniowane w ciele klasy nie są widoczne w ciałach metod jako zwykłe zmienne (do tej reguły wracamy w następnym podrozdziale). Kontrola argumentów przez `raise ValueError` z komunikatem to zasada z rozdziału [8. Wyjątki i zarządzanie zasobami](../08-wyjatki/zglaszanie-wyjatkow.md#instrukcja-raise): metoda, która nie może wykonać operacji, zgłasza wyjątek zamiast pozostawić obiekt w niepoprawnym stanie bez żadnego sygnału.

## Klasa jako obiekt

Klasa nie jest tylko zapisem w kodzie źródłowym — po wykonaniu instrukcji `class` istnieje jako obiekt, tak jak funkcja po instrukcji `def` (rozdział [6. Funkcje](../06-funkcje/definiowanie-funkcji.md#funkcja-jako-obiekt)). Ma własny typ, nazwę i docstring, a wywołana zachowuje się jak funkcja zwracająca nowy obiekt:

```python title="klasa-jako-obiekt.py"
class Czlowiek:
    """Osoba o imieniu, nazwisku i wieku."""

    def __init__(self, imie, nazwisko, wiek=20):
        self.imie = imie
        self.nazwisko = nazwisko
        self.wiek = wiek


c = Czlowiek("Jan", "Kowalski")
print(type(c), c.__class__)
print(type(c) is Czlowiek)
print(type(Czlowiek), Czlowiek.__name__)
print(callable(Czlowiek), callable(c))


def utworz(klasa, *argumenty):
    """Zwraca nowy obiekt podanej klasy."""
    return klasa(*argumenty)


print(utworz(int, "7"), utworz(Czlowiek, "Anna", "Nowak").imie)
print([klasa.__name__ for klasa in (int, str, Czlowiek)])
```

```{ .text .no-copy }
<class '__main__.Czlowiek'> <class '__main__.Czlowiek'>
True
<class 'type'> Czlowiek
True False
7 Anna
['int', 'str', 'Czlowiek']
```

Funkcja `type()` z rozdziału 2 zwraca dla instancji jej klasę — ten sam obiekt, który zapisaliśmy pod nazwą `Czlowiek` — a atrybut `__class__` daje to samo. Typem samej klasy jest `type`: klasy są instancjami typu `type`, tak jak liczby są instancjami `int`. Klasa jest obiektem wywoływalnym w sensie z rozdziału [6. Funkcje](../06-funkcje/funkcje-jako-obiekty.md#obiekty-wywoywalne): `callable(Czlowiek)` zwraca `True`, a wywołanie tworzy instancję. Sama instancja `c` wywoływalna nie jest — obiekty, które można wywoływać jak funkcje, poznamy w rozdziale o modelu danych. <!-- TODO: link po powstaniu rozdziału o modelu danych -->

Skoro klasa jest obiektem, można ją przekazać jako argument, umieścić w krotce czy liście i przypisać do innej nazwy — funkcja `utworz()` przyjmuje klasę i wywołuje ją, nie wiedząc, czy dostała typ wbudowany, czy nasz. Domyślna reprezentacja `<__main__.Czlowiek object at ...>` pochodzi z klasy `object` i nie mówi nic o stanie obiektu; w podrozdziale o reprezentacji nauczymy się ją zastąpić własną.
