# Składnia wzorców

Wzorzec (ang. *pattern*) to łańcuch, w którym większość znaków oznacza samą siebie, a kilkanaście **metaznaków** ma znaczenie specjalne: powtórzenie, dowolny znak, początek wiersza. Ten podrozdział wprowadza je po kolei na krótkich przykładach, zawsze z wynikiem.

## Pierwsze dopasowanie

```python title="pierwsze.py"
import re

tekst = "Zamówienie 1042 z 2026-09-23: 3 sztuki, 149.00 zł"
print(re.search(r"\d+", tekst))
dopasowanie = re.search(r"\d{4}-\d{2}-\d{2}", tekst)
print(dopasowanie.group(), dopasowanie.start(), dopasowanie.end(), dopasowanie.span())
print(re.match(r"\d+", tekst), re.match(r"Zam", tekst))
print(re.fullmatch(r"\d+", "1042"), re.fullmatch(r"\d+", "1042 "))
print(re.findall(r"\d+", tekst))
print("\\d" == r"\d", len("\n"), len(r"\n"))
```

```{ .text .no-copy }
<re.Match object; span=(11, 15), match='1042'>
2026-09-23 18 28 (18, 28)
None <re.Match object; span=(0, 3), match='Zam'>
<re.Match object; span=(0, 4), match='1042'> None
['1042', '2026', '09', '23', '3', '149', '00']
True 1 2
```

`re.search()` szuka wzorca w dowolnym miejscu tekstu i zwraca obiekt **dopasowania** (ang. *match*) albo `None`, gdy nic nie znajdzie — dlatego wynik sprawdzamy w warunku, zanim odczytamy `group()` (dopasowany fragment), `start()`, `end()` i `span()`. `re.match()` dopasowuje tylko od początku tekstu, `re.fullmatch()` wymaga, by wzorzec objął cały tekst — spacja na końcu `"1042 "` wyklucza dopasowanie. Wzorce zapisujemy jako **surowe łańcuchy** (ang. *raw string*) `r"…"` z rozdziału 3 „Python Notatki”: w zwykłym łańcuchu Python sam interpretuje sekwencje ucieczki, więc ukośnik trzeba by podwoić (`"\\d"` to ten sam łańcuch co `r"\d"`), `"\n"` jest jednym znakiem nowego wiersza, nie dwoma znakami dla modułu `re`, a `"\b"` — znakiem cofania zamiast granicy słowa.

## Metaznaki, klasy i kwantyfikatory

```python title="metaznaki.py"
import re

proby = [
    (r"kot", "kot, kotek, skot"),
    (r"k.t", "kot kit kt"),
    (r"[kp]ot", "kot pot lot"),
    (r"[a-f0-9]+", "cafe 42 zebra"),
    (r"[^0-9 ]+", "abc 123 def"),
    (r"\d+", "tel. 600 100 200"),
    (r"\w+", "zażółć_1 jaźń!"),
    (r"\s", "a b\tc"),
    (r"ko?t", "kt kot koot"),
    (r"ko*t", "kt kot koot"),
    (r"ko+t", "kt kot koot"),
    (r"\d{2,3}", "1 22 333 4444"),
    (r"^\w+", "pierwsze słowo drugie"),
    (r"\w+$", "pierwsze słowo drugie"),
    (r"\bkot\b", "kot kotek skot"),
    (r"pies|kot", "kot i pies"),
    (r"3\.50", "3.50 3x50"),
]
for wzorzec, tekst in proby:
    print(f"{wzorzec:<12} {tekst!r:<26} {re.findall(wzorzec, tekst)}")
```

```{ .text .no-copy }
kot          'kot, kotek, skot'         ['kot', 'kot', 'kot']
k.t          'kot kit kt'               ['kot', 'kit']
[kp]ot       'kot pot lot'              ['kot', 'pot']
[a-f0-9]+    'cafe 42 zebra'            ['cafe', '42', 'eb', 'a']
[^0-9 ]+     'abc 123 def'              ['abc', 'def']
\d+          'tel. 600 100 200'         ['600', '100', '200']
\w+          'zażółć_1 jaźń!'           ['zażółć_1', 'jaźń']
\s           'a b\tc'                   [' ', '\t']
ko?t         'kt kot koot'              ['kt', 'kot']
ko*t         'kt kot koot'              ['kt', 'kot', 'koot']
ko+t         'kt kot koot'              ['kot', 'koot']
\d{2,3}      '1 22 333 4444'            ['22', '333', '444']
^\w+         'pierwsze słowo drugie'    ['pierwsze']
\w+$         'pierwsze słowo drugie'    ['drugie']
\bkot\b      'kot kotek skot'           ['kot']
pies|kot     'kot i pies'               ['kot', 'pies']
3\.50        '3.50 3x50'                ['3.50']
```

