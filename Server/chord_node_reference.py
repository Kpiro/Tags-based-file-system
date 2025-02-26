import json
import socket
from typing import List
from const import *
from utils_server import calculate_hash

class ChordNodeReference:
    def __init__(self, ip: str, port: int = 8001):
        self.id = calculate_hash(f'{ip}:{port}')
        self.ip = ip
        self.port = port

    def _send_data(self, op: int, data: str = None) -> bytes:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, self.port))
                s.sendall(f'{op},{data}'.encode('utf-8'))
                return json.loads(s.recv(1024).decode('utf-8'))
        except Exception as e:
            print(f"Error sending data: {e}")
            response = {'state':'Error','message':'🔌Problema de conexión'}
            return response
        
    # Method to find the predecessor of a given id
    def find_predecessor(self, id: int) -> 'ChordNodeReference':
        response = self._send_data(FIND_PREDECESSOR, str(id)).decode('utf-8').split(',')
        ip = response[1]
        return ChordNodeReference(ip, self.port)

    # Property to get the successor of the current node
    @property
    def succ(self) -> 'ChordNodeReference':
        response = self._send_data(GET_SUCCESSOR)
        if response['state']!= 'Error':
            return ChordNodeReference(response['ip'], self.port)
        else:
            print(response['message'])

    # Property to get the predecessor of the current node
    @property
    def pred(self) -> 'ChordNodeReference':
        response = self._send_data(GET_PREDECESSOR)
        if response['state']!= 'Error':
            return ChordNodeReference(response['ip'], self.port)
        else:
            print(response['message'])

    # Method to notify the current node about another node
    def notify(self, node: 'ChordNodeReference'):
        response = self._send_data(NOTIFY, f'{node.id},{node.ip}')
        if response['state']=='Error':
            print(response['message'])
    def reverse_notify(self, node: 'ChordNodeReference'):
        response = self._send_data(REVERSE_NOTIFY, f'{node.id},{node.ip}')
        if response['state']=='Error':
            print(response['message'])

    def not_alone_notify(self, node: 'ChordNodeReference'):
        response = self._send_data(NOT_ALONE_NOTIFY, f'{node.id},{node.ip}')
        if response['state']=='Error':
            print(response['message'])

    # Method to check if the predecessor is alive
    def check_node(self) -> bool:
        response = self._send_data(CHECK_NODE)
        if response['state']=='Error':
            print(response['message'])
            return False
        else:
            return True
        
    
    def lookup(self, id: int):
        response = self._send_data(LOOKUP, str(id))
        if response['state']!= 'Error':
            return ChordNodeReference(response['ip'], self.port)
        else:
            print(response['message'])
    
    # ----------------- DATABASE -------------------------------------
    def add_files_to_tag(self, tag: str, file_names: List[str]):
        """Appends files names to tag (works from any node)"""
        response = self._send_data(ADD_FILES_TO_TAG, f"{tag},{file_names}")
        return response
    
    def add_tags_to_file(self, file_name: List[str], tag_names: str,len = None, content=None):
        """Appends tags names to file (works from any node)"""
       
        if len and content:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.ip, self.port))
                    s.sendall(f'{ADD_TAGS_TO_FILE_UPLOAD},{file_name},{len},{tag_names}'.encode('utf-8'))
                    response = s.recv(1024).decode('utf-8')
                    if response == 'OK':
                        s.sendall(content)
                        print('mando content')
                        response = json.loads(s.recv(1024).decode('utf-8'))
                        print('recibio respuesta')
                        print(response)
                    else:
                        response = {'state':'Error','message':'🔌Problema de conexión'}

            except Exception as e:
                print(f"Error sending data: {e}")
                response = {'state':'Error','message':'🔌Problema de conexión'}
        else:
            response = self._send_data(ADD_TAGS_TO_FILE, f"{file_name},{tag_names}")

        print('antes del return : ', response)
        return response
    
    def download_file(self,file_name):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, self.port))
                s.sendall(f'{DOWNLOAD_FILE},{file_name}'.encode('utf-8'))
                json_recv = json.loads(s.recv(1024).decode('utf-8'))
                if json_recv['state'] == 'OK':
                    file_size = int(json_recv['file_size'])
                    # Variable para almacenar el archivo en memoria
                    file_data = bytearray()  # Usamos bytearray para eficiencia en concatenación
                    # Recibir el archivo en bloques
                    received_size = 0
                    while received_size < file_size:
                        data = s.recv(1024)  # Recibir 1024 bytes
                        if not data:
                            break
                        file_data.extend(data)  # Agregar los datos a la variable
                        received_size += len(data)
                    return file_data,file_size
                else:
                    return {'state':'Error','message':'File {filename} could not be downloaded'}
        except Exception as e:
            return {'state':'Error','message':'🔌Connection Problem'}

    def get_files_from_tag(self, tag_name:str):
        """Get files with the given tag"""
        response = self._send_data(GET_FILES_FROM_TAG, f"{tag_name}").decode('utf-8')
        return response
    
    def get_tags_from_file(self, file_name:str):
        """Get files with the given tag"""
        response = self._send_data(GET_TAGS_FROM_FILE, f"{file_name}").decode('utf-8')
        return response
    
    def delete_file(self, file_name:str):
        """Get files with the given tag"""
        response = self._send_data(DELETE_FILE, f"{file_name}").decode('utf-8')
        return response
    
    def delete_files_from_tag(self, tag_name:str):
        """Get files with the given tag"""
        response = self._send_data(DELETE_FILES_FROM_TAG, f"{tag_name}").decode('utf-8')
        return response
    
    def delete_tags_from_file(self, file_name:str):
        """Get files with the given tag"""
        response = self._send_data(DELETE_TAGS_FROM_FILE, f"{file_name}").decode('utf-8')
        return response
    
    def get_all_files(self):
        """Get all files that belong to a server"""
        response = self._send_data(GET_ALL_FILES).decode('utf-8')
        return response
    
    def __str__(self) -> str:
        return f'{self.id},{self.ip},{self.port}'

    def __repr__(self) -> str:
        return str(self)
    