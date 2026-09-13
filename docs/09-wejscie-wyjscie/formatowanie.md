# Formatowanie tekstu

F-stringi znamy od podrozdziału [Typy proste](../03-nazwy-typy/typy-proste.md#f-stringi): wyrażenie w nawiasach klamrowych trafia do tekstu, a po dwukropku można podać liczbę miejsc po przecinku czy szerokość pola. Korzystaliśmy z nich w każdym rozdziale, ale zawsze w podstawowym zakresie. Ten podrozdział uzupełnia wiedzę o pełny **mini-język specyfikacji formatu** (ang. *format specification mini-language*) — wspólny dla f-stringów, funkcji `format()` i metody `str.format()` — oraz o dwa mechanizmy, które spotkamy w cudzym kodzie i w bibliotece standardowej: operator `%`, używany przez moduł `logging` z rozdziału 8, i metodę `str.format()`. Na koniec, dla dociekliwych, t-stringi i moduł `pprint`.

## F-stringi — wyrażenia, konwersje i pola zagnieżdżone

Pole f-stringa ma trzy części: wyrażenie, opcjonalną **konwersję** po wykrzykniku i opcjonalną **specyfikację formatu** (ang. *format specification*) po dwukropku — `{wyrażenie!konwersja:specyfikacja}`. Wyrażeniem może być dowolne wyrażenie Pythona, także wywołanie funkcji albo wyrażenie warunkowe. Konwersja `!r` wstawia `repr()` zamiast `str()` (znana z rozdziału 8), `!s` wymusza `str()`, a `!a` — `ascii()`, czyli `repr()` z zapisem znaków spoza ASCII sekwencjami ucieczki. Znak `=` po wyrażeniu wstawia jego tekst wraz ze znakiem równości i wartością, co przydaje się przy diagnostyce; specyfikacja formatu może być sama zapisana w polu zagnieżdżonym, dzięki czemu szerokość albo precyzję ustala się w czasie działania programu:

```python title="pola.py"
imie = "Ala"
wiek = 30
cena = 19.99
szerokosc = 10

print(f"{imie} ma {wiek} lat")
print(f"{imie!r} ma {wiek!s} lat, {'ż'!a}")
print(f"{wiek=}, {cena=:.1f}")
print(f"{wiek = }")
print(f"[{imie:>{szerokosc}}]")
print(f"{len(imie)} {'pełnoletnia' if wiek >= 18 else 'niepełnoletnia'}")
```

```{ .text .no-copy }
Ala ma 30 lat
'Ala' ma 30 lat, '\u017c'
wiek=30, cena=20.0
wiek = 30
[       Ala]
3 pełnoletnia
```

Zapis `{wiek=}` daje `wiek=30` — po znaku równości wartość jest wstawiana jak przez `repr()`, chyba że podamy własną specyfikację, jak w `{cena=:.1f}`; spacje wokół `=` są zachowywane. Pole zagnieżdżone `{szerokosc}` wewnątrz specyfikacji `>{szerokosc}` zostało zastąpione wartością `10`, zanim specyfikacja została odczytana. Wewnątrz pola nie można użyć znaku `\` w Pythonie starszym niż 3.12; od wersji 3.12 f-stringi dopuszczają w polach dowolne wyrażenia, także z cudzysłowami tego samego rodzaju, co cudzysłowy całego łańcucha.

## Mini-język specyfikacji formatu

Specyfikacja formatu jest łańcuchem o ustalonej budowie; każdy element jest opcjonalny, ale kolejność jest stała:

```{ .text .no-copy }
[[wypełnienie]wyrównanie][znak][z][#][0][szerokość][grupowanie][.precyzja][typ]
```

Kolejne sekcje omawiają te elementy grupami; pełny opis, wraz z gramatyką, zawiera dokumentacja w sekcji *Format Specification Mini-Language* ([docs.python.org/3/library/string.html#formatspec](https://docs.python.org/3/library/string.html#formatspec)).

### Szerokość, wypełnienie i wyrównanie

**Szerokość** to minimalna liczba znaków pola — krótsza wartość jest dopełniana, dłuższa nie jest obcinana. **Wyrównanie** określa, po której stronie stoi dopełnienie: `<` do lewej (domyślne dla tekstu), `>` do prawej (domyślne dla liczb), `^` do środka, a `=` — tylko dla liczb — wstawia dopełnienie między znak a cyfry. Znak **wypełnienia** podaje się bezpośrednio przed wyrównaniem; domyślnie jest nim spacja. Dla liczb zero przed szerokością jest skrótem dla wypełnienia `0` z wyrównaniem `=`. **Precyzja** po kropce ma dla tekstu inne znaczenie niż dla liczb: obcina łańcuch do podanej liczby znaków:

```python title="wyrownanie.py"
print(f"[{'ab':6}]|[{'ab':>6}]|[{'ab':^6}]|[{'ab':*^6}]")
print(f"[{42:6}]|[{42:<6}]|[{42:06}]|[{42:=+6}]|[{-42:=+6}]")
print(f"[{'abcdef':.3}]|[{'abcdef':8.3}]")
```

```{ .text .no-copy }
[ab    ]|[    ab]|[  ab  ]|[**ab**]
[    42]|[42    ]|[000042]|[+   42]|[-   42]
[abc]|[abc     ]
```

### Liczby — znak, separatory, precyzja i systemy

Element **znak** steruje wypisywaniem znaku liczby: `+` wypisuje znak zawsze, `-` (domyślnie) tylko dla liczb ujemnych, a spacja wstawia spację przed liczbą dodatnią, dzięki czemu kolumny dodatnich i ujemnych wartości są wyrównane. **Grupowanie** wstawia separator tysięcy: `,` albo `_` (dla typów `b`, `o` i `x` podkreślenie grupuje co cztery cyfry); od Pythona 3.14 separator można podać także po precyzji, dla części ułamkowej. Litera `z` (od Pythona 3.11) zamienia ujemne zero, jakie może powstać z zaokrąglenia, na zwykłe zero. **Precyzja** dla liczb zmiennoprzecinkowych to liczba cyfr po przecinku (typ `f`) albo liczba cyfr znaczących (typ `g`). Znak `#` wymusza postać alternatywną — dla systemów liczbowych przedrostek `0b`, `0o`, `0x`:

```python title="liczby.py"
x = 1234567.891

print(f"{x:,.2f}|{x:_.1f}|{3.14159265:.,}")
print(f"{42:+d}|{42: d}|{-42: d}")
print(f"{255:b}|{255:o}|{255:x}|{255:X}|{255:#x}|{255:08b}")
print(f"{x:e}|{x:.3e}|{x:g}|{0.000123:g}")
print(f"{0.256:.1%}|{2 / 3:.3f}|{1e6:,.0f}")
```

```{ .text .no-copy }
1,234,567.89|1_234_567.9|3.141,592,65
+42| 42|-42
11111111|377|ff|FF|0xff|11111111
1.234568e+06|1.235e+06|1.23457e+06|0.000123
25.6%|0.667|1,000,000
```

Zapis `{0.256:.1%}` mnoży wartość przez 100 i dopisuje znak procentu, a `{1e6:,.0f}` wypisuje liczbę zmiennoprzecinkową bez części ułamkowej i z separatorem tysięcy — to typowy sposób prezentacji kwot. Typ `g` wybiera sam między zapisem stałym a wykładniczym, w zależności od wielkości liczby, i usuwa końcowe zera. Specyfikacja bez typu działa dla `float` podobnie, z dwiema różnicami: bez podanej precyzji wypisuje tyle cyfr, ile potrzeba do wiernego odtworzenia liczby (jak `repr()`), i zawsze zostawia co najmniej jedną cyfrę po przecinku. Zapis `.,` bez liczby po kropce oznacza grupowanie części ułamkowej co trzy cyfry bez zmiany precyzji.

### Typy prezentacji

Ostatni element specyfikacji, **typ prezentacji** (ang. *presentation type*), określa, jak wartość ma być zapisana. Najczęściej używane zbiera tabela:

| Typ | Dla | Znaczenie |
|---|---|---|
| `s` | tekst | łańcuch (domyślny dla `str`, można pominąć) |
| `d` | `int` | zapis dziesiętny (domyślny dla `int`) |
| `b`, `o`, `x`, `X` | `int` | zapis dwójkowy, ósemkowy, szesnastkowy małymi/wielkimi literami |
| `c` | `int` | znak o podanym kodzie Unicode |
| `f`, `F` | `float` | zapis stały, precyzja = cyfry po przecinku (domyślnie 6) |
| `e`, `E` | `float` | zapis wykładniczy |
| `g`, `G` | `float` | zapis ogólny — stały albo wykładniczy, precyzja = cyfry znaczące |
| `%` | `float` | procent: wartość razy 100 z typem `f` i znakiem `%` |
| brak | dowolny | jak `s` dla tekstu, `d` dla `int`; dla `float` jak `g`, lecz bez precyzji wypisuje wszystkie potrzebne cyfry i zawsze co najmniej jedną po przecinku |

Liczbę całkowitą można sformatować typem zmiennoprzecinkowym (`f"{42:.2f}"` daje `42.00`), ale nie odwrotnie: `f"{3.5:d}"` zgłasza `ValueError`. Precyzja nie jest dozwolona dla typów całkowitych.

## Wypisywanie tabel

Połączenie szerokości, wyrównania i precyzji pozwala wypisać dane tabelarycznie bez żadnych dodatkowych narzędzi. Tekst wyrównujemy do lewej, liczby do prawej, a każdą kolumnę opisuje jedna specyfikacja użyta zarówno w nagłówku, jak i w wierszach:

```python title="tabela.py"
produkty = [("chleb", 4.5, 2), ("masło", 8.99, 1), ("ser żółty", 32.0, 0.25)]

print(f"{'Produkt':<12}{'Cena':>8}{'Ilość':>8}{'Wartość':>10}")
print("-" * 38)
suma = 0
for nazwa, cena, ilosc in produkty:
    wartosc = cena * ilosc
    suma += wartosc
    print(f"{nazwa:<12}{cena:>8.2f}{ilosc:>8}{wartosc:>10.2f}")
print("-" * 38)
print(f"{'Razem':<28}{suma:>10.2f}")
```

```{ .text .no-copy }
Produkt         Cena   Ilość   Wartość
--------------------------------------
chleb           4.50       2      9.00
masło           8.99       1      8.99
ser żółty      32.00    0.25      8.00
--------------------------------------
Razem                            25.99
```

Kolumna `Ilość` nie ma typu prezentacji, więc `2` i `0.25` są wypisane w postaci naturalnej dla swojego typu, a wyrównanie do prawej ustawia je pod sobą. Szerokości najlepiej przechowywać w nazwach albo obliczać z danych — `max(len(nazwa) for nazwa, _, _ in produkty)` — i wstawiać polami zagnieżdżonymi, jak w pierwszej sekcji. Tabele z danych wczytanych z pliku wrócą w ostatnim podrozdziale rozdziału.

## Funkcja `format()` i metoda `str.format()`

F-string jest wygodnym zapisem dla operacji, którą wykonuje funkcja wbudowana `format(wartość, specyfikacja)` — to samo, co interpreter wykonuje dla każdego pola. Można z niej korzystać wprost, gdy specyfikacja jest wartością obliczaną w programie. Metoda `str.format()` jest natomiast starszą postacią f-stringa: pola `{}` w szablonie są wypełniane argumentami wywołania — pozycyjnie, według indeksów albo według nazw — a specyfikacje formatu są te same:

```python title="format-metoda.py"
x = 1234567.891

print(format(x, ",.2f"))
print(format("ab", "*^6"))
print("{} ma {} lat".format("Ala", 30))
print("{1} i {0}".format("a", "b"))
print("{imie:>6}|{cena:.2f}".format(imie="Ala", cena=19.99))

szablon = "{nazwa:<10}{wartosc:>8.2f}"
for nazwa, wartosc in [("a", 1), ("bb", 22.5)]:
    print(szablon.format(nazwa=nazwa, wartosc=wartosc))
```

```{ .text .no-copy }
1,234,567.89
**ab**
Ala ma 30 lat
b i a
   Ala|19.99
a             1.00
bb           22.50
```

Metoda `str.format()` ma jedną przewagę nad f-stringiem: szablon jest zwykłym łańcuchem, który można zapisać w nazwie, wczytać z pliku albo przekazać do funkcji i wypełnić wielokrotnie, jak `szablon` w przykładzie. Gdy wartości są znane w miejscu zapisu, f-string jest krótszy i czytelniejszy, i to on jest podstawową formą w tej książce.

## Operator `%`

Najstarszym mechanizmem formatowania w Pythonie jest operator `%` z łańcuchem po lewej stronie i wartością albo krotką wartości po prawej. Wieloznaczniki w łańcuchu — `%s`, `%d`, `%f`, `%r`, `%x` — odpowiadają typom prezentacji, a między znakiem `%` a literą można podać szerokość i precyzję; `%%` wypisuje sam znak procentu. Ten mechanizm poznaliśmy pośrednio w podrozdziale [Logowanie zamiast print](../08-wyjatki/logging.md#formatowanie-komunikatow): moduł `logging` formatuje komunikaty właśnie tak, z argumentami przekazanymi osobno:

```python title="operator-procent.py"
print("%s ma %d lat" % ("Ala", 30))
print("%5.2f|%-6s|%x|%%" % (3.14159, "ab", 255))
print("%(imie)s: %(ocena).1f" % {"imie": "Ala", "ocena": 4.75})
print("%r" % "Ala")
```

```{ .text .no-copy }
Ala ma 30 lat
 3.14|ab    |ff|%
Ala: 4.8
'Ala'
```

Pojedynczą wartość podajemy bez krotki, kilka — w krotce, a przy wieloznacznikach z nazwą w nawiasach — w słowniku. Operatora `%` nie stosujemy w nowym kodzie do formatowania tekstu (f-string robi to samo czytelniej), ale trzeba go rozumieć: spotkamy go w starszym kodzie, w dokumentacji i w komunikatach `logging`, gdzie jest formą właściwą, bo formatowanie następuje dopiero po sprawdzeniu progu.

## Szablony t-string i moduł `pprint` (dla dociekliwych)

F-string łączy tekst od razu. Od Pythona 3.14 literał z przedrostkiem `t` — **t-string** (ang. *template string*) — zwraca zamiast gotowego tekstu obiekt `Template` z modułu `string.templatelib`, który przechowuje osobno fragmenty stałe i wstawiane wartości wraz z ich specyfikacjami. Program może je przetworzyć przed połączeniem — na przykład ująć każdą wartość w nawiasy, zabezpieczyć ją przed wstawieniem do kodu HTML albo zapytania do bazy danych:

```python title="szablon.py"
from string.templatelib import Interpolation

imie = "Ala"
wiek = 30
szablon = t"{imie} ma {wiek:>4} lat"

print(type(szablon).__name__)
print(szablon.strings)
print(szablon.values)
for czesc in szablon:
    if isinstance(czesc, Interpolation):
        print(czesc.expression, "->", czesc.value, "| specyfikacja:", repr(czesc.format_spec))
    else:
        print(repr(czesc))


def w_nawiasach(szablon):
    """Zwraca tekst szablonu z każdą wstawioną wartością w nawiasach kwadratowych."""
    czesci = []
    for czesc in szablon:
        if isinstance(czesc, Interpolation):
            czesci.append(f"[{format(czesc.value, czesc.format_spec)}]")
        else:
            czesci.append(czesc)
    return "".join(czesci)


print(w_nawiasach(szablon))
```

```{ .text .no-copy }
Template
('', ' ma ', ' lat')
('Ala', 30)
imie -> Ala | specyfikacja: ''
' ma '
wiek -> 30 | specyfikacja: '>4'
' lat'
[Ala] ma [  30] lat
```

Atrybut `strings` zawiera fragmenty stałe (zawsze o jeden więcej niż wartości — tu pierwszy jest pusty, bo szablon zaczyna się od pola), `values` — wstawione wartości, a iteracja po szablonie daje na przemian fragmenty i obiekty `Interpolation` z wyrażeniem, wartością, konwersją (`conversion`, tu `None`) i specyfikacją formatu; puste fragmenty są w iteracji pomijane. Funkcja `w_nawiasach()` składa tekst sama, wywołując `format()` ze specyfikacją z pola. W codziennym formatowaniu t-stringi nie są potrzebne; ich miejsce to biblioteki, które muszą przetworzyć wartości, zanim trafią do tekstu.

Drugie narzędzie, moduł `pprint` (ang. *pretty print*), wypisuje zagnieżdżone struktury danych w czytelnym układzie — z podziałem na wiersze i wcięciami — gdy `print()` daje jeden długi wiersz:

```python title="pprint-demo.py"
from pprint import pprint

dane = {
    "imie": "Ala",
    "oceny": [4.5, 5.0, 3.5, 4.0],
    "adres": {"miasto": "Kraków", "kod": "30-001"},
}
print(dane)
pprint(dane, width=40)
```

```{ .text .no-copy }
{'imie': 'Ala', 'oceny': [4.5, 5.0, 3.5, 4.0], 'adres': {'miasto': 'Kraków', 'kod': '30-001'}}
{'adres': {'kod': '30-001',
           'miasto': 'Kraków'},
 'imie': 'Ala',
 'oceny': [4.5, 5.0, 3.5, 4.0]}
```

Funkcja `pprint()` domyślnie sortuje klucze słowników (argument `sort_dicts=False` to wyłącza) i łamie wiersze, gdy struktura nie mieści się w szerokości podanej argumentem `width` (domyślnie 80 znaków). Przydaje się przy oglądaniu danych wczytanych z plików JSON, do których wracamy w ostatnim podrozdziale; wcześniej zajmiemy się tym, dokąd sformatowany tekst trafia — funkcją `print()` i strumieniami.
