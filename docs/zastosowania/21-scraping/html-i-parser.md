# HTML i parser

Dokument HTML to tekst ze znacznikami, który przeglądarka zamienia w drzewo elementów. Parser robi to samo dla programu: zamiast przeszukiwać tekst, wybieramy z drzewa elementy po nazwie, klasie czy atrybucie.

## Struktura strony

```html title="fragment"
<ul class="produkty">
  <li class="produkt" data-id="1"><a href="produkt-1.html">Czajnik elektryczny</a> <span class="cena">149,00 zł</span></li>
</ul>
```

**Element** `li` ma **atrybuty** (ang. *attribute*) `class` i `data-id` oraz zawartość: element `a` z atrybutem `href` i tekstem, spację i element `span`. Elementy zagnieżdżają się w **drzewo dokumentu** (ang. *document tree*): `ul` jest rodzicem `li`, `a` i `span` są rodzeństwem. Do wskazywania elementów służą **selektory CSS** (ang. *CSS selector*) znane z arkuszy stylów: `li.produkt` to element `li` z klasą `produkt`, `a[href]` — odsyłacz z atrybutem `href`, `ul > li` — bezpośrednie dziecko, `li[data-id='1'] a` — odsyłacz wewnątrz wskazanego `li`. Selektory odczytujemy w przeglądarce: narzędzia deweloperskie (++f12++, „Zbadaj element”) pokazują drzewo i klasy każdego elementu.

## Strona testowa

```python title="zbuduj_sklep.py"
"""Buduje stronę testową sklepu: dwie strony listy, strony produktów, koszyk i robots.txt."""

import json
from pathlib import Path

PRODUKTY = [
    ("Czajnik elektryczny", "149,00", "4,5", {"Moc": "2200 W", "Pojemność": "1,7 l"}),
    ("Toster dwukomorowy", "199,00", "4,2", {"Moc": "850 W", "Programy": "6"}),
    ("Ekspres przelewowy", "329,90", "4,7", {"Moc": "1000 W", "Pojemność": "1,25 l"}),
    ("Blender kielichowy", "259,00", None, {"Moc": "1200 W", "Pojemność": "1,5 l"}),
    ("Mikser ręczny", "119,50", "4,0", {"Moc": "450 W", "Biegi": "5"}),
    ("Waga kuchenna", "69,99", "4,8", {"Zakres": "5 kg", "Dokładność": "1 g"}),
    ("Robot planetarny", "1 299,00", "4,9", {"Moc": "1500 W", "Pojemność": "5 l"}),
    ("Frytkownica beztłuszczowa", "449,00", "4,4", {"Moc": "1700 W", "Pojemność": "4,5 l"}),
    ("Sokowirówka", None, "3,9", {"Moc": "800 W"}),
    ("Grill elektryczny", "289,00", "4,1", {"Moc": "2000 W", "Powierzchnia": "30 × 25 cm"}),
]
NA_STRONIE = 6


def strona_listy(numer, produkty, pierwszy, jest_dalej):
    pozycje = "\n".join(
        f'<li class="produkt" data-id="{pierwszy + i}"><a href="produkt-{pierwszy + i}.html">{nazwa}</a> '
        + (f'<span class="cena">{cena} zł</span>' if cena else '<span class="cena brak">cena na zapytanie</span>')
        + (f' <span class="ocena">{ocena}</span>' if ocena else "")
        + "</li>"
        for i, (nazwa, cena, ocena, _) in enumerate(produkty)
    )
    dalej = f'<a class="dalej" href="strona-{numer + 1}.html">Następna strona</a>' if jest_dalej else ""
    return f"""<!DOCTYPE html>
<html lang="pl"><head><meta charset="utf-8"><title>Sklep AGD — strona {numer}</title></head>
<body><h1>Sklep AGD</h1><nav><a href="index.html">Start</a> <a href="koszyk/">Koszyk</a></nav>
<ul class="produkty">
{pozycje}
</ul>
<nav class="strony">{dalej}</nav>
</body></html>
"""


def strona_produktu(numer, nazwa, cena, ocena, dane):
    wiersze = "\n".join(f"<tr><th>{klucz}</th><td>{wartosc}</td></tr>" for klucz, wartosc in dane.items())
    oferta = {"price": cena.replace(" ", "").replace(",", ".") if cena else None, "priceCurrency": "PLN"}
    ld = json.dumps({"@type": "Product", "sku": f"AGD-{numer:03d}", "name": nazwa, "offers": oferta}, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="pl"><head><meta charset="utf-8"><title>{nazwa} — Sklep AGD</title>
<script type="application/ld+json">{ld}</script></head>
<body><h1 class="nazwa">{nazwa}</h1>
<p class="cena">{f"{cena} zł" if cena else "cena na zapytanie"}</p>
<table class="dane">
{wiersze}
</table>
<p class="opis">Produkt <b>{nazwa}</b> z gwarancją 24 miesiące.<br>Wysyłka w 48 godzin.</p>
<a href="index.html">Wróć do listy</a>
</body></html>
"""


def zbuduj(katalog=Path("sklep")):
    (katalog / "koszyk").mkdir(parents=True, exist_ok=True)
    strony = [PRODUKTY[i : i + NA_STRONIE] for i in range(0, len(PRODUKTY), NA_STRONIE)]
    for numer, produkty in enumerate(strony, 1):
        plik = "index.html" if numer == 1 else f"strona-{numer}.html"
        (katalog / plik).write_text(strona_listy(numer, produkty, (numer - 1) * NA_STRONIE + 1, numer < len(strony)), encoding="utf-8")
    for numer, (nazwa, cena, ocena, dane) in enumerate(PRODUKTY, 1):
        (katalog / f"produkt-{numer}.html").write_text(strona_produktu(numer, nazwa, cena, ocena, dane), encoding="utf-8")
    (katalog / "koszyk" / "index.html").write_text("<html><body><h1>Koszyk</h1></body></html>", encoding="utf-8")
    (katalog / "robots.txt").write_text("User-agent: *\nDisallow: /koszyk/\n", encoding="utf-8")
    return sorted(p.name for p in katalog.iterdir())


if __name__ == "__main__":
    print(zbuduj())
```

