# Zasięg nazw i domknięcia

Wywołanie funkcji tworzy nowe nazwy — parametry i nazwy przypisywane w ciele — które po zakończeniu wywołania przestają istnieć. Jednocześnie ciało funkcji może korzystać z nazw zdefiniowanych poza nią, np. z funkcji wbudowanych albo z nazw modułu. Ta strona porządkuje, gdzie Python przechowuje nazwy, jak je wyszukuje i w jakich okolicznościach funkcja może zmienić nazwę spoza własnego ciała. Zbudowany tu model prowadzi do pojęcia domknięcia, na którym opierają się dekoratory z końca rozdziału. <!-- TODO: link po powstaniu strony dekoratory.md -->

## Przestrzenie nazw i zasięgi

**Przestrzeń nazw** (ang. *namespace*) to odwzorowanie nazw na obiekty. W programie istnieje ich kilka naraz: przestrzeń **wbudowana** z nazwami takimi jak `len` czy `print`, tworzona przy uruchomieniu interpretera; przestrzeń **globalna** modułu, do której trafiają nazwy przypisywane na najwyższym poziomie skryptu; oraz przestrzeń **lokalna** funkcji, tworzona przy każdym jej wywołaniu i usuwana po jego zakończeniu. Przypisanie nie kopiuje obiektu — wiąże nazwę z obiektem w jednej z tych przestrzeni, zgodnie z modelem z rozdziału [3. Nazwy i typy](../03-nazwy-typy/obiekty-i-pamiec.md).

**Zasięg** (ang. *scope*) to obszar tekstu programu, w którym dana przestrzeń nazw jest bezpośrednio dostępna, czyli w którym samą nazwą (bez kropki) odwołujemy się do jej zawartości. Gdy interpreter napotyka zwykłą nazwę, przeszukuje zasięgi od najbardziej wewnętrznego na zewnątrz:

```{ .text .no-copy }
L  lokalny      (ang. local)     — bieżąca funkcja
E  otaczający   (ang. enclosing) — funkcje, w których bieżąca funkcja jest zagnieżdżona
G  globalny     (ang. global)    — moduł
B  wbudowany    (ang. built-in)  — nazwy wbudowane
```

Skrót **LEGB** jest wygodnym modelem wyszukiwania zwykłych nazw, wystarczającym na potrzeby tego rozdziału. Współczesny Python ma również zasięgi szczególne: zasięg klasy, który omówimy przy klasach, oraz zasięgi adnotacji, do których wracamy przy narzędziach analizy typów. <!-- TODO: linki po powstaniu rozdziału o klasach i rozdziału o narzędziach analizy typów -->

```python title="cztery-poziomy.py"
x = "globalna"


def zewnetrzna():
    x = "otaczajaca"

    def wewnetrzna():
        x = "lokalna"
        print(x)

    def czytajaca():
        print(x)

    wewnetrzna()
    czytajaca()


zewnetrzna()
print(x)
print(len)
```

```{ .text .no-copy }
lokalna
otaczajaca
globalna
<built-in function len>
```

Trzy różne obiekty noszą tę samą nazwę `x`, każdy w innej przestrzeni. Funkcja `wewnetrzna()` ma własne `x`, więc odczyt kończy się w zasięgu lokalnym. Funkcja `czytajaca()` nie wiąże `x` u siebie, więc wyszukiwanie przechodzi do zasięgu otaczającego, czyli do przestrzeni wywołania `zewnetrzna()`. Na poziomie modułu `x` oznacza obiekt globalny, a `len` znajduje się dopiero w przestrzeni wbudowanej. Odczyt nazwy nieznalezionej w żadnym zasięgu zgłasza `NameError: name 'nieznana' is not defined`.

