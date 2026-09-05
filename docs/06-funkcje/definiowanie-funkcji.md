# Definiowanie funkcji

Dotychczas korzystaliśmy z funkcji wbudowanych (`print()`, `len()`, `sorted()`) oraz z metod obiektów. W tym podrozdziale definiujemy funkcje własne. Funkcja to nazwany fragment programu, który otrzymuje dane przez **parametry** i przekazuje wynik instrukcją `return`. Dzięki funkcjom unikamy powtarzania kodu i nadajemy fragmentom programu czytelne nazwy — ten sam fragment można wywołać wielokrotnie z różnymi danymi.

## Anatomia definicji i wywołania

Definicję rozpoczyna **nagłówek**: słowo kluczowe `def`, nazwa funkcji (obowiązują zasady nazywania z rozdziału [3. Nazwy i typy](../03-nazwy-typy/nazwy-i-slowa-kluczowe.md), a więc `snake_case`), w nawiasach lista parametrów rozdzielonych przecinkami, a po nawiasie dwukropek. Poniżej, z wcięciem (rozdział [2. Konsola](../02-konsola/pierwszy-skrypt.md)), znajduje się **ciało** funkcji:

```python title="pole-prostokata.py"
def pole_prostokata(a, b):
    return a * b


print(pole_prostokata(3, 4))
wynik = pole_prostokata(2.5, 2)
print(wynik, type(wynik))
```

```{ .text .no-copy }
12
5.0 <class 'float'>
```

Nazwy `a` i `b` to parametry — wewnątrz ciała są zwykłymi nazwami, które przy każdym wywołaniu otrzymują przekazane wartości. **Wywołanie** to nazwa funkcji z nawiasami, w których podajemy **argumenty**, czyli wartości przekazywane parametrom (rozróżnienie to rozwija strona Argumenty i parametry). Wywołanie jest wyrażeniem, a jego wartością jest wynik funkcji — można go wypisać, przypisać do nazwy albo użyć w dalszych obliczeniach. Funkcja nie sprawdza typów przekazanych wartości: raz otrzymała liczby całkowite (wynik `12`), raz zmiennoprzecinkową (wynik `5.0`) — jest to konsekwencja dynamicznego typowania omówionego w rozdziale 3.

!!! note "Definicja jest instrukcją"
    Instrukcja `def` wykonuje się jak każda inna instrukcja programu: w chwili
    wykonania tworzy **obiekt funkcji** i wiąże go z podaną nazwą — dokładnie tak,
    jak przypisanie wiąże nazwę z obiektem. Ciało funkcji nie jest wtedy
    wykonywane (jego składnia została sprawdzona wcześniej, przy kompilacji
    całego pliku). Kod ciała uruchamia się dopiero przy wywołaniu, i to za każdym
    razem od nowa.

Skrypt jest wykonywany od góry do dołu, dlatego funkcję trzeba zdefiniować, zanim zostanie wywołana:

```python title="przed-definicja.py"
print(pole_prostokata(1, 2))


def pole_prostokata(a, b):
    return a * b
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "przed-definicja.py", line 1, in <module>
    print(pole_prostokata(1, 2))
          ^^^^^^^^^^^^^^^
NameError: name 'pole_prostokata' is not defined
```

Komunikat o błędzie, czyli **ślad wywołań** (ang. *traceback*), wskazuje plik, numer wiersza i fragment kodu, w którym wystąpił błąd. W tracebackach przytaczanych w książce skracamy ścieżkę do samej nazwy pliku — interpreter wypisuje ścieżkę pełną.

Ciało funkcji nie może być puste. Jeżeli funkcja ma na razie nic nie robić (np. jako szkic programu), używamy instrukcji `pass`, poznanej przy pętlach w rozdziale [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md). Brak wcięcia po nagłówku kończy się błędem `IndentationError: expected an indented block after function definition on line 1`. Z kolei liczba argumentów w wywołaniu musi odpowiadać liczbie parametrów — wywołanie `pole_prostokata(3)` zgłasza `TypeError: pole_prostokata() missing 1 required positional argument: 'b'`. Sposoby uelastycznienia tej reguły (wartości domyślne, zmienna liczba argumentów) opisuje strona Argumenty i parametry. <!-- TODO: link po powstaniu strony argumenty-i-parametry.md -->

