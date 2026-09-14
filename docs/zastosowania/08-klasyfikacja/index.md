# 8. Klasyfikacja

Pierwszy model z rozdziału 7 rozpoznawał gatunek irysa z dokładnością 97% — z uwagą, że dokładność nie wystarcza, gdy klasy są nierównoliczne albo błędy mają różną wagę. Ten rozdział zostaje przy klasyfikacji i uzupełnia to, czego pierwszemu modelowi brakowało: miary, które rozróżniają rodzaje błędów i pozwalają dobrać próg decyzyjny do kosztu pomyłki; dwie rodziny modeli, które w praktyce rozwiązują większość zadań klasyfikacji — regresję logistyczną oraz drzewa i lasy losowe — wraz z tym, jak czytać ich parametry; oraz sposób wyboru modelu i interpretacji jego błędów.

Dane rozdziału to wbudowany w scikit-learn zbiór Breast Cancer Wisconsin: 569 guzów opisanych trzydziestoma cechami wyliczonymi z obrazu mikroskopowego, z diagnozą złośliwy lub łagodny. To zadanie, w którym rodzaj błędu ma znaczenie: przeoczenie guza złośliwego kosztuje więcej niż niepotrzebne dalsze badanie — dlatego rozdział konsekwentnie traktuje nowotwór złośliwy jako klasę pozytywną. Do miar wieloklasowych wraca zbiór wine z rozdziału 7.

Rozdział buduje na całym rozdziale 7 (podział, potok, walidacja krzyżowa, `GridSearchCV`, przeuczenie) oraz na rozdziałach 2 i 3 tej części; wersje bibliotek są takie same jak tam — scikit-learn 1.9.1, pandas 3.0.5, Matplotlib 3.11.2 — i plik wymagań nie wymaga zmian.

---

## W tym rozdziale

1. [Miary klasyfikacji](miary.md) — macierz pomyłek, precyzja, czułość i F1, próg decyzyjny, krzywa ROC i AUC, klasy nierównoliczne, wiele klas
2. [Regresja logistyczna](regresja-logistyczna.md) — model liniowy dla klasyfikacji, współczynniki i iloraz szans, regularyzacja, wiele klas, granica liniowa
3. [Drzewa decyzyjne i lasy losowe](drzewa-i-lasy.md) — drzewo i jego reguły, głębokość i przeuczenie, ważność cech, las losowy, wzmacnianie gradientowe
4. [Wybór modelu i interpretacja](wybor-i-interpretacja.md) — porównanie modeli wieloma miarami, ważność permutacyjna, analiza błędów, próg według kosztu, model końcowy
