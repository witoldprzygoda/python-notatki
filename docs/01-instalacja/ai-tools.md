# Narzędzia AI

Zastosowanie narzędzi sztucznej inteligencji (ang. *artificial intelligence*, AI) w programowaniu, a zwłaszcza w jego nauce, jest obszarem rozwijającym się bardzo szybko. Podrozdział przedstawia stan z października 2026 roku i ogranicza się do zasad oraz podstawowych funkcji; szczegóły interfejsów zmieniają się co kilka miesięcy, dlatego w razie rozbieżności rozstrzyga aktualna dokumentacja producenta.

Narzędzia typu ChatGPT czy Claude wygenerują bez trudu dowolny kod, który będzie np. rozwiązaniem zadania, a nawet gotowym kodem projektu.

!!! warning "W ten sposób niczego się nie nauczymy"
    Korzystanie z gotowych rozwiązań nie buduje jednak umiejętności programowania.
    Nie oznacza to, że takich narzędzi należy unikać — wręcz przeciwnie; istotny
    jest sposób ich używania: jako pomocy w zrozumieniu materiału, nie jako
    zastępstwa własnej pracy.

## Rodzaje narzędzi

Narzędzia AI wspierające programistę tworzą trzy grupy:

- **asystenci czatowi** — usługi prowadzące rozmowę w przeglądarce lub w osobnej aplikacji (np. ChatGPT, Claude); kod przenosimy między czatem a edytorem samodzielnie,
- **asystenci w edytorze** — podpowiadają kod w trakcie pisania i prowadzą rozmowę w panelu edytora, z dostępem do plików projektu (np. GitHub Copilot w VSC),
- **agenci kodujący** (ang. *coding agents*) — na podstawie opisu zadania samodzielnie planują i wykonują kolejne kroki: zmieniają pliki, uruchamiają polecenia i testy, poprawiają napotkane błędy; działają w edytorze albo w terminalu.

Wszystkie trzy grupy korzystają z **dużych modeli językowych** (ang. *large language models*, LLM), które generują tekst — w tym kod — na podstawie wzorców wyuczonych z ogromnych zbiorów danych. Z tego źródła wynikają cechy wspólne wszystkim narzędziom, omówione w ostatniej sekcji: odpowiedź bywa błędna mimo pewnego tonu, a to samo pytanie zadane ponownie daje zwykle nieco inną odpowiedź.

Dalej omawiamy GitHub Copilot, ponieważ działa bezpośrednio w VSC — edytorze używanym w tej książce — i jest dostępny bezpłatnie.

## GitHub Copilot w VSC

### Dostęp i uruchomienie

