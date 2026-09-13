# 11. Model danych — metody specjalne i protokoły

W rozdziale 10 obiekty własnych klas zyskały stan, metody, właściwości i czytelną reprezentację dzięki trzem metodom specjalnym: `__init__`, `__repr__` i `__str__`. Są one częścią większej całości — **modelu danych** (ang. *data model*) Pythona, czyli zbioru metod specjalnych, przez które język realizuje operatory, funkcje wbudowane i instrukcje. Dodawanie liczb to wywołanie `__add__`, długość listy — `__len__`, pętla `for` — `__iter__` i `__next__`, instrukcja `with` — `__enter__` i `__exit__`. Typy wbudowane nie mają tu żadnych przywilejów: `(3).__add__(4)` daje `7`, a własna klasa, która zdefiniuje te same metody, staje się pełnoprawnym uczestnikiem języka — można ją dodawać, porównywać, indeksować, przeglądać pętlą i otwierać instrukcją `with`. Umowę co do nazw i zachowania metod oczekiwanych w danej sytuacji nazywamy protokołem; rozdział 8 wprowadził pierwszy z nich, protokół menedżera kontekstu.

Rozdział domyka kilka wątków rozpoczętych wcześniej: iteratory i `StopIteration` z rozdziału 4 oraz dwuargumentową funkcję `iter()` z rozdziału 6 poznajemy od strony klasy, menedżer kontekstu z rozdziału 8 piszemy jako klasę, obiekt z metodą `write()` zapowiedziany w rozdziale 9 powstaje przy obiektach plikopodobnych, a `__eq__` z `__hash__`, `__format__`, `__call__` i deskryptory zapowiedziane w rozdziale 10 otrzymują pełne omówienie. Ostatni podrozdział, o deskryptorach, ma charakter uzupełniający — wyjaśnia mechanizm stojący za właściwościami i metodami, a można go pominąć przy pierwszej lekturze. Dziedziczenie wielokrotne, klasy abstrakcyjne i klasy danych, które korzystają z metod specjalnych na większą skalę, omawia rozdział o zaawansowanych mechanizmach obiektowych. <!-- TODO: link po powstaniu rozdziału o zaawansowanych mechanizmach obiektowych -->

---

## W tym rozdziale

1. [Przeciążanie operatorów](operatory.md) — operator jako metoda specjalna, arytmetyka, `NotImplemented` i operacje odbite, operacje złożone, porównania i `total_ordering`, `__hash__`, operator `@` i `singledispatchmethod`
2. [Protokoły kolekcji i wywołania](kolekcje-i-wywolania.md) — protokół jako umowa, `__len__` i `__bool__`, indeksowanie z wycinkami i indeksem krotkowym, `__contains__`, `__call__`, `collections.abc`
3. [Protokół iteracji](iteracja.md) — obiekt iterowalny a iterator, pętla `for` od środka, iterator jako klasa, oddzielenie kolekcji od iteratora, `__iter__` jako funkcja generatorowa, protokół sekwencji, typowe błędy
4. [Menedżery kontekstu i obiekty plikopodobne](menedzery-kontekstu.md) — `__enter__` i `__exit__`, tłumienie wyjątków, klasa a `@contextmanager`, obiekt z metodą `write()`, `__format__`
5. [Deskryptory](deskryptory.md) — podrozdział uzupełniający: protokół deskryptorów, walidator wielokrotnego użytku, deskryptory danych i niedanych, kolejność wyszukiwania atrybutu, `property` i metody związane jako deskryptory
