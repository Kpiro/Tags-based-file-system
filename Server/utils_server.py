from colorama import Fore, Style
import hashlib
from const import *


def auto_save(method):
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self.save_database()
        return result
    return wrapper


def calculate_hash(value : str, m: int = 7):
    """Calcula el hash de una clave usando SHA-1."""
    return int(hashlib.sha1(value.encode('utf-8')).hexdigest(), 16) % (2**m)

# Function to check if n id is between two other id's in chord ring
def inbetween(k: int, start: int, end: int) -> bool:
    if start < end:
        return start < k <= end
    else:  # The interval wraps around 0
        return start < k or k <= end

# Cut a list by commas and ignore the commas inside a list   
def process_data(data: str):
    start = data.find('[')
    if start != -1:
        return data[:start-1].split(',') + [data[start:]]

    return data.split(',')

class Response():
    def __init__(self,msg=''):
        self.msg = msg
        self.icon = ''
    def __str__(self):
        return f'{self.icon} {self.msg}'
        
class ErrorMSG(Response):
    def __init__(self, msg):
        super().__init__(msg = msg)
        self.icon = '❌[ERROR]'
class SuccesMSG(Response):
    def __init__(self, msg):
        super().__init__(msg = msg)
        self.icon = '✅[SUCCESSFULLY OPERATION]'

class FilesMSG(Response):
    def __init__(self, msg,file_list, tag_list=None):
        super().__init__(msg = msg)
        self.icon = '🗂️[FILES]\n'
        self.file_list = file_list
        self.tag_list = tag_list
        self.msg = self.show_files(file_list)

    def show_files(self):
        if self.tag_list:
            for i,file,tags in enumerate(zip(self.file_list,self.tag_list)):
                self.msg += f'{Fore.WHITE}{i+1}- {file} : {tags}\n'
        else:
            for i,file in enumerate(self.file_list):
                self.msg += f'{Fore.WHITE}{i+1}- {file}\n'


    

    

   