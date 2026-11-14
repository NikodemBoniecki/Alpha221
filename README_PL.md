# Alpha221: algorytm genetyczny do optymalizacji portfela

Projekt z kursu sztucznej inteligencji na Collegium Da Vinci, informatyka, grupa L2 / L3, rok akademicki 2026/2027.

[English README](README.md) | [Karta tematu](karta-tematu.md) | [Project card in English](project_card_en.md)

## Co robi projekt

Planujemy stworzyć narzędzie, które pomoże inwestorom indywidualnym podzielić kapitał między wybrane akcje. Na podstawie historycznych cen dziennych i limitu ryzyka system zaproponuje wagi spółek w portfelu oraz pokaże szacowany zwrot i ryzyko. Na początek skupimy się na spółkach z sektorów AI, gamedev i półprzewodników.

## Technika AI

Wybraliśmy algorytm genetyczny i samodzielnie zaimplementujemy jego główne elementy. Pozwoli nam przeszukiwać wiele możliwych zestawów wag portfela z uwzględnieniem limitu ryzyka. Wyniki porównamy z modelem Markowitza i prostym portfelem równoważonym.

## Wyniki

Nie mamy jeszcze wyników, bo nie zaczęliśmy implementacji. Naszym celem jest zwracanie wyłącznie portfeli spełniających limit ryzyka i osiągnięcie mediany zwrotu na poziomie co najmniej 95% wyniku Markowitza w pięciu przypadkach testowych.

## Jak uruchomić

W repozytorium nie ma jeszcze uruchamialnego kodu. Wraz ze szkieletem projektu dodamy wersję Pythona, zależności, konfigurację danych, polecenie uruchomienia i miejsce zapisu wyników. Tiingo EOD to na razie tylko możliwe źródło danych: plany Starter i Trial nie pozwalają trwale przechowywać danych, a nasze porównanie algorytmu AI wymaga licencji Enterprise. Przed pobraniem danych uzyskamy tę licencję albo wybierzemy zbiór z odpowiednimi prawami. Szczegóły opisaliśmy w [notatce o Tiingo](docs/tiingo-data-notes.md).

## Zespół

- Kacper Nowaczyk: projekt algorytmu genetycznego i jego operatory.
- Adam Remfeld: wybór licencjonowanego źródła, pozyskanie i przygotowanie danych.
- Nikodem Boniecki: punkty odniesienia, ewaluacja, integracja i dokumentacja.

## Dokumentacja

Zobacz [pełną dokumentację po polsku](docs/dokumentacja.md), [abstrakt techniczny po angielsku](docs/abstract_en.md) i [nasze notatki o danych Tiingo](docs/tiingo-data-notes.md).