| Zapis | Znaczenie |
|---|---|
| `.` | dowolny znak poza nowym wierszem |
| `[kp]`, `[a-f0-9]`, `[^0-9 ]` | **klasa znaków** (ang. *character class*): jeden z wymienionych, z zakresu, spoza listy |
| `\d`, `\w`, `\s` | cyfra, znak słowa (litery, cyfry, `_`), biały znak; wielkie litery `\D`, `\W`, `\S` — przeciwieństwa |
| `?`, `*`, `+` | **kwantyfikator** (ang. *quantifier*): 0–1, 0 lub więcej, 1 lub więcej powtórzeń |
| `{n}`, `{m,n}`, `{m,}` | dokładnie n, od m do n, co najmniej m powtórzeń |
| `^`, `$` | **kotwica** (ang. *anchor*): początek i koniec tekstu (z flagą `MULTILINE` — wiersza) |
| `\b` | granica słowa: między znakiem słowa a znakiem spoza `\w` albo początkiem lub końcem tekstu |
| <code>a&#124;b</code> | alternatywa |
| `\.`, `\(`, `\\` | metaznak potraktowany dosłownie |

`re.findall()` zwraca listę wszystkich dopasowań — wygodne do prób. Kwantyfikator dotyczy elementu bezpośrednio przed nim: `ko+t` to `k`, jedno lub więcej `o`, `t`. Klasa `\w` obejmuje litery wszystkich alfabetów, więc `zażółć` jest jednym słowem; `\b` nie zużywa znaku, tylko sprawdza położenie, dlatego `\bkot\b` odrzuca `kotek` i `skot`. Znaki specjalne wewnątrz klasy `[...]` tracą znaczenie, a `^` na pierwszym miejscu klasy oznacza negację.

## Zachłanność

```python title="zachlannosc.py"
import re

html = "<b>pogrubione</b> i <i>kursywa</i>"
print(re.findall(r"<.+>", html))
print(re.findall(r"<.+?>", html))
print(re.findall(r"<[^>]+>", html))
print(re.search(r"\d{2,4}", "123456").group(), re.search(r"\d{2,4}?", "123456").group())
print(re.findall(r"\w+?", "abc"), re.findall(r"a*", "baa"))
```

```{ .text .no-copy }
['<b>pogrubione</b> i <i>kursywa</i>']
['<b>', '</b>', '<i>', '</i>']
['<b>', '</b>', '<i>', '</i>']
1234 12
['a', 'b', 'c'] ['', 'aa', '']
```

Kwantyfikatory są **zachłanne** (ang. *greedy*): biorą jak najwięcej znaków, dopóki reszta wzorca może się dopasować — `<.+>` sięga od pierwszego `<` do ostatniego `>`. Znak `?` po kwantyfikatorze czyni go **leniwym** (ang. *lazy*): bierze jak najmniej, więc `<.+?>` kończy na najbliższym `>`. Często lepsza od leniwości jest klasa zanegowana `[^>]+`, która nie może przeskoczyć znaku `>`, więc nie wymaga prób i cofania. Wzorce, które mogą dopasować pusty tekst (`a*`), dopasowują go wszędzie tam, gdzie nie ma dopasowania niepustego — tu na początku i na końcu tekstu — stąd puste elementy listy.

## Grupy

```python title="grupy.py"
import re

wpis = "2026-09-23 14:05 ERROR baza: brak połączenia"
m = re.search(r"(\d{4})-(\d{2})-(\d{2}) (\d{2}:\d{2}) (\w+) (.*)", wpis)
print(m.groups())
print(m.group(1), m.group(5), m.group(0)[:16])
m = re.search(r"(?P<data>\d{4}-\d{2}-\d{2}) (?P<czas>\d{2}:\d{2}) (?P<poziom>\w+) (?P<tresc>.*)", wpis)
print(m.groupdict())
print(m["poziom"], m.span("tresc"))
print(re.findall(r"(\w+)@(\w+)\.pl", "jan@firma.pl, ewa@szkola.pl"))
print(re.findall(r"\w+@(?:\w+)\.pl", "jan@firma.pl, ewa@szkola.pl"))
print(re.findall(r"(\w)\1", "kotek panny Anny mocno hałasuje"))
print(re.search(r"(?P<cudzyslow>['\"]).*?(?P=cudzyslow)", "napis 'w cudzysłowie' i drugi").group())
```

