import json
import program_errors
import urllib.request


def send_request(request: urllib.request) -> tuple:
    '''sends a request to the server and montitors any errors that might occur.
    If the server can't connect or the status code is not 200 or if the
    data can't be interpreted as json, the custom api exception is raised'''
    ENCODING = 'utf-8'
    
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        error_url = e.url
        status_code = e.code
        raise program_errors.ApiFailureError(e.url, 'not 200', e.code)
    except urllib.error.URLError:
        raise program_errors.ApiFailureError(request.full_url, 'network')
        

    status_code = response.getcode()
    if status_code != 200:
        raise ApiFailureError(request.full_url, 'not 200', status_code)
        
    data = response.read()
    response.close()
    try:
        text = data.decode(encoding = ENCODING)
    except UnicodeDecodeError:
        raise program_errors.ApiFailureError(request.full_url, 'format',
                                             status_code)
    
    try:
        json_data = json.loads(text)
    except json.JSONDecodeError:
        raise program_errors.ApiFailureError(request.full_url, 'format',
                                             status_code)
        
    return (json_data, request.full_url)

def access_json_data(data: dict, keys: list[str], path: str = None,
                     url: str = None, cast: type = None) -> str:
    '''safely access any json data and raises an exception if the data is not
    formatted as expected. Method is called most of the time when json data
    from a file or api is accessed. Cast will cast the final value and
    return the casted value, which may not return a string'''
    try:
        for key in keys:
            data = data[key]
            
        if cast != None:
            data = cast(data)
            
        return data
    except (KeyError, TypeError, IndexError, ValueError):
        if path != None:
            raise program_errors.FileFailureError(path, 'format')
        else:
            #if program hasn't failed by now, status code must be 200
            raise program_errors.ApiFailureError(url, 'format', status_code=200)
    
