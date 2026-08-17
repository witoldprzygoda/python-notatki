# Typy proste

## Typ bool

Typ logiczny, posiada dwa stany `True` i `False` (zapisywane wielką literą). Wartość `True` odpowiada umownie liczbie 1, a `False` — liczbie 0. Co istotne, w kontekście logicznym oceniane są także obiekty innych typów: wszystko, co nie jest zerem, obiektem pustym lub `None`, jest traktowane jako prawda:

```{ .python .no-copy }
>>> logika = True
>>> if logika:
...     print("to jest prawda")
```

!!! info "Słowo kluczowe None"
    Słowo kluczowe `None` oznacza brak wartości. `None` to **nie** to samo co `0`,
    `False` lub pusty ciąg — jest wartością własnego, odrębnego typu (`NoneType`).

Choć Python pozwala na elastyczne podejście do operacji na obiektach, nie piszmy składni, która jest jakościowo fatalna i nieczytelna.

<!-- TODO: przykłady z PDF (zrzuty): „niepoważne” pomysły składniowe; kreatywne
     podejścia do zmiennych logicznych; warunek zwracający tekst dla None -->

Należy również wiedzieć, że język Python dla operatorów `or` lub `and` stosuje strategię „skróconego wyrażenia” (ang. *short-circuiting*), czyli „leniwej ewaluacji” (ang. *lazy evaluation*).

Operator `and` działa w ten sposób, że jeśli lewa strona jest `False`, to Python nie ocenia prawej strony, ponieważ wynik całego wyrażenia musi być `False`. Jeśli lewa strona jest `True`, to Python musi sprawdzić prawą stronę, aby określić wartość wyrażenia. Zatem:

- `True and True` → zwraca wynik ostatniej operacji, czyli prawej strony.
- `False and X` → zawsze zwraca `False`, bez potrzeby sprawdzania X.

Operator `or` działa w ten sposób, że jeśli lewa strona jest `True`, to Python nie ocenia prawej strony, ponieważ wynik całego wyrażenia musi być `True`. W przypadku, gdy lewa strona jest `False`, Python musi sprawdzić prawą stronę. Zatem:

- `True or X` → zwraca wynik lewej strony.
- `False or X` → musi sprawdzić X.

Dzięki temu mechanizmowi można optymalizować kod i unikać niepotrzebnych obliczeń, co jest szczególnie przydatne, gdy obliczenia na prawej stronie są kosztowne.

## Typ int

W Pythonie wartość liczby całkowitej nie jest ograniczona liczbą bajtów i może rozszerzać się do limitu dostępnej pamięci. Wszystkie typy całkowite w Python3 to po prostu `int`:

```{ .python .no-copy }
>>> import sys
>>> x = 100**10000+1     # ogromna liczba
>>> sys.getsizeof(x)     # rozmiar 8884
```

Domyślną podstawą dla typu całkowitego jest podstawa dziesiętna. Z odpowiednimi przedrostkami możemy wyrazić liczbę w systemie dwójkowym, ósemkowym bądź szesnastkowym, otrzymując w konsoli wartość przeliczoną na system dziesiętny.

<!-- TODO: przykład z PDF (zrzut): 0b..., 0o..., 0x... -->

Przeliczenie do tych systemów można również wykonać za pomocą wbudowanych funkcji, takich jak `bin()`, `oct()` czy `hex()` — funkcje te dają na wyjściu typ `str`. Konwersję łańcucha znakowego na typ całkowity o określonej bazie można wykonać operatorem `int(x=0, base=10)`, gdzie `x` to wartość lub łańcuch znakowy do konwersji na podstawę `base` (0, 2–36); baza 0 oznacza interpretację ciągu dokładnie jako literał całkowity.

## Typ float

Liczby zmiennoprzecinkowe są reprezentowane w sprzęcie komputerowym jako ułamki o podstawie 2 (binarne). Niestety, większość ułamków dziesiętnych nie może być reprezentowana dokładnie jako ułamki binarne. W konsekwencji liczby dziesiętne zmiennoprzecinkowe są przybliżane przez binarne liczby faktycznie przechowywane w maszynie.

