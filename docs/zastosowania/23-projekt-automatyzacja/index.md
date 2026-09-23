# 23. Projekt: narzędzie automatyzujące

Ścieżka Automatyzacja kończy się narzędziem, które łączy jej cztery rozdziały w jeden program uruchamiany bez udziału człowieka. **Monitor cen** pobiera ceny produktów ze sklepu internetowego, zapisuje każdy pomiar w bazie, porównuje kolejne pomiary — zmiany cen, produkty nowe i brakujące — i tworzy raport: arkusz Excel z cenami dwóch ostatnich pomiarów, zmianami i wykresem oraz dokument Word z podsumowaniem. Narzędzie ma podpolecenia, kody wyjścia i dziennik, instaluje się jako polecenie i uruchamia z harmonogramu zadań systemu.

Sklepem jest strona testowa z rozdziału 21 podawana przez lokalny serwer, a zmianę cen między pomiarami symuluje skrypt, który podmienia ceny w plikach HTML wzorcem z rozdziału 19. Pobieranie z uprzejmością i rozbiór stron pochodzą wprost z rozdziału 21 — dwa moduły kopiujemy bez zmian — arkusz i dokument powstają jak w rozdziale 22, a interfejs wiersza poleceń stosuje reguły z rozdziału 20 i podpolecenia z rozdziału 17. Nowe są trzy moduły: historia pomiarów w SQLite (rozdział 13), analiza zmian i raport.

Z części „Python Notatki” rozdział korzysta z rozdziałów 5 (zbiory), 7 (`__main__`) i 16 (pytest). Projekt zamyka ścieżkę i całą część „Python Zastosowania”.

```text title="requirements.txt"
httpx==0.28.1
beautifulsoup4==4.15.0
openpyxl==3.1.5
python-docx==1.2.0
pytest==9.1.1
```

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

---

## W tym rozdziale

1. [Założenia i architektura](architektura.md) — wymagania, przepływ danych, układ pakietu, pliki z rozdziału 21, konfiguracja pakietu
2. [Moduły narzędzia](moduly.md) — historia pomiarów, analiza zmian, raport, wiersz poleceń, przebieg
3. [Testy i wdrożenie](testy-i-wdrozenie.md) — testy, instalacja polecenia, harmonogram zadań, dziennik w pliku, lista kontrolna, zakończenie części
