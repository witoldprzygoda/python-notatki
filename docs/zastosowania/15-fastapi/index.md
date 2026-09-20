# 15. FastAPI

Serwer w `http.server` z rozdziału 14 pokazał każdy element interfejsu API, ale każdy trzeba było napisać ręcznie: rozbiór ścieżki, dekodowanie JSON-a, sprawdzanie pól, kody błędów, nagłówki. **Framework webowy** (ang. *web framework*) przejmuje te obowiązki i zostawia programiście decyzje z dziedziny: co jest zasobem, jakie dane przyjmuje i co zwraca. **FastAPI** wyprowadza wszystko z definicji funkcji Pythona: adnotacje typów z rozdziału 3 „Python Notatki” stają się walidacją parametrów, klasa modelu — opisem treści żądania i odpowiedzi, a dokumentacja interfejsu powstaje z kodu i jest dostępna w przeglądarce.

Rozdział zaczyna od aplikacji z trzema trasami, uruchomienia jej serwerem uvicorn i obejrzenia dokumentacji. Druga strona wprowadza bibliotekę **Pydantic**, na której FastAPI opiera modele danych: ograniczenia pól, komunikaty walidacji, modele zagnieżdżone. Trzecia strona przepisuje serwer sklepu z rozdziału 14 — klient napisany tam działa z nową aplikacją bez zmian. Czwarta łączy aplikację z warstwą danych z rozdziału 13: sesja bazy na każde żądanie, zamówienia zapisywane w SQLite, a na koniec model uczenia maszynowego udostępniony jako usługa. Ostatnia strona testuje aplikację bez uruchamiania serwera i omawia uruchomienie u odbiorcy.

Wersje w chwili pisania: FastAPI 0.141.1, Pydantic 2.13.5, uvicorn 0.53.0 (serwer), Starlette 1.6.0 (podstawa FastAPI, instalowana razem z nim). Klient testowy FastAPI opiera się na pakiecie **httpx2** — następcy biblioteki httpx wydanym pod nową nazwą, o tym samym interfejsie; z samym httpx 0.28 działa, ale ostrzega o wycofaniu. Pakiet `scikit-learn` jest potrzebny tylko w sekcji „Model za API”. Dane to sklep z rozdziałów 13–14 — najpierw w pamięci, potem w bazie z modułów `modele.py`, `baza.py`, `operacje.py` i `dane_przykladowe.py` z rozdziału 13, które kopiujemy do katalogu projektu; strona trzecia korzysta też z modułu `sklep_api.py` z rozdziału 14. Rozdział buduje na rozdziałach 3 (adnotacje typów), 6 (dekoratory, generatory), 8 (wyjątki, `with`), 9 (JSON, zmienne środowiskowe), 10 (klasy, własne wyjątki), 12 (klasy danych), 15 (wątki) i 16 (pytest) części „Python Notatki” oraz na rozdziałach 13 i 14 tej części. Do pliku wymagań dopisujemy cztery wiersze:

```text title="requirements.txt"
pandas==3.0.5
pytest==9.1.1
sqlalchemy==2.0.54
httpx==0.28.1
fastapi==0.141.1
uvicorn==0.53.0
httpx2==2.13.0
scikit-learn==1.9.1
```

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

---

## W tym rozdziale

1. [Pierwsza aplikacja](pierwsza-aplikacja.md) — aplikacja i trasy, pierwsze żądania, uruchomienie serwera, dokumentacja interfejsu, klient testowy
2. [Modele danych — Pydantic](modele.md) — model i walidacja, treść żądania i model odpowiedzi, modele zagnieżdżone i schematy
3. [Serwer sklepu](sklep.md) — trasy w routerach i własne błędy, żądania do sklepu, klient z rozdziału 14, porównanie z `http.server`
4. [API nad warstwą danych](baza.md) — silnik przy starcie i sesja na żądanie, zamówienia w bazie, model za API
5. [Testy i uruchomienie](testy-i-uruchomienie.md) — testy z klientem testowym, uruchomienie u odbiorcy (opcje serwera, konfiguracja i dziennik), lista kontrolna