## Instrukcja return

Instrukcja `return` kończy wykonanie funkcji i przekazuje podaną wartość do miejsca wywołania. Funkcja bez instrukcji `return` (albo z `return` bez wartości) również zwraca wynik — jest nim obiekt `None`, wprowadzony w rozdziale [3. Nazwy i typy](../03-nazwy-typy/typy-proste.md):

```python title="powitanie.py"
def powitanie(imie):
    print("Witaj,", imie)


wynik = powitanie("Anna")
print(wynik)
print(wynik is None)
```

```{ .text .no-copy }
Witaj, Anna
None
True
```

!!! warning "print to nie return"
    Funkcja `powitanie()` wypisuje tekst na ekran, ale niczego nie zwraca — jej
    wynikiem jest `None`. Częstym błędem początkujących jest zastępowanie
    `return` przez `print()`: taka funkcja „pokazuje” wynik, lecz nie da się go
    użyć w dalszych obliczeniach. Wynik obliczeń zwracamy instrukcją `return`,
    a wypisujemy dopiero w miejscu wywołania.

Instrukcja `return` może wystąpić w ciele funkcji wielokrotnie, np. w gałęziach instrukcji warunkowej (rozdział [4. Sterowanie przepływem](../04-sterowanie/wyrazenia-warunkowe.md)). Pierwsza napotkana kończy funkcję — pozwala to obsłużyć przypadek szczególny na początku i nie zagłębiać dalszego kodu w kolejne poziomy wcięć:

```python title="dziel.py"
def dziel(a, b):
    if b == 0:
        return None
    return a / b


print(dziel(1, 0))
print(dziel(1, 4))
```

```{ .text .no-copy }
None
0.25
```

Zgodnie z zaleceniem PEP 8 wszystkie instrukcje `return` w jednej funkcji są tu spójne: skoro jedna gałąź zwraca wartość, druga zwraca ją jawnie (`return None`), zamiast kończyć się bez instrukcji `return`. Zwracanie `None` jako sygnału błędu jest rozwiązaniem tymczasowym — właściwy mechanizm, wyjątki, poznamy w jednym z dalszych rozdziałów. <!-- TODO: link po powstaniu rozdziału o wyjątkach -->

Funkcja może zwrócić kilka wartości naraz. Zapis `return min(dane), max(dane)` to poznane w rozdziale [5. Typy złożone](../05-typy-zlozone/krotka.md) **pakowanie** wartości w krotkę, którą w miejscu wywołania można od razu rozpakować:

```python title="min-max.py"
def min_max(dane):
    return min(dane), max(dane)


wynik = min_max([3, 1, 7, 2])
print(wynik, type(wynik))
najmniejsza, najwieksza = min_max([3, 1, 7, 2])
print(najmniejsza, najwieksza)
```

```{ .text .no-copy }
(1, 7) <class 'tuple'>
1 7
```

Instrukcja `return` ma sens wyłącznie wewnątrz funkcji — użyta poza nią zgłasza `SyntaxError: 'return' outside function`.

## Docstring i funkcja help()

W podrozdziale [Pierwszy skrypt](../02-konsola/pierwszy-skrypt.md) wspomnieliśmy o **docstringu** (ang. *documentation string*) — łańcuchu znakowym pełniącym rolę dokumentacji. W funkcji jest nim łańcuch będący **pierwszą instrukcją ciała**. Interpreter zapisuje go w atrybucie `__doc__` obiektu funkcji, a funkcja `help()`, poznana w rozdziale [2. Konsola](../02-konsola/konsola-w-praktyce.md), wyświetla go razem z nagłówkiem funkcji:

```python title="srednia.py"
def srednia(liczby):
    """Oblicza średnią arytmetyczną liczb.

    Argument liczby to niepusta sekwencja liczb.
    """
    return sum(liczby) / len(liczby)


help(srednia)
```

```{ .text .no-copy }
Help on function srednia in module __main__:

srednia(liczby)
    Oblicza średnią arytmetyczną liczb.

    Argument liczby to niepusta sekwencja liczb.

```

