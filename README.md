This program takes a target location and a list of weather-related queries, then prints weather information for the nearest National Weather Service forecast location. It supports both live API calls (Nominatim + NWS) and local JSON files for offline testing.

How It Works

1. The program reads several lines of input describing:

  How to determine the target location (TARGET NOMINATIM or TARGET FILE).

  Where to get weather data (WEATHER NWS or WEATHER FILE).

  One or more weather queries (temperature, humidity, wind, precipitation).

  A reverse-geocoding source (REVERSE NOMINATIM or REVERSE FILE).

2. It geocodes the target, fetches the NWS hourly forecast, answers each query, and prints:

  Target coordinates

  Forecast location

  Reverse-geocoded address

  Each query result with timestamp

  Required API attributions

Example Input
TARGET NOMINATIM Bren Hall, Irvine, CA
WEATHER NWS
TEMPERATURE AIR F 12 MAX
NO MORE QUERIES
REVERSE NOMINATIM

Example Output
FORECAST 33.6545/N 117.8330/W
1 Sunnyhill, Irvine, CA
2024-11-07T23:00:00Z 77.0000
