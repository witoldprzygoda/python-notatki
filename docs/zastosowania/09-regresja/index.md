# 9. Regresja i przygotowanie danych

Klasyfikacja odpowiadała na pytanie „która klasa”; **regresja** odpowiada na pytanie „ile”: jaka będzie cena mieszkania, zużycie energii, czas dostawy. Warsztat z rozdziałów 7 i 8 — podział, potok, walidacja krzyżowa, model bazowy, krzywe walidacji — pozostaje ten sam, zmieniają się miary (błąd zamiast dokładności) i modele (regresja liniowa z regularyzacją, drzewa i lasy w wersji regresyjnej). Rozdział uzupełnia też to, czego zbiory wbudowane w scikit-learn nie wymagały: **przygotowanie danych** — kodowanie cech tekstowych, uzupełnianie braków i skalowanie w jednym potoku, który uczy się wyłącznie na zbiorze treningowym.

Dane rozdziału to `mieszkania.csv` — 400 ofert mieszkań z pięciu dzielnic, z powierzchnią, liczbą pokoi, piętrem, rokiem budowy (z brakami), stanem (kategoria porządkowa z brakami), windą, odległością od centrum i ceną — dane przykładowe generowane skryptem z pierwszego podrozdziału, o zależnościach wzorowanych na rynku. Plik jest do pobrania: [mieszkania.csv](dane/mieszkania.csv); skrypty uruchamiamy w katalogu z plikiem.

Rozdział buduje na całych rozdziałach 7 i 8, na rozdziale 4 (typy kolumn, braki, kategorie) i rozdziale 2 (metoda najmniejszych kwadratów i R²); wersje bibliotek jak w rozdziale 7 — scikit-learn 1.9.1, pandas 3.0.5, Matplotlib 3.11.2 — bez zmian w pliku wymagań.

---

## W tym rozdziale

1. [Regresja liniowa i miary błędu](regresja-liniowa.md) — dane o mieszkaniach, MAE, RMSE i R², model bazowy, regresja liniowa na cechach liczbowych, reszty
2. [Przygotowanie danych](przygotowanie-danych.md) — typy kolumn, kodowanie kategorii, imputacja braków, `ColumnTransformer` i potok, współczynniki po kodowaniu, wyciek celu
3. [Regularyzacja i inżynieria cech](regularyzacja-i-cechy.md) — cechy wielomianowe, regresja grzbietowa i `alpha`, lasso jako selekcja cech, transformacja celu
4. [Modele nieliniowe i wybór](modele-nieliniowe.md) — drzewo regresji, las i wzmacnianie gradientowe, porównanie modeli, ważność permutacyjna, model końcowy, lista kontrolna
