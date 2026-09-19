# 14. HTTP i API

Warstwa danych z rozdziału 13 działa w jednym procesie na jednej maszynie. Aplikacje, z których korzystają inni, komunikują się przez sieć, a wspólną podstawą tej komunikacji jest **HTTP** (ang. *Hypertext Transfer Protocol*): protokół, którym przeglądarka pobiera strony, a programy wymieniają dane w formacie JSON. Program może być po obu stronach: jako **klient** pyta usługi o kursy walut, pogodę czy stan zamówienia, jako **serwer** udostępnia własne dane innym programom przez **interfejs API** (ang. *application programming interface*).

Rozdział zaczyna od samego protokołu: co dokładnie jest przesyłane, gdy program prosi o dane, i jak wygląda odpowiedź. Serwer piszemy najpierw w bibliotece standardowej — moduł `http.server` z trasami, kodami stanu i odpowiedziami JSON — żeby zobaczyć, co w rozdziale 15 przejmie framework FastAPI. Klientem jest biblioteka **httpx** (wersja 0.28.1) — nowsza od popularnej biblioteki `requests`, o niemal identycznym interfejsie, używana przez FastAPI w testach. Rozdział zamyka klient API jako moduł z własnymi wyjątkami, ponawianiem i testami bez sieci oraz zasady projektowania interfejsu, które serwer z rozdziału spełnia.

Dane rozdziału to sklep w pamięci lokalnego serwera — trzy produkty i składane do nich zamówienia — oraz jedno prawdziwe API: kursy walut Narodowego Banku Polskiego, dostępne bez klucza. Plików do pobrania nie ma. Rozdział buduje na rozdziałach 8 (wyjątki, `with`), 9 (JSON), 10 (klasy, własne wyjątki), 15 (wątki, `urllib.request`) i 16 (pytest, atrapy) części „Python Notatki” oraz na rozdziale 13 tej części. Do pliku wymagań dopisujemy jeden wiersz:

```text title="requirements.txt"
pandas==3.0.5
pytest==9.1.1
sqlalchemy==2.0.54
httpx==0.28.1
```

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

---

## W tym rozdziale

1. [Protokół HTTP](protokol.md) — żądanie i odpowiedź, protokół w surowej postaci, adresy URL, metody i kody stanu, nagłówki i treść
2. [Serwer w bibliotece standardowej](serwer.md) — trasy i odpowiedzi JSON, pierwsze żądania, błędy jako odpowiedzi, uruchomienie z terminala
3. [Klient HTTP — httpx](klient.md) — żądanie GET, klient i połączenia, błędy sieci i limit czasu, duże odpowiedzi, prawdziwe API kursów walut
4. [Interfejs API w praktyce](api.md) — zasady REST, moduł klienta API z ponawianiem, testy z atrapą transportu, klucze i konfiguracja, lista kontrolna
