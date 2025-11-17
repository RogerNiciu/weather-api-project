import class_utils
import json
import program_errors
import urllib.request

class WeatherForecastWithFile:
    '''class if weather is taken from a file'''
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.json_data = self.get_json_data()
        
    def get_json_data(self) -> dict:
        '''tries to convert file into a dict, raises error if file is not
        found or not in json format'''
        try:
            with open(self.file_name, 'r') as file:
                json_data = json.loads(file.read())
                return json_data
        except FileNotFoundError:
            raise api_utils.FileFailureError(self.file_name, 'missing')
        except json.JSONDecodeError:
            raise program_errors.FileFailureError(self.file_name, 'format')

    def get_weather_list(self, num_of_iterations: int) -> list:
        '''calls _get_weather_list to make a weather list based on the file data
        and num_of_iterations, which determines the length of the list'''
        return _get_weather_list(self.json_data, num_of_iterations,
                                 path=self.file_name)

    def get_coordinate_list(self) -> list:
        '''calls _get_coordinate_list to get a list of the coordinates that
        show the area covered by the weather station'''
        return _get_coordinate_list(self.json_data, path = self.file_name)

    def average_coordinates(self) -> tuple:
        '''calls _get_average_coordinates to get the average latitude and
        longitude of the coordinates from the coordinate list'''
        return _get_average_coordinates(self.get_coordinate_list())

class WeatherForecastWithApi:
    FORMAT = 'geo+json'
    BASE_API_URL = 'https://api.weather.gov'
    EMAIL = 'rniciu@uci.edu'
    HEADERS = ({'User-Agent':
                'https://www.ics.uci.edu/~thornton/icsh32/ProjectGuide/'
                f'/project3/{EMAIL}', 'Accept': f'application/{FORMAT}'})

    def __init__(self, latitude, longitude):
        self.latitude, self.longitude = self.round_coordinates(latitude,
                                                               longitude)
        json_data = self.get_json_data()
        self.json_data = json_data[0]
        self.url = json_data[1]
        
    def get_json_data(self) -> dict:
        '''connects and sends request to server, which returns a new url
        that specifies which weather station to ask for the weather, then
        sends another request and returns the data'''
        url = self._make_url()
        request = self._make_request(url)
        json_data = self._send_request(request)
        
        
        new_url = class_utils.access_json_data(json_data,
            [0, 'properties', 'forecastHourly'], url=request.full_url)
        
        request = self._make_request(new_url)
        json_data = self._send_request(request)
        return json_data
    
    def _make_url(self):
        '''API specification of url to connect to'''
        return (f'{self.BASE_API_URL}/points/{self.latitude},'
                f'{self.longitude}')
    
    def _make_request(self, url: str) -> urllib.request.Request:
        '''makes a urllib.request.Request to send to the server'''
        return urllib.request.Request(url, headers = self.HEADERS)
    
    def _send_request(self, request: urllib.request.Request) -> dict:
        '''calls class_utils to send the request and handle any errors'''
        return class_utils.send_request(request)
    
    def round_coordinates(self, latitude: float, longitude: float) -> tuple:
        '''rounds the coordinates before adding them to the url per API
        documentation'''
        latitude = round(latitude, 4)
        longitude = round(longitude, 4)
        return (latitude, longitude)

    def get_weather_list(self, num_of_iterations: int) -> list:
        '''asks _get_weather_list for the weather list'''
        return _get_weather_list(self.json_data, num_of_iterations,
                                 url=self.url)

    def get_coordinate_list(self) -> list:
        '''asks _get_coordinate_list for the coordinates representing the
        area of the weather station'''
        return _get_coordinate_list(self.json_data, self.url)

    def average_coordinates(self) -> list:
        '''gets the average latitude and longitude of the weather station
        points'''
        return _get_average_coordinates(self.get_coordinate_list())

    
def _get_weather_list(json_data: dict, num_of_iterations: int, url=None,
                      path=None) -> list:
    '''creates a weather list that includes temperature, humidity, wind,
    and precipitation with a specified length of num_of_iterations'''
    weather_list = []

    used_data = class_utils.access_json_data(json_data,
        ['properties', 'periods'], url=url, path=path)

    max_iterations = len(used_data)
    if max_iterations < num_of_iterations:
        num_of_iterations = max_iterations

    for period_num in range(num_of_iterations):
        time = class_utils.access_json_data(used_data,
            [period_num, 'startTime'], url=url, path=path)
        temp = class_utils.access_json_data(used_data,
            [period_num, 'temperature'], url=url, path=path)
        humidity = class_utils.access_json_data(used_data,
            [period_num, 'relativeHumidity', 'value'], url=url, path=path)
        wind = class_utils.access_json_data(used_data,
            [period_num, 'windSpeed'], url=url, path=path)
        precipitation =  class_utils.access_json_data(used_data,
            [period_num, 'probabilityOfPrecipitation', 'value'], url=url,
                                                      path=path)

        #changes wind = '20.6 mph' to wind = 20.6 (for example)
        if wind != '':
            wind = class_utils.access_json_data(wind.split(), [0], url=url,
                                                path=path, cast = float)

        #important: this order is used later to access specific info
        weather_list.append([time, temp, humidity, wind, precipitation])
                                
    return weather_list

def _get_coordinate_list(json_data: dict, path:str = None,
                         url:str = None) -> list:
    '''gets a coordinate list from the weather station area'''
    coordinate_list = []
    for coordinate in class_utils.access_json_data(json_data,
        ['geometry', 'coordinates', 0], path = path, url = url):
        
        coordinate_list.append([
            class_utils.access_json_data(coordinate, [0], path = path,
                                            url = url, cast = float),
            class_utils.access_json_data(coordinate, [1], path = path,
                                         url = url, cast = float)]),
        
    return coordinate_list

def _get_average_coordinates(coordinate_list) -> tuple:
    '''gets the average coordinate of the weather station area'''
    unique_coordinate_list = list(set(tuple(c) for c in coordinate_list))

    lat_values = []
    lon_values = []
    for coordinate in unique_coordinate_list:
        #coordinates are given as longitude, latitude pairs
        lat_values.append(coordinate[1])
        lon_values.append(coordinate[0])

    
    average_lat = sum(lat_values)/len(lat_values)
    average_lon = sum(lon_values)/len(lon_values)
    
    return (average_lat, average_lon)