```{ .text .no-copy }
['index.html', 'koszyk', 'produkt-1.html', 'produkt-10.html', 'produkt-2.html', 'produkt-3.html', 'produkt-4.html', 'produkt-5.html', 'produkt-6.html', 'produkt-7.html', 'produkt-8.html', 'produkt-9.html', 'robots.txt', 'strona-2.html']
```

Skrypt zapisuje w katalogu `sklep/` to, co wygenerowałby sklep internetowy: listę produktów podzieloną na dwie strony z odsyłaczem „Następna strona”, stronę każdego produktu z tabelą danych technicznych, opisem i blokiem JSON-LD (dane strukturalne, które sklepy dodają dla wyszukiwarek), koszyk oraz `robots.txt`, który zabrania robotom wchodzić do koszyka. Dane mają celowe nieregularności: jeden produkt bez ceny, jeden bez oceny, cena z separatorem tysięcy — takie, jakie spotyka się na prawdziwych stronach. Katalog pozostaje na dysku na potrzeby dalszych skryptów.

## Wybieranie elementów

```python title="parser.py"
from pathlib import Path

from bs4 import BeautifulSoup

zupa = BeautifulSoup(Path("sklep/index.html").read_text(encoding="utf-8"), "html.parser")
print(zupa.title.string)
produkty = zupa.select("li.produkt")
print(len(produkty), produkty[0])
pierwszy = produkty[0]
print(pierwszy.a.get_text(), pierwszy.a["href"], pierwszy["data-id"], pierwszy.select_one("span.cena").get_text())
print([li.a.get_text() for li in produkty][:3])
print(zupa.select_one("a.dalej")["href"], zupa.select_one("a.wstecz"))
print([li.a.get_text() for li in zupa.select("li.produkt:not(:has(span.ocena))")])
print(zupa.select_one("li[data-id='3'] a")["href"], [odsylacz["href"] for odsylacz in zupa.select("nav a")], pierwszy["class"])
druga = BeautifulSoup(Path("sklep/strona-2.html").read_text(encoding="utf-8"), "html.parser")
print(druga.select_one("span.cena.brak").get_text(), druga.select_one("a.dalej"))
```

```{ .text .no-copy }
Sklep AGD — strona 1
6 <li class="produkt" data-id="1"><a href="produkt-1.html">Czajnik elektryczny</a> <span class="cena">149,00 zł</span> <span class="ocena">4,5</span></li>
Czajnik elektryczny produkt-1.html 1 149,00 zł
['Czajnik elektryczny', 'Toster dwukomorowy', 'Ekspres przelewowy']
strona-2.html None
['Blender kielichowy']
produkt-3.html ['index.html', 'koszyk/', 'strona-2.html'] ['produkt']
cena na zapytanie None
```

`BeautifulSoup(tekst, "html.parser")` buduje drzewo; nazwa zmiennej `zupa` nawiązuje do nazwy biblioteki. `select()` zwraca listę elementów pasujących do selektora CSS, `select_one()` — pierwszy z nich albo `None`, dlatego przy niepewnym selektorze wynik sprawdzamy przed odczytem, jak dopasowanie w rozdziale 19. Element zachowuje się jak słownik atrybutów (`pierwszy["data-id"]`), a `get_text()` zwraca jego tekst bez znaczników; atrybut `class` jest listą, bo element może mieć wiele klas. Skrót `pierwszy.a` daje pierwszy element `a` wewnątrz. Selektory `:not()` i `:has()` pozwalają wybrać produkty bez oceny jednym selektorem, bez pętli, a `span.cena.brak` — element z dwiema klasami naraz. Druga strona listy nie ma odsyłacza „dalej”, co później zakończy przejście po stronach. Wydrukowany element pokazuje, że drzewo przechowuje cały HTML fragmentu.

