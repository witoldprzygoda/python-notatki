# Metaprogramowanie

Ten podrozdział ma charakter uzupełniający. **Metaprogramowanie** (ang. *metaprogramming*) to pisanie kodu, który tworzy lub zmienia inny kod w czasie działania programu. Dekoratory z rozdziału 6 były jego pierwszą postacią; tu schodzimy poziom niżej — do klas jako obiektów, funkcji `type()` tworzącej klasy, dekoratorów klas, metody `__init_subclass__` i **metaklas** (ang. *metaclass*), czyli klas, których instancjami są klasy. Kończymy przestrogą przed `eval()` i `exec()`. Wiedza ta tłumaczy, jak działają `@dataclass`, `abc.ABC` czy `Enum`; we własnym kodzie potrzebna jest rzadko.

## Klasa jako obiekt typu `type`

W rozdziale 10 ustaliliśmy, że klasa jest obiektem, a jej typem jest `type`. Dotyczy to wszystkich klas — także wbudowanych — a sam `type` jest własną instancją:

```python title="klasa-jako-obiekt-type.py"
class Zewnetrzna:
    class Wewnetrzna:
        pass

    def metoda(self):
        pass


print(type(Zewnetrzna), type(int), type(type))
print(Zewnetrzna.__name__, Zewnetrzna.Wewnetrzna.__name__, Zewnetrzna.Wewnetrzna.__qualname__)
print(Zewnetrzna.metoda.__qualname__, Zewnetrzna.__module__, Zewnetrzna.__bases__)
print("__name__" in vars(Zewnetrzna), "__module__" in vars(Zewnetrzna))
```

```{ .text .no-copy }
<class 'type'> <class 'type'> <class 'type'>
Zewnetrzna Wewnetrzna Zewnetrzna.Wewnetrzna
Zewnetrzna.metoda __main__ (<class 'object'>,)
False True
```

Obok `__name__` klasa ma nazwę kwalifikowaną `__qualname__` z rozdziału 6, uwzględniającą klasy zewnętrzne — przydatną w śladach wywołań i dziennikach, gdy kilka klas ma tę samą krótką nazwę — oraz `__module__` i `__bases__`. Atrybut `__name__` nie jest wpisem w słowniku klasy z rozdziału 10; przechowuje go sam obiekt typu `type`, podobnie jak `__bases__` i `__mro__`. Atrybut `__module__` jest natomiast zwykłym wpisem słownika klasy, jak w wydruku `__dict__` w rozdziale 10.

## Funkcja `type()` z trzema argumentami

Skoro klasa jest instancją `type`, można ją utworzyć wywołaniem `type(nazwa, bazy, słownik)`: nazwa staje się `__name__`, krotka baz — `__bases__` (pusta krotka daje `(object,)`), a słownik — zawartością przestrzeni nazw klasy. Instrukcja `class` jest wygodnym zapisem tego wywołania — dla klasy bez własnej metaklasy, o czym niżej:

```python title="type-trzy-argumenty.py"
def przedstaw(self):
    return f"Jestem {self.imie}."


Czlowiek = type("Czlowiek", (), {"gatunek": "Homo sapiens", "przedstaw": przedstaw})
Student = type("Student", (Czlowiek,), {"__init__": lambda self, imie: setattr(self, "imie", imie)})

s = Student("Jan")
print(s.przedstaw(), s.gatunek, type(s).__name__)
print(Student.__bases__, Student.__mro__ == (Student, Czlowiek, object))
print(isinstance(Czlowiek, type), Czlowiek.__dict__["przedstaw"] is przedstaw)
```

```{ .text .no-copy }
Jestem Jan. Homo sapiens Student
(<class '__main__.Czlowiek'>,) True
True True
```

Funkcja `przedstaw()` zdefiniowana poza klasą stała się metodą, bo trafiła do słownika klasy — dokładnie tak jak funkcje z ciała `class` w rozdziale 11 przy metodach związanych. Tworzenie klas przez `type()` przydaje się, gdy zestaw pól lub metod jest znany dopiero w czasie działania — tak działa wewnątrz `namedtuple()` z rozdziału 7. Funkcje umieszczone w słowniku spoza ciała `class` nie mają jednak komórki `__class__`, którą kompilator tworzy dla metod zapisanych w ciele klasy, więc bezargumentowe `super()` w nich nie działa — to jedna z różnic między instrukcją `class` a gołym wywołaniem `type()`.

