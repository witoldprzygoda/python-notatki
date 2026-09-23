# Wzorce w praktyce

Cztery zadania, w których wyrażenia regularne zastępują ręczne rozbieranie tekstu: dziennik serwera, dane w swobodnym tekście, nazwy plików i dokument wielowierszowy. Każde kończy się zwykłymi strukturami Pythona — słownikami, licznikami, listami — bo wyrażenie tylko wycina, a liczy i porządkuje reszta programu.

## Dziennik serwera

```text title="dziennik.log"
INFO:     Started server process [26348]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:52115 - "GET /produkty HTTP/1.1" 200 OK
INFO:     127.0.0.1:52115 - "GET /produkty/3 HTTP/1.1" 200 OK
INFO:     127.0.0.1:52116 - "POST /zamowienia HTTP/1.1" 201 Created
INFO:     127.0.0.1:52116 - "GET /produkty/9 HTTP/1.1" 404 Not Found
INFO:     10.0.0.7:41002 - "POST /zamowienia HTTP/1.1" 409 Conflict
INFO:     10.0.0.7:41002 - "GET /klienci/1/podsumowanie HTTP/1.1" 200 OK
INFO:     10.0.0.7:41003 - "POST /zamowienia HTTP/1.1" 422 Unprocessable Content
INFO:     127.0.0.1:52120 - "GET /produkty?kategoria=ksi%C4%85%C5%BCki HTTP/1.1" 200 OK
INFO:     127.0.0.1:52121 - "GET /docs HTTP/1.1" 200 OK
INFO:     Shutting down
```

```python title="dziennik.py"
import re
from collections import Counter
from pathlib import Path

ZADANIE = re.compile(
    r"""
    (?P<adres>\d{1,3}(?:\.\d{1,3}){3}):(?P<port>\d+)\s-\s
    "(?P<metoda>[A-Z]+)\s(?P<sciezka>\S+)\sHTTP/[\d.]+"\s
    (?P<kod>\d{3})\s(?P<opis>.*)
    """,
    re.VERBOSE,
)
zadania = [m.groupdict() for m in map(ZADANIE.search, Path("dziennik.log").read_text(encoding="utf-8").splitlines()) if m]
print(len(zadania), zadania[0])
print(Counter(z["kod"] for z in zadania).most_common())
print(Counter(re.sub(r"\d+", "{id}", z["sciezka"].split("?")[0]) for z in zadania).most_common(3))
print(Counter(z["adres"] for z in zadania if not z["kod"].startswith("2")))
```

```{ .text .no-copy }
9 {'adres': '127.0.0.1', 'port': '52115', 'metoda': 'GET', 'sciezka': '/produkty', 'kod': '200', 'opis': 'OK'}
[('200', 5), ('201', 1), ('404', 1), ('409', 1), ('422', 1)]
[('/zamowienia', 3), ('/produkty', 2), ('/produkty/{id}', 2)]
Counter({'10.0.0.7': 2, '127.0.0.1': 1})
```

Wiersz żądania w dzienniku uvicorn z rozdziału 15 ma stały układ: adres z portem, myślnik, linia żądania w cudzysłowie, kod i opis. Wzorzec w trybie `VERBOSE` zapisuje ten układ z grupami nazwanymi — cztery liczby adresu IP przez grupę nieprzechwytującą z powtórzeniem, ścieżka jako ciąg znaków niebiałych — a wiersze bez dopasowania (start, zatrzymanie) odpadają w warunku `if m`. Dalej pracują `Counter` z rozdziału 7 „Python Notatki” i drugie, małe wyrażenie, które zastępuje liczby w ścieżce wspólnym symbolem, żeby zliczyć trasy, nie pojedyncze produkty.

## Dane z tekstu

```python title="z-tekstu.py"
import re

tekst = """Prosimy o kontakt: jan.kowalski@firma.pl lub tel. 600-100-200 (po 16:00).
Faktura nr FV/2026/09/0142 z dnia 23.09.2026, płatna do 7.10.2026.
Adres biura: 33-300 Nowy Sącz, ul. Długa 7; drugi telefon +48 12 444 55 66."""

print(re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", tekst))
telefony = re.findall(r"(?:\+48[ -]?)?\d(?:[ -]?\d){8}", tekst)
print(telefony, [re.sub(r"\D", "", t)[-9:] for t in telefony])
print(re.findall(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b", tekst))
print([f"{rok}-{int(m):02d}-{int(d):02d}" for d, m, rok in re.findall(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b", tekst)])
print(re.search(r"\b\d{2}-\d{3}\b", tekst).group(), re.search(r"FV/\d{4}/\d{2}/\d+", tekst).group())
```

```{ .text .no-copy }
['jan.kowalski@firma.pl']
['600-100-200', '+48 12 444 55 66'] ['600100200', '124445566']
[('23', '09', '2026'), ('7', '10', '2026')]
['2026-09-23', '2026-10-07']
33-300 FV/2026/09/0142
```

Tekst pisany dla ludzi nie ma stałego układu, więc wzorce opisują kształt danych: adres e-mail jako znaki nazwy, `@`, domena z co najmniej jedną kropką; telefon jako cyfra i osiem par „opcjonalny separator, cyfra” — dziewięć cyfr z pojedynczymi spacjami lub myślnikami w dowolnych miejscach, bez separatora na końcu — opcjonalnie z prefiksem kraju; data w zapisie polskim z grupami, z których budujemy zapis ISO; kod pocztowy i numer faktury po ich stałym kształcie. Dwa nawyki: kotwice `\b` zapobiegają dopasowaniu fragmentu dłuższej liczby, a normalizację (usunięcie separatorów i prefiksu kraju, dopełnienie zerami) robimy poza wzorcem. Wzorzec e-maila jest praktyczny, nie pełny — pełna składnia adresu jest zbyt złożona na wyrażenie regularne, a jedynym pewnym sprawdzeniem adresu jest wysłanie wiadomości.

