# Wzorce projektowe

Ten podrozdział ma charakter uzupełniający. **Wzorce projektowe** (ang. *design patterns*) — nazwane, sprawdzone rozwiązania powtarzających się problemów projektowych — powstały w językach, w których większość rozwiązań wymaga klas. W Pythonie część z nich sprowadza się do idiomów języka: funkcje są obiektami, klasy można przechowywać w słowniku, a moduł jest importowany raz. Pokazujemy cztery wzorce, które w kodzie w Pythonie spotyka się najczęściej — Fabrykę, Strategię, Obserwatora i Singleton — każdy w postaci klasowej i, gdzie to naturalne, w postaci uproszczonej przez mechanizmy z wcześniejszych rozdziałów.

## Wzorce a idiomy Pythona

Wzorzec opisuje problem i strukturę rozwiązania, nie konkretny kod. „Fabryka” to miejsce, które tworzy obiekty właściwej klasy na podstawie danych wejściowych; „Strategia” — wymienny algorytm; „Obserwator” — powiadamianie zainteresowanych o zdarzeniu; „Singleton” — klasa o jednej instancji. W Pythonie strukturę tę realizują nie tylko klasy: strategią może być zwykła funkcja przekazana jako argument (rozdział 6), obserwatorem — funkcja w liście, a fabryką — słownik nazw i klas. Wzorce warto znać, bo nazywają rozwiązania i ułatwiają rozmowę o projekcie; nie warto ich stosować tam, gdzie wystarczy funkcja.

## Fabryka z rejestrem

**Fabryka** (ang. *factory*) pojazdów z podrozdziału o mixinach i klasach abstrakcyjnych miała słownik typów zapisany na stałe w metodzie klasy. Wersja z **rejestrem** (ang. *registry*) pozwala dopisywać nowe typy bez zmiany kodu fabryki — zgodnie z zasadą otwarte/zamknięte z podrozdziału o zasadach projektowania:

```python title="fabryka-rejestr.py"
from abc import ABC, abstractmethod


class Pojazd(ABC):
    @abstractmethod
    def jedz(self):
        """Zwraca opis jazdy."""


class Samochod(Pojazd):
    def jedz(self):
        return "jadę samochodem"


class Rower(Pojazd):
    def jedz(self):
        return "jadę rowerem"


class FabrykaPojazdow:
    """Tworzy pojazdy według nazwy typu z rejestru klas."""

    _rejestr = {}

    @classmethod
    def zarejestruj(cls, nazwa, klasa):
        if not issubclass(klasa, Pojazd):
            raise TypeError(f"{klasa.__name__} nie jest pojazdem")
        cls._rejestr[nazwa] = klasa

    @classmethod
    def utworz(cls, nazwa, *args, **kwargs):
        try:
            klasa = cls._rejestr[nazwa]
        except KeyError:
            raise ValueError(f"nieznany typ pojazdu: {nazwa!r}") from None
        return klasa(*args, **kwargs)

    @classmethod
    def dostepne(cls):
        return sorted(cls._rejestr)


FabrykaPojazdow.zarejestruj("samochod", Samochod)
FabrykaPojazdow.zarejestruj("rower", Rower)
print(FabrykaPojazdow.dostepne())
print(FabrykaPojazdow.utworz("rower").jedz())


class Hulajnoga(Pojazd):
    def jedz(self):
        return "jadę hulajnogą"


FabrykaPojazdow.zarejestruj("hulajnoga", Hulajnoga)
print(FabrykaPojazdow.utworz("hulajnoga").jedz())
try:
    FabrykaPojazdow.utworz("łódź")
except ValueError as e:
    print("ValueError:", e)
try:
    FabrykaPojazdow.zarejestruj("liczba", int)
except TypeError as e:
    print("TypeError:", e)
```

```{ .text .no-copy }
['rower', 'samochod']
jadę rowerem
jadę hulajnogą
ValueError: nieznany typ pojazdu: 'łódź'
TypeError: int nie jest pojazdem
```

