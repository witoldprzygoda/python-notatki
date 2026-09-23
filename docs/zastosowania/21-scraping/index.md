# 21. Pobieranie i parsowanie stron

Nie każde źródło danych ma API. Cennik, rozkład jazdy, lista ogłoszeń czy katalog produktów istnieją często tylko jako strony WWW przeznaczone dla ludzi; program, który ma je przetwarzać, musi pobrać dokument HTML i wydobyć z niego dane. **Pobieranie stron** (ang. *web scraping*) składa się z dwóch umiejętności: pobrania dokumentu — klientem httpx z rozdziału 14 — i jego rozbioru (parsowania) **parserem HTML**, który zamienia tekst znaczników w drzewo elementów. Wyrażenia regularne z rozdziału 19 wystarczają do fragmentów tekstu, ale nie do HTML: przy zmiennej kolejności atrybutów, zagnieżdżeniach i komentarzach wzorce zawodzą, podczas gdy parser rozumie strukturę dokumentu.

Rozdział pracuje na stronie testowej: skrypt buduje niewielki sklep — dwie strony listy produktów, strony produktów z tabelą danych i plik `robots.txt` — a lokalny serwer z biblioteki standardowej podaje go pod adresem `127.0.0.1`. Dzięki temu przykłady działają bez sieci, dają zawsze ten sam wynik i nie obciążają cudzego serwera; te same funkcje działają z prawdziwym adresem. Kolejne strony rozdziału przechodzą od selektorów CSS w bibliotece BeautifulSoup, przez klienta z identyfikacją, `robots.txt`, odstępem między żądaniami i pamięcią podręczną, do modułu zbierającego rekordy z wielu stron, narzędzia wiersza poleceń z rozdziału 20 z testami oraz zasad prawnych i etycznych, które odróżniają dopuszczalne pobieranie od nadużycia.

Biblioteki: httpx (jak w rozdziale 14), **BeautifulSoup** (pakiet `beautifulsoup4`) do budowy drzewa dokumentu i selektorów CSS oraz `lxml` jako parser szybszy od `html.parser` z biblioteki standardowej; pytest do testów. Rozdział buduje na rozdziałach 9 (pliki, CSV i JSON), 15 (wątki) i 16 (pytest) części „Python Notatki” oraz 14 (HTTP i httpx), 19 (wzorce) i 20 (narzędzia wiersza poleceń) tej części.

```text title="requirements.txt"
httpx==0.28.1
beautifulsoup4==4.15.0
lxml==6.1.3
pytest==9.1.1
```

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

---

## W tym rozdziale

1. [HTML i parser](html-i-parser.md) — struktura strony, strona testowa, wybieranie elementów, poruszanie się po drzewie, wyrażenia regularne a parser
2. [Pobieranie stron](pobieranie.md) — serwer testowy, klient httpx, uprzejmość wobec serwera
3. [Dane ze stron](dane-ze-stron.md) — moduł pobierania, rekordy z HTML, przejście po stronach i zapis, strony dynamiczne
4. [Narzędzie i zasady](narzedzie.md) — narzędzie zbieracz, testy z serwerem testowym, zasady prawne i etyczne, lista kontrolna
