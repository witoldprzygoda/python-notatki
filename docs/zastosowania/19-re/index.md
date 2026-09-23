# 19. Wyrażenia regularne

Ścieżka Automatyzacja zajmuje się programami, które wykonują pracę za nas: przeszukują i porządkują teksty, obsługują wiersz poleceń, pobierają strony, czytają i piszą pliki pakietu Office i obrazy. Zaczyna się od narzędzia wspólnego dla wszystkich tych zadań. **Wyrażenie regularne** (ang. *regular expression*, w skrócie *regex*) to zapis wzorca tekstu: „cztery cyfry, myślnik, dwie cyfry”, „słowo zaczynające się wielką literą”, „wszystko między nawiasami”. Moduł `re` z biblioteki standardowej wyszukuje takie wzorce, wycina dopasowane fragmenty, dzieli tekst i zamienia — tam, gdzie metody `str` z rozdziału 3 „Python Notatki” wymagałyby kilku pętli i warunków. Rozdział 7 części „Python Notatki” odłożył ten temat jako osobną umiejętność; tu omawiamy go systematycznie.

Rozdział omawia kolejno: składnię wzorców i obiekt dopasowania, cztery operacje modułu, zastosowania — dziennik serwera z rozdziału 15, dane wyciągane z tekstu, nazwy plików, dokument Markdown — oraz pułapki: nawroty, które potrafią zatrzymać program na sekundy, i granicę, za którą wyrażenie regularne przestaje być właściwym narzędziem.

Biblioteka standardowa wystarcza — moduł `re` w Pythonie 3.14.7 (kwantyfikatory dzierżawcze i grupy atomowe istnieją od wersji 3.11, nazwa wyjątku `PatternError` od 3.13); pytest służy testom wzorców. Rozdział buduje na rozdziałach 3 (łańcuchy i metody `str`), 7 (`Counter`), 9 (pliki, `pathlib`) i 16 (pytest) części „Python Notatki” oraz na rozdziale 15 tej części (dziennik uvicorn). Plików do pobrania nie ma; dziennik przykładowy jest blokiem w tekście.

```text title="requirements.txt"
pytest==9.1.1
```

---

## W tym rozdziale

1. [Składnia wzorców](skladnia.md) — pierwsze dopasowanie, metaznaki, klasy i kwantyfikatory, zachłanność, grupy, flagi
2. [Wyszukiwanie, dzielenie i zamiana](operacje.md) — wszystkie dopasowania, dzielenie, zamiana, wzorce skompilowane i błędy
3. [Wzorce w praktyce](praktyka.md) — dziennik serwera, dane z tekstu, nazwy plików, dokument wielowierszowy
4. [Pułapki, wydajność i testy](pulapki.md) — nawroty, walidacja, testy wzorców, granice zastosowania, lista kontrolna
