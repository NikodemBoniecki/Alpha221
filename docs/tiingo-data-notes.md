# Tiingo EOD: co musimy ustalić

Sprawdziliśmy oficjalną dokumentację, cennik i warunki Tiingo 14.11.2026. Warunki mogą się zmienić, więc sprawdzimy je ponownie przed użyciem API.

## Wybór danych

Do projektu interesują nas historyczne ceny dzienne EOD. Dla każdego symbolu zapytanie ma postać:

```text
https://api.tiingo.com/tiingo/daily/{ticker}/prices?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD
```

Musimy wybrać konkretne tickery i stały zakres dat. Sam zapis „50 do 100 spółek przez pięć lat” nie określa jeszcze zbioru danych. Przed pobraniem sprawdzimy dostępność każdego symbolu oraz jego zakres dat przez endpoint metadanych. Lista dostępnych symboli może zawierać też symbole zarezerwowane, więc sama lista nie wystarczy. [Dokumentacja EOD](https://www.tiingo.com/documentation/end-of-day)

API zwraca JSON domyślnie, a parametr `format=csv` pozwala wybrać CSV. Odpowiedź zawiera ceny surowe i skorygowane, w tym `adjClose`. Do obliczania zwrotów użyjemy `adjClose`, ponieważ korekta uwzględnia splity i dywidendy. W dokumentacji projektu zapiszemy dokładny zestaw tickerów, daty, format i użyte pole.

## Konto i token

Do zapytań potrzebujemy konta Tiingo i przypisanego do niego API tokenu. Token możemy wysłać w nagłówku `Authorization: Token <token>`. Przechowamy go lokalnie jako zmienną środowiskową, nigdy w repozytorium ani w adresie URL. [Instrukcja połączenia z API](https://www.tiingo.com/documentation/general/connecting)

Aktualny cennik planu Starter podaje 500 różnych symboli miesięcznie, 50 zapytań na godzinę, 1000 dziennie, 1 GB transferu miesięcznie i do pięciu lat historii. Przy jednym zapytaniu na ticker 50 do 100 spółek oznacza co najmniej dwie partie zapytań rozłożone w czasie. To są limity techniczne, ale sam Starter nie daje praw potrzebnych do naszego benchmarku. [Cennik i limity](https://www.tiingo.com/pricing)

## Licencja jest teraz przeszkodą

Warunki Starter i Trial nie pozwalają trwale przechowywać danych Tiingo ani produktów pochodnych, takich jak obliczone wyniki. Można je przetwarzać tylko tymczasowo, w pamięci lub nietrwałej pamięci podręcznej, a następnie usunąć.

Warunki Tiingo wymagają licencji Enterprise do testowania, ewaluowania lub porównywania systemu AI/ML na tych danych. Nasz plan zakłada porównanie algorytmu genetycznego z Markowitzem i portfelem 1/N, więc ten zapis dotyczy planowanego eksperymentu. Plan Power nie znosi tego osobnego wymogu. Przeczytaliśmy to w sekcjach 1.6 i 1.7(d)(iv) [warunków Tiingo](https://www.tiingo.com/tos/). Przed pobraniem danych zapytamy Tiingo o licencję Enterprise dla projektu uczelnianego. Jeśli nie będzie dostępna, wybierzemy inne dane, których licencja pozwala na zapis i ewaluację.

## Co wybierzemy przed pobraniem

1. Konkretne tickery z obszarów AI, gamedev i półprzewodników.
2. Stały zakres dat, nie dłuższy niż dostępna historia dla każdego tickera.
3. Pole `adjClose` oraz format JSON albo CSV.
4. Źródło z licencją pozwalającą na trwałe przechowywanie i porównawczą ewaluację. Dla Tiingo najpierw uzyskamy zgodę/licencję Enterprise.

Na razie nie wybieramy płatnego planu w panelu Tiingo ani nie pobieramy danych. Najpierw ustalimy, czy Tiingo może przyznać odpowiednie prawa, albo przejdziemy na alternatywny zbiór.
