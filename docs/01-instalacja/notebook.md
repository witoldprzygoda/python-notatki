# Notebook

Innym bardzo popularnym rozwiązaniem rozwijania kodu w Pythonie jest **Jupyter Notebook** ([jupyter.org](https://jupyter.org/)), który ma formę serwera uruchamianego na własnym komputerze, a edycja odbywa się najczęściej w przeglądarce internetowej.

Osoby decydujące się na taką strategię pracy z Pythonem zazwyczaj wykonują instalację poprzez pakiet **Anaconda** ([anaconda.com](https://www.anaconda.com/download)), który ma własną strategię zarządzania pakietami o nazwie **Conda** ([docs.conda.io](https://docs.conda.io/en/latest/)).

Ponieważ dysponujemy już lokalnym interpreterem, Jupyter Notebook możemy zainstalować bezpośrednio — najlepiej w aktywnym środowisku wirtualnym projektu (opis w podrozdziale [Wirtualne środowisko venv](venv.md)), gdyż instalacja pociąga za sobą znaczną liczbę pakietów zależnych:

```powershell title="Terminal"
python -m pip install notebook
```

Następnie, również w terminalu, uruchamiamy serwer:

```powershell title="Terminal"
jupyter notebook
```

Powinna otworzyć się domyślna przeglądarka — jeżeli tak się nie stanie, należy otworzyć ją samodzielnie i w polu adresowym wprowadzić adres wypisany na końcu komunikatów w terminalu.

<!-- TODO: screenshot — interfejs Jupyter Notebook w przeglądarce -->

Nowy notebook rozpoczynamy poleceniem menu **New → Notebook**.

<!-- TODO: screenshot — menu New → Notebook -->

W kolejnych polach można pisać kod Pythona lub dokumentację oraz uruchamiać je (**Run**). Takie podejście jest bardzo popularne w szeroko pojętej analizie i przetwarzaniu danych. Notebook można zapisać (pliki z rozszerzeniem `.ipynb`).