Klasa `Hulajnoga` powstała po fabryce i została dopisana do rejestru bez ingerencji w `FabrykaPojazdow`; `issubclass()` z rozdziału 10 sprawdza, czy rejestrowana klasa jest pojazdem. Rejestr jest atrybutem klasy — celowo wspólnym dla wszystkich wywołań, jak licznik z rozdziału 10. Wywołanie `zarejestruj()` można uczynić automatycznym przy definicji każdej klasy pochodnej, o czym mowa w podrozdziale o metaprogramowaniu przy metodzie `__init_subclass__`.

## Strategia

**Strategia** (ang. *strategy*) wydziela wymienny algorytm do osobnego obiektu, który można podmienić w czasie działania programu. W postaci klasowej algorytmy są klasami pochodnymi od wspólnej klasy abstrakcyjnej:

```python title="strategia.py"
from abc import ABC, abstractmethod


class Sortowanie(ABC):
    @abstractmethod
    def sortuj(self, dane):
        """Zwraca posortowaną kopię danych."""


class SortowanieBabelkowe(Sortowanie):
    def sortuj(self, dane):
        wynik = list(dane)
        for i in range(len(wynik)):
            for j in range(len(wynik) - 1 - i):
                if wynik[j] > wynik[j + 1]:
                    wynik[j], wynik[j + 1] = wynik[j + 1], wynik[j]
        return wynik


class SortowanieWbudowane(Sortowanie):
    def sortuj(self, dane):
        return sorted(dane)


class Sorter:
    """Sortuje dane wybraną strategią, którą można wymienić."""

    def __init__(self, strategia):
        self.strategia = strategia

    def wykonaj(self, dane):
        return self.strategia.sortuj(dane)


sorter = Sorter(SortowanieBabelkowe())
print(sorter.wykonaj([3, 1, 2]), type(sorter.strategia).__name__)
sorter.strategia = SortowanieWbudowane()
print(sorter.wykonaj([3, 1, 2]), type(sorter.strategia).__name__)
```

```{ .text .no-copy }
[1, 2, 3] SortowanieBabelkowe
[1, 2, 3] SortowanieWbudowane
```

W Pythonie strategia bez własnego stanu nie potrzebuje klasy — wystarczy funkcja, bo funkcje są obiektami pierwszej klasy z rozdziału 6:

```python title="strategia-funkcje.py"
def sortowanie_babelkowe(dane):
    wynik = list(dane)
    for i in range(len(wynik)):
        for j in range(len(wynik) - 1 - i):
            if wynik[j] > wynik[j + 1]:
                wynik[j], wynik[j + 1] = wynik[j + 1], wynik[j]
    return wynik


class Sorter:
    def __init__(self, strategia=sorted):
        self.strategia = strategia

    def wykonaj(self, dane):
        return self.strategia(dane)


sorter = Sorter(sortowanie_babelkowe)
print(sorter.wykonaj([3, 1, 2]), sorter.strategia.__name__)
sorter.strategia = sorted
print(sorter.wykonaj([3, 1, 2]), sorter.strategia.__name__)
print(Sorter(lambda dane: sorted(dane, reverse=True)).wykonaj([3, 1, 2]))
```

```{ .text .no-copy }
[1, 2, 3] sortowanie_babelkowe
[1, 2, 3] sorted
[3, 2, 1]
```

Klasy strategii mają sens, gdy algorytm potrzebuje konfiguracji lub stanu między wywołaniami albo gdy kilka powiązanych operacji ma być wymienianych razem; w pozostałych przypadkach funkcja jest prostsza i równie wymienna. Tak samo działają argumenty `key=` funkcji `sorted()` z rozdziału 6 — to strategia porównywania przekazana jako funkcja.

## Obserwator

**Obserwator** (ang. *observer*) rozdziela źródło zdarzeń od kodu, który ma na nie reagować: źródło przechowuje listę obserwatorów i powiadamia ich o każdym zdarzeniu, nie znając ich klas. W Pythonie obserwatorem jest dowolny obiekt wywoływalny:

