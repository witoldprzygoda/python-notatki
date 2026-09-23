# Wyszukiwanie, dzielenie i zamiana

Moduł `re` ma cztery operacje: znaleźć (`search`, `findall`, `finditer`), podzielić (`split`), zamienić (`sub`) i sprawdzić w całości (`fullmatch`). Każda przyjmuje wzorzec i tekst; ten podrozdział pokazuje ich odmiany i wzorzec skompilowany, który przydaje się, gdy ten sam wzorzec działa wiele razy.

## Wszystkie dopasowania

```python title="wszystkie.py"
import re

tekst = "Anna: 600 100 200, Jan: 601-200-300, biuro: 12 444 55 66"
print(re.findall(r"\d[\d -]{7,}\d", tekst))
print(re.findall(r"(\w+): (\d[\d -]+\d)", tekst))
for m in re.finditer(r"(?P<kto>\w+): (?P<numer>\d[\d -]+\d)", tekst):
    print(m.span(), m["kto"], "→", m["numer"].replace(" ", "").replace("-", ""))
print(sum(1 for _ in re.finditer(r"\d", tekst)), len(re.findall(r"\d", tekst)))
```

```{ .text .no-copy }
['600 100 200', '601-200-300', '12 444 55 66']
[('Anna', '600 100 200'), ('Jan', '601-200-300'), ('biuro', '12 444 55 66')]
(0, 17) Anna → 600100200
(19, 35) Jan → 601200300
(37, 56) biuro → 124445566
27 27
```

`findall()` zwraca listę tekstów, a przy grupach — listę ich zawartości: krotek, a przy jednej grupie łańcuchów; `finditer()` zwraca iterator obiektów dopasowania, więc mamy położenie, grupy nazwane i możliwość przetworzenia każdego trafienia bez budowania listy. Do policzenia trafień wystarczy dowolne z nich. Wzorzec numeru telefonu jest celowo luźny: cyfra, potem cyfry, spacje i myślniki, na końcu cyfra — ujednolicenie zapisu robimy już w Pythonie.

## Dzielenie

```python title="dzielenie.py"
import re

print(re.split(r"[;,]\s*", "jabłka; gruszki,śliwki , wiśnie"))
print(re.split(r"\s+", "  wiele   spacji\ti tabulator "))
print("  wiele   spacji\ti tabulator ".split())
print(re.split(r"(\d+)", "rozdział 12 strona 7"))
print(re.split(r"\n(?=\d+\.)", "1. pierwszy\nciąg dalszy\n2. drugi", maxsplit=1))
```

```{ .text .no-copy }
['jabłka', 'gruszki', 'śliwki ', 'wiśnie']
['', 'wiele', 'spacji', 'i', 'tabulator', '']
['wiele', 'spacji', 'i', 'tabulator']
['rozdział ', '12', ' strona ', '7', '']
['1. pierwszy\nciąg dalszy', '2. drugi']
```

`re.split()` dzieli po każdym dopasowaniu — kilka separatorów naraz, z otaczającymi spacjami — tam, gdzie `str.split()` przyjmuje tylko jeden. Dla samych białych znaków `split()` bez argumentu robi to samo i pomija puste fragmenty na brzegach, których `re.split()` nie pomija. Grupa przechwytująca we wzorcu sprawia, że separatory trafiają do wyniku, a `maxsplit` ogranicza liczbę cięć. `(?=…)` to **wyprzedzenie** (ang. *lookahead*): warunek na to, co następuje, bez zużywania znaków — tu dzielimy przed numerem punktu, nie usuwając go.

## Zamiana

