# 4. pandas — tabele

Dane z pomiarów, sprzedaży czy ankiet mają postać tabeli: wiersze to obserwacje, kolumny to cechy o różnych typach — liczby, napisy, daty, a w wielu miejscach braki. Tablice NumPy z rozdziału 2 tej części przechowują jeden typ i nie mają nazw kolumn, a tablica strukturalna z rozdziału 1 nazywa pola, lecz braki i typy mieszane obsługuje z trudem; moduł `csv` z rozdziału 9 „Python Notatki” czyta tabelę, ale każdą wartość oddaje jako napis. Biblioteka **pandas** łączy jedno z drugim: buduje na tablicach NumPy tabelę z nazwanymi, typowanymi kolumnami i indeksem wierszy, wczytuje ją z plików wielu formatów i pozwala wybierać, czyścić i przekształcać dane bez pętli.

Ten rozdział uczy pracy z pojedynczą tabelą: od `Series` i `DataFrame`, przez wczytywanie i zapis, selekcję, typy i braki, po przekształcenia kolumn i wykres z tabeli. Następny rozdział ścieżki dodaje analizę — grupowanie, łączenie tabel, przestawianie i szeregi czasowe. Rozdział buduje na rozdziałach 9 i 14 „Python Notatki” oraz na rozdziałach 1–3 tej części: dane leżą w katalogu projektu z rozdziału 1, obliczenia wektorowe i maski pochodzą z rozdziału 2, a wykresy dopracowujemy metodami z rozdziału 3.

Wersje odniesienia: pandas 3.0.5 na NumPy 2.5.3 i Pythonie 3.14.7; pliki Excel obsługuje openpyxl 3.1.5, a Parquet oraz przechowywanie kolumn typu `str` — pyarrow 25.0.1 (bez niego pandas przechowałby napisy w wolniejszych tablicach `object`). Do pliku wymagań projektu z rozdziału 1 dopisujemy trzy wiersze:

```text title="requirements.txt"
numpy==2.5.3
matplotlib==3.11.2
ipykernel==7.3.0
jupyterlab==4.6.3
pandas==3.0.5
openpyxl==3.1.5
pyarrow==25.0.1
```

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

Wydanie pandas 3.0 (styczeń 2026) zmieniło dwie rzeczy widoczne w każdym listingu: kolumny tekstowe mają typ `str` zamiast dawnego `object`, a każda ramka lub seria wyprowadzona z innej zachowuje się jak kopia — to model **kopiowania przy zapisie** (ang. *copy-on-write*) — bez ostrzeżeń o „kopii czy widoku” znanych z materiałów o starszych wersjach. Wydruki w rozdziale pochodzą z pandas 3; w starszych wersjach różnią się typami kolumn i ostrzeżeniami.

Rozdział pracuje na dwóch plikach: `zamowienia.csv` (dziesięć wierszy z dziewięcioma zamówieniami sklepu, jedno powtórzone; dane przykładowe) i `pomiary.csv` z rozdziału 1. Oba są osadzone w podrozdziale o wczytywaniu i dostępne do pobrania: [zamowienia.csv](dane/zamowienia.csv), [pomiary.csv](dane/pomiary.csv); skrypty uruchamiamy w katalogu z plikami danych; w projekcie z rozdziału 1 byłby to `dane/surowe/`, a ścieżki w listingach należałoby wtedy dostosować.

---

## W tym rozdziale

1. [Series i DataFrame](series-i-dataframe.md) — seria z etykietami, tabela kolumn, indeks, relacja do NumPy, wyświetlanie
2. [Wczytywanie i zapis](wczytywanie-i-zapis.md) — `read_csv()` z polskimi separatorami, pierwsze oględziny, `to_csv()`, Excel, JSON i Parquet, duże pliki porcjami
3. [Selekcja i filtrowanie](selekcja.md) — `loc` i `iloc`, maski logiczne, `query()`, sortowanie, przypisywanie w modelu kopiowania przy zapisie
4. [Typy, braki i czyszczenie](typy-i-braki.md) — typy kolumn i `Int64`, daty i `.dt`, wartości brakujące, duplikaty, typ kategorialny
5. [Przekształcenia i wykres z tabeli](przeksztalcenia.md) — nowe kolumny, akcesor `.str`, `map()` i `apply()`, przedziały, `plot()`
