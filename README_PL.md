# Alpha221: algorytm genetyczny do optymalizacji portfela

Projekt z kursu sztucznej inteligencji na Collegium Da Vinci, informatyka, grupa L2 / L3, rok akademicki 2026/2027.

[English README](README.md) | [Karta tematu](karta-tematu.md) | [Project card in English](project_card_en.md)

## Co robi projekt

Program pomaga porównać sposoby podziału kapitału między wybrane akcje. Wczytuje historyczne ceny dzienne i limit ryzyka, a następnie proponuje wagi spółek oraz szacuje zwrot i ryzyko. Może użyć lokalnego pliku CSV albo syntetycznych danych demonstracyjnych. Zbioru danych rynkowych jeszcze nie wybraliśmy.

## Technika AI

Program używa algorytmu genetycznego do przeszukiwania możliwych wag portfela z uwzględnieniem limitu ryzyka. Porównuje wynik z optymalizatorem Markowitza i prostym portfelem równoważonym. Obecny szkielet w Pythonie zawiera główny algorytm i oba punkty odniesienia.

## Wyniki

Nie oceniliśmy jeszcze algorytmu na licencjonowanych danych rynkowych. Naszym celem jest zwracanie wyłącznie portfeli spełniających limit ryzyka i osiągnięcie mediany zwrotu na poziomie co najmniej 95% wyniku Markowitza w pięciu przypadkach testowych. Wbudowane dane syntetyczne służą do uruchomienia programu, nie do raportowania wyników projektu.

## Jak uruchomić

Wymagania: Python 3.10 lub nowszy.

```bash
git clone https://github.com/NikodemBoniecki/Alpha221.git
cd Alpha221
python -m pip install -r requirements.txt
python -m alpha221
```

Domyślne polecenie generuje ceny syntetyczne i zapisuje porównanie w `results/comparison.csv`. Własny plik CSV można podać poleceniem `python -m alpha221 --input data/prices.csv --risk-limit 0.25`. Plik musi zawierać kolumnę `date`, a potem po jednej kolumnie skorygowanej ceny zamknięcia dla każdego tickera. Tiingo EOD pozostaje możliwym źródłem, ale do porównania algorytmu AI jego aktualne warunki wymagają licencji Enterprise. Użyjemy Tiingo dopiero po uzyskaniu licencji albo wybierzemy inne źródło z odpowiednimi prawami. Szczegóły opisaliśmy w [notatce o Tiingo](docs/tiingo-data-notes.md).

## Zespół

- Kacper Nowaczyk: projekt algorytmu genetycznego i jego operatory.
- Adam Remfeld: wybór licencjonowanego źródła, pozyskanie i przygotowanie danych.
- Nikodem Boniecki: punkty odniesienia, ewaluacja, integracja i dokumentacja.

## Dokumentacja

Zobacz [pełną dokumentację po polsku](docs/dokumentacja.md), [abstrakt techniczny po angielsku](docs/abstract_en.md) i [nasze notatki o danych Tiingo](docs/tiingo-data-notes.md).
