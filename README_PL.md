# Alpha221: algorytm genetyczny do optymalizacji portfela

Projekt z kursu sztucznej inteligencji na Collegium Da Vinci, informatyka, grupa L2 / L3, rok akademicki 2026/2027.

[English README](README.md) | [Karta tematu](karta-tematu.md) | [Project card in English](project_card_en.md)

## Co robi projekt

Program pomaga inwestorom indywidualnym porównać sposoby podziału kapitału między wybrane akcje. Wczytuje historyczne ceny dzienne i limit ryzyka, a następnie proponuje wagi spółek oraz szacuje zwrot i ryzyko. Może użyć lokalnego pliku CSV albo syntetycznych danych demonstracyjnych. Wybraliśmy [zbiór dziennych cen akcji z licencją CC0](https://www.kaggle.com/datasets/borismarjanovic/price-volume-data-for-all-us-stocks-etfs), ale jeszcze go nie pobraliśmy.

## Technika AI

Program używa algorytmu genetycznego do przeszukiwania możliwych wag portfela z uwzględnieniem limitu ryzyka. Porównuje wynik z optymalizatorem Markowitza i prostym portfelem równoważonym. Obecny szkielet w Pythonie zawiera główny algorytm i oba punkty odniesienia.

## Wyniki

Nie oceniliśmy jeszcze algorytmu na danych rynkowych. Celem jest, aby każdy portfel GA spełniał limit ryzyka, a mediana pięciu rocznych relacji zwrotu GA do Markowitza wyniosła co najmniej 0,95. Dane syntetyczne służą do uruchomienia programu, nie do raportowania wyników projektu.

## Jak uruchomić

Wymagania: Python 3.10 lub nowszy.

```bash
git clone https://github.com/NikodemBoniecki/Alpha221.git
cd Alpha221
python -m pip install -r requirements.txt
python -m alpha221
```

Domyślne polecenie generuje ceny syntetyczne i zapisuje porównanie w `results/comparison.csv`. Własny plik CSV można podać poleceniem `python -m alpha221 --input data/prices.csv --risk-limit 0.25`. Plik musi zawierać kolumnę `date`, a potem po jednej kolumnie ceny zamknięcia dla każdego tickera. Planujemy przygotować ten plik z pięciu plików tickerów pobranych z Kaggle. Szczegóły dotyczące licencji Tiingo opisaliśmy w [notatce](docs/tiingo-data-notes.md).

Pliki Kaggle można połączyć do wspólnego CSV i uruchomić porównanie dla każdego roku poleceniami:

```bash
python -m alpha221.prepare --source data/raw/Stocks --tickers NVDA AMD MSFT EA TTWO --start 2012-01-03 --end 2017-01-03 --output data/prices.csv
python -m alpha221 --input data/prices.csv --yearly --risk-limit 0.25
```

Raport roczny zapisuje wyniki dla dostępnych lat oraz medianę relacji GA do Markowitza w `results/comparison.csv` i terminalu.

## Zespół

- Kacper Nowaczyk: projekt algorytmu genetycznego i jego operatory.
- Adam Remfeld: wybór licencjonowanego źródła, pozyskanie i przygotowanie danych.
- Nikodem Boniecki: punkty odniesienia, ewaluacja, integracja i dokumentacja.

## Dokumentacja

Zobacz [pełną dokumentację po polsku](docs/dokumentacja.md), [abstrakt techniczny po angielsku](docs/abstract_en.md) i [nasze notatki o danych Tiingo](docs/tiingo-data-notes.md).
