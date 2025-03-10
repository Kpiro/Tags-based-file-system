import json
import os
import shutil
from colorama import Fore, Style
import hashlib
from const import *
import socket


def update_neighbor_data(update_function, conn = None, two_params = True):
    obj_name = conn.recv(1024).decode('utf-8')
    
    if two_params:
        conn.sendall('OK'.encode('utf-8'))
        recv = conn.recv(1024)
        if recv:
            obj_list = json.loads(recv.decode('utf-8'))
        else:
            obj_list = []
        update_function(obj_name,obj_list)
        conn.sendall('OK'.encode('utf-8'))
    else:
        update_function(obj_name)
        conn.sendall('OK'.encode('utf-8'))
    


    
def notify_neighbor(op: int, ip: str, obj_name: str, obj_list: list = None, content = None):
    sock = get_socket(ip)

    sock.sendall(f'{op}'.encode('utf-8'))
    resp = sock.recv(1024).decode('utf-8')
    if resp != 'OK':
        raise Exception ('ACK negative!')
    
    if content:
        sock.sendall(f'{obj_name},{len(content)}'.encode('utf-8'))
        resp = sock.recv(1024).decode('utf-8')
        if resp != 'OK':
            raise Exception ('ACK negative!')
        
        sock.sendall(content)
        resp = sock.recv(1024).decode('utf-8')
        if resp != 'OK':
            raise Exception ('ACK negative!')
    else:
        sock.sendall(obj_name.encode('utf-8'))
        resp = sock.recv(1024).decode('utf-8')
        if resp != 'OK':
            raise Exception ('ACK negative!')
        
        if obj_list:
            sock.sendall(json.dumps(obj_list).encode('utf-8'))
            resp = sock.recv(1024).decode('utf-8')
            if resp != 'OK':
                raise Exception ('ACK negative!')
            
    print(' 🔄 Replication updated in server "{ip}"')
    sock.close()

    



def to_json_list(dict):
    return {key: list(value) for key, value in dict.items()}

def to_json_set(dict):
    return {key: set(value) for key, value in dict.items()}

def remove_server_dir(id):
    folder_dir = os.path.join(MAIN_DIR, str(id))
    if os.path.exists(folder_dir):
        try:
            shutil.rmtree(folder_dir)
            print(f'📁 La carpeta "{id}" fue eliminado satisfactoriamente.')
        except Exception:
            print(f'No se pudo eliminar la carpeta "{id}"')
    else:
        print(f'La carpeta "{id}" no existe.')

def get_socket(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
    conn.sendall(f'{file_name},{file_size}'.encode('utf-8'))
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
    conn.sendall('end-file'.encode('utf-8')) 
def recv_multiple_files(conn):
    file_list = []
    len_list = []
    content_list = []
    while True:
        file_info = conn.recv(1024).decode('utf-8')
        print('😍file_info', file_info)
        if file_info == 'end-file':
            print('😍entrar al break')
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





    

    

   