## Nazwy plików

```python title="pliki.py"
import re
from pathlib import Path

katalog = Path("raporty")
katalog.mkdir(exist_ok=True)
for nazwa in ("raport 23.09.2026 v2.pdf", "Raport 1.10.2026.pdf", "raport_15.08.2026_final.pdf", "notatki.txt"):
    (katalog / nazwa).write_text("", encoding="utf-8")

WZORZEC = re.compile(r"(?i)raport[ _](?P<d>\d{1,2})\.(?P<m>\d{1,2})\.(?P<rok>\d{4})(?P<reszta>.*)\.pdf")
for plik in sorted(katalog.iterdir()):
    m = WZORZEC.fullmatch(plik.name)
    if m is None:
        print("pomijam:", plik.name)
        continue
    dopisek = re.sub(r"[ _]+", "-", m["reszta"]).strip("-")
    nowa = f"raport-{m['rok']}-{int(m['m']):02d}-{int(m['d']):02d}" + (f"-{dopisek}" if dopisek else "") + ".pdf"
    plik.rename(katalog / nowa)
    print(plik.name, "→", nowa)
print(sorted(p.name for p in katalog.iterdir()))
```

```{ .text .no-copy }
pomijam: notatki.txt
Raport 1.10.2026.pdf → raport-2026-10-01.pdf
raport 23.09.2026 v2.pdf → raport-2026-09-23-v2.pdf
raport_15.08.2026_final.pdf → raport-2026-08-15-final.pdf
['notatki.txt', 'raport-2026-08-15-final.pdf', 'raport-2026-09-23-v2.pdf', 'raport-2026-10-01.pdf']
```

Nazwy plików z datą w zapisie polskim nie sortują się chronologicznie; po zmianie na zapis `rok-miesiąc-dzień` sortowanie alfabetyczne jest sortowaniem po dacie. `fullmatch()` na nazwie odrzuca pliki spoza schematu, `(?i)` znosi rozróżnianie wielkości liter w całym wzorcu (`Raport`, także `.PDF`), a grupa `reszta` przenosi dopiski (`v2`, `final`) w ujednoliconej postaci. `Path.rename()` z rozdziału 9 „Python Notatki” wykonuje zmianę; przy większej liczbie plików warto najpierw wypisać plan, a zmieniać dopiero po sprawdzeniu.

## Dokument wielowierszowy

```python title="markdown.py"
import re

dokument = """# Sklep — instrukcja

Uruchomienie opisano w [rozdziale 18](../18-projekt-aplikacja/index.md).

## Instalacja

Zobacz [pakowanie](../17-pakowanie/index.md) oraz [PyPI](https://pypi.org/).

~~~powershell
python -m pip install sklep
~~~

## Użycie

Polecenie `sklep-serwer` uruchamia usługę; szczegóły w [dokumentacji](http://127.0.0.1:8000/docs).
"""

print(re.findall(r"^(#{1,6})\s+(.+)$", dokument, re.MULTILINE))
odsylacze = re.findall(r"\[([^\]]+)\]\(([^)\s]+)\)", dokument)
print(odsylacze)
print([adres for _, adres in odsylacze if re.match(r"https?://", adres)])
bez_kodu = re.sub(r"^~~~.*?^~~~\n?", "", dokument, flags=re.MULTILINE | re.DOTALL)
print(bez_kodu.count("\n"), dokument.count("\n"), "~~~" in bez_kodu)
print(re.findall(r"`([^`]+)`", bez_kodu))
```

```{ .text .no-copy }
[('#', 'Sklep — instrukcja'), ('##', 'Instalacja'), ('##', 'Użycie')]
[('rozdziale 18', '../18-projekt-aplikacja/index.md'), ('pakowanie', '../17-pakowanie/index.md'), ('PyPI', 'https://pypi.org/'), ('dokumentacji', 'http://127.0.0.1:8000/docs')]
['https://pypi.org/', 'http://127.0.0.1:8000/docs']
12 15 False
['sklep-serwer']
```

Nagłówki Markdown to wiersze zaczynające się od `#` — kotwica `^` z flagą `MULTILINE` sprawdza początek każdego wiersza, a grupa z `{1,6}` daje poziom nagłówka. Odsyłacz `[tekst](adres)` opisujemy klasami zanegowanymi: tekst bez `]`, adres bez `)` i spacji — bez zachłannego `.+`, które połączyłoby dwa odsyłacze w jednym wierszu. Blok kodu — tu w **ogrodzeniu** (ang. *fence*) `~~~`, równoważnym potrójnemu odwrotnemu apostrofowi — którego treść usuwamy, by nie zakłócała dalszych wyszukiwań, ciągnie się przez wiele wierszy, więc potrzebne są obie flagi: `MULTILINE` dla kotwic na początku wierszy ogrodzenia i `DOTALL`, by leniwe `.*?` przeszło przez nowe wiersze. Ten sam schemat — kotwice na wiersze, `DOTALL` na bloki — obsługuje pliki konfiguracyjne i dzienniki wielowierszowe.
