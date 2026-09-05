# Argumenty i parametry

Na poprzedniej stronie parametry i argumenty pojawiły się w najprostszej postaci: tyle wartości w wywołaniu, ile nazw w nagłówku, w tej samej kolejności. Python udostępnia znacznie więcej możliwości: argumenty przekazywane przez nazwę, wartości domyślne, zmienną liczbę argumentów oraz ograniczenia sposobu przekazywania. Zaczynamy od uporządkowania terminologii, a pełną składnię nagłówka funkcji poznajemy na końcu, gdy poszczególne jej elementy będą już znane.

## Parametr a argument

**Parametr** (ang. *parameter*) to nazwa występująca w nagłówku definicji funkcji. **Argument** (ang. *argument*) to konkretna wartość przekazana funkcji podczas wywołania. W definicji `def przedstaw(imie, wiek)` parametrami są `imie` i `wiek`; w wywołaniu `przedstaw("Ala", 21)` argumentami są łańcuch `"Ala"` i liczba `21`. W tej najprostszej postaci nagłówka każdy parametr zostaje przy wywołaniu związany z dokładnie jednym argumentem; wyjątki od tej reguły poznamy w sekcji o zmiennej liczbie argumentów.

Argumenty można przekazywać na dwa sposoby. **Argument pozycyjny** (ang. *positional argument*) trafia do parametru na podstawie kolejności. **Argument nazwany** (ang. *keyword argument*) — zapis `nazwa=wartość`, spotkany już przy konstruktorze `dict()` w rozdziale [5. Typy złożone](../05-typy-zlozone/slownik.md) — trafia do parametru o wskazanej nazwie, niezależnie od kolejności. Oba sposoby można łączyć:

```python title="przedstaw.py"
def przedstaw(imie, wiek):
    print(f"{imie}, {wiek} lat")


przedstaw("Ala", 21)
przedstaw(wiek=23, imie="Bartek")
przedstaw("Celina", wiek=22)
```

```{ .text .no-copy }
Ala, 21 lat
Bartek, 23 lat
Celina, 22 lat
```

Obowiązuje jedna reguła kolejności: w wywołaniu argumenty pozycyjne wypisane wprost muszą poprzedzać argumenty nazwane. Zapis odwrotny jest błędem składni, wykrywanym jeszcze przed uruchomieniem programu:

```python title="kolejnosc-argumentow.py"
def przedstaw(imie, wiek):
    print(f"{imie}, {wiek} lat")


przedstaw(imie="Ala", 21)
```

```{ .text .no-copy }
  File "kolejnosc-argumentow.py", line 5
    przedstaw(imie="Ala", 21)
                            ^
SyntaxError: positional argument follows keyword argument
```

Argumenty nazwane poprawiają czytelność wywołań z wieloma wartościami — czytelnik nie musi pamiętać, co oznacza trzecia liczba w nawiasie. Z tego powodu w rozdziale [5. Typy złożone](../05-typy-zlozone/lista.md) argumenty `key` i `reverse` funkcji `sorted()` i metody `sort()` zapisywaliśmy z nazwą, np. `sorted(["bbb", "a", "cc"], key=len)` czy `owoce.sort(key=str.lower, reverse=True)` — jak się okaże na końcu tej strony, w tych funkcjach jest to zresztą jedyny dopuszczalny sposób.

## Wartości domyślne

Parametr może mieć **wartość domyślną** (ang. *default value*), zapisaną w nagłówku po znaku `=`. Taki parametr staje się opcjonalny: jeżeli wywołanie nie przekaże mu argumentu, otrzyma wartość domyślną:

```python title="wartosc-domyslna.py"
def przedstaw(imie, wiek, miasto="Kraków"):
    print(f"{imie}, {wiek} lat, {miasto}")


przedstaw("Ala", 21)
przedstaw("Bartek", 23, "Gdańsk")
przedstaw("Celina", 22, miasto="Toruń")
```

```{ .text .no-copy }
Ala, 21 lat, Kraków
Bartek, 23 lat, Gdańsk
Celina, 22 lat, Toruń
```

Wśród parametrów przyjmujących argumenty pozycyjne te z wartością domyślną muszą stać za parametrami bez niej — w przeciwnym razie interpreter nie mógłby ustalić, do którego parametru trafia argument pozycyjny (wyjątek dotyczący parametrów tylko nazwanych omawiamy na końcu strony). Nagłówek `def przedstaw(imie, miasto="Kraków", wiek):` kończy się błędem `SyntaxError: parameter without a default follows parameter with a default`.