```python title="zamiana.py"
import re

print(re.sub(r"\s+", " ", "wiele   spacji\ti  tabulator"))
print(re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3.\2.\1", "od 2026-09-23 do 2026-10-01"))
print(re.sub(r"(?P<imie>\w+)@(?P<domena>[\w.]+)", r"\g<imie> [at] \g<domena>", "jan@firma.pl, ewa@szkola.edu.pl"))
print(re.sub(r"\d+", lambda m: f"{int(m.group()) * 2}", "3 sztuki po 149 zł"))
print(re.sub(r"\b(\w)(\w*)", lambda m: m.group(1).upper() + m.group(2), "nowy sącz nad dunajcem"))
print(re.sub(r"\d", "#", "600 100 200", count=3))
print(re.subn(r"[aeiouyąęó]", "", "wyrażenia regularne"))
print(re.sub(r"(\d+) zł", r"\1 PLN", "cena: 149 zł, było 199 zł"))
```

```{ .text .no-copy }
wiele spacji i tabulator
od 23.09.2026 do 01.10.2026
jan [at] firma.pl, ewa [at] szkola.edu.pl
6 sztuki po 298 zł
Nowy Sącz Nad Dunajcem
### 100 200
('wrżn rglrn', 9)
cena: 149 PLN, było 199 PLN
```

`re.sub()` zamienia każde dopasowanie na tekst zastępczy, w którym `\1` i `\g<nazwa>` wstawiają zawartość grup — tak zmieniamy kolejność części daty bez rozbierania jej ręcznie. Gdy zamiana wymaga obliczenia, zamiast tekstu podajemy funkcję: dostaje obiekt dopasowania i zwraca tekst. `count` ogranicza liczbę zamian, a `subn()` zwraca też ich liczbę. Tekst zastępczy również zapisujemy jako surowy łańcuch, bo `"\1"` w zwykłym łańcuchu to znak o kodzie 1.

## Wzorce skompilowane i błędy

```python title="kompilacja.py"
import re

data = re.compile(r"(?P<rok>\d{4})-(?P<miesiac>\d{2})-(?P<dzien>\d{2})")
print(data.pattern, data.groups, data.groupindex)
print(data.search("dziś 2026-09-23").group("rok"), data.findall("2026-09-23 i 2026-10-01"))
print(data.sub(r"\g<dzien>.\g<miesiac>", "od 2026-09-23"), data.fullmatch("2026-09-23") is not None)
print(re.escape("cena: 3.50 zł (brutto)?"))
szukane = "3.50"
print(re.findall(szukane, "3.50 3x50 3-50"), re.findall(re.escape(szukane), "3.50 3x50 3-50"))
try:
    re.compile(r"(\d+")
except re.PatternError as blad:
    print(type(blad).__name__, "—", blad, "— pozycja", blad.pos)
```

```{ .text .no-copy }
(?P<rok>\d{4})-(?P<miesiac>\d{2})-(?P<dzien>\d{2}) 3 {'rok': 1, 'miesiac': 2, 'dzien': 3}
2026 [('2026', '09', '23'), ('2026', '10', '01')]
od 23.09 True
cena:\ 3\.50\ zł\ \(brutto\)\?
['3.50', '3x50', '3-50'] ['3.50']
PatternError — missing ), unterminated subpattern at position 0 — pozycja 0
```

`re.compile()` zamienia wzorzec w obiekt z tymi samymi metodami co funkcje modułu — `search()`, `findall()`, `sub()`, `fullmatch()` — oraz atrybutami `pattern`, `groups` i `groupindex`. Funkcje modułu i tak kompilują wzorce i trzymają ostatnie w pamięci podręcznej, więc kompilacja nie przyspiesza małych skryptów; opłaca się jako stała modułu — jedna nazwa dla wzorca używanego w wielu miejscach. `re.escape()` poprzedza ukośnikiem metaznaki w tekście, który ma być dopasowany dosłownie — bez niej `3.50` pasuje też do `3x50`. Błędny wzorzec zgłasza `PatternError` (do Pythona 3.12 `re.error`; stara nazwa nadal działa) z komunikatem i pozycją błędu; wzorce z danych zewnętrznych kompilujemy w bloku `try`.