Po uruchomieniu skryptu opcją `-i` (podrozdział [Pierwszy skrypt](../02-konsola/pierwszy-skrypt.md)) możemy obejrzeć sam atrybut:

```{ .python .no-copy }
>>> srednia.__doc__
'Oblicza średnią arytmetyczną liczb.\n\nArgument liczby to niepusta sekwencja liczb.\n'
```

W atrybucie `__doc__` nie ma wcięć obecnych w kodzie — od Pythona 3.13 kompilator usuwa z docstringu wspólne wcięcie wierszy. Krótki opis mieści się w jednym wierszu, wraz z zamykającymi cudzysłowami, np. `"""Zwraca kwadrat liczby x."""`. Łańcuch umieszczony w innym miejscu ciała jest zwykłym, porzucanym wyrażeniem, nie dokumentacją:

```{ .python .no-copy }
>>> def zle():
...     x = 1
...     """To nie jest docstring."""
...     return x
...
>>> print(zle.__doc__)
None
```

!!! info "Konwencje PEP 257"
    Zasady pisania docstringów zbiera dokument
    [PEP 257](https://peps.python.org/pep-0257/): potrójne podwójne cudzysłowy;
    docstring jednowierszowy zamykamy w tym samym wierszu; wielowierszowy składa
    się z wiersza podsumowania, pustego wiersza i dalszego opisu, a zamykające
    cudzysłowy stoją w osobnym wierszu. PEP 257 zaleca w języku angielskim tryb
    rozkazujący („Return…”); w polskich przykładach w tej książce stosujemy
    konsekwentnie formę „Zwraca…”, „Oblicza…”, „Sprawdza…”.

Brak docstringu w funkcji pylint zgłasza jako *Missing function or method docstring* — analogicznie do ostrzeżenia dla modułu opisanego w podrozdziale [Konfigurowanie narzędzi](../01-instalacja/konfiguracja.md). Ten sam mechanizm dokumentuje cały moduł: łańcuch na początku pliku trafia do atrybutu `__doc__` modułu; wrócimy do niego przy modułach. <!-- TODO: link po powstaniu rozdziału o modułach -->

## Adnotacje w sygnaturze

W podrozdziale [Konwersje i adnotacje typów](../03-nazwy-typy/konwersje-i-adnotacje.md) poznaliśmy adnotacje zmiennych. Parametry funkcji adnotujemy tak samo, zapisem `nazwa: typ`, a typ wartości zwracanej — strzałką `->` przed dwukropkiem kończącym nagłówek. Python **nie sprawdza** zgodności z adnotacjami w czasie wykonania:

```python title="adnotacje.py"
def kwadrat(x: int) -> int:
    return x * x


print(kwadrat(3))
print(kwadrat(2.5))
print(kwadrat("ab"))
```

```{ .text .no-copy }
9
6.25
Traceback (most recent call last):
  File "adnotacje.py", line 7, in <module>
    print(kwadrat("ab"))
          ~~~~~~~^^^^^^
  File "adnotacje.py", line 2, in kwadrat
    return x * x
           ~~^~~
TypeError: can't multiply sequence by non-int of type 'str'
```

Wywołanie z liczbą zmiennoprzecinkową zakończyło się poprawnie, a błąd przy łańcuchu zgłosiło dopiero mnożenie — nie adnotacja. Adnotacje są informacją dla czytelnika kodu oraz dla narzędzi: serwer językowy Pylance i program mypy (opisane w rozdziale 3) potrafią na ich podstawie ostrzec o niezgodności typów jeszcze przed uruchomieniem programu.

!!! info "Adnotacje w Pythonie 3.14"
    Od wersji 3.14 ([PEP 649](https://peps.python.org/pep-0649/) i
    [PEP 749](https://peps.python.org/pep-0749/)) adnotacje są domyślnie
    ewaluowane **leniwie**: interpreter nie oblicza wyrażeń adnotacji przy
    wykonywaniu instrukcji `def`, lecz zapamiętuje je i oblicza dopiero na
    żądanie — np. gdy o adnotacje zapyta narzędzie analizy typów. W adnotacji
    można więc użyć nazwy, która zostanie zdefiniowana później albo nie istnieje
    wcale. W starszych wersjach adnotacje były domyślnie obliczane natychmiast
    i taka definicja kończyła się wyjątkiem `NameError`. Sposoby odczytu
    adnotacji poznamy później, przy narzędziach analizy typów.
    <!-- TODO: link po powstaniu rozdziału o narzędziach analizy typów -->

Poniższy skrypt używa w adnotacjach nazwy, która nigdzie nie została zdefiniowana:

```python title="adnotacje-leniwe.py"
def powitanie(imie: Napis) -> Napis:
    return "Witaj, " + imie


print(powitanie("Anno"))
```

```{ .text .no-copy }
Witaj, Anno
```

Program działa, ponieważ wyrażenie adnotacji nie zostało obliczone — żadne narzędzie nie zażądało jego wartości.

!!! tip "Odstępy według PEP 8"
    Po dwukropku adnotacji stawiamy spację, a strzałkę `->` otaczamy spacjami:
    `def f(x: int) -> str:`.

## Funkcja jako obiekt

Zgodnie z modelem opisanym w rozdziale [3. Nazwy i typy](../03-nazwy-typy/obiekty-i-pamiec.md) nazwa funkcji jest referencją do obiektu — obiektu klasy `function`:

```{ .python .no-copy }
>>> def pole_prostokata(a, b):
...     return a * b
...
>>> type(pole_prostokata)
<class 'function'>
>>> pole_prostokata
<function pole_prostokata at 0x...>
>>> pole = pole_prostokata
>>> pole(2, 3)
6
>>> pole is pole_prostokata
True
>>> pole.__name__
'pole_prostokata'
```

Adres wypisany po `at` jest szczegółem implementacyjnym i u czytelnika będzie inny. Przypisanie `pole = pole_prostokata` nie kopiuje funkcji, lecz tworzy drugą nazwę tego samego obiektu. Atrybut `__name__` przechowuje nazwę nadaną w instrukcji `def`, niezależnie od tego, przez którą nazwę funkcję wywołujemy; podobnie atrybut `__doc__` przechowuje docstring.

!!! note "Nawiasy decydują"
    `pole_prostokata` to obiekt funkcji, a `pole_prostokata(2, 3)` to wynik jej
    wywołania. Próba użycia samego obiektu w działaniu arytmetycznym kończy się
    błędem `TypeError: unsupported operand type(s) for +: 'function' and 'int'`.
    Skoro funkcja jest obiektem, można ją przekazać innej funkcji jako argument
    albo zwrócić z funkcji — te możliwości rozwija strona Funkcje jako obiekty.
    <!-- TODO: link po powstaniu strony funkcje-jako-obiekty.md -->

Obiektami są także funkcje wbudowane, choć należą do innej klasy niż funkcje zdefiniowane instrukcją `def`:

```{ .python .no-copy }
>>> type(len)
<class 'builtin_function_or_method'>
>>> len.__name__
'len'
>>> abs.__doc__
'Return the absolute value of the argument.'
```

Nazwa klasy funkcji wbudowanych jest szczegółem implementacyjnym CPythona; istotne jest to, że i one mają atrybuty `__name__` oraz `__doc__`.

## Konwencje zapisu funkcji

Kod w tej książce stosuje się do kilku zasad zapisu funkcji, w większości pochodzących z [PEP 8](https://peps.python.org/pep-0008/) (por. sekcja o formatowaniu w podrozdziale [Konfigurowanie narzędzi](../01-instalacja/konfiguracja.md)):

- nazwy funkcji zapisujemy w `snake_case` i dobieramy tak, by mówiły, co funkcja robi (`pole_prostokata`, `min_max`);
- definicje funkcji na najwyższym poziomie pliku oddzielamy dwoma pustymi wierszami — stąd odstępy w przykładowych skryptach tego rozdziału;
- każda funkcja przeznaczona do użycia przez innych ma docstring;
- instrukcje `import` umieszczamy na początku pliku, nie w ciele funkcji;
- zasada ogólna, spoza PEP 8: jedna funkcja wykonuje jedno, dobrze nazwane zadanie — długą funkcję lepiej podzielić na kilka krótszych.
