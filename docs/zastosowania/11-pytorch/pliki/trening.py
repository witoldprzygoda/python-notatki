"""Pętla treningowa dla modeli PyTorch — moduł rozdziału 11."""

import torch


def trenuj(model, dane, strata, epoki, lr=0.001, X_wal=None, y_wal=None, cierpliwosc=None, weight_decay=0.0):
    """Trenuje model optymalizatorem Adam na porcjach z DataLoadera `dane`.

    Zwraca historię strat: średnią stratę treningową każdej epoki oraz — gdy podano
    X_wal i y_wal — stratę walidacyjną. Z `cierpliwosc` przerywa trening, gdy strata
    walidacyjna nie maleje przez tyle epok z rzędu, i przywraca najlepsze wagi.
    """
    optymalizator = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    historia = {"trening": [], "walidacja": []}
    najlepsza, najlepsze_wagi, bez_poprawy = float("inf"), None, 0
    for _ in range(epoki):
        model.train()
        suma = 0.0
        for X_porcja, y_porcja in dane:
            optymalizator.zero_grad()
            wartosc = strata(model(X_porcja), y_porcja)
            wartosc.backward()
            optymalizator.step()
            suma += wartosc.item() * len(X_porcja)
        historia["trening"].append(suma / len(dane.dataset))
        if X_wal is None:
            continue
        wartosc_wal = strata(przewiduj(model, X_wal), y_wal).item()
        historia["walidacja"].append(wartosc_wal)
        if wartosc_wal < najlepsza:
            najlepsza, bez_poprawy = wartosc_wal, 0
            najlepsze_wagi = {nazwa: tensor.clone() for nazwa, tensor in model.state_dict().items()}
        elif cierpliwosc is not None:
            bez_poprawy += 1
            if bez_poprawy >= cierpliwosc:
                break
    if cierpliwosc is not None and najlepsze_wagi is not None:
        model.load_state_dict(najlepsze_wagi)
    return historia


def przewiduj(model, X):
    """Wynik modelu w trybie oceny, bez śledzenia gradientów."""
    model.eval()
    with torch.no_grad():
        return model(X)
