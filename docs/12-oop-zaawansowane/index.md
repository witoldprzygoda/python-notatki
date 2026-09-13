# 12. Programowanie obiektowe — mechanizmy zaawansowane

Rozdział 10 nauczył nas definiować klasy i budować hierarchie z dziedziczeniem pojedynczym, a rozdział 11 — włączać własne klasy w mechanizmy języka przez metody specjalne. Ten rozdział zamyka blok obiektowy mechanizmami, które pojawiają się, gdy hierarchie rosną, a klas przybywa: dziedziczeniem po kilku klasach naraz z jego regułami kolejności, mixinami i klasami abstrakcyjnymi jako narzędziami kształtowania hierarchii, klasami danych i wyliczeniami jako codziennym sposobem zapisu rekordów i stałych oraz — dla dociekliwych — wzorcami projektowymi i metaprogramowaniem, czyli kodem tworzącym klasy.

Kolejność podrozdziałów odpowiada malejącej potrzebie znajomości mechanizmu: dziedziczenie wielokrotne i MRO trzeba rozumieć, bo tłumaczą zachowanie `super()` i błędy w hierarchiach; klasy abstrakcyjne i mixiny porządkują projekt; `@dataclass`, `NamedTuple` i `Enum` zastępują ręcznie pisane klasy w większości programów i dopełniają instrukcję `match` z rozdziału 4. Wzorce projektowe i metaprogramowanie pokazują, jak z tych samych elementów — klas jako obiektów, funkcji pierwszej klasy, dekoratorów — powstają biblioteki, których używamy; można je pominąć przy pierwszej lekturze. Rozdział domyka zapowiedzi z rozdziałów 7 (klasy danych po `namedtuple`), 9 (zapis własnych typów do JSON), 10 (MRO, kompozycja i wzorce, Singleton przez dekorator) i 11 (klasy abstrakcyjne, `__getattribute__` przy metaklasach). Adnotacje typów, które klasy danych i protokoły zapisują w kodzie, stają się w pełni użyteczne dopiero z narzędziami analizy statycznej — omawianymi w rozdziale o narzędziach analizy typów. <!-- TODO: link po powstaniu rozdziału o narzędziach analizy typów -->

---

## W tym rozdziale

1. [Dziedziczenie wielokrotne i MRO](dziedziczenie-wielokrotne.md) — wiele klas bazowych, problem diamentu, algorytm C3 krok po kroku, `super()` a MRO, kooperatywne `__init__`, niespójne MRO, śledzenie `__new__` i `__init__` w hierarchii
2. [Mixiny, kompozycja i klasy abstrakcyjne](mixiny-i-abstrakcja.md) — mixiny, tabela dziedziczenie / mixin / kompozycja, `abc.ABC` i `@abstractmethod`, fabryka pojazdów, `typing.Protocol`, zasady projektowania
3. [Klasy danych — dataclass, NamedTuple i Enum](klasy-danych.md) — `@dataclass`, `field()` i `__post_init__`, opcje `frozen`/`order`/`slots`/`kw_only`, dziedziczenie, `asdict()` i JSON, `NamedTuple`, wyliczenia, `match`/`case` z klasami danych
4. [Wzorce projektowe](wzorce-projektowe.md) — podrozdział uzupełniający: wzorce a idiomy, Fabryka z rejestrem, Strategia, Obserwator, Singleton przez dekorator klasy
5. [Metaprogramowanie](metaprogramowanie.md) — podrozdział uzupełniający: klasa jako obiekt typu `type`, `type()` z trzema argumentami, łańcuch `type.__call__` → `__new__` → `__init__`, dekoratory klas, `__init_subclass__`, metaklasy, przestroga przed `eval()` i `exec()`
