# 5. pandas — analiza

Rozdział 4 zakończył się tabelą wczytaną, oczyszczoną i wzbogaconą o kolumny. Pytania, które stawiamy takiej tabeli, rzadko dotyczą pojedynczych wierszy: ile sprzedano w każdej kategorii i miesiącu, którzy klienci odpowiadają za większość przychodu, jak sprzedaż zmienia się z tygodnia na tydzień, co wynika z połączenia zamówień z danymi klientów. Odpowiedzi wymagają **grupowania**, **przestawiania**, **łączenia** tabel i pracy z **szeregiem czasowym** — czterech mechanizmów pandas, które ten rozdział omawia po kolei, a na koniec pokazuje, jak z nich złożyć wydajny, powtarzalny potok analizy.

Rozdział buduje na całym rozdziale 4 tej części (selekcja, typy, braki, przekształcenia) oraz na rozdziałach 2 i 3 (średnia ruchoma, wykresy szeregów czasowych); z części „Python Notatki” korzysta z rozdziałów 9 (ścieżki i `glob()`), 13 (pomiary czasu) i 16 (testy). Wersje odniesienia jak w rozdziale 4: pandas 3.0.5, NumPy 2.5.3, Matplotlib 3.11.2, pyarrow 25.0.1; tabele w formacie Markdown wypisuje pakiet tabulate 0.10.0, a test modułu uruchamia pytest 9.1.1 z rozdziału 16 „Python Notatki” — oba dopisujemy do pliku wymagań projektu z rozdziału 4:

```text title="requirements.txt"
numpy==2.5.3
matplotlib==3.11.2
ipykernel==7.3.0
jupyterlab==4.6.3
pandas==3.0.5
openpyxl==3.1.5
pyarrow==25.0.1
tabulate==0.10.0
pytest==9.1.1
```

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

Dane rozdziału to `zamowienia-2025.csv` — 240 zamówień sklepu z pierwszego półrocza 2025 roku, wygenerowanych skryptem z pierwszego podrozdziału (dane przykładowe generowane ze stałym ziarnem) — oraz `klienci.csv` z siedmioma klientami. Oba pliki są do pobrania: [zamowienia-2025.csv](dane/zamowienia-2025.csv), [klienci.csv](dane/klienci.csv); skrypty uruchamiamy w katalogu z plikami.

---

## W tym rozdziale

1. [Grupowanie](grupowanie.md) — `groupby()`, agregacje z nazwami, indeks wielopoziomowy, `transform()`, `filter()` i `apply()` na grupach
2. [Tabele przestawne i kształt danych](przestawianie.md) — `pivot_table()`, `crosstab()`, postać długa i szeroka, `stack()` i `unstack()`, tabela do raportu
3. [Łączenie tabel](laczenie.md) — `merge()` i rodzaje złączeń, klucze i walidacja, pułapki, `concat()` z wielu plików, `join()`
4. [Szeregi czasowe](szeregi-czasowe.md) — indeks czasowy, `resample()`, okna kroczące, przesunięcia i zmiany, luki i strefy czasowe
5. [Wydajność i potok analizy](wydajnosc-i-potok.md) — pomiary na dużej tabeli, agregacje wbudowane, pamięć i Parquet, `pipe()`, moduł z testem
