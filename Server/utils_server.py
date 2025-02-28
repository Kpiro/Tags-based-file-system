from colorama import Fore, Style
import hashlib
from const import *
import socket
def get_socket(ip):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, DEFAULT_DATA_PORT))
        return s
def is_between(k: int, start: int, end: int) -> bool:
    if start < end:
        return start < k <= end
    else:  # The interval wraps around 0
        return start < k or k <= end
    
def recv_file(file_size, conn):
    file_data = bytearray()
    received_size = 0
    while received_size < file_size:
        data = conn.recv(1024)  # Recibir 1024 bytes
        if not data:
            break
        file_data.extend(data)  # Agregar los datos a la variable
        received_size += len(data)
    return file_data
def send_file(file_name, file_size,file_content,conn):
    conn.sendall(f'{file_name},{file_size}')
    resp = conn.recv(1024).decode('utf-8')
    conn.sendall(file_content)
    resp = conn.recv(1024).decode('utf-8')
    return resp   

def send_multiple_files(file_list, get_file_function, conn):
    for file_name in file_list:
        file_content, file_size = get_file_function(file_name)
        resp = send_file(file_name,file_size,file_content,conn)
        if resp != 'OK':
            break
            #FATAL
    conn.sendall('end-file') 
def recv_multiple_files(conn):
    file_list = []
    len_list = []
    content_list = []
    while True:
        file_info = conn.recv(1024).decode('utf-8')
        if file_info == 'end_file':
            break
        
        conn.send('OK'.encode('utf-8'))
        file_info = file_info.split(',')
        file_name = file_info[0]
        file_size = int(file_info[1])
        file_list.append(file_name)
        len_list.append(file_size)
        # Variable para almacenar el archivo en memoria
        file_data = recv_file(file_size,conn)
        content_list.append(file_data)
        conn.send('OK'.encode('utf-8'))
    return file_list,len_list,content_list


def auto_save(method):
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self.save_database()
        return result
    return wrapper


def calculate_hash(ip : int, m: int = 7):
    """Calcula el hash de una clave usando SHA-1."""
    return int(hashlib.sha1(f'{ip}'.encode('utf-8')).hexdigest(), 16) % (2**m)

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


def show_files(file_list,tag_list):
    msg = ''
    if tag_list:
        for i,(file,tags) in enumerate(zip(file_list,tag_list)):
            msg += f'{Fore.WHITE}{i+1}- {file} : {tags}\n'
    else:
        for i,file in enumerate(file_list):
            msg += f'{Fore.WHITE}{i+1}- {file}\n'
    return msg
class FilesMSG(Response):
    def __init__(self, file_list, tag_list=None):
        print('filemsg',file_list)
        super().__init__(msg = show_files(file_list,tag_list))
        self.icon = '🗂️[FILES]\n'





    

    

   