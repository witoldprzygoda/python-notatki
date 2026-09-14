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

Ścieżka danych jest ukończona; rozdziały 10–12 ścieżki uczenia maszynowego oraz pozostałe ścieżki są w przygotowaniu.