Copilot wymaga konta w serwisie **GitHub**. Użytkownik bez wykupionej subskrypcji otrzymuje plan **Copilot Free** z miesięcznymi limitami podpowiedzi i zapytań. Zweryfikowani studenci korzystają bezpłatnie z planu **Copilot Student**: status studenta potwierdza się w programie GitHub Education ([github.com/education](https://github.com/education)), a uprawnienie jest sprawdzane co miesiąc. Bieżący zakres i limity planów opisuje [dokumentacja GitHub](https://docs.github.com/en/copilot/get-started/plans).

Aby włączyć Copilota, wskazujemy jego ikonę na pasku stanu u dołu okna VSC, wybieramy **Use AI Features** i logujemy się kontem GitHub.

### Podpowiedzi w trakcie pisania

Podczas pisania Copilot proponuje dalszy ciąg kodu, wyświetlany szarym tekstem za kursorem (ang. *ghost text*). Podpowiedź powstaje na podstawie kontekstu: komentarza, nazw i otaczającego kodu. Przykładowo, po wpisaniu w pliku Pythona komentarza:

```{ .python .no-copy }
# wypisz kwadraty liczb od 1 do 5
```

Copilot zaproponuje kilka wierszy realizujących opis; ich dokładna postać może się różnić przy kolejnych próbach. Podpowiedź obsługujemy klawiszami:

- ++tab++ — przyjęcie całej podpowiedzi,
- ++esc++ — odrzucenie,
- ++ctrl+right++ — przyjęcie tylko następnego słowa.

Oprócz dopisywania kodu w miejscu kursora Copilot przewiduje także następną zmianę w innym miejscu pliku (ang. *next edit suggestions*) — np. po zmianie nazwy zmiennej w jednym wierszu proponuje poprawienie pozostałych wystąpień. Dostępność takiej podpowiedzi sygnalizuje strzałka na marginesie edytora; ++tab++ przenosi do niej kursor i ją przyjmuje.

Podpowiedzi można czasowo wstrzymać poleceniem **Snooze** z menu Copilota na pasku stanu — każde użycie wydłuża przerwę o pięć minut. Wszystkie funkcje AI w VSC wyłącza ustawienie w pliku `settings.json` (otwieranie tego pliku opisuje sekcja [Usuwanie Pylance](konfiguracja.md#usuwanie-pylance)):

```json title="settings.json"
"chat.disableAIFeatures": true
```

### Czat i agenci

Rozmowę z Copilotem prowadzimy w widoku czatu (++ctrl+alt+i++) albo bezpośrednio w edytorze: czat w wierszu (ang. *inline chat*, ++ctrl+i++) dotyczy zaznaczonego fragmentu kodu. W widoku czatu wybieramy jednego z wbudowanych agentów:

- **Ask** — odpowiada na pytania i objaśnia kod, nie zmieniając plików,
- **Plan** — przygotowuje plan zmian i zadaje pytania doprecyzowujące; gotowy plan można przekazać do realizacji,
- **Agent** — samodzielnie realizuje opisane zadanie: odnajduje potrzebne pliki, zmienia je, uruchamia polecenia w terminalu i poprawia napotkane błędy.

Zmiany wprowadzone przez agenta edytor pokazuje jako różnice względem poprzedniej treści; każdą przyjmujemy (**Keep**) albo wycofujemy (**Undo**), a polecenie **Restore Checkpoint** przywraca pliki do stanu sprzed wybranego zapytania. Polecenia uruchamiane przez agenta podlegają uprawnieniom: w ustawieniu domyślnym typowe polecenia, które jedynie odczytują dane, wykonują się samoczynnie, a pozostałe — np. usuwające pliki — wymagają naszej zgody. Ustawień zezwalających agentowi na wszystkie działania bez potwierdzenia nie włączamy.

Kontekst zapytania wskazujemy w polu czatu:

- `#` — dołączenie pliku (`#file`) albo całego projektu (`#codebase`),
- `/` — gotowe polecenia, np. `/explain` (objaśnienie zaznaczonego kodu), `/fix` (propozycja poprawki), `/tests` (propozycja testów),
- `@` — uczestnicy wyspecjalizowani w danej dziedzinie, np. `@terminal` (polecenia powłoki) czy `@vscode` (funkcje i ustawienia edytora).

Pełny i aktualny opis zawiera [dokumentacja VSC](https://code.visualstudio.com/docs/copilot/overview).

## Zasady pracy z asystentem

- **Najpierw własna próba.** Zadanie rozwiązujemy samodzielnie, a asystenta prosimy o pomoc dopiero przy konkretnej trudności — o objaśnienie komunikatu o błędzie lub pojęcia albo o wskazanie kierunku, nie o gotowe rozwiązanie. Podczas ćwiczeń wstrzymujemy podpowiedzi w edytorze.
- **Rozumienie każdego wiersza.** Przyjmujemy wyłącznie kod, który potrafimy objaśnić; fragment niezrozumiały wyjaśniamy (np. poleceniem `/explain`) albo odrzucamy.
- **Sprawdzanie wyniku.** Model językowy formułuje odpowiedzi błędne równie pewnym tonem jak poprawne: potrafi zaproponować kod z błędem logicznym, wywołanie nieistniejącej funkcji albo rozwiązanie nieaktualne. Zaproponowany kod uruchamiamy i sprawdzamy na przykładach, także nietypowych.
- **Zmienność odpowiedzi.** To samo pytanie zadane ponownie daje zwykle inną odpowiedź, ponieważ model dobiera kolejne fragmenty tekstu z określonym prawdopodobieństwem. Różne propozycje warto porównać, zamiast przyjmować pierwszą.
- **Jeden aktywny asystent.** Kilka rozszerzeń AI włączonych jednocześnie zgłasza konkurencyjne podpowiedzi w tym samym miejscu — podobnie jak Pylance i pylint, których diagnostyka się dubluje (sekcja [Usuwanie Pylance](konfiguracja.md#usuwanie-pylance)).
- **Poufność.** Treść zapytań i dołączone pliki trafiają do zewnętrznej usługi; nie przekazujemy w nich haseł, kluczy dostępowych ani danych osobowych.