Skoro przestrzeń wbudowana jest przeszukiwana na końcu, nazwa przypisana w module albo w funkcji **przesłania** nazwę wbudowaną. Przypisanie `list = [1, 2]` na poziomie skryptu sprawia, że dalsze wywołanie `list("abc")` kończy się błędem `TypeError: 'list' object is not callable`; usunięcie własnej nazwy instrukcją `del` przywraca dostęp do funkcji wbudowanej. Z tego powodu unikamy nazw takich jak `list`, `str`, `sum`, `max` czy `id` dla własnych obiektów — linter pylint ostrzega przed takim przesłonięciem.

Własny, niejawny zasięg mają złożenia poznane w rozdziale [5. Typy złożone](../05-typy-zlozone/zlozenia.md). Nazwa sterująca złożeniem nie jest widoczna na zewnątrz i nie zmienia nazwy o tym samym brzmieniu z otaczającego zasięgu — inaczej niż nazwa sterująca zwykłą pętlą `for`, która po pętli zachowuje ostatnią wartość:

```python title="zlozenie-zasieg.py"
x = 10
wyniki = [x * 2 for x in range(3)]
print(wyniki)
print(x)

for i in range(3):
    pass
print(i)
```

```{ .text .no-copy }
[0, 2, 4]
10
2
```

