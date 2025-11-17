import operator
import datetime

def feels_like_temperature(t: float, h: float, w: float) -> float:
    '''finds the 'feels like' temperature using temperature(F), humidity(%),
    and wind speed (mph)'''
    if t >= 68:
        return heat_index(t, h)
    elif t <= 50 and w > 3:
        return wind_chill(t, w)
    else:
        return t
    
def heat_index(t: float, h: float) -> float:
    '''returns the feels like temperature if the temperature is above 68F'''
    return (-42.379
            + 2.04901523 * t
            + 10.14333127 * h
            + -0.22475541 * t * h
            + -0.00683783 * (t**2)
            + -0.05481717 * (h**2)
            + 0.00122874 * (t**2) * h
            + 0.00085282 * t * (h**2)
            + -0.00000199 * (t**2) * (h**2))

def wind_chill(t: float, w: float) -> float:
    '''determines the feels like temp if the temp is below 50F and the wind
    speed is above 3mph'''
    return (35.74
            + 0.6215 * t
            + -35.75 * (w**0.16)
            + 0.4275 * t * (w**0.16))

def celsius_to_fahrenheit(t: float) -> float:
    return t * 1.8 + 32

def fahrenheit_to_celsius(t: float) -> float:
    return (t - 32) * 5 / 9

def process_query(query, weather_finder: list) -> str:
    '''for each query line, the query is split up into its components and
    the response is returned'''
    split_query = query.split()
    limit = split_query[-1]
    length = int(split_query[-2])
    weather_type = split_query[0]
    weather_list = weather_finder.get_weather_list(length)
    specific_weather_list = []
    
    if weather_type == 'TEMPERATURE':
        temp_scale = split_query[2]
        temp_type = split_query[1]
        
        if temp_type == 'FEELS':
            specific_weather_list = calculate_feels_temps(weather_list)

        else:
            specific_weather_list = get_specific_weather_list(weather_list,
                                                      weather_type)

        if temp_scale == 'C':
            specific_weather_list = calculate_celsius_list(
                specific_weather_list)
        
    else:
        specific_weather_list = get_specific_weather_list(weather_list,
                                                      weather_type)
    
    if limit == 'MAX':
        weather_time_value = max(specific_weather_list,
                                 key = operator.itemgetter(1))
    else:
        weather_time_value = min(specific_weather_list,
                                 key = operator.itemgetter(1))

    formatted_date_time = format_date_time(weather_time_value)
    
    processed_query = (f'{formatted_date_time} {weather_time_value[1]:.4f}')
    
    weather_percents = {'HUMIDITY', 'PRECIPITATION'}
    if weather_type in weather_percents:
        processed_query += '%'

    return processed_query

def get_specific_weather_list(weather_list: list, weather_type: str) -> tuple:
    '''creates a weather list where each elements is a tuple of the date/time
    of the start of the period and the weather type that is wanted''' 
    specific_weather_list = []

    #same order as weather_forecast line 144
    weather_codes = {'TEMPERATURE': 1, 'HUMIDITY': 2, 'WIND': 3,
                     'PRECIPITATION': 4}
    
    for period in weather_list:
        if (period[weather_codes[weather_type]] != '' and
            type(period[weather_codes[weather_type]]) == int or
             type(period[weather_codes[weather_type]]) == float):
            #time is always included as period[0]
            specific_weather_list.append([period[0], period[weather_codes[
                weather_type]]])

    return specific_weather_list

def calculate_feels_temps(weather_list: list) -> list:
    '''calculates the feels like temp from a weather list and returns a list
    of the updated values'''
    feels_temps = []
    for period in weather_list:
        feels_temps.append([period[0], feels_like_temperature(
            period[1], period[2], period[3])])
    return feels_temps

def calculate_celsius_list(specific_weather_list: list) -> list:
    '''calculates the celsius values of a temp and updates the list with the new
    values'''
    for index in range(len(specific_weather_list)):
        specific_weather_list[index][1] = (fahrenheit_to_celsius(
            specific_weather_list[index][1]))
    return specific_weather_list

def format_date_time(weather_time_value: tuple) -> str:
    '''returns the date and time in specified format with utc time'''
    weather_date_time = weather_time_value[0]
    local_date_time = datetime.datetime.fromisoformat(weather_date_time)
    utc_date_time = local_date_time.astimezone(datetime.timezone.utc)
    utc_iso = utc_date_time.isoformat().replace('+00:00', 'Z')
    return utc_iso
    
