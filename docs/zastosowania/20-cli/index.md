# 20. Narzędzia wiersza poleceń

Program automatyzujący pracę najczęściej nie ma okna: uruchamia się go z terminala, z argumentami, w potoku z innymi programami albo z harmonogramu zadań. Rozdział 7 „Python Notatki” wprowadził `argparse`, pomoc generowaną z opisu argumentów i kody wyjścia, a rozdział 17 tej części — podpolecenia i instalację polecenia z pakietu. Ten rozdział zbiera pozostałe składniki **narzędzia wiersza poleceń** (ang. *command-line tool*): opcje, które zachowują się tak, jak użytkownik terminala oczekuje, strumienie i kody wyjścia pozwalające łączyć narzędzia w potoki, dziennik na `stderr`, uruchamianie innych programów, konfigurację z pliku i środowiska oraz testy, które sprawdzają narzędzie bez terminala.

Dwa narzędzia towarzyszą całemu rozdziałowi: `porzadek` porządkuje pliki w katalogu według rozszerzenia albo daty, z **próbnym uruchomieniem** (ang. *dry run*) i dziennikiem, a `licznik` jest filtrem tekstu — liczy wiersze, słowa i dopasowania wzorca w plikach albo na wejściu standardowym, jak narzędzia systemowe. Oba są zwykłymi skryptami z funkcją `main(argv)`, więc da się je wywołać z testu, uruchomić jako proces potomny i zainstalować jako polecenie.

Rozdział korzysta wyłącznie z biblioteki standardowej (`argparse`, `sys`, `logging`, `pathlib`, `shutil`, `subprocess`, `tempfile`, `tomllib`); pytest służy testom. Buduje na rozdziałach 7 (`argparse`, kody wyjścia), 8 (`logging`), 9 (strumienie, `pathlib`, `shutil`, `tomllib`) i 16 (pytest) części „Python Notatki” oraz na rozdziałach 17 (punkty wejścia) i 19 (wzorce) tej części. Plików do pobrania nie ma — pliki przykładowe tworzą skrypty.

```text title="requirements.txt"
pytest==9.1.1
```

---

## W tym rozdziale

1. [Argumenty i opcje](argumenty.md) — narzędzie porządkujące, uruchomienie i pomoc, reguły projektowania opcji
2. [Strumienie, kody wyjścia i dziennik](strumienie.md) — filtr tekstu, potoki i kody wyjścia, dziennik na `stderr`, kodowanie na Windows
3. [Procesy, pliki i konfiguracja](procesy.md) — procesy potomne, archiwa i narzędzia systemowe, źródła konfiguracji
4. [Od skryptu do polecenia](narzedzie.md) — testy narzędzia, polecenie w pakiecie, alternatywy, lista kontrolna