Dla systemu dziesiętnego 1/3 jest przybliżane przez 0.333… Podobnie w systemie dwójkowym 1/10 to 0.00011001100110011… Na większości dzisiejszych maszyn ułamki zmiennoprzecinkowe są aproksymowane za pomocą ułamka binarnego, przy czym licznik wykorzystuje pierwsze 53 bity (zaczynając od najbardziej znaczącego), a mianownik jest potęgą dwójki. W przypadku 1/10 ułamek binarny to `3602879701896397 / 2**55` — zbliżony, ale nie do końca równy prawdziwej wartości 1/10. Co więcej, dwie różne liczby mogą mieć takie samo przybliżenie. Sprawdźmy:

```{ .python .no-copy }
>>> x = 0.1
>>> y = 0.10000000000000001
>>> x.as_integer_ratio()   # (3602879701896397, 36028797018963968)
>>> # mianownik to 2**55
>>> y.as_integer_ratio()   # (3602879701896397, 36028797018963968)
>>> format(x, '.50f')      # '0.1000000000000000055511151231257827021181583404541'
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
    Liczba to: `(-1)^znak * 2^wykładnik * mantysa`. Komputer stara się przekonwertować
    0.1 na najbliższy ułamek, jaki może, w postaci `J/2**N`, gdzie J i N są liczbami
    całkowitymi.

Sytuacja z typami float mogłaby się wydawać nieciekawa; na szczęście w Pythonie mamy moduły rozszerzające, które poprawnie radzą sobie z problemem operacji na wielkościach zmiennoprzecinkowych (moduł [decimal](https://docs.python.org/3/library/decimal.html)) oraz wielkościach, które można wyrazić w postaci liczb wymiernych (moduł [fractions](https://docs.python.org/3/library/fractions.html)).

## Typ complex

Liczby zespolone reprezentowane przez część rzeczywistą i urojoną:

```{ .python .no-copy }
>>> x = conjugate(2,3)   # albo: x = 2 + 3j
>>> x.real               # 2
>>> x.imag               # 3
>>> x.conjugate()        # sprzężenie liczby zespolonej
```

<!-- TODO-AKTUALIZACJA: w pierwszej linii zapewne miało być complex(2,3),
     nie conjugate(2,3) — do weryfikacji w źródle -->

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

Surowy (*raw*) string jest poprzedzony literą `r`:

```{ .python .no-copy }
>>> print('C:\some\name')    # tu \n oznacza nową linię
>>> print(r'C:\some\name')   # r powoduje brak interpretowania zawartości
```

Stringi rozciągnięte na wiele linii za pomocą `"""..."""` lub `'''...'''` można również wydrukować:

```{ .python .no-copy }
print("""\
Usage: thingy [OPTIONS]
     -h                        Display this usage message
     -H hostname               Hostname to connect to
""")
```

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

Odwołanie się do indeksu spoza zakresu jest błędem (`IndexError: string index out of range`). Indeksowanie może się odbywać również na zasadzie podania zakresu oraz kroku (co ile pozycji) — jest to bardzo wydajny sposób na selekcję wybranych części łańcucha (*slicing*). Na wyciętym fragmencie można stosować wszystko to, co na łańcuchu znakowym.

<!-- TODO: przykłady z PDF (zrzuty): slicing na stringach -->

Nawet jeden znak w cudzysłowie to jest typ `str`. Kod danego znaku w standardzie Unicode można pozyskać za pomocą funkcji `ord()`, zaś odczytać znak za pomocą funkcji `chr()` — zakres argumentów jest od 0 do 1114111. Na przykład `ord('a')` to 97, a `chr(2620)` to znaczek czaszki ☠ (czy się wyświetli, zależy od zastosowanego fontu).

Obszerne informacje o typie str oraz możliwościach jego formatowania — [docs.python.org/3/library/string.html](https://docs.python.org/3/library/string.html) — omówimy przy innej okazji.
