# Atrybuty klasy, metody klasowe i statyczne

Atrybuty instancji z poprzedniego podrozdziału należą do pojedynczego obiektu. Klasa może jednak przechowywać także dane wspólne dla wszystkich swoich instancji — stałą, licznik utworzonych obiektów, wartość domyślną — oraz metody, które nie potrzebują konkretnego obiektu. W tym podrozdziale odróżniamy atrybuty klasy od atrybutów instancji, poznajemy pułapkę modyfikowalnego atrybutu klasy, zaglądamy do przestrzeni nazw klasy (domykając zapowiedź zasięgu klasy z rozdziału 6), ograniczamy atrybuty przez `__slots__` i uzupełniamy metody instancji o metody klasy i metody statyczne.

## Atrybut klasy a atrybut instancji

**Atrybut klasy** (ang. *class attribute*) to nazwa przypisana bezpośrednio w ciele klasy, poza metodami. Istnieje w jednym egzemplarzu, wspólnym dla klasy i wszystkich jej instancji — w przeciwieństwie do atrybutu instancji, który każdy obiekt ma własny. Typowym zastosowaniem jest licznik utworzonych obiektów:

```python title="licznik.py"
class Bug:
    """Obiekt z identyfikatorem nadawanym z licznika klasy."""

    licznik = 0

    def __init__(self):
        Bug.licznik += 1
        self.id = Bug.licznik


b1 = Bug()
b2 = Bug()
print(Bug.licznik, b1.licznik, b2.licznik)
print(b1.id, b2.id)
print(b1.__dict__, b2.__dict__)
```

```{ .text .no-copy }
2 2 2
1 2
{'id': 1} {'id': 2}
```

Atrybut `licznik` jest dostępny zarówno przez klasę (`Bug.licznik`), jak i przez każdą instancję (`b1.licznik`), a jego zmiana w `__init__` jest widoczna wszędzie, bo istnieje tylko jeden licznik. Atrybut `id` należy do instancji: słowniki `__dict__` obu obiektów zawierają wyłącznie jego, a `licznik` w nich nie występuje — jest przechowywany w klasie. Odczyt `b1.licznik` działa dzięki kolejności wyszukiwania atrybutów: dla zwykłych atrybutów Python sprawdza najpierw słownik instancji, a gdy nazwy tam nie ma — słownik jej klasy (właściwości z następnego podrozdziału są wyjątkiem: mają pierwszeństwo przed słownikiem instancji). Z tej kolejności wynika zachowanie, które zaskakuje przy pierwszym spotkaniu:

```python title="przeslanianie.py"
class Czlowiek:
    gatunek = "Homo sapiens"

    def __init__(self, imie):
        self.imie = imie


c1 = Czlowiek("Jan")
c2 = Czlowiek("Anna")
c1.gatunek = "Homo neanderthalensis"
print(c1.gatunek, "|", c2.gatunek, "|", Czlowiek.gatunek)
print(c1.__dict__)
print(type(c1).gatunek)
Czlowiek.gatunek = "Homo sapiens sapiens"
print(c1.gatunek, "|", c2.gatunek)
```

```{ .text .no-copy }
Homo neanderthalensis | Homo sapiens | Homo sapiens
{'imie': 'Jan', 'gatunek': 'Homo neanderthalensis'}
Homo sapiens
Homo neanderthalensis | Homo sapiens sapiens
```

Przypisanie `c1.gatunek = ...` nie zmienia atrybutu klasy — tworzy nowy atrybut instancji `c1`, który od tej chwili **przesłania** (ang. *shadows*) atrybut klasy przy odczycie przez `c1`. Obiekt `c2` i sama klasa nadal widzą pierwotną wartość, a atrybut klasy pozostaje dostępny z `c1` przez `type(c1).gatunek`. Dopiero przypisanie do klasy, `Czlowiek.gatunek = ...`, zmienia wspólną wartość — widzi ją `c2`, ale nie `c1`, którego własny atrybut nadal przesłania atrybut klasy. Zasada jest prosta: przypisanie przez instancję zawsze trafia do instancji, przypisanie przez klasę — do klasy. Dlatego w `__init__` klasy `Bug` licznik zwiększamy zapisem `Bug.licznik += 1`; zapis `self.licznik += 1` odczytałby wartość z klasy, a wynik zapisał w instancji, tworząc dla każdego obiektu osobny licznik równy 1.

## Pułapka: modyfikowalny atrybut klasy