## Łańcuch tworzenia obiektu — `type.__call__`, `__new__` i `__init__`

W rozdziale 10 wywołanie klasy opisaliśmy jako `__new__` i `__init__`. Kto je wywołuje? Wywołanie `Foo(42)` to wywołanie obiektu `Foo`, a więc — zgodnie z rozdziałem 11 — metoda `__call__` jego typu, czyli `type.__call__`. To ona wywołuje `__new__`, sprawdza, czy wynik jest instancją klasy, i dopiero wtedy wywołuje `__init__`. Metaklasa z własnym `__call__` pozwala zobaczyć ten łańcuch:

```python title="verbose.py"
class Verbose(type):
    """Metaklasa wypisująca kroki tworzenia obiektu."""

    def __call__(cls, *args, **kwargs):
        print(f"1. {type(cls).__name__}.__call__ dla klasy {cls.__name__}")
        obiekt = cls.__new__(cls, *args, **kwargs)
        print(f"2. __new__ zwróciło obiekt klasy {type(obiekt).__name__}")
        if isinstance(obiekt, cls):
            obiekt.__init__(*args, **kwargs)
            print("3. __init__ wykonane")
        return obiekt


class Foo(metaclass=Verbose):
    def __new__(cls, x):
        print(f"   Foo.__new__(x={x})")
        return super().__new__(cls)

    def __init__(self, x):
        print(f"   Foo.__init__(x={x})")
        self.x = x


f = Foo(42)
print(f.x, type(Foo).__name__)
```

```{ .text .no-copy }
1. Verbose.__call__ dla klasy Foo
   Foo.__new__(x=42)
2. __new__ zwróciło obiekt klasy Foo
   Foo.__init__(x=42)
3. __init__ wykonane
42 Verbose
```

Zapis `metaclass=Verbose` w nagłówku sprawia, że `Foo` jest instancją `Verbose`, a nie `type`; a ponieważ `Verbose` dziedziczy po `type`, `Foo` zachowuje się jak zwykła klasa, z jednym dodatkiem. Kod `__call__` odtwarza to, co `type.__call__` robi domyślnie — łącznie z regułą z rozdziału 10, że `__init__` jest pomijane, gdy `__new__` nie zwróci instancji klasy.

## Dekoratory klas

Dekorator klasy to funkcja przyjmująca klasę i zwracająca klasę — tę samą, po modyfikacji, albo inną — lub, jak `singleton()` z poprzedniego podrozdziału, inny obiekt zastępujący klasę. Klasa jest już w pełni utworzona, gdy dekorator ją otrzymuje, więc może dopisać metody, sprawdzić poprawność definicji albo zarejestrować klasę gdzie indziej:

```python title="dekorator-klasy.py"
def dodaj_repr(klasa):
    """Dopisuje klasie __repr__ zbudowane z atrybutów instancji."""

    def __repr__(self):
        atrybuty = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{type(self).__name__}({atrybuty})"

    klasa.__repr__ = __repr__
    return klasa


def wymagaj(*nazwy):
    """Dekorator z argumentami: sprawdza, czy klasa definiuje podane metody."""

    def dekorator(klasa):
        brakuje = [nazwa for nazwa in nazwy if not callable(getattr(klasa, nazwa, None))]
        if brakuje:
            raise TypeError(f"klasa {klasa.__name__} nie definiuje metod: {', '.join(brakuje)}")
        return klasa

    return dekorator


@dodaj_repr
@wymagaj("pole")
class Kwadrat:
    def __init__(self, bok):
        self.bok = bok

    def pole(self):
        return self.bok**2


print(Kwadrat(3), Kwadrat(3).pole())
try:
    @wymagaj("pole", "obwod")
    class Trojkat:
        pass
except TypeError as e:
    print("TypeError:", e)
```

```{ .text .no-copy }
Kwadrat(bok=3) 9
TypeError: klasa Trojkat nie definiuje metod: pole, obwod
```

