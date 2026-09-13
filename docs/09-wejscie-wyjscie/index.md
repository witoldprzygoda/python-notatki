# 9. Wejście, wyjście i pliki

Program, który nie wymienia danych z otoczeniem, nie ma zastosowania. Dotąd wymiana ta ograniczała się do `print()` i `input()` z rozdziału 2, f-stringów z rozdziału 3 oraz funkcji `open()`, której w rozdziale 8 używaliśmy bez wyjaśnienia. Ten rozdział jest przekrojowy: zaczyna od tego, jak liczby i tekst mają wyglądać na ekranie — pełnego mini-języka formatowania — a kończy na formatach danych, w których programy wymieniają informacje z arkuszami kalkulacyjnymi i aplikacjami. Po drodze przechodzi przez strumienie standardowe i terminal, pliki tekstowe z kodowaniem znaków, pliki binarne i bajty oraz ścieżki i katalogi.

Wspólny model rozdziału to **strumień tekstowy**: obiekt, do którego `print()` pisze i z którego `input()` czyta, niezależnie od tego, czy po drugiej stronie jest ekran terminala, plik na dysku, potok do innego programu czy bufor w pamięci. Między strumieniem a światem stoi kodowanie, zamieniające znaki na bajty — najczęstsze źródło problemów z plikami na Windows, dlatego poświęcamy mu osobną, dokładną sekcję. Podrozdział o animacjach w terminalu ma charakter uzupełniający: rozwija materiał z notatek kursu i można go pominąć przy pierwszej lekturze.

Rozdział domyka zapowiedzi z rozdziału [8. Wyjątki i zarządzanie zasobami](../08-wyjatki/index.md) — pełne omówienie `open()`, `redirect_stdout()` i `chdir()`, dziennik `logging` w pliku, operator `%` — oraz sygnaturę `print()` z rozdziału 2 i typy binarne z katalogu typów rozdziału 3.

---

## W tym rozdziale

1. [Formatowanie tekstu](formatowanie.md) — pola f-stringów, mini-język specyfikacji formatu, tabele, `format()` i `str.format()`, operator `%`, t-stringi i `pprint`
2. [Funkcja print i strumienie](print-i-strumienie.md) — sygnatura `print()`, znaki sterujące, strumienie standardowe i przekierowania, kodowanie strumieni, buforowanie, `file=` i `redirect_stdout()`, `input()` i koniec wejścia
3. [Animacje w terminalu](animacje-w-terminalu.md) — podrozdział uzupełniający: nadpisywanie wiersza, wskaźnik postępu, piłeczka, sekwencje ANSI
4. [Pliki tekstowe](pliki-tekstowe.md) — tryby otwarcia, odczyt i zapis, kodowanie i strona kodowa, BOM, `errors=`, `newline`, dziennik w pliku, `seek()` i `tell()`
5. [Typ bytes i pliki binarne](bytes-i-pliki-binarne.md) — znaki a bajty, `bytes`, `bytearray`, `memoryview`, tryby `rb`/`wb`, sygnatury plików, `struct`, `io.StringIO` i `io.BytesIO`
6. [Ścieżki i system plików](pathlib.md) — `Path`, katalog roboczy, przeglądanie katalogów, kopiowanie i usuwanie, `read_text()` i `write_text()`, `os`, `shutil` i `tempfile`
7. [Formaty danych — CSV i JSON](csv-i-json.md) — `csv` z `newline=""`, `DictReader` i `DictWriter`, pliki z Excela, `json`, `python -m json`, zapis stanu programu, `tomllib`, `pickle` i `compression`
