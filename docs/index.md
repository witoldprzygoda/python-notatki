# Python Notatki

„Python Notatki” to podręcznik języka Python. Prowadzi czytelnika od instalacji interpretera i przygotowania środowiska pracy, przez pierwsze eksperymenty w konsoli i systematyczne omówienie typów danych oraz konstrukcji języka, po programowanie obiektowe, wydajność, tablice NumPy, współbieżność i warsztat programisty. Druga część, „Python Zastosowania”, obejmuje biblioteki i ich zastosowania, ułożone w niezależne ścieżki do wyboru.

Stanem odniesienia jest **Python 3.14** instalowany za pomocą narzędzia **Python Install Manager** w systemie Windows.

## Python Notatki

1. [Instalacja i środowisko pracy](01-instalacja/index.md) — Python Install Manager, pip, środowiska wirtualne, konfiguracja narzędzi
2. [Konsola](02-konsola/index.md) — praca w konsoli interaktywnej i pierwszy skrypt
3. [Nazwy i typy](03-nazwy-typy/index.md) — nazwy, typy proste, konwersje, obiekty i pamięć, operatory
4. [Sterowanie przepływem](04-sterowanie/index.md) — instrukcje warunkowe, pętle i iteratory
5. [Typy złożone](05-typy-zlozone/index.md) — lista, krotka, słownik, zbiory, złożenia
6. [Funkcje](06-funkcje/index.md) — definiowanie, argumenty, zasięg nazw i domknięcia, rekurencja, funkcje generatorowe, dekoratory
7. [Moduły, pakiety i biblioteka standardowa](07-moduly/index.md) — moduły i import, skrypt jako program, argumenty wiersza poleceń, pakiety, struktura projektu i pierwsze testy, biblioteka standardowa i collections, functools, itertools
8. [Wyjątki i zarządzanie zasobami](08-wyjatki/index.md) — obsługa i zgłaszanie wyjątków, styl EAFP i testy wyjątków, instrukcja with, diagnostyka i debugger, logowanie
9. [Wejście, wyjście i pliki](09-wejscie-wyjscie/index.md) — formatowanie tekstu, print i strumienie, animacje w terminalu, pliki tekstowe i binarne, ścieżki, CSV i JSON
10. [Klasy i obiekty](10-klasy/index.md) — definicja klasy, atrybuty i metody, właściwości, dziedziczenie i własne wyjątki, cykl życia obiektu
11. [Model danych — metody specjalne i protokoły](11-model-danych/index.md) — przeciążanie operatorów, protokoły kolekcji i wywołania, iteracja, menedżery kontekstu i obiekty plikopodobne, deskryptory
12. [Programowanie obiektowe — mechanizmy zaawansowane](12-oop-zaawansowane/index.md) — dziedziczenie wielokrotne i MRO, mixiny i klasy abstrakcyjne, klasy danych, wzorce projektowe, metaprogramowanie
13. [Wydajność i optymalizacja](13-wydajnosc/index.md) — pomiar czasu i profilowanie, optymalizacja kodu, drogi przyspieszania
14. [NumPy i Matplotlib](14-numpy-matplotlib/index.md) — tablice ndarray, operacje wektorowe, wykresy w stylu obiektowym
15. [Współbieżność — wątki, procesy i GIL](15-wspolbieznosc/index.md) — wątki i GIL, synchronizacja, procesy i pule wykonawców, pomiary i asyncio
16. [Warsztat programisty i dalsza droga](16-warsztat/index.md) — pytest zaawansowany, adnotacje typów i mypy, Ruff, pre-commit i CI, co dalej

## Python Zastosowania

Część „Python Zastosowania” składa się ze ścieżek — niezależnych, skończonych samouczków bibliotek: dane, uczenie maszynowe, aplikacje, automatyzacja. Każda ścieżka zakłada znajomość języka z części „Python Notatki” i kończy się projektem spinającym jej narzędzia; [wprowadzenie](zastosowania/index.md) opisuje układ i wymagania.

**Ścieżka danych**

1. [Jupyter i warsztat danych](zastosowania/01-jupyter/index.md) — notatnik w VSC, środowisko projektu danych, czytanie dokumentacji bibliotek, pierwsza analiza
2. [NumPy w praktyce](zastosowania/02-numpy/index.md) — tablice wielowymiarowe, statystyka i porządkowanie, algebra liniowa, losowość i symulacje, wydajność i pamięć
3. [Matplotlib w praktyce](zastosowania/03-matplotlib/index.md) — anatomia wykresu, wykresy dla danych, szeregi czasowe, wiele paneli, wykres do raportu
4. [pandas — tabele](zastosowania/04-pandas-tabele/index.md) — Series i DataFrame, wczytywanie i zapis, selekcja, typy i braki, przekształcenia
5. [pandas — analiza](zastosowania/05-pandas-analiza/index.md) — grupowanie, tabele przestawne, łączenie tabel, szeregi czasowe, wydajność i potok
6. [Projekt: raport z danych](zastosowania/06-projekt-dane/index.md) — zadanie, dane i decyzje, potok z testami, raport z rysunkami i tabelami
7. [Uczenie maszynowe — pojęcia i warsztat](zastosowania/07-ml-pojecia/index.md) — pojęcia, pierwszy model od początku do końca, warsztat scikit-learn, przeuczenie i uczciwa ocena
8. [Klasyfikacja](zastosowania/08-klasyfikacja/index.md) — miary klasyfikacji, regresja logistyczna, drzewa decyzyjne i lasy losowe, wybór modelu i interpretacja
9. [Regresja i przygotowanie danych](zastosowania/09-regresja/index.md) — regresja liniowa i miary błędu, przygotowanie danych, regularyzacja i inżynieria cech, modele nieliniowe i wybór

Rozdziały 10–12 ścieżki uczenia maszynowego oraz pozostałe ścieżki są w przygotowaniu.