Skoro atrybut klasy jest jeden, to gdy jest obiektem modyfikowalnym — listą, słownikiem, zbiorem — każda instancja modyfikuje ten sam obiekt. Poniższa klasa miała dawać każdej grupie własną listę studentów:

```python title="grupa.py"
class Grupa:
    studenci = []

    def dodaj(self, nazwisko):
        self.studenci.append(nazwisko)


g1 = Grupa()
g2 = Grupa()
g1.dodaj("Kowalski")
print(g1.studenci, g2.studenci, g1.studenci is g2.studenci)
```

```{ .text .no-copy }
['Kowalski'] ['Kowalski'] True
```

Metoda `dodaj()` nie przypisuje niczego do `self.studenci` — wywołuje `append()` na obiekcie odczytanym przez `self.studenci`, a tym obiektem jest lista z klasy. Obie grupy dzielą jedną listę, co potwierdza `is`. To ta sama pułapka, którą znamy z rozdziału [6. Funkcje](../06-funkcje/argumenty-i-parametry.md#puapka-modyfikowalnej-wartosci-domyslnej) jako modyfikowalną wartość domyślną parametru: obiekt utworzony raz, przy definicji, jest współdzielony przez wszystkie wywołania — tu przez wszystkie instancje. Rozwiązanie jest to samo: obiekt modyfikowalny tworzymy dla każdej instancji osobno, w `__init__`:

```python title="grupa-poprawiona.py"
class Grupa:
    def __init__(self):
        self.studenci = []

    def dodaj(self, nazwisko):
        self.studenci.append(nazwisko)


g1 = Grupa()
g2 = Grupa()
g1.dodaj("Kowalski")
print(g1.studenci, g2.studenci, g1.studenci is g2.studenci)
```

```{ .text .no-copy }
['Kowalski'] [] False
```

Atrybuty klasy nadają się na stałe i wartości niemodyfikowalne — liczby, łańcuchy, krotki — oraz na dane celowo wspólne, jak licznik. Wszystko, co opisuje stan pojedynczego obiektu, powinno być atrybutem instancji tworzonym w `__init__`.

## Przestrzeń nazw klasy

W rozdziale [6. Funkcje](../06-funkcje/zasieg-nazw-i-domkniecia.md#przestrzenie-nazw-i-zasiegi) poznaliśmy przestrzenie nazw modułu i funkcji. Klasa ma własną: podczas wykonywania instrukcji `class` Python tworzy nową przestrzeń nazw, wykonuje w niej ciało klasy — przypisania i definicje funkcji trafiają właśnie tam — a na końcu buduje obiekt klasy, którego atrybutami są wszystkie zapisane w niej nazwy.

### Słownik `__dict__` klasy

Tak jak instancja, klasa ma atrybut `__dict__` z zawartością swojej przestrzeni nazw:

```python title="przestrzen-nazw.py"
class Czlowiek:
    """Osoba o imieniu, nazwisku i wieku."""

    gatunek = "Homo sapiens"

    def __init__(self, imie, nazwisko, wiek=20):
        self.imie = imie
        self.nazwisko = nazwisko
        self.wiek = wiek

    def przedstaw(self):
        return f"{self.imie} {self.nazwisko}"


print(list(Czlowiek.__dict__))
print(type(Czlowiek.__dict__).__name__)
print(Czlowiek.__dict__["gatunek"], "|", Czlowiek.__dict__["__doc__"])
print(Czlowiek.__static_attributes__)
```

```{ .text .no-copy }
['__module__', '__firstlineno__', '__doc__', 'gatunek', '__init__', 'przedstaw', '__static_attributes__', '__dict__', '__weakref__']
mappingproxy
Homo sapiens | Osoba o imieniu, nazwisku i wieku.
('imie', 'nazwisko', 'wiek')
```

Obok atrybutu `gatunek` i obu metod — w kolejności definicji — słownik zawiera wpisy dodane przez interpreter: `__module__` z nazwą modułu, `__doc__` z docstringiem, `__firstlineno__` z numerem wiersza, w którym zaczyna się definicja, oraz `__static_attributes__` — krotkę nazw atrybutów przypisywanych przez `self.` w metodach klasy (oba ostatnie od Pythona 3.13). Wpisy `__dict__` i `__weakref__` są techniczne: zapewniają instancjom słownik atrybutów i obsługę słabych referencji, o których mowa w podrozdziale o cyklu życia obiektu. Słownik klasy jest widokiem tylko do odczytu (typ `mappingproxy`); atrybuty klasy zmieniamy przypisaniem `Czlowiek.gatunek = ...`, nie przez `__dict__`. Metody są w tym słowniku zwykłymi funkcjami — to dostęp przez instancję, `c.przedstaw`, wiąże funkcję z obiektem i tworzy metodę, która przy wywołaniu przekaże `self`.

### Zasięg ciała klasy

Ciało klasy tworzy zasięg, ale szczególny: nazwy w nim przypisane nie są widoczne w ciałach metod jako zwykłe zmienne. Reguła LEGB z rozdziału 6 pomija zasięg klasy — z wnętrza metody Python szuka nazwy w zasięgu lokalnym metody, w funkcjach otaczających, w module i wśród nazw wbudowanych, ale nie w klasie:

```python title="zasieg-klasy.py"
class Licznik:
    start = 10

    def pokaz(self):
        return start


print(Licznik().pokaz())
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "zasieg-klasy.py", line 8, in <module>
    print(Licznik().pokaz())
          ~~~~~~~~~~~~~~~^^
  File "zasieg-klasy.py", line 5, in pokaz
    return start
           ^^^^^
NameError: name 'start' is not defined. Did you mean: 'self.start'?
```

Interpreter podpowiada rozwiązanie: do atrybutu klasy z wnętrza metody odwołujemy się przez instancję (`self.start`) albo przez klasę (`Licznik.start`) — dokładnie tak, jak w klasie `Bug` na początku podrozdziału. Ta sama reguła dotyczy metod: metodę wywołujemy przez `self.metoda()`, nigdy po samej nazwie. Nazwy z ciała klasy są za to widoczne w samym ciele — kolejne przypisania mogą korzystać z poprzednich, na przykład `koniec = start + 5` wprost pod `start = 10`.

### Introspekcja

**Introspekcja** (ang. *introspection*) to badanie i modyfikowanie obiektu w czasie działania programu, między innymi po nazwie atrybutu podanej jako łańcuch. Atrybuty można odczytywać, ustawiać, sprawdzać i usuwać także w ten sposób — funkcjami wbudowanymi `getattr()`, `setattr()`, `hasattr()` i `delattr()`. Przydaje się to, gdy nazwa atrybutu jest znana dopiero w czasie działania programu, na przykład pochodzi z pliku konfiguracyjnego albo z nagłówka pliku CSV z rozdziału 9:

```python title="introspekcja.py"
class Czlowiek:
    gatunek = "Homo sapiens"

    def __init__(self, imie, nazwisko):
        self.imie = imie
        self.nazwisko = nazwisko


c = Czlowiek("Jan", "Kowalski")
print(getattr(c, "imie"), getattr(c, "wiek", None))
setattr(c, "wiek", 34)
print(c.wiek, vars(c))
print(hasattr(c, "wiek"), hasattr(Czlowiek, "wiek"), hasattr(Czlowiek, "gatunek"))
delattr(c, "wiek")
print(hasattr(c, "wiek"))

for nazwa, wartosc in [("imie", "Anna"), ("nazwisko", "Nowak")]:
    setattr(c, nazwa, wartosc)
print(vars(c))
```

```{ .text .no-copy }
Jan None
34 {'imie': 'Jan', 'nazwisko': 'Kowalski', 'wiek': 34}
True False True
False
{'imie': 'Anna', 'nazwisko': 'Nowak'}
```

Wywołanie `getattr(c, "wiek", None)` zwraca trzeci argument zamiast zgłaszać `AttributeError`, gdy atrybutu nie ma; bez tego argumentu zachowuje się jak zapis `c.wiek`. Funkcja `vars(obiekt)` zwraca ten sam słownik co `obiekt.__dict__`. Wynik `hasattr(Czlowiek, "wiek")` to `False`, bo `wiek` należy do instancji, nie do klasy — `hasattr(Czlowiek, "gatunek")` daje `True`. W pętli `setattr()` przypisuje atrybuty według listy par nazwa–wartość, czego składnią `obiekt.nazwa = ...` zapisać się nie da. Introspekcja nie zastępuje zwykłej składni w codziennym kodzie; jest narzędziem dla bibliotek i kodu ogólnego, który pracuje z obiektami nieznanych klas.

Do obiektu można nawet dodać metodę po jego utworzeniu, wiążąc funkcję z obiektem za pomocą `types.MethodType`; podobnie jak dodawanie atrybutów spoza `__init__`, jest to możliwość języka, a nie praktyka:

```python title="dodana-metoda.py"
import types


class Czlowiek:
    def __init__(self, imie):
        self.imie = imie


def przywitaj(self):
    return f"Dzień dobry, jestem {self.imie}."


c = Czlowiek("Jan")
c.przywitaj = types.MethodType(przywitaj, c)
print(c.przywitaj(), type(c.przywitaj).__name__)
```

```{ .text .no-copy }
Dzień dobry, jestem Jan. method
```

## Atrybut `__slots__`

Słownik `__dict__` daje instancjom swobodę — dowolny atrybut w dowolnej chwili — kosztem pamięci na przechowywanie dowolnych atrybutów i słownika `__dict__` w każdym obiekcie oraz kosztem literówek, które zamiast błędu tworzą nowy atrybut. Klasa może zrezygnować ze słownika, wymieniając dozwolone atrybuty instancji w atrybucie klasy `__slots__`:

```python title="slots.py"
class Punkt:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y


p = Punkt(1, 2)
p.x = 10
print(p.x, p.y, hasattr(p, "__dict__"))
try:
    p.z = 3
except AttributeError as e:
    print("AttributeError:", e)
```

```{ .text .no-copy }
10 2 False
AttributeError: 'Punkt' object has no attribute 'z' and no __dict__ for setting new attributes
```

Instancje klasy z `__slots__` nie mają słownika `__dict__`, a przypisanie nazwy spoza krotki kończy się `AttributeError` — literówka w nazwie atrybutu zostaje wykryta natychmiast. Miejsce na wymienione atrybuty jest zarezerwowane w samym obiekcie, więc obiekty są mniejsze, a dostęp do atrybutów nieco szybszy; różnica ma znaczenie przy milionach instancji, na przykład punktach albo rekordach danych, i wtedy warto ją zmierzyć — pomiar pokazujemy w podrozdziale [Optymalizacja kodu](../13-wydajnosc/optymalizacja-kodu.md#pamiec-__slots__-z-pomiarem) rozdziału 13. W zwykłych klasach `__slots__` nie jest potrzebne. Jego współdziałanie z dziedziczeniem omawiamy w podrozdziale o cyklu życia obiektu.

## Metody klasy — `@classmethod`

Metoda instancji otrzymuje obiekt jako pierwszy argument. **Metoda klasy** (ang. *class method*) otrzymuje zamiast niego klasę — parametr nazywany konwencjonalnie `cls` — i można ją wywołać zarówno przez klasę, jak i przez instancję. Definiuje ją dekorator `@classmethod` (składnia `@` z rozdziału [6. Funkcje](../06-funkcje/dekoratory.md#skadnia)). Najczęstsze zastosowanie to **konstruktor alternatywny** (ang. *alternative constructor*): metoda klasy, która buduje obiekt z danych w innej postaci niż parametry `__init__`:

```python title="student.py"
class Student:
    def __init__(self, imie, nazwisko):
        self.imie = imie
        self.nazwisko = nazwisko

    @classmethod
    def z_napisu(cls, napis):
        """Zwraca studenta z napisu „Imię Nazwisko”."""
        imie, nazwisko = napis.split()
        return cls(imie, nazwisko)

    @classmethod
    def ze_slownika(cls, dane):
        """Zwraca studenta ze słownika z kluczami imie i nazwisko."""
        return cls(dane["imie"], dane["nazwisko"])


s1 = Student("Jan", "Kowalski")
s2 = Student.z_napisu("Anna Nowak")
s3 = Student.ze_slownika({"imie": "Piotr", "nazwisko": "Zieliński"})
print(s1.nazwisko, s2.nazwisko, s3.nazwisko)
s4 = s1.z_napisu("Ewa Lis")
print(type(s4).__name__, s4.imie)
```

```{ .text .no-copy }
Kowalski Nowak Zieliński
Student Ewa
```

Wewnątrz metody klasy nie ma `self` — nie ma jeszcze żadnego obiektu — jest za to `cls`, czyli klasa, przez którą metodę wywołano. Nowy obiekt tworzymy wywołaniem `cls(...)`, a nie `Student(...)`: dzięki temu metoda odziedziczona przez klasę pochodną utworzy obiekt tej klasy pochodnej, co pokażemy w podrozdziale o dziedziczeniu. Wywołanie przez instancję, `s1.z_napisu(...)`, jest dozwolone — Python przekazuje jako `cls` klasę obiektu `s1` — ale w praktyce metody klasy wywołujemy przez klasę, bo tak czyta się ich intencję. Wzorzec ten stosuje biblioteka standardowa: `dict.fromkeys()`, `int.from_bytes()` z rozdziału 9 czy `datetime.date.today()` to konstruktory alternatywne zapisane jako metody klasy.

## Metody statyczne — `@staticmethod`

**Metoda statyczna** (ang. *static method*) nie otrzymuje ani obiektu, ani klasy — jest zwykłą funkcją umieszczoną w przestrzeni nazw klasy, bo logicznie do niej należy. Definiuje ją dekorator `@staticmethod`:

```python title="student-static.py"
class Student:
    def __init__(self, imie, nazwisko):
        self.imie = imie
        self.nazwisko = nazwisko

    @staticmethod
    def czy_pelne(napis):
        """Sprawdza, czy napis zawiera imię i nazwisko."""
        return len(napis.split()) > 1

    @classmethod
    def z_napisu(cls, napis):
        """Zwraca studenta z napisu „Imię Nazwisko”."""
        if not cls.czy_pelne(napis):
            raise ValueError(f"oczekiwano imienia i nazwiska, otrzymano {napis!r}")
        imie, nazwisko = napis.split()
        return cls(imie, nazwisko)


print(Student.czy_pelne("Jan Kowalski"), Student.czy_pelne("Kowalski"))
s = Student.z_napisu("Jan Kowalski")
print(s.czy_pelne("Anna Nowak"))
try:
    Student.z_napisu("Kowalski")
except ValueError as e:
    print("ValueError:", e)
```

```{ .text .no-copy }
True False
True
ValueError: oczekiwano imienia i nazwiska, otrzymano 'Kowalski'
```

Metodę statyczną wywołujemy przez klasę (`Student.czy_pelne(...)`) albo przez instancję (`s.czy_pelne(...)`) — w obu przypadkach Python nie dokłada żadnego pierwszego argumentu. Wywołanie przez instancję jest poprawne, choć zwykle mniej czytelne niż przez klasę. Metoda statyczna nie otrzymuje ani obiektu, ani klasy, więc nie ma dostępu do stanu instancji, a do atrybutów klasy — tylko przez jej nazwę zapisaną na stałe; jeśli potrzebuje obiektu albo klasy przekazanej przez Pythona, powinna być metodą instancji albo klasy. Alternatywą dla metody statycznej jest zwykła funkcja w module obok klasy — w Pythonie to równie dobre rozwiązanie, a `@staticmethod` wybieramy, gdy funkcja ma sens wyłącznie w kontekście klasy i chcemy ją znaleźć pod jej nazwą.

## Porównanie trzech rodzajów metod

| Rodzaj | Dekorator | Pierwszy parametr | Dostęp | Typowe zastosowanie |
|---|---|---|---|---|
| metoda instancji | brak | `self` (obiekt) | atrybuty obiektu i klasy | operacje na stanie obiektu |
| metoda klasy | `@classmethod` | `cls` (klasa) | atrybuty klasy | konstruktory alternatywne, operacje na klasie |
| metoda statyczna | `@staticmethod` | brak | brak | funkcja pomocnicza związana z klasą |

Wszystkie trzy w jednej klasie:

```python title="kolo.py"
import math


class Kolo:
    """Koło o zadanym promieniu."""

    def __init__(self, promien):
        self.promien = promien

    def pole(self):
        """Zwraca pole koła."""
        return math.pi * self.promien**2

    @classmethod
    def ze_srednicy(cls, srednica):
        """Zwraca koło o podanej średnicy."""
        return cls(srednica / 2)

    @staticmethod
    def czy_poprawny_promien(wartosc):
        """Sprawdza, czy wartość może być promieniem."""
        return isinstance(wartosc, (int, float)) and wartosc > 0


k = Kolo.ze_srednicy(10)
print(k.promien, round(k.pole(), 2))
print(Kolo.czy_poprawny_promien(5), Kolo.czy_poprawny_promien(-1))
```

```{ .text .no-copy }
5.0 78.54
True False
```

Metoda `pole()` potrzebuje promienia konkretnego koła, więc jest metodą instancji; `ze_srednicy()` tworzy nowe koło, więc jest metodą klasy; `czy_poprawny_promien()` nie potrzebuje ani koła, ani klasy, więc jest metodą statyczną. Pytanie „czego metoda potrzebuje: obiektu, klasy czy niczego?” rozstrzyga wybór w każdym przypadku.