Istotny jest **moment obliczenia** wartości domyślnej. Wyrażenie po znaku `=` jest obliczane **jeden raz, podczas wykonywania instrukcji `def`** — nie przy każdym wywołaniu. Obliczona wtedy wartość jest zapamiętywana w obiekcie funkcji i używana we wszystkich wywołaniach, które nie przekażą własnego argumentu:

```python title="moment-obliczenia.py"
stawka = 5


def koszt(godziny, cena=stawka):
    return godziny * cena


stawka = 10
print(koszt(3))
print(koszt(3, stawka))
print(koszt.__defaults__)
```

```{ .text .no-copy }
15
30
(5,)
```

Późniejsze przypisanie nowego obiektu nazwie `stawka` nie ma wpływu na zapamiętaną wartość domyślną `5` — wartością domyślną parametru `cena` jest obiekt, na który `stawka` wskazywała w chwili wykonania instrukcji `def`. Zapamiętane wartości domyślne przechowuje atrybut `__defaults__` obiektu funkcji; dla funkcji `koszt` jest to krotka `(5,)`.

### Pułapka modyfikowalnej wartości domyślnej

Skoro obiekt domyślny powstaje raz, wszystkie wywołania korzystające z wartości domyślnej otrzymują **ten sam obiekt**. Dla obiektów niemodyfikowalnych (liczby, łańcuchy, `None`, krotki o niemodyfikowalnych elementach) nie ma to znaczenia. Dla obiektów modyfikowalnych, np. listy, ma to znaczenie: każda modyfikacja w miejscu jest widoczna w kolejnych wywołaniach:

```python title="lista-domyslna.py"
def dodaj(element, lista=[]):
    lista.append(element)
    return lista


print(dodaj(1))
print(dodaj(2))
print(dodaj(3, [10]))
print(dodaj(4))
```

```{ .text .no-copy }
[1]
[1, 2]
[10, 3]
[1, 2, 4]
```

Drugie wywołanie dopisuje element do listy pozostawionej przez pierwsze; trzecie, z własną listą, nie modyfikuje listy domyślnej, więc czwarte otrzymuje ją ponownie, wciąż z dwoma elementami. Nie jest to osobliwość języka, lecz bezpośrednia konsekwencja momentu utworzenia obiektu domyślnego oraz semantyki referencji z rozdziału [5. Typy złożone](../05-typy-zlozone/referencje-i-kopiowanie.md).

Jeżeli funkcja ma za każdym razem zaczynać od nowej listy, stosujemy idiom z wartością domyślną `None` i tworzymy obiekt wewnątrz ciała:

```python title="idiom-none.py"
def dodaj(element, lista=None):
    if lista is None:
        lista = []
    lista.append(element)
    return lista


print(dodaj(1))
print(dodaj(2))
print(dodaj(3, [10]))
```

```{ .text .no-copy }
[1]
[2]
[10, 3]
```

Wartość `None` jest niemodyfikowalna, więc może być bezpiecznie współdzielona; nowa lista powstaje dopiero przy wywołaniu, i to tylko wtedy, gdy wywołujący nie przekazał własnej. Porównanie z `None` zapisujemy operatorem `is` (rozdział [3. Nazwy i typy](../03-nazwy-typy/operatory.md)).

!!! warning "Wartość domyślna powstaje raz"
    Listy, słowniki i zbiory zwykle nie powinny być wartościami domyślnymi —
    zastępujemy je wartością `None` i tworzeniem obiektu w ciele funkcji. Ta
    sama zasada dotyczy każdego wyrażenia w nagłówku: jest obliczane przy
    definicji, nie przy wywołaniu. Współdzielenie obiektu domyślnego bywa
    jednak zamierzone; taki przypadek pokażemy przy dekoratorach.
    <!-- TODO: link po powstaniu strony dekoratory.md -->

## Przekazywanie referencji do obiektów

Model z rozdziału [3. Nazwy i typy](../03-nazwy-typy/obiekty-i-pamiec.md) obowiązuje także przy wywołaniu funkcji: nazwy wskazują na obiekty, a wywołanie **wiąże parametr z obiektem przekazanym jako argument** — dokładnie tak, jak zrobiłoby to przypisanie. Python nie przekazuje „zmiennej” ani jej kopii; dokumentacja (FAQ) stwierdza, że argumenty są przekazywane przez przypisanie (ang. *passed by assignment*), a ponieważ przypisanie tworzy jedynie referencję do obiektu, nazwa w wywołaniu i parametr nie są dwiema postaciami jednej „zmiennej”. W efekcie, gdy argumentem jest nazwa, parametr i ta nazwa wskazują jeden obiekt — jak `M = L` w rozdziale [5. Typy złożone](../05-typy-zlozone/referencje-i-kopiowanie.md).

