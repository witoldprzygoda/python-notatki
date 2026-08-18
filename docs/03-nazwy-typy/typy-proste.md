# Typy proste

## Typ bool

Typ logiczny, posiada dwa stany `True` i `False` (zapisywane wielką literą). Wartość `True` odpowiada umownie liczbie 1, a `False` — liczbie 0. Co istotne, w kontekście logicznym oceniane są także obiekty innych typów: wszystko, co nie jest zerem, obiektem pustym lub `None`, jest traktowane jako prawda:

```{ .python .no-copy }
>>> logika = True
>>> if logika:
...     print("to jest prawda")
```

Pełny katalog wartości fałszywych (ang. *falsy*) obejmuje: `False`, `0`, `0.0`, `0j`, pusty łańcuch `''`, puste kolekcje `[]`, `()`, `{}`, `set()`, `frozenset()` (poznamy je w rozdziale [5. Typy złożone](../05-typy-zlozone/index.md)), pusty zakres `range(0)` oraz `None`. Wszystko inne jest prawdziwe (ang. *truthy*).

!!! info "Słowo kluczowe None"
    Słowo kluczowe `None` oznacza brak wartości. `None` to **nie** to samo co `0`,
    `False` lub pusty ciąg — jest wartością własnego, odrębnego typu (`NoneType`).
    Wartości `0`, `''` czy `[]` są fałszywe w kontekście logicznym, ale **nie są**
    `None`. Do sprawdzania braku wartości służy zapis `x is None` (opis w podrozdziale
    [Operatory](operatory.md)).

Choć Python pozwala na elastyczne podejście do operacji na obiektach, nie piszmy składni, która jest jakościowo fatalna i nieczytelna.

<!-- TODO: przykłady z PDF (zrzuty): „niepoważne” pomysły składniowe; kreatywne
     podejścia do zmiennych logicznych; warunek zwracający tekst dla None -->

Należy również wiedzieć, że język Python dla operatorów `or` lub `and` stosuje strategię „skróconego wyrażenia” (ang. *short-circuiting*), czyli „leniwej ewaluacji” (ang. *lazy evaluation*).

Operator `and` działa w ten sposób, że jeśli lewa strona jest fałszywa, to Python nie ocenia prawej strony, ponieważ wynik całego wyrażenia musi być fałszywy. Jeśli lewa strona jest prawdziwa, to Python musi sprawdzić prawą stronę, aby określić wartość wyrażenia. Operator `or` działa odwrotnie: jeśli lewa strona jest prawdziwa, prawa strona nie jest oceniana.

Istotna właściwość, o której często się zapomina: **`and` i `or` nie zwracają wartości `True`/`False` — zwracają jeden z operandów**:

```{ .python .no-copy }
>>> 1 and 2 and 3        # wszystkie prawdziwe → ostatni operand
3
>>> 1 and 0 and 3        # 0 jest fałszywe → krótka ścieżka, zwraca 0
0
>>> 0 or '' or 'hello'   # pierwszy prawdziwy operand
'hello'
>>> 0 or '' or []        # wszystkie fałszywe → ostatni operand
[]
```

Mechanizm ten pozwala optymalizować kod i unikać niepotrzebnych obliczeń (zwłaszcza gdy prawa strona jest kosztowna), a także zapisywać wartości domyślne, np. `name = input() or 'Anonim'`.

## Typ int

W Pythonie wartość liczby całkowitej nie jest ograniczona liczbą bajtów i może rozszerzać się do limitu dostępnej pamięci. Wszystkie typy całkowite w Pythonie 3 to po prostu `int`:

```{ .python .no-copy }
>>> import sys
>>> x = 100**10000+1     # ogromna liczba
>>> sys.getsizeof(x)     # rozmiar 8884
```

Czytelność długich literałów poprawia separator `_` (od Pythona 3.6), który interpreter po prostu ignoruje:

```{ .python .no-copy }
>>> x = 1_000_000
>>> x
1000000
```

Domyślną podstawą dla typu całkowitego jest podstawa dziesiętna. Z odpowiednimi przedrostkami możemy wyrazić liczbę w systemie dwójkowym (`0b`), ósemkowym (`0o`) bądź szesnastkowym (`0x`), otrzymując w konsoli wartość przeliczoną na system dziesiętny:

```{ .python .no-copy }
>>> 0b1010     # binarnie
10
>>> 0o17       # ósemkowo
15
>>> 0xFF       # szesnastkowo
255
```

Przeliczenie do tych systemów można również wykonać za pomocą wbudowanych funkcji `bin()`, `oct()` czy `hex()` — funkcje te dają na wyjściu typ `str`:

```{ .python .no-copy }
>>> bin(42)
'0b101010'
>>> oct(42)
'0o52'
>>> hex(42)
'0x2a'
```

