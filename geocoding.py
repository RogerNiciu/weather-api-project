import class_utils
import program_errors
import json
import time
import urllib.request


class ForwardGeocodingWithFile:
    '''class to get the coordinates of a location description using a flie'''
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.json_data = self.get_json_data()
        
    def get_json_data(self) -> dict:
        '''attempts to convert the file data into a dict using json.loads,
        raises exceptions if it fails'''
        try:
            with open(self.file_name, 'r') as file:
                json_data = json.loads(file.read())
                return json_data
        except OSError:
            raise program_errors.FileFailureError(self.file_name, 'missing')
        except json.decoder.JSONDecodeError:
            raise program_errors.FileFailureError(self.file_name, 'format')
        
    def get_coordinates(self) -> tuple:
        '''returns the coordinates from the file'''
        return (class_utils.access_json_data(self.json_data, [0, 'lat'],
                    path=self.file_name, cast=float),
                class_utils.access_json_data(self.json_data, [0, 'lon'],
                    path=self.file_name, cast=float))

class ForwardGeocodingWithApi:
    UCINETID = 'rniciu'
    FORMAT = 'jsonv2'
    BASE_API_URL = 'https://nominatim.openstreetmap.org/search'
    HEADERS = {'Referer': 'https://www.ics.uci.edu/~thornton/icsh32'
               f'/ProjectGuide/Project3/{UCINETID}'}

    def __init__(self, target: str):
        self.target = target
        json_data = self.get_json_data()
        self.json_data = json_data[0]
        self.url = json_data[1]
        
    def get_json_data(self) -> dict:
        '''attemps to get json data but waits 1 second before contacting
        server, and returns the data as a dict''' 
        time.sleep(1)
        url = self._make_url(self.target)
        request = self._make_request(url)
        json_data = self._send_request(request)
        return json_data

    def _make_url(self, target: str) -> str:
        '''makaes a url to send to server based on queries'''
        encoded_params = urllib.parse.urlencode([('q', target), ('format',
                                                                 'jsonv2')])
        return f'{self.BASE_API_URL}?{encoded_params}'

    def _make_request(self, url: str) -> urllib.request.Request:
        '''makes a request using url and headers'''
        return urllib.request.Request(url, headers = self.HEADERS)
                                      
    def _send_request(self, request: urllib.request.Request) -> dict:
        '''sends request'''
        return class_utils.send_request(request)
        
    def get_coordinates(self) -> tuple:
        '''gets the coordinates specifying where the input location is'''
        return (class_utils.access_json_data(self.json_data, [0, 'lat'],
                url=self.url, cast=float),
                class_utils.access_json_data(self.json_data, [0, 'lon'],
                url=self.url, cast=float))

class ReverseGeocodingWithFile:
    def __init__(self, file_name):
        self.file_name = file_name
        self.json_data = self.get_json_data()
        
    def get_json_data(self) -> dict:
        '''attmeps to get json data and catches any errors to raise custom
        error'''
        try:
            with open(self.file_name, 'r') as file:
                json_data = json.loads(file.read())
                return json_data
        except OSError:
            raise program_errors.FileFailureError(self.file_name, 'missing')
        except json.decoder.JSONDecodeError:
            raise program_errors.FileFailureError(self.file_name, 'format')

    def get_location(self) -> str:
        '''gets name of location from file'''
        return class_utils.access_json_data(self.json_data, ['display_name'],
                                            path=self.file_name)

class ReverseGeocodingWithApi:
    UCINETID = 'rniciu'
    FORMAT = 'jsonv2'
    BASE_API_URL = 'https://nominatim.openstreetmap.org/reverse'
    HEADERS = {'Referer': 'https://www.ics.uci.edu/~thornton/icsh32'
               f'/ProjectGuide/Project3/{UCINETID}'}

    def __init__(self, coordinates):
        self.lat, self.lon = coordinates
        json_data = self.get_json_data()
        self.json_data = json_data[0]
        self.url = json_data[1]
        
    def get_json_data(self) -> dict:
        '''gets data from server and turns it into a dict'''
        time.sleep(1)
        url = self._make_url(self.lat, self.lon)
        request = self._make_request(url)
        json_data = self._send_request(request)
        return json_data

    def _make_url(self, lat: float, lon: float) -> str:
        '''creates url to send to server'''
        encoded_params = urllib.parse.urlencode([('lat', lat), ('lon', lon),
                                                 ('format', 'jsonv2')])
        return f'{self.BASE_API_URL}?{encoded_params}'

    def _make_request(self, url: str) -> urllib.request.Request:
        return urllib.request.Request(url, headers = self.HEADERS)
                                      
    def _send_request(self, request: urllib.request.Request) -> dict:
        return class_utils.send_request(request)

    def get_location(self):
        '''gets location description based on server response'''
        return class_utils.access_json_data(self.json_data, ['display_name'],
                                            url=self.url)

def format_coordinates(coordinates: tuple):
    '''formats the coordinates to match the requirements of ending in /N, /S,
    /E, or /W'''
    lat, lon = coordinates

    if lat >= 0:
        lat = f'{lat}/N'
    else:
        lat = f'{-lat}/S'

    if lon >= 0:
        lon = f'{lon}/E'
    else:
        lon = f'{-lon}/W'

    return (lat, lon)