```python title="obserwator.py"
class Wydarzenie:
    """Lista obserwatorów powiadamianych przy każdym wystąpieniu zdarzenia."""

    def __init__(self):
        self._obserwatorzy = []

    def subskrybuj(self, obserwator):
        self._obserwatorzy.append(obserwator)

    def anuluj(self, obserwator):
        self._obserwatorzy.remove(obserwator)

    def powiadom(self, *args, **kwargs):
        for obserwator in list(self._obserwatorzy):
            obserwator(*args, **kwargs)


class Sklep:
    def __init__(self):
        self.nowy_produkt = Wydarzenie()
        self._produkty = []

    def dodaj_produkt(self, nazwa):
        self._produkty.append(nazwa)
        self.nowy_produkt.powiadom(nazwa)


def powiadomienie_email(nazwa):
    print(f"e-mail: nowy produkt {nazwa}")


class Licznik:
    def __init__(self):
        self.ile = 0

    def __call__(self, nazwa):
        self.ile += 1


sklep = Sklep()
licznik = Licznik()
sklep.nowy_produkt.subskrybuj(powiadomienie_email)
sklep.nowy_produkt.subskrybuj(licznik)
sklep.dodaj_produkt("laptop")
sklep.nowy_produkt.anuluj(powiadomienie_email)
sklep.dodaj_produkt("monitor")
print("powiadomień:", licznik.ile)
```

```{ .text .no-copy }
e-mail: nowy produkt laptop
powiadomień: 2
```

Sklep nie wie, że ktoś wysyła e-maile ani że ktoś liczy powiadomienia — wywołuje jedynie `powiadom()`. Obserwatorami są funkcja i obiekt z `__call__` z rozdziału 11, wymienne dzięki wspólnemu protokołowi wywołania. Metoda `powiadom()` iteruje po kopii listy, aby obserwator mógł w trakcie powiadamiania anulować subskrypcję bez naruszenia pętli. Ten wzorzec jest podstawą programowania sterowanego zdarzeniami (ang. *event-driven programming*) — w bibliotece tkinter metoda `bind()` rejestruje obserwatora zdarzeń okna dokładnie tak, jak `subskrybuj()`; wracamy do tego w rozdziale o tkinter. <!-- TODO: link po powstaniu rozdziału o tkinter -->

## Singleton przez dekorator klasy

W rozdziale 10 Singleton powstał przez `__new__`, z pułapką ponownego `__init__`. Prostszą i wolną od tej pułapki postać daje **dekorator klasy** — funkcja przyjmująca klasę i zwracająca obiekt, który ją zastępuje pod tą samą nazwą (mechanizm dekoratora z rozdziału 6 zastosowany do instrukcji `class` zamiast `def`):

```python title="singleton-dekorator.py"
def singleton(klasa):
    """Zamienia klasę w fabrykę zwracającą zawsze tę samą instancję."""
    instancja = None

    def pobierz(*args, **kwargs):
        nonlocal instancja
        if instancja is None:
            instancja = klasa(*args, **kwargs)
        return instancja

    return pobierz


@singleton
class Polaczenie:
    def __init__(self, adres):
        print("otwieram połączenie z", adres)
        self.adres = adres


p1 = Polaczenie("baza.example")
p2 = Polaczenie("inny.example")
print(p1 is p2, p2.adres)
print(type(Polaczenie).__name__, callable(Polaczenie))
```

```{ .text .no-copy }
otwieram połączenie z baza.example
True baza.example
function True
```

Po udekorowaniu nazwa `Polaczenie` wskazuje funkcję `pobierz()` — domknięcie z rozdziału 6 pamiętające pierwszą utworzoną instancję. `__init__` wykonało się raz, a drugie wywołanie zwróciło istniejący obiekt, ignorując nowy adres. Ceną jest utrata klasy: `Polaczenie` nie jest już klasą, więc `isinstance(p1, Polaczenie)` zgłosi `TypeError`, a dziedziczenie po niej jest niemożliwe. Singleton — w każdej postaci — ma też wady projektowe: wprowadza stan globalny, utrudnia testowanie (nie da się utworzyć nowego obiektu na potrzeby testu z rozdziału 7) i ukrywa zależności. W Pythonie zwykle wystarcza moduł: jest importowany raz, a jego zmienne i funkcje pełnią rolę jedynej instancji bez żadnej klasy.
