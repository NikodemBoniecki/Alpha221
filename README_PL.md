# Alpha221: optymalizacja portfela z limitem ryzyka

Projekt na laboratorium sztucznej inteligencji, Collegium Da Vinci, grupa L2/L3, rok akademicki 2026/2027.

[English README](README.md) · [Karta tematu](project_card_PL.md) · [Dokumentacja techniczna](docs/dokumentacja.md)

## Cel

Program porównuje algorytm genetyczny (GA), model Markowitza i prosty portfel 1/N na tych samych cenach. Koszyk obejmuje 15 spółek oraz dwa ETF-y: SPY i ETFBW20TR.WA. GA wybiera dokładnie 10 spółek i przeznacza na nie 80% portfela. Każda wybrana spółka ma wagę 1-20%. Pozostałe 20% przypada na ETF-y, po co najmniej 1% na każdy. Celem GA jest jak najwyższe oszacowane prawdopodobieństwo zysku w USD po 6 miesiącach, bez przekroczenia limitu zmienności. Markowitz korzysta z tych samych budżetów, ale nie musi wybierać dokładnie 10 spółek. Portfel 1/N dzieli obie części po równo.

## Dane

Pobieracz korzysta z Yahoo Finance przez bibliotekę yfinance. Historyczne `Adj Close` przelicza na USD po kursie z danego dnia. Nie uzupełnia brakujących cen instrumentów. Audyt sprawdza ticker, walutę, typ instrumentu, strefę giełdy, dywidendy, splity i dopasowanie FX. Dla danych tygodniowych zapisuje też dzień, z którego faktycznie pochodzi cena.

Sprawdzony zbiór z okresu 21.11.2019-20.11.2026 ma 1703 wspólne sesje dzienne i 366 cen tygodniowych dla 17 instrumentów. Nie znaleźliśmy braków, duplikatów, niedodatnich cen ani luk między tygodniami. Każdy potrzebny kurs FX był dostępny tego samego dnia. Dane i raporty są lokalne i ignorowane przez Git.

Domyślne polecenie dwuletnie zweryfikowane 21.11.2026 utworzyło 485 wspólnych sesji dziennych i 105 cen tygodniowych (104 okresy zwrotu) do 20.11.2026.

## Uruchomienie

Wymagany Python 3.10 lub nowszy. Instrukcję sprawdzono na Pythonie 3.12.10.

~~~bash
python -m pip install -r requirements.txt
python -m alpha221.market_data
python -m alpha221 --input data/prices_weekly_usd.csv --frequency weekly --risk-limit 0.22
~~~

Pobieracz domyślnie używa względnego okresu `2y`. Zapisuje dzienne ceny skorygowane w USD do `data/prices.csv`, tygodniowe do `data/prices_weekly_usd.csv`, najnowsze ceny do `data/latest_prices_usd.csv`, audyt instrumentów do `results/market_data_audit.csv`, audyt kalendarza do `results/market_data_calendar_audit.csv` i manifest odtwarzalności do `data/market_data_manifest.json`.

Odtworzenie dokładnego siedmioletniego zbioru użytego w ewaluacji:

~~~bash
python -m alpha221.market_data --start 2019-11-21 --end 2026-11-21 --minimum-common-rows 1600 --prices-output data/raw/prices_7y_usd.csv --weekly-output data/raw/prices_weekly_7y_usd.csv --latest-output data/raw/latest_prices_7y_usd.csv --audit-output results/market_data_audit_7y.csv --calendar-audit-output results/market_data_calendar_audit_7y.csv --manifest-output data/raw/market_data_manifest_7y.json
~~~

Pięcioletni test poza próbą:

~~~bash
python -m alpha221 --input data/raw/prices_weekly_7y_usd.csv --frequency weekly --risk-limit 0.22 --walk-forward --fold-output results/walk_forward_folds_7y.csv --summary-output results/walk_forward_summary_7y.csv
~~~

Polecenie porównania powyżej uruchamia tygodniowy model docelowych ograniczeń na dwuletnim oknie treningowym; nie jest to test poza próbą. Częstotliwość tygodniowa używa annualizacji 52 okresów rocznie; dzienna używa 252:

~~~bash
python -m alpha221 --input data/prices.csv --frequency daily --risk-limit 0.22
~~~

Bez pliku wejściowego python -m alpha221 używa syntetycznych danych demonstracyjnych.

## Stan projektu

Gotowe są: pobieranie i audyt danych, przeliczenie walut, ograniczenia wag, bootstrap tygodniowy, test walk-forward i sprawdzenie wszystkich 3003 składów. W teście historycznym GA uzyskał 199,71%, Markowitz 319,40%, a 1/N 177,29%. Każda metoda zakończyła zyskiem 9 z 10 okresów. Wyniki nie uwzględniają prowizji ani podatków. Brakuje jeszcze przeliczenia kwoty inwestycji na liczbę jednostek.

## Źródło i ograniczenia

yfinance jest nieoficjalnym narzędziem korzystającym z publicznie dostępnych interfejsów Yahoo Finance. To projekt edukacyjny, nie produkt inwestycyjny. Yahoo zastrzega ograniczenia dotyczące wykorzystania i redystrybucji danych; nie publikujemy pobranych szeregów cenowych. Szczegóły znajdują się w [dokumentacji](docs/dokumentacja.md).
