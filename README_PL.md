# Alpha221: optymalizacja portfela z limitem ryzyka

Projekt na laboratorium sztucznej inteligencji, Collegium Da Vinci, grupa L2/L3, rok akademicki 2026/2027.

[English README](README.md) · [Karta tematu](karta-tematu.md) · [Dokumentacja techniczna](docs/dokumentacja.md)

## Cel

Porównujemy algorytm genetyczny (GA), optymalizację Markowitza i portfel równoważony 1/N na wspólnych danych cenowych. Koszyk zawiera 15 spółek oraz dwa ETF-y: SPY na S&P 500 i ETFBW20TR.WA na WIG20TR. GA przeznacza 80% na dokładnie 10 wybranych spółek (1–20% portfela na każdą) i 20% na dwa ETF-y (minimum 1% na każdy), a jego celem jest szacowane prawdopodobieństwo dodatniego zwrotu USD w 6 miesięcy przy limicie rocznej zmienności. Markowitz używa tego samego podziału, limitu 20% na spółkę i minimum 1% na ETF, ale nie ma wymogu dokładnie 10 spółek; 1/N dzieli 80% równo między 15 spółek i 20% po równo między ETF-y. Bootstrap blokowy i test kroczący są już zaimplementowane; pierwszy wynik poza próbą opisano w dokumentacji.

## Dane

Pobieracz używa yfinance do pobrania ostatnich dwóch lat dziennych notowań z Yahoo Finance. Przelicza ceny historyczne na USD, używając skorygowanych cen zamknięcia oraz kursów z właściwych dat. Nie uzupełnia cen akcji ani ETF-ów w dni bez sesji. Z kompletnych wspólnych sesji tworzy również próbkę tygodniową: ostatnią wspólną sesję w każdym tygodniu.

Zweryfikowany zrzut 2-letni z 20.11.2026 zawiera 485 wspólnych obserwacji dziennych i 105 cen tygodniowych (104 okresy zwrotu). Siedmioletni zbiór do testu został pobrany lokalnie i przeszedł kontrolę: 1703 ceny dzienne oraz 366 tygodniowych dla 17 instrumentów, bez luk w tygodniowym indeksie i z kursem FX dostępnym tego samego dnia. Pliki danych i raport pozostają lokalne i są ignorowane przez Git. Polecenie odtworzenia pełnego zbioru znajduje się w [dokumentacji](docs/dokumentacja.md).

## Uruchomienie

Wymagany Python 3.10 lub nowszy.

~~~bash
python -m pip install -r requirements.txt
python -m alpha221.market_data
python -m alpha221 --input data/prices_weekly_usd.csv --frequency weekly --risk-limit 0.22
~~~

Pobieracz zapisuje dzienne ceny skorygowane w USD do data/prices.csv, tygodniowe do data/prices_weekly_usd.csv, najnowsze ceny zamknięcia do data/latest_prices_usd.csv, raport kontroli do results/market_data_audit.csv, a manifest pobrania do data/market_data_manifest.json.

Polecenie porównania powyżej uruchamia tygodniowy model docelowych ograniczeń na dwuletnim oknie treningowym; nie jest to test poza próbą. Częstotliwość tygodniowa używa annualizacji 52 okresów rocznie; dzienna używa 252:

~~~bash
python -m alpha221 --input data/prices.csv --frequency daily --risk-limit 0.22
~~~

Bez pliku wejściowego python -m alpha221 używa syntetycznych danych demonstracyjnych.

## Stan projektu

Pobieranie, kontrola jakości, przeliczenie walut, ograniczenia wag, bootstrap tygodniowy, pięcioletni test kroczący i pełne przeszukanie 3003 zestawów są zaimplementowane. Nadal do zrobienia pozostaje przeliczenie alokacji kwoty inwestycji na liczbę jednostek.

## Źródło i ograniczenia

yfinance jest nieoficjalnym narzędziem korzystającym z publicznie dostępnych interfejsów Yahoo Finance. To projekt edukacyjny, nie produkt inwestycyjny. Yahoo zastrzega ograniczenia dotyczące wykorzystania i redystrybucji danych; nie publikujemy pobranych szeregów cenowych. Szczegóły znajdują się w [dokumentacji](docs/dokumentacja.md).