## Poruszanie się po drzewie

```python title="drzewo.py"
import json
from pathlib import Path

from bs4 import BeautifulSoup

zupa = BeautifulSoup(Path("sklep/produkt-1.html").read_text(encoding="utf-8"), "lxml")
print(zupa.h1.get_text(), zupa.h1["class"], zupa.h1.parent.name)
dane = {wiersz.th.get_text(): wiersz.td.get_text() for wiersz in zupa.select("table.dane tr")}
print(dane)
opis = zupa.select_one("p.opis")
print(repr(opis.get_text()), "|", opis.get_text(" ", strip=True))
print([dziecko.name for dziecko in opis.children])
print(repr(opis.b.string), repr(opis.b.next_sibling), opis.find_next_sibling("a")["href"])
print(zupa.find("p", class_="cena").get_text(), zupa.find_all("a", href=True)[-1].get_text())
print(json.loads(zupa.select_one('script[type="application/ld+json"]').string)["offers"])
```

```{ .text .no-copy }
Czajnik elektryczny ['nazwa'] body
{'Moc': '2200 W', 'Pojemność': '1,7 l'}
'Produkt Czajnik elektryczny z gwarancją 24 miesiące.Wysyłka w 48 godzin.' | Produkt Czajnik elektryczny z gwarancją 24 miesiące. Wysyłka w 48 godzin.
[None, 'b', None, 'br', None]
'Czajnik elektryczny' ' z gwarancją 24 miesiące.' index.html
149,00 zł Wróć do listy
{'price': '149.00', 'priceCurrency': 'PLN'}
```

Poza selektorami drzewo ma nawigację: `parent`, `children`, `next_sibling`, `find_next_sibling()`. Wśród dzieci elementu są nie tylko elementy, lecz także fragmenty tekstu (`name` równe `None`) — dlatego `get_text()` łączy fragmenty rozdzielone `<br>` bez spacji, a `get_text(" ", strip=True)` łączy fragmenty separatorem i obcina białe znaki. `string` zwraca tekst elementu, który zawiera tylko tekst, `find()` i `find_all()` wybierają po nazwie i atrybutach (parametr `class_` z podkreśleniem, bo `class` jest słowem kluczowym Pythona). Tabela danych zamienia się w słownik jednym wyrażeniem, a blok JSON-LD w słownik przez `json.loads()` — gdy strona ma dane strukturalne, są one pewniejszym źródłem niż tekst widoczny dla użytkownika. Tu parser to `lxml` — wyniki są te same, różnice omawia koniec strony.

## Wyrażenia regularne a parser

```python title="porownanie.py"
import re

from bs4 import BeautifulSoup

html = """<a href="/a.html" class="x">A</a> <a class="y" href="/b.html">B</a>
<a title="Wielki > mały" href="/c.html">C</a> <!-- <a href="/stary.html">stary</a> -->"""
print(re.findall(r'<a href="([^"]+)"', html))
print(re.findall(r'<a [^>]*href="([^"]+)"', html))
print([odsylacz["href"] for odsylacz in BeautifulSoup(html, "html.parser").find_all("a")])
```

```{ .text .no-copy }
['/a.html', '/stary.html']
['/a.html', '/b.html', '/stary.html']
['/a.html', '/b.html', '/c.html']
```

Pierwszy wzorzec pomija odsyłacze, w których `href` nie jest pierwszym atrybutem; drugi nie znajduje tego ze znakiem `>` w atrybucie, a oba przyjmują odsyłacz z komentarza, którego przeglądarka nie pokazuje. Parser zwraca dokładnie trzy widoczne odsyłacze, bo rozumie atrybuty, cudzysłowy i komentarze. Wyrażenia regularne pozostają narzędziem do tekstu wewnątrz elementów — ceny, daty, numery — po tym, jak parser ten tekst wydobędzie.

Wybór parsera: `html.parser` jest w bibliotece standardowej i wystarcza do większości stron; `lxml` jest wyraźnie szybszy i tolerancyjny wobec błędnego HTML, ale wymaga instalacji pakietu. Oba wskazujemy nazwą w drugim argumencie `BeautifulSoup`, więc zmiana parsera to zmiana jednego słowa. Nazwę parsera podajemy zawsze jawnie — bez niej biblioteka wybiera najlepszy zainstalowany i ostrzega (`GuessedAtParserWarning`), że wynik może się różnić między komputerami.
