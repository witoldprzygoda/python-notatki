# Część II — Biblioteki Pythona (zarys strategii)

Decyzja autora z 13 IX 2026: część I książki (kurs języka) kończy się rozdziałem 16 „Warsztat programisty i dalsza droga”. Rozdziały 17 (pandas) i 18 (tkinter) z `PLAN_ROZWOJU.md` przechodzą do części II; ich projekty pozostają w planie jako punkt wyjścia. Szczegółowy plan części II powstanie po domknięciu części I.

## Założenia

- Ten sam serwis i repozytorium: wspólne konwencje redakcyjne, harness `scripts/verify_page.py`, odsyłacze względne; w nawigacji osobna sekcja „Część II — Biblioteki” z własną numeracją (do rozstrzygnięcia).
- Rozdziały pogrupowane w ścieżki, nie w jeden ciąg; ścieżki aplikacji i automatyzacji są niezależne od ścieżki danych i mogą być realizowane wybiórczo.
- Osobne środowisko wirtualne na rozdział z zapisem wersji pakietów; wersje weryfikowane przy pisaniu każdego rozdziału.
- Harness rozszerzony o pakiety zewnętrzne (venv rozdziału) i o wykresy generowane skryptem do `img/` (wzorzec z rozdziału 14).
- Kryterium doboru: najpierw to, czego wymagają zajęcia i kierunek studiów, potem umiejętności ogólne (dane, WWW, interfejs, automatyzacja).

## Ścieżki i rozdziały (propozycja)

| Ścieżka | Rozdziały | Uwagi |
|---|---|---|
| Warsztat pracy z bibliotekami (otwierający) | notatniki Jupyter w VSC; środowisko na projekt z przypiętymi wersjami; czytanie dokumentacji API; reguła „najpierw biblioteka standardowa” | 1 rozdział |
| Ścieżka danych (rdzeń części II) | NumPy w pełnym zakresie (rozwinięcie rozdziału 14); Matplotlib w pełnym zakresie; pandas (Series/DataFrame, CSV/Excel/JSON, groupby, łączenie) — z projektu rozdziału 17; SciPy w wyborze (statystyka, optymalizacja); scikit-learn — pierwsze kroki | 4–5 rozdziałów; kolejność według zależności |
| Ścieżka aplikacji | bazy danych (`sqlite3`, potem SQLAlchemy); HTTP i API (requests/httpx, JSON); backend WWW (Flask lub FastAPI — jeden wybrany); interfejs graficzny (tkinter — z projektu rozdziału 18; PySide jako nota); pakowanie do `.exe` (PyInstaller) i publikacja pakietu | 4–5 rozdziałów |
| Ścieżka automatyzacji | wyrażenia regularne (`re`, pytanie otwarte nr 2 planu); narzędzia wiersza poleceń (argparse/typer, rich); pobieranie i parsowanie stron (Beautiful Soup); pliki Office i obrazy (openpyxl, Pillow) | 2–3 rozdziały |

## Zapowiedzi z części I do domknięcia w części II

- Rozdział 14, `ndarray.md` (Zapis i odczyt): pandas — tabele danych z nazwanymi kolumnami.
- Rozdział 14, `przyklady-i-rozszerzenia.md` (SciPy): SciPy i scikit-learn w pełnym zakresie.
- Rozdział 15, `synchronizacja.md` (Wątki a interfejs graficzny): tkinter — `after()` i kolejka w programie okienkowym.

## Do rozstrzygnięcia przez autora

1. Część II w tym serwisie (sekcja nawigacji) czy jako osobny serwis.
2. Które ścieżki wchodzą do pierwszego wydania części II.
3. Numeracja rozdziałów części II (kontynuacja od 17 czy osobna, np. II.1).
