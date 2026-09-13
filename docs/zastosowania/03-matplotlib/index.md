# 3. Matplotlib w praktyce

Rozdział 14 „Python Notatki” nauczył rysować: styl obiektowy, `subplots()`, linie i znaczniki, adnotacje, wykres punktowy, słupkowy i histogram, siatka paneli, zapis do pliku. Ten rozdział uczy rysować **dobrze** — tak, aby wykres odpowiadał na pytanie o dane i nadawał się do raportu bez poprawek: sterowanie podziałkami, skalami i ramką, wykresy z niepewnością i rozkładami, daty na osi, układy wielu paneli oraz warsztat wykresu do publikacji, od stylu domowego po skrypt generujący wszystkie rysunki raportu.

Rozdział buduje na rozdziale 14 „Python Notatki” w całości oraz na rozdziałach 1 i 2 tej części — dane pochodzą z tablic NumPy i generatora z ziarnem, a wzorce pracy z notatnika i projektu danych obowiązują bez zmian. Wersje odniesienia: Matplotlib 3.11.2 i NumPy 2.5.3 na Pythonie 3.14.7, w środowisku projektu z rozdziału 1. Każdy wykres w rozdziale powstał z listingu, który go poprzedza.

---

## W tym rozdziale

1. [Anatomia wykresu i style](anatomia-wykresu.md) — obiekty rysunku, lokalizatory i formatery podziałek, skale i osie bliźniacze, ramka i siatka, `rcParams` i arkusze stylu
2. [Wykresy dla danych](wykresy-danych.md) — przedziały niepewności, słupki grupowane i skumulowane, rozkłady, zależności i nakładanie punktów
3. [Daty i szeregi czasowe](szeregi-czasowe.md) — daty NumPy na osi, formatery dat, wygładzanie i okresy, porównanie szeregów, `datetime` a `np.datetime64`
4. [Wiele paneli i układ](wiele-paneli-i-uklad.md) — małe wielokrotności, mozaika paneli, wstawki i wspólna legenda, spójne kolory, układ automatyczny a ręczny
5. [Wykres do raportu i publikacji](zapis-i-raport.md) — format i rozdzielczość, styl domowy, czytelność, PDF wielostronicowy, skrypt generujący, pułapki prezentacji
