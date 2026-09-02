# Wyrażenia warunkowe

## Wyrażenie if, elif, else {#wyrazenie-if-elif-else data-activity-section="true"}

Kluczową rolę grają odpowiednie wcięcia kodu. Wyrażenia if mogą być zagnieżdżone, ale odpowiednie głębokości wcięć muszą być zachowane.

```python title="warunki.py"
x = int(input("Wpisz liczbe calkowita: "))
if x < 0:
    x = 0
    print('Ujemna zmieniona na zero')
elif x == 0:
    print('Zero')
elif x == 1:
    print('Jeden')
else:
    print('Wiecej niz jeden')
```

Warunkiem może być dowolny obiekt oceniany w kontekście logicznym (katalog wartości fałszywych w rozdziale [3. Nazwy i typy](../03-nazwy-typy/typy-proste.md)). Wykorzystuje to idiomatyczny test pustości: zamiast `if len(data) == 0` piszemy po prostu `if not data`.

## Operator trójskładnikowy {#operator-trojskadnikowy data-activity-section="true"}

W wielu językach programowania istnieje operator trójargumentowy — jego idea polega na tym, że spełnienie warunku logicznego pociąga za sobą zwrócenie pierwszego obiektu, a niespełnienie — drugiego. Dokładnie to samo można osiągnąć za pomocą instrukcji if… elif, niemniej chodzi o elegancję i zwięzłość zapisu. W Pythonie rolę taką pełni składnia: `value_if_true if condition else value_if_false`. Badany warunek jest pośrodku, po lewej przed `if` jest wartość zwracana przy spełnieniu warunku, a po prawej za `else` — przy niespełnieniu. Prosty przykład:

```{ .python .no-copy }
>>> x = 10
>>> wynik = "duzo" if x > 5 else "malo"
>>> wynik
'duzo'
```

Możliwe jest zagnieżdżanie trójskładnikowych instrukcji warunkowych; trzeba przy tym uważać, żeby zapisana logika odpowiadała rzeczywiście naszym zamiarom. Przykład z podwójnie zagnieżdżonym warunkiem if:

```python title="zagniezdzenia.py"
a = False
b = True
if a:
    print("1")
else:
    if not b:
        print("2")
    else:
        print("3")   # ten warunek spełniony
```

Kod ten można zapisać skrótowo:

```{ .python .no-copy }
c = "1" if a else "2" if not b else "3"
print(c)
```

Inny przykład — z trzech liczb chcemy wskazać największą:

```python title="maks3.py"
a, b, c = 4, 5, 1
max_abc = a if a > b and a > c else b if b > c else c
print(max_abc)
```

## Operator przypisania w wyrażeniu := {#operator-przypisania-w-wyrazeniu data-activity-section="true"}

Operator `:=` (wprowadzony w rozdziale [3. Nazwy i typy](../03-nazwy-typy/operatory.md)) bywa użyteczny, ale łatwo o jego nadużycie. Nieczytelność kodu może być pogłębiona poprzez modyfikowanie obiektów, na których wyliczane są wartości logiczne — za pomocą `:=` można zmieniać „w locie” wartość, czyniąc całe wyrażenie mało przejrzystym i podatnym na błędy. Dodatkowo operator `:=` wymaga zastosowania nawiasów `( )` ze względu na priorytety operacji:

```{ .python .no-copy }
b = 1   # dla jakiej wartości b jakie a?
a = b if (b:=b-1) else (b:=-10)
print(a)
```

## Pola wyboru match {#pola-wyboru-match data-activity-section="true"}

W Python 3.10 została dodana struktura językowa dopasowania do pól wielokrotnego wyboru, która często funkcjonuje w innych językach pod nazwą switch… case. Jej ogólna składnia to:

```{ .text .no-copy }
match obiekt:
    case <wartosc1>:
        <akcja1>
    case <wartosc2>:
        <akcja2>
    case _:
        <akcja domyslna>
```

Przykład poniżej spowoduje wywołanie `print(3)`; gdyby nie było przypadku pasującego, weszlibyśmy do pola `_`. W miejscach <akcja> może być dowolny kod, może być instrukcja return, jeśli cały fragment jest częścią funkcji.

```python title="match1.py"
t = "raz"
match t:
    case "jeden":
        print(1)
    case "dwa":
        print(2)
    case "raz":
        print(3)
    case _:
        print("a jednak")
```

Wartości poszczególnych pól mogą być różnych typów:

```python title="match2.py"
t = 2   # również t = 3 zostanie zaliczone do przypadku 3.0
match t:
    case "jeden":
        print(1)
    case 2:
        print("dwa int")
    case 3.0:
        print("trzy float")
```

Wartości pól wyborów mogą być wielokrotne, połączone `|` (or):

```{ .python .no-copy }
    case "jeden" | 2:
        print(1, "lub dwa int")
```

Mogą tam wystąpić również typy złożone (rozdział [5. Typy złożone](../05-typy-zlozone/index.md)), nawet w połączeniu z symbolem `_` (traktowanym jako wieloznacznik, ang. *wildcard*). Omówienie innych ciekawych przypadków zawiera oficjalny samouczek: [PEP 636 — Structural Pattern Matching: Tutorial](https://peps.python.org/pep-0636/).

<div data-activity-slot="wyrazenia-warunkowe-activities"></div>