Konsekwencje są dwie. Modyfikacja obiektu **w miejscu** przez parametr jest widoczna po wywołaniu, bo dotyczy wspólnego obiektu. Natomiast **przypisanie** nowego obiektu do parametru zmienia jedynie lokalne powiązanie nazwy i nie ma wpływu na nazwę użytą w wywołaniu:

```python title="append-a-przypisanie.py"
def dopisz(lista):
    lista.append(99)


def zastap(lista):
    lista = [99]


dane = [1, 2]
dopisz(dane)
print(dane)
zastap(dane)
print(dane)
```

```{ .text .no-copy }
[1, 2, 99]
[1, 2, 99]
```

Obiekty niemodyfikowalne, np. liczby, można w funkcji jedynie zastąpić nowym obiektem — a to, jak wyżej, nie zmienia niczego na zewnątrz. Nowy wynik trzeba zwrócić i przypisać w miejscu wywołania:

```python title="zwieksz.py"
def zwieksz(n):
    n += 1
    return n


x = 5
zwieksz(x)
print(x)
x = zwieksz(x)
print(x)
```

```{ .text .no-copy }
5
6
```

Operator `+=` zachowuje się różnie w zależności od typu obiektu. Dla liczby `n += 1` tworzy nowy obiekt i wiąże z nim nazwę `n` — stąd brak wpływu na `x`. Dla listy `lista += [4]` działa jak metoda `extend()`, czyli modyfikuje obiekt w miejscu, podczas gdy `lista = lista + [4]` tworzy nową listę i wiąże ją tylko z nazwą lokalną:

```python title="plus-rowna-sie.py"
def dolacz(lista):
    lista += [4]


def nowa(lista):
    lista = lista + [4]


dane = [1, 2, 3]
dolacz(dane)
print(dane)
nowa(dane)
print(dane)
```

```{ .text .no-copy }
[1, 2, 3, 4]
[1, 2, 3, 4]
```

## Zmienna liczba argumentów

Dotychczas liczba argumentów musiała odpowiadać liczbie parametrów. Dwa specjalne rodzaje parametrów zbierają nadmiarowe argumenty: pozycyjne do krotki, nazwane do słownika. Oba wykorzystują poznane w rozdziale [5. Typy złożone](../05-typy-zlozone/krotka.md) **pakowanie**.

### Parametr *args

Parametr poprzedzony gwiazdką zbiera wszystkie argumenty pozycyjne, które nie trafiły do wcześniejszych parametrów, i pakuje je w **krotkę**:

```python title="suma.py"
def suma(*liczby):
    print(liczby, type(liczby))
    return sum(liczby)


print(suma(1, 2, 3))
print(suma())
```

```{ .text .no-copy }
(1, 2, 3) <class 'tuple'>
6
() <class 'tuple'>
0
```

Znaczenie niesie gwiazdka, nie nazwa parametru: `liczby` jest zwykłą nazwą, którą dobieramy według treści. Zwyczajowo, gdy zebrane argumenty nie mają wspólnego znaczenia, używa się nazwy `args` (od ang. *arguments*) — jest to konwencja, nie element składni. Parametr z gwiazdką może stać po zwykłych parametrach; wtedy zbiera tylko argumenty pozycyjne wykraczające poza nie, a przy ich braku otrzymuje krotkę pustą:

```python title="zainteresowania.py"
def przedstaw(imie, *zainteresowania):
    print(imie, zainteresowania)


przedstaw("Ala")
przedstaw("Bartek", "szachy", "rower")
```

```{ .text .no-copy }
Ala ()
Bartek ('szachy', 'rower')
```

### Parametr **kwargs

Parametr poprzedzony dwiema gwiazdkami zbiera argumenty nazwane, które nie odpowiadają żadnemu parametrowi, i pakuje je w **słownik** — kluczami są nazwy argumentów, wartościami przekazane obiekty. Zwyczajowa nazwa to `kwargs` (od ang. *keyword arguments*) — podobnie jak `args` jest to konwencja, nie wymóg języka:

```python title="opisz.py"
def opisz(**cechy):
    print(type(cechy))
    for nazwa, wartosc in cechy.items():
        print(f"{nazwa}: {wartosc}")


opisz(kolor="czerwony", rozmiar=42)
```