!!! note "Dla dociekliwych — globals() i locals()"
    Funkcja wbudowana `globals()` zwraca słownik będący przestrzenią globalną
    modułu — przypisanie do tego słownika tworzy lub zmienia nazwę globalną.
    Funkcja `locals()` wywołana w ciele funkcji zwraca natomiast, od Pythona
    3.13 ([PEP 667](https://peps.python.org/pep-0667/)), niezależną **migawkę**
    bieżących wiązań lokalnych: zmiany w zwróconym słowniku nie wpływają na
    nazwy lokalne funkcji, a późniejsze przypisania nie zmieniają wcześniej
    pobranej migawki. Obie funkcje służą do diagnostyki, nie do sterowania
    programem.

## Nazwy lokalne

O tym, czy nazwa jest lokalna w funkcji, decyduje **cała treść jej ciała**, a nie kolejność wykonania. Reguła brzmi: jeżeli nazwa jest gdziekolwiek w ciele funkcji wiązana — m.in. przez przypisanie, parametr, nagłówek pętli `for`, definicję zagnieżdżoną, instrukcję `import` czy `del` — to jest nazwą lokalną w całym ciele, chyba że zadeklarowano inaczej (deklaracje omawiamy dalej). Kompilator ustala to podczas analizy bloku funkcji, zanim jakakolwiek jej instrukcja zostanie wykonana.

Sam **odczyt** nazwy spoza funkcji nie wymaga niczego szczególnego — wyszukiwanie przechodzi do zasięgu globalnego:

```python title="odczyt-globalnej.py"
stawka = 5


def koszt(godziny):
    return godziny * stawka


print(koszt(3))
```

```{ .text .no-copy }
15
```

Jeżeli jednak w ciele funkcji pojawia się **przypisanie** do tej nazwy, nazwa staje się lokalna — w przestrzeni lokalnej powstaje nowe wiązanie nazwy `stawka`, a wiązanie globalne pozostaje bez zmian:

```python title="lokalna-przeslania.py"
stawka = 5


def koszt(godziny):
    stawka = 100
    return godziny * stawka


print(koszt(3))
print(stawka)
```

```{ .text .no-copy }
300
5
```

Z tej reguły wynika jeden z najczęstszych błędów początkujących. Zapis `licznik += 1` jest przypisaniem do nazwy `licznik`, więc `licznik` jest w całym ciele funkcji nazwą lokalną — a odczyt nazwy lokalnej, która nie została jeszcze związana z żadnym obiektem, zgłasza `UnboundLocalError`:

```python title="licznik-blad.py"
licznik = 0


def zwieksz():
    licznik += 1


zwieksz()
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "licznik-blad.py", line 8, in <module>
    zwieksz()
    ~~~~~~~^^
  File "licznik-blad.py", line 5, in zwieksz
    licznik += 1
    ^^^^^^^
UnboundLocalError: cannot access local variable 'licznik' where it is not associated with a value
```

Ten sam błąd zgłosi odczyt `print(x)` umieszczony przed przypisaniem `x = 20` w tej samej funkcji — nazwa `x` jest lokalna w całym ciele, a więc również w wierszu poprzedzającym przypisanie. `UnboundLocalError` jest odmianą `NameError` i oznacza dokładnie tyle: nazwa została zaklasyfikowana jako lokalna, ale w chwili odczytu nie ma jeszcze wartości.

Zupełnie inaczej wygląda **modyfikacja obiektu** przez jego metodę. Wywołanie `elementy.append(3)` nie wiąże nazwy `elementy` z niczym nowym — odczytuje ją (znajdując obiekt w zasięgu globalnym) i zmienia ten obiekt w miejscu:

```python title="append-bez-deklaracji.py"
elementy = [1, 2]


def dodaj():
    elementy.append(3)


dodaj()
print(elementy)
```

```{ .text .no-copy }
[1, 2, 3]
```

!!! note "Wiązanie nazwy a modyfikacja obiektu"
    O lokalności decyduje wyłącznie **wiązanie nazwy**: `nazwa = …`,
    `nazwa += …`, `for nazwa in …`, parametr, `def nazwa`, a także `del nazwa`.
    Wywołanie metody,
    przypisanie do elementu (`lista[0] = …`) czy do klucza słownika nie wiąże
    nazwy — modyfikuje obiekt, do którego nazwa prowadzi. Rozróżnienie to
    poznaliśmy już przy przekazywaniu referencji na stronie
    [Argumenty i parametry](argumenty-i-parametry.md).

## Funkcje zagnieżdżone i zmienne wolne

Instrukcja `def` może wystąpić w ciele innej funkcji. Taka **funkcja zagnieżdżona** (ang. *nested function*) jest tworzona przy każdym wywołaniu funkcji zewnętrznej, jest widoczna wyłącznie w jej ciele i ma dostęp do jej nazw:

```python title="zagniezdzona.py"
def sformatuj(dane):
    def wiersz(element):
        return f"- {element}"

    return "\n".join(wiersz(d) for d in dane)


print(sformatuj(["jabłka", "gruszki"]))
print(wiersz("śliwki"))
```

```{ .text .no-copy }
- jabłka
- gruszki
Traceback (most recent call last):
  File "zagniezdzona.py", line 9, in <module>
    print(wiersz("śliwki"))
          ^^^^^^
NameError: name 'wiersz' is not defined
```

Funkcja pomocnicza `wiersz()` istnieje tylko podczas wywołania `sformatuj()`; na poziomie modułu nazwa `wiersz` nie jest związana z niczym. Zagnieżdżanie stosujemy właśnie wtedy, gdy funkcja pomocnicza ma sens wyłącznie wewnątrz jednej funkcji.

Nazwa używana w ciele funkcji, lecz w nim niewiązana, to **zmienna wolna** (ang. *free variable*). W funkcji `wiersz()` jedyną użytą nazwą jest parametr `element`, a więc nazwa lokalna; w poniższym przykładzie `wiadomosc` jest natomiast zmienną wolną funkcji `wewnetrzna()`, rozstrzyganą w zasięgu otaczającym:

```python title="zmienna-wolna.py"
def zewnetrzna():
    wiadomosc = "witaj"

    def wewnetrzna():
        print(wiadomosc)

    wewnetrzna()


zewnetrzna()
```

```{ .text .no-copy }
witaj
```

Zmienną wolną jest formalnie także `print` — nazwa niezwiązana w `wewnetrzna()`, znaleziona dopiero w przestrzeni wbudowanej. Dla dalszych rozważań istotne są zmienne wolne rozstrzygane w zasięgu **otaczającej funkcji**; dokumentacja nazywa je zmiennymi domknięcia (ang. *closure variables*), a powód tej nazwy wyjaśnia sekcja o domknięciach.

## Deklaracje global i nonlocal

Reguła lokalności ma dwa jawne wyjątki. Deklaracja `global` wskazuje, że wymienione nazwy w całym ciele funkcji oznaczają nazwy przestrzeni **globalnej modułu** — także przypisania do nich zmieniają więc wiązania modułu, zamiast tworzyć nazwy lokalne:

```python title="global-licznik.py"
licznik = 0


def zwieksz():
    global licznik
    licznik += 1


zwieksz()
zwieksz()
print(licznik)
```

```{ .text .no-copy }
2
```

Deklaracja obowiązuje w całym ciele funkcji i musi poprzedzać każde użycie nazwy — umieszczenie `global licznik` po wcześniejszym `print(licznik)` w tej samej funkcji kończy się błędem `SyntaxError: name 'licznik' is used prior to global declaration`, wykrywanym przed uruchomieniem programu.

!!! warning "global nie jest sposobem na przechowywanie stanu"
    Deklaracja `global` służy do jawnego wskazania nielicznych sytuacji,
    w których funkcja ma zmienić nazwę modułu. Funkcja, która zamiast
    przyjmować dane przez parametry i oddawać wynik przez `return` sięga do
    nazw globalnych, utrudnia śledzenie przepływu danych: jej wynik zależy od
    tego, co inne fragmenty programu zrobiły wcześniej. Częste używanie
    `global` jest zwykle sygnałem, że kod warto przebudować.

Drugi wyjątek dotyczy funkcji zagnieżdżonych. Deklaracja `nonlocal` wskazuje, że wymienione nazwy oznaczają **istniejącą** nazwę z najbliższego otaczającego zasięgu funkcji, w którym ta nazwa jest związana — nigdy z modułu:

```python title="licznik-nonlocal.py"
def utworz_licznik():
    licznik = 0

    def nastepny():
        nonlocal licznik
        licznik += 1
        return licznik

    return nastepny


licz = utworz_licznik()
print(licz())
print(licz())
print(licz())
inny = utworz_licznik()
print(inny())
```

```{ .text .no-copy }
1
2
3
1
```

Bez deklaracji `nonlocal` przypisanie `licznik += 1` uczyniłoby `licznik` nazwą lokalną funkcji `nastepny()` i skończyłoby się znanym już `UnboundLocalError`. Deklaracja odsyła do wiązania z przestrzeni wywołania `utworz_licznik()`, dzięki czemu kolejne wywołania `licz()` zwracają rosnące wartości. Funkcja `utworz_licznik()` nie wywołuje `nastepny()`, lecz zwraca sam obiekt funkcji — zgodnie z sekcją o funkcji jako obiekcie na stronie [Definiowanie funkcji](definiowanie-funkcji.md); nazwa `licz` staje się drugą nazwą tej funkcji, którą można wywoływać wielokrotnie. Drugie wywołanie `utworz_licznik()` tworzy zupełnie nową przestrzeń z własnym licznikiem — stąd `inny()` zaczyna od `1`. Do tego przykładu wracamy w następnej sekcji.

Deklaracja `nonlocal` jest potrzebna tylko przy ponownym wiązaniu nazwy. Funkcja zagnieżdżona, która modyfikuje w miejscu obiekt z otaczającego zasięgu, obywa się bez niej — zgodnie z regułą z sekcji o nazwach lokalnych, wywołanie metody nie wiąże nazwy:

```python title="rejestr.py"
def utworz_rejestr():
    wpisy = []

    def dodaj(element):
        wpisy.append(element)
        return wpisy

    return dodaj


zapisz = utworz_rejestr()
zapisz("a")
print(zapisz("b"))
```

```{ .text .no-copy }
['a', 'b']
```

Ograniczenia `nonlocal` sprawdza kompilator: nazwa musi być związana w zasięgu którejś z funkcji otaczających, w przeciwnym razie zgłaszany jest `SyntaxError: no binding for nonlocal 'brak' found`; deklaracja na poziomie modułu zgłasza `SyntaxError: nonlocal declaration not allowed at module level`. Różnicę między trzema rodzajami przypisania podsumowuje przykład wzorowany na samouczku Pythona:

```python title="trzy-zasiegi.py"
def test_zasiegow():
    def lokalnie():
        napis = "lokalny"

    def nielokalnie():
        nonlocal napis
        napis = "nielokalny"

    def globalnie():
        global napis
        napis = "globalny"

    napis = "testowy"
    lokalnie()
    print("po przypisaniu lokalnym:", napis)
    nielokalnie()
    print("po przypisaniu nonlocal:", napis)
    globalnie()
    print("po przypisaniu global:", napis)


test_zasiegow()
print("w zasięgu globalnym:", napis)
```

```{ .text .no-copy }
po przypisaniu lokalnym: testowy
po przypisaniu nonlocal: nielokalny
po przypisaniu global: nielokalny
w zasięgu globalnym: globalny
```

Przypisanie lokalne w `lokalnie()` utworzyło nową nazwę i nie zmieniło `napis` z `test_zasiegow()`. Deklaracja `nonlocal` zmieniła wiązanie w `test_zasiegow()`, a `global` — wiązanie na poziomie modułu, którego wcześniej nie było; wewnątrz `test_zasiegow()` nazwa `napis` nadal oznacza obiekt „nielokalny”.

## Domknięcia

Wracamy do funkcji zagnieżdżonej, która odczytuje nazwę z funkcji zewnętrznej — tym razem, jak w liczniku z poprzedniej sekcji, funkcja zewnętrzna nie wywołuje jej, lecz zwraca ją jako wynik:

```python title="mnoznik.py"
def mnoznik(przez):
    def pomnoz(wartosc):
        return wartosc * przez

    return pomnoz


razy_dwa = mnoznik(2)
razy_trzy = mnoznik(3)
print(razy_dwa(10))
print(razy_trzy(10))
print(razy_dwa)
```

```{ .text .no-copy }
20
30
<function mnoznik.<locals>.pomnoz at 0x...>
```

Wywołanie `mnoznik(2)` już się zakończyło, jego przestrzeń lokalna została usunięta, a mimo to zwrócona funkcja nadal ma dostęp do wartości parametru `przez`. Funkcja `pomnoz()` zachowuje wiązanie swojej zmiennej wolnej `przez` — i to niezależnie dla każdego wywołania `mnoznik()`: `razy_dwa` zachowuje wiązanie `przez` z `2`, `razy_trzy` — z `3`. Funkcję wraz z zachowanymi wiązaniami zmiennych wolnych nazywamy **domknięciem** (ang. *closure*), a `mnoznik()` jest **fabryką funkcji**: każde wywołanie tworzy nową funkcję z własnymi wiązaniami. Zapis `mnoznik.<locals>.pomnoz` w reprezentacji obiektu informuje, że `pomnoz` została zdefiniowana lokalnie wewnątrz `mnoznik`; adres po `at` jest, jak poprzednio, szczegółem implementacyjnym.

Licznik z poprzedniej sekcji jest domknięciem, które swoją zmienną wolną nie tylko odczytuje, lecz także zmienia — dlatego wymaga deklaracji `nonlocal`. Stan zachowany między wywołaniami `licz()` nie jest globalny i nie ma nazwy w przestrzeni modułu: istnieje wyłącznie w zachowanych wiązaniach tego jednego domknięcia.

Domknięcie zachowuje **wiązanie** zmiennej wolnej, a nie wartość z chwili definicji. Jeżeli funkcja zewnętrzna zmieni to wiązanie po utworzeniu funkcji wewnętrznej, ta ostatnia odczyta nową wartość:

```python title="biezace-wiazanie.py"
def zewnetrzna():
    wartosc = 1

    def wewnetrzna():
        return wartosc

    wartosc = 2
    return wewnetrzna


f = zewnetrzna()
print(f())
```

```{ .text .no-copy }
2
```

!!! note "Dla dociekliwych — atrybuty domknięcia"
    Model danych Pythona udostępnia atrybut `__closure__` obiektu funkcji —
    krotkę **komórek** (ang. *cells*) przechowujących wiązania zmiennych
    domknięcia, z wartością dostępną przez `cell_contents` — oraz atrybut
    `co_freevars` obiektu kodu `__code__` z nazwami tych zmiennych. Dla
    `razy_dwa` z przykładu `mnoznik.py` `co_freevars` daje
    `('przez',)`, a `razy_dwa.__closure__[0].cell_contents` daje `2`; funkcja
    `mnoznik` nie ma zmiennych domknięcia, więc jej `__closure__` to `None`.
    Atrybuty te są udokumentowane w Language Reference; sposób przechowywania
    komórek i ich reprezentacja są szczegółem implementacyjnym CPythona.

## Późne wiązanie nazw

Skoro funkcja odczytuje wiązanie zmiennej wolnej dopiero w chwili **wywołania** — obojętnie, czy jest to nazwa globalna, czy zmienna domknięcia — funkcje tworzone w pętli zachowują się inaczej, niż sugeruje ich zapis. Poniższy skrypt tworzy trzy funkcje, z których każda ma zwrócić „swoją” wartość `i`:

```python title="pozne-wiazanie.py"
funkcje = []
for i in range(3):
    def pokaz():
        return i

    funkcje.append(pokaz)

print([f() for f in funkcje])
i = 10
print([f() for f in funkcje])
```

```{ .text .no-copy }
[2, 2, 2]
[10, 10, 10]
```

Pętla `for` nie tworzy zasięgu, więc `i` jest jedną nazwą modułu, a w każdej z trzech funkcji `i` jest zmienną wolną rozstrzyganą w zasięgu globalnym — dopiero przy wywołaniu. Wszystkie trzy odczytują wtedy bieżące wiązanie: po pętli `2`, po kolejnym przypisaniu `10`. Zjawisko to nazywa się **późnym wiązaniem** (ang. *late binding*) i dotyczy każdej funkcji odwołującej się do zmiennej wolnej, niezależnie od tego, czy jest ona rozstrzygana w zasięgu globalnym, czy — jak w domknięciu — w zasięgu funkcji otaczającej; także wyrażeń lambda, które poznamy na następnej stronie. <!-- TODO: link po powstaniu strony funkcje-jako-obiekty.md -->

Zapamiętanie wartości z chwili tworzenia funkcji można osiągnąć na dwa sposoby, korzystając wyłącznie z poznanych już mechanizmów. Pierwszy to **wartość domyślna parametru**, obliczana — jak wiemy ze strony [Argumenty i parametry](argumenty-i-parametry.md) — podczas wykonywania instrukcji `def`:

```python title="pozne-wiazanie-domyslna.py"
funkcje = []
for i in range(3):
    def pokaz(i=i):
        return i

    funkcje.append(pokaz)

print([f() for f in funkcje])
```

```{ .text .no-copy }
[0, 1, 2]
```

Drugi to **fabryka funkcji**: każde wywołanie funkcji zewnętrznej tworzy osobną przestrzeń lokalną, a więc osobne wiązanie nazwy `numer`, która dopiero teraz staje się zmienną domknięcia:

```python title="pozne-wiazanie-fabryka.py"
def utworz(numer):
    def pokaz():
        return numer

    return pokaz


funkcje = [utworz(i) for i in range(3)]
print([f() for f in funkcje])
```

```{ .text .no-copy }
[0, 1, 2]
```

Oba rozwiązania różnią się semantycznie. Wartość domyślna jest obliczana raz przy `def` i staje się parametrem — można ją więc nadpisać, wywołując `pokaz(7)`. Domknięcie z fabryki odwołuje się do wiązania zmiennej wolnej `numer` w przestrzeni jednego wywołania `utworz()`; tego wiązania nic już nie zmieni, bo wywołanie `utworz()` się zakończyło i żadna instrukcja nie ma dostępu do jego przestrzeni lokalnej. Fabryka wyraża zamiar wprost i nie zmienia sygnatury funkcji, dlatego zwykle jest wyborem czytelniejszym.
