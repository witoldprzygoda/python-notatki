# 6. Projekt: raport z danych

Pięć rozdziałów ścieżki danych dało narzędzia: notatnik i układ projektu, NumPy, Matplotlib, tabele pandas i ich analizę. Projekt składa je w jedną całość, taką, jaką oddaje się w pracy: z pliku surowego o typowych wadach, przez spisane decyzje czyszczenia, przetestowany potok i rysunki, do raportu w Markdown odtwarzanego jednym poleceniem. Rozdział nie wprowadza nowych bibliotek — wprowadza sposób pracy, w którym każdy wynik ma kod, który go wytworzył, a reguły czyszczenia i kluczowe agregacje — testy.

Zadanie: sklep internetowy przekazał eksport zamówień z pierwszego półrocza 2025 roku i spis klientów, a oczekuje raportu o przychodzie w czasie, kategoriach, klientach i jakości danych. Rozdział buduje na całej ścieżce: układ projektu, `README.md` i moduł w `skrypty/` z rozdziału 1, mediana z rozdziału 2, styl i skrypt generujący rysunki z rozdziału 3, czyszczenie z rozdziału 4, grupowanie, `resample()`, `merge()` i `to_markdown()` z rozdziału 5; z części „Python Notatki” — moduły z rozdziału 7, `pathlib` z rozdziału 9 i pytest z rozdziałów 7 i 16. Wersje jak w rozdziale 5 (pandas 3.0.5, Matplotlib 3.11.2, pyarrow 25.0.1, tabulate 0.10.0, pytest 9.1.1); plik wymagań projektu jest taki sam jak tam.

Dane projektu — plik surowy `zamowienia_surowe.csv` (245 wierszy, dane przykładowe generowane skryptem z pierwszego podrozdziału, z celowo wprowadzonymi wadami) i `klienci.csv` — są do pobrania: [zamowienia_surowe.csv](dane/surowe/zamowienia_surowe.csv), [klienci.csv](dane/surowe/klienci.csv). Wszystkie skrypty rozdziału uruchamiamy z katalogu projektu, w którym leży katalog `dane/surowe/`.

---

## W tym rozdziale

1. [Zadanie, dane i decyzje](zadanie-i-dane.md) — pytania raportu, układ projektu, plik surowy, eksploracja i dziennik decyzji czyszczenia
2. [Potok — czyszczenie, analiza i testy](potok.md) — moduł przygotowania, moduł analizy, podgląd wyników, testy pytest
3. [Raport — rysunki, tabele i dokument](raport.md) — rysunki z funkcji, skrypt generujący, dokument Markdown, README i lista kontrolna