```{ .text .no-copy }
<class 'dict'>
kolor: czerwony
rozmiar: 42
```

Tak właśnie działa konstruktor `dict(a="alpha")` z rozdziału 5 — argumenty nazwane trafiają do słownika. Oba rodzaje parametrów mogą wystąpić w jednym nagłówku, w kolejności: parametry zwykłe, parametr z gwiazdką, parametr z dwiema gwiazdkami:

```python title="pakowanie.py"
def fun(pierwszy, *pozostale, **nazwane):
    print(pierwszy, pozostale, nazwane)


fun(111, "aaa", 222, klucz1="abc", klucz2=3.14)
fun(111)
```

```{ .text .no-copy }
111 ('aaa', 222) {'klucz1': 'abc', 'klucz2': 3.14}
111 () {}
```

### Rozpakowanie argumentów w wywołaniu

Te same operatory użyte w **wywołaniu** działają odwrotnie: `*` rozpakowuje obiekt iterowalny na osobne argumenty pozycyjne, a `**` rozpakowuje słownik (ogólniej: dowolny typ odwzorowujący, ang. *mapping*) na argumenty nazwane. Gwiazdkę w wywołaniu spotkaliśmy już przy `zip(*pary)` w rozdziale [5. Typy złożone](../05-typy-zlozone/krotka.md) i przy `print(*sys.path, sep='\n')` w rozdziale [1. Instalacja i środowisko pracy](../01-instalacja/sciezki-i-utrzymanie.md):

```python title="rozpakowanie.py"
def przedstaw(imie, wiek, miasto="Kraków"):
    print(f"{imie}, {wiek} lat, {miasto}")


dane = ("Ala", 21)
przedstaw(*dane)
opis = {"imie": "Bartek", "wiek": 23, "miasto": "Toruń"}
przedstaw(**opis)
print(list(range(*[3, 6])))
```

```{ .text .no-copy }
Ala, 21 lat, Kraków
Bartek, 23 lat, Toruń
[3, 4, 5]
```

Rozpakowanie `**` wymaga słownika z kluczami będącymi łańcuchami — nazwami parametrów albo, gdy funkcja ma parametr z dwiema gwiazdkami, dowolnymi nazwami trafiającymi do jego słownika. Przekazanie listy po dwóch gwiazdkach kończy się błędem `TypeError: __main__.przedstaw() argument after ** must be a mapping, not list`, a obiektu nieiterowalnego po jednej gwiazdce — `TypeError: __main__.przedstaw() argument after * must be an iterable, not int`. Przedrostek `__main__.` w nazwie funkcji to nazwa modułu, w którym funkcja została zdefiniowana; moduły omawiamy w następnym rozdziale. <!-- TODO: link po powstaniu rozdziału o modułach -->

!!! note "Gwiazdka w definicji i w wywołaniu"
    W nagłówku funkcji `*` i `**` **pakują** nadmiarowe argumenty do krotki
    i słownika; w wywołaniu **rozpakowują** obiekt iterowalny i słownik na
    osobne argumenty. Jest to ten sam mechanizm, który przy krotce pozwolił
    zapisać `t = (*l,)`. Analogiczny zapis `{**a, **b}` buduje nowy słownik
    z par obu słowników — jest odpowiednikiem poznanego w rozdziale 5
    operatora `|`.

## Parametry tylko pozycyjne i tylko nazwane

Zwykły parametr przyjmuje argument pozycyjny albo nazwany. Nagłówek może to ograniczyć dwoma znacznikami. Parametry przed ukośnikiem `/` są **tylko pozycyjne** (ang. *positional-only*) — nie można ich przekazać przez nazwę:

```python title="podziel.py"
def podziel(a, b, /):
    return a / b


print(podziel(6, 3))
print(podziel(a=6, b=3))
```

```{ .text .no-copy }
2.0
Traceback (most recent call last):
  File "podziel.py", line 6, in <module>
    print(podziel(a=6, b=3))
          ~~~~~~~^^^^^^^^^^
TypeError: podziel() got some positional-only arguments passed as keyword arguments: 'a, b'
```

Parametry po samotnej gwiazdce `*` są **tylko nazwane** (ang. *keyword-only*) — należy je przekazać przez nazwę; mogą, lecz nie muszą mieć wartości domyślnej, i to niezależnie od tego, czy poprzedzające je parametry ją mają:

```python title="polacz.py"
def polacz(a, b, *, sep):
    return a + sep + b


print(polacz("Ala", "Bartek", sep=" i "))
print(polacz("Ala", "Bartek", " i "))
```

