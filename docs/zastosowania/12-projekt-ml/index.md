# 12. Projekt: od danych do modelu

Pięć rozdziałów ścieżki uczenia maszynowego dało pojęcia i warsztat, klasyfikację, regresję z przygotowaniem danych, uczenie bez nadzoru i sieci neuronowe. Projekt składa je w całość taką, jaką oddaje się w pracy: z pliku surowego o typowych wadach, przez spisane decyzje, przetestowany potok i uczciwe porównanie modeli, do zapisanego modelu z progiem dobranym do kosztu błędu, raportu i skryptu, którym odbiorca oceni nowych klientów. Rozdział nie wprowadza nowych bibliotek — wprowadza sposób pracy, w którym każda liczba w raporcie ma kod, a każda decyzja — zapis i test.

Zadanie: operator usług internetowych przekazał eksport 2000 klientów z informacją, którzy zrezygnowali w ciągu ostatniego roku, i chce co miesiąc wskazywać klientów, którym opłaca się złożyć ofertę zatrzymującą. Koszty uzgodnione z odbiorcą: utrata klienta, którego model przeoczył, kosztuje średnio 500 zł rocznego przychodu; oferta złożona każdemu wskazanemu klientowi — 80 zł. Te dwie liczby decydują o progu decyzyjnym i o tym, czy model w ogóle się opłaca wobec dwóch rozwiązań bez modelu: oferty dla wszystkich i oferty dla nikogo.

Rozdział buduje na całej ścieżce — podział, walidacja krzyżowa i zapis modelu z rozdziału 7, AUC, próg według kosztu i ważność permutacyjna z rozdziału 8, `ColumnTransformer`, imputacja i wyciek celu z rozdziału 9, sieć z rozdziału 11 — oraz na projekcie z rozdziału 6 (układ, dziennik decyzji, testy, raport Markdown); z części „Python Notatki” korzysta z rozdziałów 7 (moduły, `sys.argv`), 9 (`pathlib`) i 16 (pytest). Wersje i plik wymagań jak w rozdziale 7: scikit-learn 1.9.1, pandas 3.0.5, Matplotlib 3.11.2, pytest 9.1.1; PyTorch nie jest potrzebny.

Dane projektu — plik surowy `klienci.csv` (2010 wierszy, dane przykładowe generowane skryptem z pierwszego podrozdziału, z celowo wprowadzonymi wadami) i `nowi_klienci.csv` do oceny — są do pobrania: [klienci.csv](dane/surowe/klienci.csv), [nowi_klienci.csv](dane/nowi_klienci.csv). Wszystkie skrypty uruchamiamy z katalogu projektu, w którym leży katalog `dane/`.

---

## W tym rozdziale

1. [Zadanie, dane i decyzje](zadanie-i-dane.md) — zadanie i koszt błędu, układ projektu, plik surowy, eksploracja z wykryciem wycieku celu, dziennik decyzji
2. [Potok, modele i wybór](potok-i-modele.md) — moduł przygotowania, kandydaci i porównanie w walidacji krzyżowej, próg według kosztu, testy pytest
3. [Model końcowy, raport i użycie](model-i-raport.md) — skrypt treningowy z jednorazową oceną i pakietem modelu, raport Markdown, ocena nowych klientów z kontrolą wejścia, lista kontrolna projektu