Dekoratory składają się jak w rozdziale 6 — `@wymagaj("pole")` działa pierwszy, potem `@dodaj_repr`. Dekoratorami klas są `@dataclass` z podrozdziału o klasach danych i `@total_ordering` z rozdziału 11: obie funkcje przyjmują gotową klasę i dopisują jej metody, dokładnie jak `dodaj_repr()`. Dekorator sprawdzający interfejs, jak `wymagaj()`, jest lżejszą alternatywą dla klasy abstrakcyjnej, gdy nie chcemy narzucać dziedziczenia; a dekorator `singleton()` z poprzedniego podrozdziału pokazał wariant zwracający zamiast klasy inny obiekt.

## Metoda `__init_subclass__`

Fabryka z rejestrem z poprzedniego podrozdziału wymagała ręcznego wywołania `zarejestruj()` dla każdej klasy. Metoda specjalna `__init_subclass__` (od Pythona 3.6) klasy bazowej jest wywoływana automatycznie za każdym razem, gdy powstaje klasa pochodna — otrzymuje ją jako `cls`, a także argumenty nazwane podane w nagłówku `class`:

```python title="init-subclass.py"
class Wtyczka:
    """Klasa bazowa rejestrująca każdą klasę pochodną pod nazwą."""

    rejestr = {}

    def __init_subclass__(cls, nazwa=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.nazwa = nazwa or cls.__name__.lower()
        Wtyczka.rejestr[cls.nazwa] = cls
        print("zarejestrowano:", cls.nazwa)

    @classmethod
    def utworz(cls, nazwa, *args, **kwargs):
        return cls.rejestr[nazwa](*args, **kwargs)


class EksportPdf(Wtyczka):
    pass


class EksportCsv(Wtyczka, nazwa="csv"):
    pass


class EksportExcel(EksportCsv, nazwa="excel"):
    pass


print(sorted(Wtyczka.rejestr))
print(type(Wtyczka.utworz("excel")).__name__, EksportExcel.nazwa, EksportCsv.nazwa)
```

```{ .text .no-copy }
zarejestrowano: eksportpdf
zarejestrowano: csv
zarejestrowano: excel
['csv', 'eksportpdf', 'excel']
EksportExcel excel csv
```

Metoda jest niejawnie metodą klasy — nie wymaga dekoratora `@classmethod` — i działa także dla klas pochodnych klas pochodnych (`EksportExcel`). Wywołanie `super().__init_subclass__(**kwargs)` przekazuje nierozpoznane argumenty dalej, aby współpracować z innymi klasami bazowymi, a domyślna wersja tej metody w `object` zgłasza `TypeError` dla każdego nieoczekiwanego argumentu. Dla rejestrów, walidacji klas pochodnych i wymuszania konwencji `__init_subclass__` wystarcza tam, gdzie kiedyś sięgano po metaklasę.

## Własna metaklasa

Metaklasa to klasa pochodna od `type`. Jej `__new__` otrzymuje nazwę, bazy i przestrzeń nazw tworzonej klasy — dokładnie argumenty `type()` — i może je zmienić przed utworzeniem klasy; jej `__init__` dostaje już gotową klasę. Pierwszy parametr nazywamy konwencjonalnie `mcs` w `__new__` (metaklasa, bo klasy jeszcze nie ma) i `cls` w pozostałych metodach:

```python title="metaklasa.py"
class Meta(type):
    """Metaklasa dodająca klasom licznik instancji i czytelną reprezentację."""

    def __new__(mcs, nazwa, bazy, przestrzen):
        przestrzen["utworzono"] = 0
        klasa = super().__new__(mcs, nazwa, bazy, przestrzen)
        print("Meta.__new__:", nazwa, "z bazami", [b.__name__ for b in bazy])
        return klasa

    def __init__(cls, nazwa, bazy, przestrzen):
        super().__init__(nazwa, bazy, przestrzen)
        print("Meta.__init__:", cls)

    def __call__(cls, *args, **kwargs):
        cls.utworzono += 1
        return super().__call__(*args, **kwargs)

    def __repr__(cls):
        return cls.__name__


class Figura(metaclass=Meta):
    pass


class Kolo(Figura):
    pass


Kolo()
Kolo()
Figura()
print(Kolo.utworzono, Figura.utworzono)
print(Kolo.__mro__, type(Kolo) is Meta)
```

```{ .text .no-copy }
Meta.__new__: Figura z bazami []
Meta.__init__: Figura
Meta.__new__: Kolo z bazami ['Figura']
Meta.__init__: Kolo
2 1
(Kolo, Figura, <class 'object'>) True
```