```{ .text .no-copy }
Ala i Bartek
Traceback (most recent call last):
  File "polacz.py", line 6, in <module>
    print(polacz("Ala", "Bartek", " i "))
          ~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: polacz() takes 2 positional arguments but 3 were given
```

Znaczniki te występują w sygnaturach wielu funkcji wbudowanych — wyświetla je `help()`:

```{ .python .no-copy }
>>> help(len)
Help on built-in function len in module builtins:

len(obj, /)
    Return the number of items in a container.

>>> help(sorted)
Help on built-in function sorted in module builtins:

sorted(iterable, /, *, key=None, reverse=False)
    Return a new list containing all items from the iterable in ascending order.
    ...
```

Zapis `sorted(iterable, /, *, key=None, reverse=False)` wyjaśnia konwencję z rozdziału 5: sortowaną kolekcję podajemy pozycyjnie, a `key` i `reverse` wyłącznie przez nazwę. Dokumentacja Pythona zaleca ukośnik, gdy nazwy parametrów nie niosą znaczenia albo mogą się w przyszłości zmienić, a samotną gwiazdkę, gdy nazwa parametru niesie znaczenie i wymuszenie jej użycia chroni przed pomyłką w kolejności argumentów.

Pełna kolejność rodzajów parametrów w nagłówku jest następująca:

```{ .text .no-copy }
def f(tylko_pozycyjne, /, zwykle, *args, tylko_nazwane, **kwargs):
```

Poszczególne części można pomijać, ale kolejność jest stała. Przykład łączący wszystkie kategorie:

```python title="pelny-naglowek.py"
def fun(a, b=0, /, c=1, *args, d, e=2, **kwargs):
    print(a, b, c, args, d, e, kwargs)


fun(1, 2, 3, 4, 5, d=6, f=7)
fun(1, d=6)
```

```{ .text .no-copy }
1 2 3 (4, 5) 6 2 {'f': 7}
1 0 1 () 6 2 {}
```

W pierwszym wywołaniu `a` i `b` otrzymały argumenty pozycyjne, `c` również, nadmiar pozycyjny `4, 5` trafił do krotki `args`, parametr tylko nazwany `d` otrzymał wartość przez nazwę, `e` zachował wartość domyślną, a nieznany argument nazwany `f=7` trafił do słownika `kwargs`. W drugim wywołaniu użyte zostały wszystkie wartości domyślne.

Ukośnik ma jeszcze jedno praktyczne zastosowanie: pozwala użyć nazwy parametru jako klucza w `**kwargs`. Bez niego wywołanie `zapisz(5, nazwa=10)` funkcji `def zapisz(nazwa, **kwds)` zgłasza `TypeError: zapisz() got multiple values for argument 'nazwa'`, bo argument nazwany `nazwa=10` jest kierowany do parametru, który otrzymał już argument `5`. Po zmianie nagłówka na `def zapisz(nazwa, /, **kwds)` ten sam argument trafia do słownika `kwds`.

### Typowe komunikaty błędów

Niepoprawne wywołanie zgłasza `TypeError` z komunikatem, który dokładnie wskazuje przyczynę. Poniższe wiersze dotyczą funkcji `przedstaw(imie, wiek, miasto="Kraków")`, `podziel(a, b, /)` i `polacz(a, b, *, sep)` z tej strony:

| Wywołanie | Komunikat i przyczyna |
|---|---|
| `przedstaw("Ala")` | `missing 1 required positional argument: 'wiek'` — brak wymaganego argumentu |
| `przedstaw("Ala", 21, "Gdańsk", 5)` | `takes from 2 to 3 positional arguments but 4 were given` — za dużo argumentów pozycyjnych |
| `przedstaw("Ala", imie="Ola", wiek=3)` | `got multiple values for argument 'imie'` — ten sam parametr pozycyjnie i przez nazwę |
| `przedstaw("Ala", 21, kraj="PL")` | `got an unexpected keyword argument 'kraj'` — nieznany argument nazwany |
| `podziel(a=6, b=3)` | `got some positional-only arguments passed as keyword arguments: 'a, b'` — nazwa dla parametru tylko pozycyjnego |
| `polacz("Ala", "Bartek", " i ")` | `takes 2 positional arguments but 3 were given` — argument pozycyjny dla parametru tylko nazwanego |

Każdy komunikat jest poprzedzony nazwą funkcji, np. `TypeError: przedstaw() missing 1 required positional argument: 'wiek'`.
