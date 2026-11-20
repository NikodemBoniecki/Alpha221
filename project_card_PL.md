# Karta zgłoszenia tematu projektu

**Grupa:** L2 / L3 | **Zespół:** Z4 | **Aktualizacja:** 2026-11-20
Sztuczna inteligencja, laboratorium | Collegium Da Vinci | rok akademicki 2026/2027

## 1. Skład zespołu

| Imię i nazwisko | Nr albumu | Zakres |
|---|---:|---|
| Kacper Nowaczyk | 31838 | Algorytm genetyczny i jego operatory |
| Adam Remfeld | 31799 | Pozyskanie i przygotowanie danych |
| Nikodem Boniecki | 31865 | Punkty odniesienia, ewaluacja, integracja i dokumentacja |

## 2. Tytuł

- **Po polsku:** Optymalizator portfela inwestycyjnego algorytmem genetycznym przy ograniczeniu ryzyka
- **Po angielsku:** Genetic Algorithm for Risk-Constrained Investment Portfolio Optimization

## 3. Problem

Projekt bada, jak podział portfela wpływa na szacowany zwrot i ryzyko. Użytkownik podaje limit rocznej zmienności. Program ma dobrać wagi aktywów i porównać algorytm genetyczny z modelem Markowitza oraz portfelem równoważonym.

## 4. Dlaczego używamy algorytmu genetycznego?

Klasyczną optymalizację średnia-wariancja można rozwiązać bez algorytmu genetycznego. GA wybraliśmy jako metodę omawianą na zajęciach i punkt porównania dla mieszanego problemu doboru aktywów i wag.

## 5. Technologia SI

- [ ] Sieć neuronowa
- [ ] System ekspertowy lub wnioskowanie regułowe
- [x] Algorytm genetyczny
- [ ] Klasyczne uczenie maszynowe

## 6. Dane

Źródłem dziennych notowań jest Yahoo Finance, pobierane przez nieoficjalną bibliotekę yfinance. Wykorzystujemy je wyłącznie w zamkniętym projekcie edukacyjnym. Dane w CSV są lokalne i ignorowane przez Git.

| Grupa | Ticker | Waluta notowania |
|---|---|---|
| Spółki | AAPL, MSFT, NVDA, JPM, KO, TTWO, AMD, ASML, TSLA | USD |
| Spółka | UBI.PA | EUR |
| Spółki | CDR.WA, XTB.WA, PKN.WA, ASB.WA, CBF.WA | PLN |
| ETF S&P 500 | SPY | USD |
| ETF WIG20TR | ETFBW20TR.WA | PLN |

Pobieracz pobiera ostatnie dwa lata danych dla 15 spółek, dwóch ETF-ów oraz kursów USDPLN=X i EURUSD=X. Historyczne ceny skorygowane o działania korporacyjne przelicza na USD. PLN dzieli przez kurs USD/PLN, a EUR mnoży przez EUR/USD. Kurs FX przypisuje według daty notowania; gdyby dokładny dzień nie był dostępny, stosuje ostatnią wcześniejszą obserwację FX. Ceny instrumentów nie są uzupełniane.

Zrzut zweryfikowany 2026-11-20 zawiera 485 kompletnych wspólnych sesji dziennych oraz 105 tygodniowych cen, czyli 104 tygodniowe okresy zwrotu. Tygodniowa cena pochodzi z ostatniej wspólnej sesji w tygodniu; etykieta daty wskazuje piątek kończący tydzień.

## 7. Stos technologiczny

Python 3.10+, NumPy, SciPy, pandas i yfinance. Dane pobiera polecenie python -m alpha221.market_data; nie jest wymagany token API. Aplikacja jest konsolowym prototypem.

## 8. Kryteria porównania

GA ma maksymalizować szacowane prawdopodobieństwo dodatniego skumulowanego zwrotu USD w 6 miesięcy, przy limicie rocznej zmienności. Wagi będą wyznaczane z kroczącego 2-letniego okna tygodniowych danych i oceniane w 5-letnim teście poza próbą, z aktualizacją co 26 tygodni. Wyniki GA, Markowitza i 1/N będą porównywane na tych samych okresach.

GA wybiera dokładnie 10 z 15 spółek; każda wybrana spółka ma wagę 1–20% całego portfela. Łączny udział spółek to 80%, ETF-ów 20%, a każdy ETF ma minimum 1%. Markowitz ma te same limity udziałów, ale może wybrać dowolną liczbę spółek. 1/N dzieli część akcyjną po równo między 15 spółek oraz część ETF-ową po równo między dwa ETF-y.

Nie ustaliliśmy jeszcze liczbowego progu porównania metod ani końcowego protokołu ewaluacji poza próbą. Nie ma wyników końcowych.

## 9. Zakres i stan implementacji

**Działa:** pobieranie i walidacja danych, przeliczenie na USD, eksport dziennych i tygodniowych cen, loader CSV, prototyp GA, Markowitz, 1/N i annualizacja dla częstotliwości dziennej oraz tygodniowej.

**Zaimplementowano:** ograniczenia wag, wybór 10 z 15 spółek przez GA, estymację celu 6-miesięcznego bootstrapem blokowym, pięcioletni test kroczący i pełne przeszukanie 3003 podzbiorów. Do dalszej pracy: alokacja kwoty inwestycji w USD na jednostki aktywów.

GA wybiera 10 spółek z 15 i optymalizuje je na tygodniowym celu bootstrapowym. Pełne przeszukanie 3003 składów jest już zaimplementowane jako kontrola jakości; nie stanowi globalnego optimum po wszystkich możliwych wag, ponieważ wagi wewnątrz każdego składu wyznacza Markowitz.

## 10. Ograniczenia

Wyniki będą zależeć od wybranego okna historycznego i nie przewidują przyszłości. Nie uwzględniamy kosztów transakcji, podatków ani płynności. Dane Yahoo Finance nie są gwarantowane jako bezbłędne ani stale dostępne. Nie publikujemy pobranych szeregów cenowych. Projekt nie jest poradą inwestycyjną.

## 11. Repozytorium

https://github.com/NikodemBoniecki/Alpha221

## Decyzja prowadzącego

> Tę sekcję wypełnia prowadzący.

- [ ] Zatwierdzony
- [ ] Do poprawy

**Uwagi:**
