# Złożenia

Złożenia (ang. *comprehensions*) poznawaliśmy w tym rozdziale przy okazji kolejnych typów — [listowe](lista.md), [słownikowe](slownik.md) i [zbiorowe](zbiory.md). Niniejszy podrozdział zestawia wszystkie formy w jednym miejscu i wprowadza formę czwartą: wyrażenie generatorowe.

## Cztery formy złożeń

Rodzaj nawiasów decyduje o typie wyniku:

```{ .python .no-copy }
>>> [x**2 for x in range(5)]          # nawiasy prostokątne → list
[0, 1, 4, 9, 16]
>>> {x: x**2 for x in range(5)}       # klamrowe z dwukropkiem → dict
{0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
>>> {x % 3 for x in range(5)}         # klamrowe bez dwukropka → set
{0, 1, 2}
>>> (x**2 for x in range(5))          # okrągłe → generator
<generator object <genexpr> at 0x...>
```

Każda z form dopuszcza warunek `if` (selekcję elementów) oraz zagnieżdżone pętle `for` — składnia jest wspólna, zmienia się tylko sposób gromadzenia wyników.

## Wyrażenie generatorowe

Złożenie zapisane w nawiasach **okrągłych** to wyrażenie generatorowe (ang. *generator expression*) — tworzy zapowiedziany w rozdziale [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md) **generator**: jednorazowy iterator obliczający elementy leniwie, na żądanie, bez budowania całej kolekcji w pamięci:

```{ .python .no-copy }
>>> g = (x**2 for x in range(5))   # wyrażenie generatorowe
>>> g
<generator object <genexpr> at 0x...>
>>> list(g)
[0, 1, 4, 9, 16]
>>> list(g)      # generator to iterator — jednorazowy!
[]
```

Generator dziedziczy wszystkie własności iteratora: obsługuje `next()`, nie zna swojej długości, nie pozwala na indeksowanie, a przejście po nim jest jednorazowe. Jego siłą jest oszczędność pamięci — elementy powstają pojedynczo, dokładnie wtedy, gdy są potrzebne. Dlatego wyrażenie generatorowe często podaje się wprost funkcji przetwarzającej elementy, bez tworzenia listy pośredniej (nawiasy funkcji wystarczają za nawiasy wyrażenia):

```{ .python .no-copy }
>>> sum(x**2 for x in range(5))    # bez budowania listy w pamięci
30
>>> max(len(s) for s in ["kot", "krokodyl", "ryba"])
8
```

Drugim sposobem tworzenia generatorów są [funkcje generatorowe](../06-funkcje/funkcje-generatorowe.md) ze słowem kluczowym `yield`; funkcje `map()` i `filter()` omawiamy w podrozdziale [Funkcje jako obiekty](../06-funkcje/funkcje-jako-obiekty.md).

## Przykłady praktyczne

Kilka idiomów łączących złożenia z poznanymi typami:

```{ .python .no-copy }
>>> oceny = {"Ala": 5, "Bartek": 2, "Celina": 4}
>>> {v: k for k, v in oceny.items()}      # odwrócenie słownika
{5: 'Ala', 2: 'Bartek', 4: 'Celina'}
>>> [x for x in [1, 0, 2, "", 3] if x]    # odfiltrowanie wartości fałszywych
[1, 2, 3]
>>> sum(1 for x in [3, -1, 4, -2, 5] if x > 0)   # zliczenie dodatnich
3
```

Przy odwracaniu słownika trzeba pamiętać, że wartości muszą być haszowalne i unikatowe — powtórzona wartość nadpisze wcześniejszą parę (zostaje ostatnia).