Konwersję łańcucha znakowego na typ całkowity o określonej podstawie wykonuje funkcja `int()` wywołana z drugim argumentem `base` — pierwszym argumentem musi być wówczas łańcuch znakowy. Dopuszczalna podstawa to 0 lub 2–36; podstawa 0 oznacza interpretację ciągu dokładnie jako literału całkowitego:

```{ .python .no-copy }
>>> int('FF', 16)
255
>>> int('0b1010', 0)
10
```

## Typ float

Liczby zmiennoprzecinkowe są reprezentowane w sprzęcie komputerowym jako ułamki o podstawie 2 (binarne). Niestety, większość ułamków dziesiętnych nie może być reprezentowana dokładnie jako ułamki binarne. W konsekwencji liczby dziesiętne zmiennoprzecinkowe są przybliżane przez binarne liczby faktycznie przechowywane w maszynie.

Dla systemu dziesiętnego 1/3 jest przybliżane przez 0.333… Podobnie w systemie dwójkowym 1/10 to 0.00011001100110011… Na większości dzisiejszych maszyn ułamki zmiennoprzecinkowe są aproksymowane za pomocą ułamka binarnego, przy czym licznik wykorzystuje pierwsze 53 bity (zaczynając od najbardziej znaczącego), a mianownik jest potęgą dwójki. W przypadku 1/10 ułamek binarny to `3602879701896397 / 2**55` — zbliżony, ale nie do końca równy prawdziwej wartości 1/10. Co więcej, dwie różne liczby mogą mieć takie samo przybliżenie. Sprawdźmy:

```{ .python .no-copy }
>>> x = 0.1
>>> y = 0.10000000000000001
>>> x.as_integer_ratio()   # (3602879701896397, 36028797018963968)
>>> # mianownik to 2**55
>>> y.as_integer_ratio()   # (3602879701896397, 36028797018963968)
>>> format(x, '.50f')      # '0.10000000000000000555111512312578270211815834045410'
```

Z tego powodu:

```{ .python .no-copy }
>>> .1 + .1 + .1 == .3
False
```

Zaokrąglenie argumentów nie pomaga (nie poprawiamy reprezentacji składników):

```{ .python .no-copy }
>>> round(.1, 1) + round(.1, 1) + round(.1, 1) == round(.3, 1)
False
```

ale zaokrąglenie wyniku działania pomaga:

```{ .python .no-copy }
>>> round(.1 + .1 + .1, 10) == round(.3, 10)
True
```

!!! note "IEEE-754"
    Komputery 64-bitowe używają arytmetyki zmiennoprzecinkowej IEEE-754 w „podwójnej
    precyzji”: 1 bit na znak, 11 bitów na wykładnik i pozostałe 52 bity na mantysę.
    Ponieważ liczba znormalizowana ma zawsze postać 1.xxx…, wiodąca jedynka nie jest
    przechowywana (tzw. bit ukryty) — 52 bity zapisane jawnie dają więc 53 bity
    precyzji, wspomniane wyżej przy liczniku ułamka. Liczba to:
    `(-1)^znak * 2^wykładnik * mantysa`. Komputer stara się przekonwertować 0.1 na
    najbliższy ułamek, jaki może, w postaci `J/2**N`, gdzie J i N są liczbami
    całkowitymi.

Typ float reprezentuje również wartości specjalne standardu IEEE-754 — nieskończoności oraz „nie-liczbę” (ang. *not a number*):

```{ .python .no-copy }
>>> float('inf')           # nieskończoność
inf
>>> float('-inf')
-inf
>>> float('nan')           # NaN
nan
>>> import math
>>> math.isnan(float('nan'))
True
>>> math.isinf(float('inf'))
True
>>> float('inf') > 10**308     # większa od każdej liczby
True
```

Wartość `float('inf')` bywa przydatna jako wartość startowa przy wyszukiwaniu minimum — jest większa od każdej liczby, więc pierwsze porównanie zawsze ją zastąpi.

