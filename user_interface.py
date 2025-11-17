import geocoding
import program_errors
import weather_forecast
import weather_utils

def get_input() -> list[str]:
    '''asks user for input until 'NO MORE QUERIES' is typed, then allows one
    more input'''
    input_list = []
    while True:
        input_line = input().strip()
        input_list.append(input_line)
        if(input_line == 'NO MORE QUERIES'):
            break

    #one more input after 'NO MORE QUERIES' is entered
    input_line = input().strip()
    input_list.append(input_line)
    return input_list

        
def create_objects_and_attributions(input_list: list) -> tuple:
    '''creates objects based on if the input specified a file or api to do
    each task, and adds attributions if the respective api was used. Returns
    a tuple of the 3 objects and the attribution list'''
    attribution_list = []

    FORWARD_GEOCODING_ATTRIBUTION = (
        '**Forward geocoding data from OpenStreetMap')
    NWS_ATTRIBUTION = ('**Real-time weather data from National Weather Service,'
                       ' United States Department of Commerce')
    REVERSE_GEOCODING_ATTRIBUTION = (
        '**Reverse geocoding data from OpenStreetMap')
    
    first_line = input_list[0].split()
    if first_line[1] == 'NOMINATIM':
        forward_geocoder = geocoding.ForwardGeocodingWithApi(
            ' '.join(first_line[2:]))
        attribution_list.append(FORWARD_GEOCODING_ATTRIBUTION)
    elif first_line[1] == 'FILE':
        forward_geocoder = geocoding.ForwardGeocodingWithFile(first_line[2])

    second_line = input_list[1].split()
    if second_line[1] == 'NWS':
        weather_finder = (weather_forecast.WeatherForecastWithApi(
                          forward_geocoder.get_coordinates()[0],
                          forward_geocoder.get_coordinates()[1]))
        attribution_list.append(NWS_ATTRIBUTION)
    elif second_line[1] == 'FILE':
        weather_finder = weather_forecast.WeatherForecastWithFile(
            second_line[2])

    last_line = input_list[-1].split()
    if last_line[1] == 'NOMINATIM':
        reverse_geocoder = geocoding.ReverseGeocodingWithApi(
            weather_finder.average_coordinates())

        if len(attribution_list) == 0:
            attribution_list.append(REVERSE_GEOCODING_ATTRIBUTION)
        else:
            attribution_list.insert(1, REVERSE_GEOCODING_ATTRIBUTION)
    elif last_line[1] == 'FILE':
        reverse_geocoder = geocoding.ReverseGeocodingWithFile(last_line[2])

    return (forward_geocoder, weather_finder,
            reverse_geocoder, attribution_list)

def make_output_list(input_list: list, objects: tuple) -> list:
    '''makes a list of what the output should be and adds any attributions
    to the end'''
    output_list = []
    
    (forward_geocoder, weather_finder, reverse_geocoder,
     attribution_list) = objects
    
    formatted_lat, formatted_lon = (geocoding.format_coordinates(
        forward_geocoder.get_coordinates()))
    output_list.append(f'TARGET {formatted_lat} {formatted_lon}')

    formatted_lat, formatted_lon = (geocoding.format_coordinates(
        weather_finder.average_coordinates()))
    output_list.append(f'FORECAST {formatted_lat} {formatted_lon}')

    output_list.append(reverse_geocoder.get_location())

    for query in input_list[2:]:
        if query == 'NO MORE QUERIES':
            break
        output_list.append(weather_utils.process_query(query, weather_finder))

    output_list += attribution_list
    return output_list

def print_output_list(output_list: list) -> None:
    '''prints output list to user'''
    for line in output_list:
        print(line)
        
def test_program() -> None:
    '''makes it easier to test program using a list instead of typing it out'''
    input_lists = []

    #add your own queries
    input_lists.append(['TARGET NOMINATIM rancho penasquitos',
                   'WEATHER NWS',
                   'PRECIPITATION 120 MAX',
                   'TEMPERATURE FEELS C 36 MIN',
                   'TEMPERATURE AIR F 36 MAX',
                   'HUMIDITY 5 MIN',
                   'WIND 200 MAX',
                   'NO MORE QUERIES',
                   'REVERSE NOMINATIM'])

    #file test
    input_lists.append(['TARGET FILE nominatim_target.json',
                   'WEATHER FILE nws_hourly.json',
                   'TEMPERATURE AIR C 24 MAX',
                   'NO MORE QUERIES',
                   'REVERSE FILE nominatim_reverse.json'])
    
    try:
        for input_list in input_lists:
            objects = create_objects_and_attributions(input_list)
            output_list = make_output_list(input_list, objects)
            print_output_list(output_list)
    except (program_errors.ApiFailureError,
            program_errors.FileFailureError) as e:
        e.print_failure_message()
    

def run_program() -> None:
    '''runs program normally'''
    input_list = get_input()

    try:
        objects = create_objects_and_attributions(input_list)
        output_list = make_output_list(input_list, objects)
        print_output_list(output_list)
    except (program_errors.ApiFailureError,
            program_errors.FileFailureError) as e:
        e.print_failure_message()
        
        
if __name__ == '__main__':
    '''runs if not from import'''
    run_program()
    #test_program()
