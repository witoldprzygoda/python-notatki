# 10. Uczenie bez nadzoru

Rozdziały 7–9 uczyły modele na przykładach z odpowiedziami: gatunek, diagnoza, cena. **Uczenie bez nadzoru** (ang. *unsupervised learning*) obywa się bez etykiet — szuka w samych cechach struktury: grup podobnych próbek, kierunków, w których dane różnią się najbardziej, i obserwacji, które do reszty nie pasują. Nie ma tu dokładności ani błędu testowego; jest pytanie, czy znaleziona struktura coś znaczy i do czego się przyda — do opisu segmentów, do zmniejszenia liczby cech dla modelu z nadzorem, do listy ofert wymagających sprawdzenia.

Dane rozdziału to zbiory już znane: wine z rozdziałów 7–8 (178 win, 13 cech chemicznych; etykiety odmian ukrywamy przed modelami i używamy tylko do oceny wyniku), Breast Cancer Wisconsin z rozdziału 8 (30 cech silnie skorelowanych) i `mieszkania.csv` z rozdziału 9 ([plik](../09-regresja/dane/mieszkania.csv); skrypty uruchamiamy w katalogu z nim). Dochodzą dwa zbiory wbudowane w scikit-learn: syntetyczne „półksiężyce” `make_moons` i digits — 1797 obrazów cyfr o wymiarach 8 × 8 pikseli.

Rozdział buduje na rozdziale 2 (macierz odległości z rozgłaszania, wartości własne macierzy kowariancji), rozdziale 7 (skalowanie, potok) i rozdziałach 8–9 (ważność permutacyjna, cechy skorelowane, przygotowanie danych); wersje bibliotek jak w rozdziale 7 — scikit-learn 1.9.1, pandas 3.0.5, Matplotlib 3.11.2 — bez zmian w pliku wymagań.

---

## W tym rozdziale

1. [Grupowanie](grupowanie.md) — algorytm k-średnich krok po kroku, `KMeans`, liczba grup, profile grup, kształt grup i DBSCAN
2. [Redukcja wymiaru](redukcja-wymiaru.md) — analiza głównych składowych, składowe i skalowanie, PCA w potoku dla cech skorelowanych, wizualizacja t-SNE
3. [Obserwacje nietypowe](obserwacje-nietypowe.md) — błędy do wykrycia, reguła statystyczna, las izolacji, lokalny współczynnik odstawania, kiedy uczenie bez nadzoru, lista kontrolna