```{ .text .no-copy }
('2026', '09', '23', '14:05', 'ERROR', 'baza: brak połączenia')
2026 ERROR 2026-09-23 14:05
{'data': '2026-09-23', 'czas': '14:05', 'poziom': 'ERROR', 'tresc': 'baza: brak połączenia'}
ERROR (23, 44)
[('jan', 'firma'), ('ewa', 'szkola')]
['jan@firma.pl', 'ewa@szkola.pl']
['n', 'n']
'w cudzysłowie'
```

Nawiasy tworzą **grupę przechwytującą** (ang. *capturing group*): dopasowany fragment jest dostępny przez `group(n)` (numeracja od 1; `group(0)` to całość) lub `groups()`. **Grupa nazwana** `(?P<nazwa>…)` daje `groupdict()` i dostęp `m["nazwa"]` — czytelniejsze niż numery przy dłuższych wzorcach. Gdy wzorzec zawiera grupy, `findall()` zwraca zawartość grup zamiast całych dopasowań — teksty przy jednej grupie, krotki przy kilku; grupa **nieprzechwytująca** `(?:…)` grupuje bez tego skutku. **Odwołanie wsteczne** (ang. *backreference*) `\1` albo `(?P=nazwa)` wymaga powtórzenia tego, co grupa już dopasowała — podwójna litera, ten sam cudzysłów na końcu co na początku.

## Flagi

```python title="flagi.py"
import re

tekst = "Łódź\nłódź\nLODZ"
print(re.findall(r"łódź", tekst), re.findall(r"łódź", tekst, re.IGNORECASE), re.findall(r"(?i)łódź", tekst))
print(re.findall(r"^\w+$", tekst), re.findall(r"^\w+$", tekst, re.MULTILINE))
print(re.search(r"Łódź.łódź", tekst), re.search(r"Łódź.łódź", tekst, re.DOTALL).span())
print(re.findall(r"\w+", "zażółć gęślą jaźń"), re.findall(r"\w+", "zażółć gęślą jaźń", re.ASCII))
data = re.compile(
    r"""
    (?P<rok>\d{4})   # rok
    -(?P<miesiac>\d{2})  # miesiąc
    -(?P<dzien>\d{2})    # dzień
    """,
    re.VERBOSE,
)
print(data.search("od 2026-09-23").groupdict())
print(re.findall(r"a.b", "a\nb aXb", re.I | re.S))
```

```{ .text .no-copy }
['łódź'] ['Łódź', 'łódź'] ['Łódź', 'łódź']
[] ['Łódź', 'łódź', 'LODZ']
None (0, 9)
['zażółć', 'gęślą', 'jaźń'] ['za', 'g', 'l', 'ja']
{'rok': '2026', 'miesiac': '09', 'dzien': '23'}
['a\nb', 'aXb']
```

Flagi zmieniają znaczenie wzorca: `IGNORECASE` (`re.I`) zrównuje wielkość liter, także polskich; `MULTILINE` (`re.M`) każe kotwicom `^` i `$` działać na początku i końcu każdego wiersza, nie całego tekstu; `DOTALL` (`re.S`) pozwala kropce objąć znak nowego wiersza; `ASCII` (`re.A`) ogranicza `\w`, `\d`, `\s` i `\b` do znaków ASCII — polskie litery przestają być znakami słowa, stąd fragmenty `za`, `g`, `l`, `ja`; bez niej Python dopasowuje litery wszystkich alfabetów, co zwykle jest właściwe dla polskich tekstów. `VERBOSE` (`re.X`) ignoruje białe znaki i komentarze po `#` we wzorcu, więc długi wzorzec można rozpisać i opisać; spację dosłowną zapisuje się wtedy jako `\ ` albo `[ ]`. Flagi łączy się operatorem `|`, a `(?i)` na początku wzorca działa jak flaga.
