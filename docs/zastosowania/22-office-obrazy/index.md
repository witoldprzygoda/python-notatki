# 22. Pliki Office i obrazy

Wynik automatyzacji trafia najczęściej do odbiorcy, który nie uruchomi skryptu: oczekuje arkusza Excela z gotowymi formułami, dokumentu Word z tabelą i wykresem albo obrazów w ustalonym rozmiarze. Rozdział 4 tej części zapisywał tabele pandas do Excela jedną metodą; rozdział 16 wczytywał obrazy do okna. Ten rozdział sięga po biblioteki, które realizują te operacje, i pokazuje, jak programem tworzyć, formatować i czytać pliki pakietu Office oraz przetwarzać obrazy.

Trzy biblioteki, każda z jednym zadaniem: **openpyxl** pisze i czyta pliki `.xlsx` — komórki, formuły, formaty, wykresy; **python-docx** buduje i czyta dokumenty `.docx` — nagłówki, akapity, tabele, obrazy; **Pillow** otwiera, przekształca i rysuje obrazy — miniatury, przycięcia, znaki wodne, proste wykresy. Rozdział kończy narzędzie wiersza poleceń według reguł z rozdziału 20, które z pliku CSV tworzy arkusz z podsumowaniem i wykresem oraz dokument z tabelą i obrazem, wraz z testami otwierającymi wytworzone pliki z powrotem. Przykłady pracują na niewielkiej tabeli sprzedaży zapisanej w CSV; obrazy skrypty rysują same, więc nic nie trzeba pobierać.

Rozdział buduje na rozdziałach 7 (`defaultdict`), 9 (CSV, `pathlib`), 14 (matplotlib) i 16 (pytest) części „Python Notatki” oraz 4 (pandas i Excel), 16 (obrazy w tkinter), 20 (narzędzia wiersza poleceń) i 21 (rekordy z CSV) tej części.

```text title="requirements.txt"
openpyxl==3.1.5
python-docx==1.2.0
pillow==12.3.0
pytest==9.1.1
```

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

```text title="sprzedaz.csv"
data,produkt,kategoria,ilosc,cena
2026-09-01,Czajnik elektryczny,AGD,3,149.00
2026-09-01,Toster dwukomorowy,AGD,2,199.00
2026-09-02,Waga kuchenna,Akcesoria,5,69.99
2026-09-02,Ekspres przelewowy,AGD,1,329.90
2026-09-03,Mikser ręczny,AGD,2,119.50
2026-09-03,Deska do krojenia,Akcesoria,4,39.90
2026-09-04,Robot planetarny,AGD,1,1299.00
2026-09-04,Zestaw noży,Akcesoria,2,189.00
2026-09-05,Blender kielichowy,AGD,2,259.00
2026-09-05,Termos,Akcesoria,6,59.00
2026-09-06,Frytkownica beztłuszczowa,AGD,1,449.00
2026-09-06,Waga kuchenna,Akcesoria,3,69.99
```

---

## W tym rozdziale

1. [Arkusze Excel](excel.md) — zapis arkusza, odczyt arkusza, podsumowanie i wykres, arkusz a pandas
2. [Dokumenty Word](word.md) — budowa dokumentu, odczyt i szablon, format i konwersja
3. [Obrazy](obrazy.md) — otwieranie i przekształcenia, rysowanie i znak wodny, wykres słupkowy, przetwarzanie wsadowe
4. [Raport z danych](raport.md) — narzędzie raport, testy, inne formaty, lista kontrolna