Sytuacja z typami float mogłaby się wydawać nieciekawa; na szczęście w Pythonie mamy moduły rozszerzające, które poprawnie radzą sobie z problemem operacji na wielkościach zmiennoprzecinkowych (moduł [decimal](https://docs.python.org/3/library/decimal.html)) oraz wielkościach, które można wyrazić w postaci liczb wymiernych (moduł [fractions](https://docs.python.org/3/library/fractions.html)). Krótka demonstracja — dokładna arytmetyka dziesiętna i ułamkowa rozwiązują problem zdiagnozowany powyżej:

```{ .python .no-copy }
>>> from decimal import Decimal
>>> Decimal('0.1') + Decimal('0.2')
Decimal('0.3')
>>> Decimal('0.1') + Decimal('0.2') == Decimal('0.3')
True

>>> from fractions import Fraction
>>> Fraction(1, 3) + Fraction(1, 6)
Fraction(1, 2)
>>> Fraction('0.1') * 3
Fraction(3, 10)
```

## Typ complex

Liczby zespolone reprezentowane przez część rzeczywistą i urojoną. Część urojoną oznacza przyrostek `j` (nie `i`, jak w matematyce):

```{ .python .no-copy }
>>> x = complex(2, 3)    # albo: x = 2 + 3j
>>> x.real               # 2.0 (typ float)
>>> x.imag               # 3.0
>>> x.conjugate()        # (2-3j) — sprzężenie
>>> abs(x)               # moduł: sqrt(4+9)
3.605551275463989
```

Typ complex znajduje zastosowanie w obliczeniach naukowych i inżynieryjnych. Odpowiedniki funkcji matematycznych dla liczb zespolonych zawiera moduł [cmath](https://docs.python.org/3/library/cmath.html), wspomniany już w rozdziale [2. Konsola](../02-konsola/konsola-w-praktyce.md).

## Typ str

Łańcuch znakowy (typ `str`) to dowolnej długości **niezmienny** ciąg znaków w `' '` lub `" "`; można w jego wnętrzu użyć `\` do zapisania znaków specjalnych. Zwróćmy uwagę na prezentację zawartości łańcucha, gdy jest on utworzony w konsoli, oraz gdy jest argumentem funkcji print:

```{ .python .no-copy }
>>> '"Isn\'t," they said.'
>>> print('"Isn\'t," they said.')
```

Zmienną typu str tworzymy poprzez przypisanie do niej łańcucha znakowego:

```{ .python .no-copy }
>>> s = 'First line.\nSecond line.'  # \n znak nowej linii
>>> s          # bez print(), \n jest zawarte w wyjściu
>>> print(s)   # gdy print(), \n wykonuje przejście do nowej linii
```

Surowy (ang. *raw*) string jest poprzedzony literą `r`:

```{ .python .no-copy }
>>> print('C:\some\name')    # tu \n oznacza nową linię
>>> print(r'C:\some\name')   # r powoduje brak interpretowania zawartości
```

!!! warning "Niepoprawne sekwencje ucieczki"
    Zapis `'C:\some\name'` zawiera sekwencję `\s`, która nie jest poprawną sekwencją
    ucieczki — Python 3.12 i nowsze zgłaszają dla niej ostrzeżenie `SyntaxWarning`,
    a w przyszłych wersjach będzie to błąd. To dodatkowy argument za stosowaniem
    surowych łańcuchów `r'…'` przy zapisie ścieżek systemu Windows.

Stringi rozciągnięte na wiele linii za pomocą `"""..."""` lub `'''...'''` można również wydrukować:

```{ .python .no-copy }
print("""\
Usage: thingy [OPTIONS]
     -h                        Display this usage message
     -H hostname               Hostname to connect to
""")
```

### F-stringi

Prefiks `f` tworzy **f-string** (ang. *formatted string literal*, od Pythona 3.6) — łańcuch, w którym wyrażenia ujęte w nawiasy klamrowe `{ }` są obliczane i wstawiane do tekstu:

```{ .python .no-copy }
>>> imie = "Anna"
>>> wiek = 22
>>> f"Czesc {imie}, masz {wiek} lat"
'Czesc Anna, masz 22 lat'
```

Po dwukropku można podać specyfikację formatu — liczbę miejsc po przecinku, szerokość pola, system liczbowy czy separator tysięcy:

```{ .python .no-copy }
>>> f"{3.14159:.2f}"     # dwa miejsca po przecinku
'3.14'
>>> f"{42:08b}"          # binarnie, 8 pozycji z zerami
'00101010'
>>> f"{1000000:_}"       # separator tysięcy
'1_000_000'
```

F-stringi są dziś podstawowym sposobem formatowania tekstu w Pythonie — będziemy z nich regularnie korzystać. Pełny opis mini-języka formatowania zawiera dokumentacja: [docs.python.org/3/library/string.html#formatspec](https://docs.python.org/3/library/string.html#formatspec).

### Operacje na łańcuchach

Stringi można łączyć operatorem `+` oraz powielać operatorem `*`. Łączenie literałów można wykonać również bez operatora `+`:

```{ .python .no-copy }
>>> "A"*3 + 'bbb'          # 'AAAbbb'
>>> tekst = "oto" 'przyklad'
```

Indeksowanie łańcucha znakowego to nie tylko zakres od 0 do n−1 (gdzie n to długość łańcucha), ale również ujemne indeksy, jak na przykładzie poniżej:

```{ .text .no-copy }
 +---+---+---+---+---+---+
 | A | b | C | d | E | f |
 +---+---+---+---+---+---+
   0   1   2   3   4   5
  -6  -5  -4  -3  -2  -1
```

Odwołanie się do indeksu spoza zakresu jest błędem (`IndexError: string index out of range`). Indeksowanie może się odbywać również na zasadzie podania zakresu oraz kroku (co ile pozycji) — jest to bardzo wydajny sposób na selekcję wybranych części łańcucha (ang. *slicing*). Na wyciętym fragmencie można stosować wszystko to, co na łańcuchu znakowym. Zasady selekcji (załóżmy, że `tekst` jest zmienną typu str):

```{ .text .no-copy }
tekst[od:]       # wycinek od pozycji o indeksie od — do końca
tekst[:do]       # wycinek od początku do indeksu do (bez niego)
tekst[od:do]     # wycinek od indeksu od do indeksu do (wyłączając)
tekst[:]         # cały łańcuch tekst
tekst[::krok]    # co który (krok) znak; krok ujemny — od tyłu
```

Przykład (warto się przyjrzeć i poeksperymentować):

```{ .python .no-copy }
>>> tekst = "AbCdEfGhIjKlMn"   # indeksy od 0 do 13, od -14 do -1
>>> tekst[3:]          # 'dEfGhIjKlMn'
>>> tekst[:6]          # 'AbCdEf'
>>> tekst[4:8]         # 'EfGh'
>>> tekst[::2]         # 'ACEGIKM'
>>> tekst[::-1]        # 'nMlKjIhGfEdCbA'
>>> tekst[::-2]        # 'nljhfdb'
>>> tekst[-4:-1]       # 'KlM'
>>> tekst[2:-7]        # 'CdEfG'
>>> tekst[-10:-1:2]    # 'EGIKM'
>>> tekst[10:1:-2]     # 'KIGEC'
>>> tekst[-3:-11:-2]   # 'ljhf'
>>> tekst[0:10][2:4]   # 'Cd'
```

Ta sama składnia wycinków działa na wszystkich sekwencjach — wrócimy do niej przy [listach](../05-typy-zlozone/lista.md) i krotkach (rozdział 5), gdzie wycinek listy można także podstawiać i usuwać.

### Metody typu str

Długość obiektu (liczbę elementów w kolekcji) zwraca funkcja `len()` — dla pustego łańcucha wynosi 0. Typ str udostępnia ponadto szereg metod, które **nie zmieniają oryginalnego obiektu** — string jest niemutowalny, więc każda metoda zwraca nowy łańcuch (lub inną wartość). Kilka wybranych przykładów do sprawdzenia:

```{ .python .no-copy }
>>> x = " abcd ab efgh ab "
>>> x.upper()              # ' ABCD AB EFGH AB '
>>> x.lower()              # ' abcd ab efgh ab '
>>> x.strip()              # 'abcd ab efgh ab' — usuwa białe znaki z krańców
>>> x.replace("ab", "AA")  # ' AAcd AA efgh AA ' — wszystkie wystąpienia
>>> x.split(" ")           # ['', 'abcd', 'ab', 'efgh', 'ab', ''] — rozbicie po separatorze
>>> x.count("ab")          # 3 — liczba wystąpień
>>> x.startswith(" a")     # True
>>> x.find("AA")           # -1 — pierwsze wystąpienie; brak → -1
>>> x.index("AA")          # to samo co find, ale brak → wyjątek ValueError
>>> "-".join(["a", "b", "c"])   # 'a-b-c' — łączenie elementów separatorem
```

Zwróćmy uwagę, że `x.find("AA")` zwraca −1, mimo iż linijkę wyżej wykonaliśmy `replace` — metody zwracają **kopie**, oryginalny `x` pozostał niezmieniony. Warto też zauważyć puste łańcuchy w wyniku `split(" ")` — pochodzą ze spacji na krańcach; praktyczny idiom to `x.strip().split()`. Metodę `join()` — działającą na dowolnym obiekcie iterowalnym — zobaczymy w akcji w rozdziale [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md). Pełny katalog metod: [docs.python.org/3/library/stdtypes.html#string-methods](https://docs.python.org/3/library/stdtypes.html#string-methods).

### Unicode: ord i chr

W Pythonie nie ma typu reprezentującego pojedynczy znak — nawet jeden znak w cudzysłowie to typ `str`. Kod danego znaku w standardzie Unicode można pozyskać za pomocą funkcji `ord()`, zaś odczytać znak za pomocą funkcji `chr()` — zakres argumentów jest od 0 do 1114111. Na przykład `ord('a')` to 97, a `chr(9760)` — równoważnie `chr(0x2620)`, bo znak ma kod U+2620 — to znaczek czaszki ☠ (czy się wyświetli, zależy od zastosowanego fontu).
