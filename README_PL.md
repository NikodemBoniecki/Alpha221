# Alpha221 — Algorytm genetyczny do optymalizacji portfela

Projekt z kursu AI — Collegium Da Vinci, informatyka, grupa L2 / L3, rok akademicki 2026/2027.

[English README](README.md) · [Karta tematu](karta-tematu.md) · [Project card (English translation)](project_card_en.md)

## Co robi projekt

Alpha221 ma być optymalizatorem portfela dla inwestorów indywidualnych wybierających akcje, początkowo z sektorów AI, gamedev i półprzewodników. Na podstawie historycznych cen akcji i limitu ryzyka podanego przez użytkownika system ma zwracać wagi portfela maksymalizujące oczekiwany zwrot przy zachowaniu tego limitu.

## Technika AI

Projekt zakłada samodzielną implementację algorytmu genetycznego. Metoda pasuje do przeszukiwania możliwych wag portfela przy ograniczeniu ryzyka; funkcja przystosowania będzie nagradzać oczekiwany zwrot i mocno karać rozwiązania przekraczające limit ryzyka.

## Wyniki

Wyniki nie są jeszcze znane, ponieważ implementacja nie została rozpoczęta. Algorytm genetyczny zostanie oceniony na tych samych danych testowych co model średnia-wariancja Markowitza oraz portfel równoważony (1/N).

## Jak uruchomić

Repozytorium nie zawiera jeszcze uruchamialnego kodu. Wersja Pythona, zależności, konfiguracja danych, punkt wejścia i miejsce zapisu wyników zostaną opisane po dodaniu szkieletu projektu. Planowanym źródłem danych jest Tiingo EOD; korzystanie z API będzie wymagało tokenu Tiingo.

## Zespół

- Kacper Nowaczyk — wspólna praca z zespołem; indywidualny podział ról później.
- Adam Remfeld — wspólna praca z zespołem; indywidualny podział ról później.
- Nikodem Boniecki — wspólna praca z zespołem; indywidualny podział ról później.

## Dokumentacja

Dokumentacja projektu: [pełna dokumentacja po polsku](docs/dokumentacja.md) i [abstrakt techniczny po angielsku](docs/abstract_en.md).
