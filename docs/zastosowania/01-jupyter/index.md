# 1. Jupyter i warsztat danych

Praca z danymi różni się od pisania programu: pytania powstają w trakcie, wynik jednego kroku decyduje o następnym, a obok kodu potrzebne są wykresy i komentarz. Narzędziem do takiej pracy jest **notatnik** (ang. *notebook*) Jupyter — dokument złożony z komórek kodu, ich wyników i tekstu, wykonywany krok po kroku w działającym interpreterze. Ten rozdział otwiera ścieżkę danych: uczy pracy w notatniku w Visual Studio Code, organizacji projektu danych tak, aby wyniki dały się odtworzyć, czytania dokumentacji bibliotek, a na koniec przeprowadza pierwszą analizę od pliku z danymi do wykresu i wniosków.

Rozdział buduje na materiale części „Python Podstawy”: środowiskach wirtualnych i pip z rozdziału 1, modułach z rozdziału 7, plikach i ścieżkach z rozdziału 9, tablicach i wykresach z rozdziału 14 oraz narzędziach jakości z rozdziału 16. Nowych bibliotek numerycznych nie wprowadza — NumPy i Matplotlib pojawiają się w zakresie znanym z rozdziału 14; ich pełne omówienie to następne rozdziały ścieżki.

Przykłady rozdziału sprawdziliśmy na Pythonie 3.14.8 z JupyterLab 4.6.3, ipykernel 7.3.0, IPython 9.17.1, NumPy 2.5.3 i Matplotlib 3.11.2; plik wymagań z podrozdziału [Środowisko projektu danych](srodowisko-projektu.md#srodowisko-i-wersje) przypina te wersje z wyjątkiem IPythona, który instaluje się razem z ipykernel. Według stanu na 17 X 2026 najnowsze wydania to JupyterLab 4.6.4, ipykernel 7.4.0 i NumPy 2.5.4, a IPython i Matplotlib pozostają w wersjach 9.17.1 i 3.11.2.

---

## W tym rozdziale

1. [Notatnik Jupyter w VSC](notatnik-jupyter.md) — notatnik a skrypt, instalacja i pierwszy notatnik, komórki i wartość ostatniego wyrażenia, stan jądra, polecenia magiczne, pomoc, JupyterLab i eksport
2. [Środowisko projektu danych](srodowisko-projektu.md) — katalog projektu, środowisko i wersje, dane wejściowe i ścieżki, powtarzalność, z notatnika do modułu
3. [Czytanie dokumentacji bibliotek](dokumentacja-bibliotek.md) — przewodnik a opis API, docstringi i sygnatury, wersje i ostrzeżenia o wycofaniu, zasada „najpierw biblioteka standardowa”, ocena pakietu
4. [Pierwsza analiza w notatniku](pierwsza-analiza.md) — od pliku CSV przez statystyki i wykres do wniosków i skryptu
