# 10. Klasy i obiekty

Od rozdziału [3. Nazwy i typy](../03-nazwy-typy/obiekty-i-pamiec.md) powtarzamy, że w Pythonie wszystko jest obiektem: liczby, łańcuchy, listy, funkcje, moduły. Każdy z nich ma typ, atrybuty i metody. Do tej pory korzystaliśmy z typów gotowych; ten rozdział uczy definiować własne — instrukcją `class`, która opisuje, jakie dane przechowuje obiekt i co można z nim zrobić. Klasa jest przepisem, a obiekt utworzony według niego — instancją. Wszystko, co już umiemy, pozostaje w mocy: metody definiujemy instrukcją `def` z rozdziału 6, składnia `@` dekoruje metody klasy i właściwości, walidację zapewniają wyjątki z rozdziału 8, a f-stringi z rozdziałów 3 i 9 oraz `repr()` z rozdziału 7 nadają obiektom czytelną reprezentację.

Materiał obiektowy zajmuje trzy rozdziały. Ten wprowadza rdzeń: definicję klasy, atrybuty instancji i klasy, trzy rodzaje metod, właściwości i konwencje hermetyzacji, dziedziczenie pojedyncze z funkcją `super()` oraz własne klasy wyjątków — pierwsze praktyczne zastosowanie dziedziczenia, zapowiedziane w rozdziale 8. Metody specjalne, dzięki którym obiekty własnych klas współpracują z operatorami, funkcją `len()`, pętlą `for` i instrukcją `with`, omawia rozdział [11. Model danych — metody specjalne i protokoły](../11-model-danych/index.md); dziedziczenie wielokrotne, klasy abstrakcyjne, klasy danych i wzorce projektowe (ang. *design patterns*) — rozdział o zaawansowanych mechanizmach obiektowych. <!-- TODO: link po powstaniu rozdziału o zaawansowanych mechanizmach obiektowych --> Ostatni podrozdział, o cyklu życia obiektu, ma charakter uzupełniający: tłumaczy, co dzieje się między wywołaniem klasy a zwolnieniem pamięci, i można go pominąć przy pierwszej lekturze.

---

## W tym rozdziale

1. [Definicja klasy](definicja-klasy.md) — instrukcja `class`, tworzenie obiektu i `__init__`, parametr `self`, atrybuty i metody instancji, klasa jako obiekt
2. [Atrybuty klasy, metody klasowe i statyczne](atrybuty-i-metody.md) — atrybut klasy a instancji, pułapka modyfikowalnego atrybutu klasy, przestrzeń nazw i zasięg klasy, introspekcja, `__slots__`, `@classmethod`, `@staticmethod`
3. [Reprezentacja, właściwości i hermetyzacja](reprezentacja-i-wlasciwosci.md) — `__repr__` i `__str__`, `@property` z walidacją, pułapka rekurencji, konwencje `_nazwa` i `__nazwa`, klasa `property`
4. [Dziedziczenie](dziedziczenie.md) — klasa bazowa i pochodna, nadpisywanie i polimorfizm, `super()`, `isinstance()` i `issubclass()`, własne klasy wyjątków, kompozycja, zasady projektowania klas
5. [Cykl życia obiektu](cykl-zycia-obiektu.md) — podrozdział uzupełniający: `__new__` i `__init__`, Singleton, licznik referencji, `__del__`, słabe referencje, cykle i `gc`, `__slots__` a dziedziczenie
