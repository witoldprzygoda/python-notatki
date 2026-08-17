# Notebook

Innym bardzo popularnym rozwiązaniem rozwijania kodu w Pythonie jest **Jupyter Notebook** ([jupyter.org](https://jupyter.org/)), który ma formę serwera uruchamianego na naszym komputerze, a edycja najczęściej odbywa się w przeglądarce internetowej.

Jeśli ktoś decyduje się na taką strategię używania Pythona, to zazwyczaj wykonuje instalację poprzez pakiet **Anaconda** ([anaconda.com](https://www.anaconda.com/download)), który ma własną strategię zarządzania pakietami o nazwie **Conda** ([docs.conda.io](https://docs.conda.io/en/latest/)).

Ponieważ mamy zainstalowany Python w klasycznym podejściu, możemy w ten sposób zainstalować Jupyter Notebook:

```bash title="Terminal"
python -m pip install notebook
```

co skutkuje zainstalowaniem pokaźnej liczby pakietów. Następnie, również w terminalu, uruchamiamy serwer:

```bash title="Terminal"
jupyter notebook
```

Powinna otworzyć się domyślna przeglądarka — jeśli nie, to trzeba otworzyć samemu i w polu adresowym wkleić podany na końcu w terminalu adres.

<!-- TODO: screenshot — interfejs Jupyter Notebook w przeglądarce -->

Jak widać na rozwiniętym menu, można rozpocząć nowy Notebook.

<!-- TODO: screenshot — menu New → Notebook -->

W kolejnych polach można pisać kod Pythona lub dokumentację, oraz uruchamiać (**Run**). Takie podejście jest bardzo popularne w szeroko pojętej analizie i przetwarzaniu danych. Notebook można zapisać (pliki z rozszerzeniem `.ipynb`).