Klasa `Kolo` nie deklaruje metaklasy, a mimo to jest instancją `Meta` — metaklasę dziedziczy się po klasie bazowej. Metaklasa dopisała każdej klasie atrybut `utworzono` i zlicza wywołania w `__call__`; osobny licznik dla każdej klasy jest efektem `przestrzen["utworzono"] = 0` wykonywanego przy tworzeniu każdej z nich. Metoda `__repr__` metaklasy zmienia reprezentację **klas**, dlatego `__mro__` wypisuje same nazwy — to zabieg, który można było zastosować w podrozdziale o MRO zamiast listy nazw; wydruk `Meta.__init__: Figura` również korzysta z tego `__repr__`. Tak działa `abc.ABC`: metaklasa `ABCMeta` w `__new__` zbiera nazwy metod abstrakcyjnych do zbioru `__abstractmethods__`, a `object.__new__` odmawia utworzenia obiektu, dopóki zbiór nie jest pusty; `Enum` z kolei ma metaklasę, która zamienia atrybuty klasy w elementy wyliczenia.

Metaklasy są narzędziem ostatecznym. Zanim je napiszemy, warto sprawdzić, czy nie wystarczy prostszy mechanizm:

| Potrzeba | Zamiast metaklasy |
|---|---|
| dopisanie lub zmiana metod gotowej klasy | dekorator klasy |
| reakcja na powstanie klasy pochodnej, rejestr, walidacja | `__init_subclass__` |
| generowanie `__init__`, `__repr__`, `__eq__` | `@dataclass` |
| wymuszenie interfejsu | `abc.ABC` |
| kontrola dostępu do atrybutów | `@property`, deskryptor |
| zmiana samego procesu tworzenia klasy (przestrzeń nazw, bazy, wszystkie klasy w hierarchii) | metaklasa |

Dodatkowo metaklasa klasy pochodnej musi być podklasą metaklas wszystkich jej klas bazowych — inaczej definicja kończy się `TypeError: metaclass conflict` — co utrudnia łączenie hierarchii z różnymi metaklasami; to kolejny powód, aby sięgać po metaklasę jedynie wtedy, gdy pozostałe mechanizmy nie wystarczają. Metaklasa pozwala też nadpisać `__getattribute__` dla samych klas (dostęp `Klasa.atrybut`), podobnie jak `__getattribute__` zwykłej klasy z rozdziału 11 kontroluje dostęp przez instancję — to najrzadziej potrzebny i najbardziej ryzykowny z tych mechanizmów.

## Funkcje `eval()` i `exec()` — przestroga

Najbardziej dosłowną postacią metaprogramowania jest wykonanie kodu z łańcucha: `eval()` oblicza wyrażenie, `exec()` wykonuje instrukcje. Obie funkcje wykonują **wszystko**, co otrzymają, z pełnymi uprawnieniami programu — łańcuch pochodzący od użytkownika, z pliku czy z sieci może usunąć pliki albo wykraść dane. Do wczytywania danych zapisanych składnią Pythona służy `ast.literal_eval()`, które rozumie wyłącznie literały: liczby, łańcuchy i bajty, krotki, listy, słowniki, zbiory, `True`, `False` i `None`:

```python title="literal-eval.py"
import ast

tekst = "{'nazwa': 'Jan', 'oceny': [4.5, 5.0], 'aktywny': True}"
dane = ast.literal_eval(tekst)
print(type(dane).__name__, dane["oceny"])
print(eval("2 + 3 * 4"))
try:
    ast.literal_eval("__import__('os').listdir('.')")
except ValueError as e:
    print("ValueError:", str(e).partition(": ")[0])
```

```{ .text .no-copy }
dict [4.5, 5.0]
14
ValueError: malformed node or string on line 1
```

Wyrażenie z wywołaniem funkcji, które `eval()` wykonałoby bez żadnej kontroli, `ast.literal_eval()` odrzuca — w przykładzie obcinamy wydruk węzła składniowego, którym kończy się komunikat. W praktyce dane wymieniamy w formacie JSON z rozdziału 9, a `eval()` i `exec()` rezerwujemy dla kodu, który sami napisaliśmy — na przykład w narzędziach programistycznych; nigdy nie przekazujemy im tekstu z zewnątrz.
