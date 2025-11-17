class ApiFailureError(Exception):
    '''exception raised when problems related to api/web usage occur'''
    def __init__(self, url, api_error, status_code = None):
        self.status_code = status_code
        self.url = url
        self.api_error = api_error.upper()
        
    def print_failure_message(self) -> None:
        '''prints faliure message including last visited url and reason for
        failure'''
        print('FAILED')
        if self.status_code != None:
            print(f'{self.status_code} {self.url}')
        else:
            print(self.url)

        print(self.api_error.upper())
       
class FileFailureError(Exception):
    '''exception raised when problems related to reading from a file occur'''
    def __init__(self, file_path, file_error):
        self.file_path = file_path
        self.file_error = file_error

    def print_failure_message(self) -> None:
        '''prints failure message and includes file name'''
        print('FAILED')
        print(f'{self.file_path}')
        print(self.file_error.upper())

