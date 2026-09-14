# 7. Uczenie maszynowe — pojęcia i warsztat

Ścieżka danych nauczyła opisywać to, co już się zdarzyło: ile sprzedano, w których miesiącach, komu. **Uczenie maszynowe** (ang. *machine learning*) stawia inne pytanie — czego z tych danych można się nauczyć o przypadkach, których jeszcze nie widzieliśmy: do jakiego gatunku należy roślina o zmierzonych wymiarach, ile wyniesie sprzedaż w następnym miesiącu, które zamówienia odbiegają od reszty. Zamiast reguł spisanych przez programistę model dostaje przykłady i sam znajduje w nich zależność, którą potem stosuje do nowych danych.

Ten rozdział otwiera ścieżkę uczenia maszynowego i daje jej wspólne podstawy: pojęcia, którymi posługują się wszystkie kolejne rozdziały; pierwszy kompletny model — od danych do predykcji dla nowej obserwacji; warsztat biblioteki scikit-learn, w której każdy model ma ten sam interfejs; oraz zasady uczciwej oceny, bez których wynik modelu jest złudzeniem. Rozdziały 8–10 omawiają klasyfikację, regresję z przygotowaniem danych i uczenie bez nadzoru, rozdział 11 sieci neuronowe w PyTorch, a rozdział 12 zamyka ścieżkę projektem.

Rozdział zakłada ścieżkę danych: tablice i generator z ziarnem z rozdziału 2, wykresy z rozdziału 3, ramki pandas z rozdziałów 4–5 i potok z testami z rozdziału 6; z części „Python Notatki” korzysta z rozdziałów 8 (instrukcja `with`), 9 (`pickle`) i 14 (NumPy). Biblioteka **scikit-learn** w wersji 1.9.1 pociąga za sobą między innymi SciPy 1.18.1 i joblib 1.6.0; dane rozdziału to zbiory wbudowane w bibliotekę, więc nie ma plików do pobrania. Do pliku wymagań projektu dopisujemy jeden wiersz:

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
scikit-learn==1.9.1
```

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

---

## W tym rozdziale

1. [Pojęcia uczenia maszynowego](pojecia.md) — reguły a dane, zadania, cechy i etykiety, model i trening na przykładzie klasyfikatora z NumPy, uogólnianie, słownik pojęć
2. [Pierwszy model od początku do końca](pierwszy-model.md) — zbiór iris, podział na zbiory, `KNeighborsClassifier`, ocena i model bazowy, nowe obserwacje, granica decyzyjna
3. [Warsztat scikit-learn](warsztat.md) — estymator, transformatory i potok, walidacja krzyżowa, `GridSearchCV`, zapis modelu, powtarzalność
4. [Przeuczenie i uczciwa ocena](przeuczenie-i-ocena.md) — niedouczenie i przeuczenie, krzywa walidacji, krzywa uczenia, wyciek danych, mapa wyboru modelu
