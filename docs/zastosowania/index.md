# Python Zastosowania

„Python Notatki” opisują język, jego bibliotekę standardową i warsztat programisty; z bibliotek zewnętrznych wprowadzają tylko NumPy i Matplotlib. „Python Zastosowania” prowadzą dalej — do bibliotek, na których opiera się codzienna praca z Pythonem: analiza danych, uczenie maszynowe, aplikacje z bazą danych i interfejsem, automatyzacja. Ta część nie jest przeglądem całego ekosystemu; jest zbiorem **ścieżek** — skończonych samouczków, z których każdy prowadzi od podstaw wybranej dziedziny do projektu spinającego jej narzędzia.

## Układ części

| Ścieżka | Zakres | Rozdziały |
|---|---|---|
| Dane | notatnik Jupyter, NumPy i Matplotlib w praktyce, pandas, projekt: raport z danych | 1–6 |
| Uczenie maszynowe | pojęcia i warsztat, klasyfikacja, regresja, uczenie bez nadzoru, PyTorch, projekt: od danych do modelu | 7–12 |
| Aplikacje | bazy danych, HTTP i API, FastAPI, tkinter, pakowanie, projekt: aplikacja z bazą, API i oknem | 13–18 |
| Automatyzacja | wyrażenia regularne, narzędzia wiersza poleceń, pobieranie stron, pliki Office i obrazy, projekt: narzędzie automatyzujące | 19–23 |

Ścieżki są od siebie niezależne — można zacząć od dowolnej — z jednym wyjątkiem: uczenie maszynowe zakłada ścieżkę danych. Każda ścieżka kończy się projektem, po którym czytelnik jest w stanie pracować z jej bibliotekami samodzielnie, korzystając z ich dokumentacji.

## Wymagania i zasady

Ta część zakłada znajomość języka w zakresie „Python Notatki”: funkcji, modułów, wyjątków, plików, klas, tablic NumPy z rozdziału 14 i narzędzi z rozdziału 16. Każdy rozdział wymienia na wstępie rozdziały „Python Notatki”, na których buduje.

- **Jedna biblioteka na rozdział.** Gdy zadanie ma kilka równorzędnych narzędzi, wybieramy jedno i wskazuje pozostałe jednym zdaniem.
- **Wersje w chwili pisania.** Biblioteki zmieniają się szybciej niż język; każdy rozdział podaje wersje, na których sprawdzono listingi, a pakiety instalujemy w środowisku projektu z rozdziału 1 według pliku wymagań z przypiętymi wersjami.
- **Każdy listing uruchomiony.** Wyniki, wykresy i komunikaty w tekście pochodzą z rzeczywistych uruchomień; dane przykładowe są osadzone w tekście.
- **Najpierw biblioteka standardowa.** Pakiet zewnętrzny instalujemy wtedy, gdy zadanie tego wymaga, nie z przyzwyczajenia.

## Rozdziały

**Ścieżka danych**

1. [Jupyter i warsztat danych](01-jupyter/index.md) — notatnik w VSC, środowisko projektu danych, czytanie dokumentacji bibliotek, pierwsza analiza
2. [NumPy w praktyce](02-numpy/index.md) — tablice wielowymiarowe, statystyka i porządkowanie, algebra liniowa, losowość i symulacje, wydajność i pamięć
3. [Matplotlib w praktyce](03-matplotlib/index.md) — anatomia wykresu, wykresy dla danych, szeregi czasowe, wiele paneli, wykres do raportu
4. [pandas — tabele](04-pandas-tabele/index.md) — Series i DataFrame, wczytywanie i zapis, selekcja, typy i braki, przekształcenia
5. [pandas — analiza](05-pandas-analiza/index.md) — grupowanie, tabele przestawne, łączenie tabel, szeregi czasowe, wydajność i potok
6. [Projekt: raport z danych](06-projekt-dane/index.md) — zadanie, dane i decyzje, potok z testami, raport z rysunkami i tabelami

**Ścieżka uczenia maszynowego**

7. [Uczenie maszynowe — pojęcia i warsztat](07-ml-pojecia/index.md) — pojęcia, pierwszy model od początku do końca, warsztat scikit-learn, przeuczenie i uczciwa ocena
8. [Klasyfikacja](08-klasyfikacja/index.md) — miary klasyfikacji, regresja logistyczna, drzewa decyzyjne i lasy losowe, wybór modelu i interpretacja
9. [Regresja i przygotowanie danych](09-regresja/index.md) — regresja liniowa i miary błędu, przygotowanie danych, regularyzacja i inżynieria cech, modele nieliniowe i wybór
10. [Uczenie bez nadzoru](10-bez-nadzoru/index.md) — grupowanie, redukcja wymiaru, obserwacje nietypowe
11. [PyTorch — tensory i sieć neuronowa](11-pytorch/index.md) — tensory, automatyczne różniczkowanie, sieć neuronowa, klasyfikacja obrazów, trening w praktyce
12. [Projekt: od danych do modelu](12-projekt-ml/index.md) — zadanie, dane i decyzje, potok, modele i wybór, model końcowy, raport i użycie

**Ścieżka aplikacji**

13. [Bazy danych — sqlite3 i SQLAlchemy](13-bazy-danych/index.md) — moduł sqlite3, schemat i zapytania SQL, SQLAlchemy — model i sesja, relacje i zapytania ORM, warstwa danych aplikacji
14. [HTTP i API](14-http-api/index.md) — protokół HTTP, serwer w bibliotece standardowej, klient httpx, interfejs API w praktyce
15. [FastAPI](15-fastapi/index.md) — pierwsza aplikacja, modele danych Pydantic, serwer sklepu, API nad warstwą danych, testy i uruchomienie
16. [Interfejs graficzny tkinter](16-tkinter/index.md) — okno i widżety, menedżery układu, zdarzenia i zmienne kontrolne, aplikacja obiektowa z menu i dialogami, widżety ttk, Canvas, CustomTkinter, mini-projekt: menedżer kontaktów
17. [Pakowanie i dystrybucja](17-pakowanie/index.md) — pakiet do instalacji, budowanie i publikacja, zależności i wersje, aplikacja dla użytkownika
18. [Projekt: aplikacja z bazą, API i oknem](18-projekt-aplikacja/index.md) — serwer: baza i API, klient: moduł API i okno, testy, uruchomienie i dostawa

**Ścieżka automatyzacji**

19. [Wyrażenia regularne](19-re/index.md) — składnia wzorców, wyszukiwanie, dzielenie i zamiana, wzorce w praktyce, pułapki, wydajność i testy
20. [Narzędzia wiersza poleceń](20-cli/index.md) — argumenty i opcje, strumienie, kody wyjścia i dziennik, procesy, pliki i konfiguracja, od skryptu do polecenia
21. [Pobieranie i parsowanie stron](21-scraping/index.md) — HTML i parser, pobieranie stron, dane ze stron, narzędzie i zasady
22. [Pliki Office i obrazy](22-office-obrazy/index.md) — arkusze Excel, dokumenty Word, obrazy, raport z danych
23. [Projekt: narzędzie automatyzujące](23-projekt-automatyzacja/index.md) — założenia i architektura, moduły narzędzia, testy i wdrożenie

Wszystkie cztery ścieżki są ukończone.
