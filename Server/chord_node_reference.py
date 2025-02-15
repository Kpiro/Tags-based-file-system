import socket
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
                return s.recv(1024)
        except Exception as e:
            print(f"Error sending data: {e}")
            return b''
        
    # Method to find the predecessor of a given id
    def find_predecessor(self, id: int) -> 'ChordNodeReference':
        response = self._send_data(FIND_PREDECESSOR, str(id)).decode('utf-8').split(',')
        ip = response[1]
        return ChordNodeReference(ip, self.port)

    # Property to get the successor of the current node
    @property
    def succ(self) -> 'ChordNodeReference':
        response = self._send_data(GET_SUCCESSOR).decode('utf-8').split(',')
        return ChordNodeReference(response[1], self.port)

    # Property to get the predecessor of the current node
    @property
    def pred(self) -> 'ChordNodeReference':
        response = self._send_data(GET_PREDECESSOR).decode('utf-8').split(',')
        return ChordNodeReference(response[1], self.port)

    # Method to notify the current node about another node
    def notify(self, node: 'ChordNodeReference'):
        self._send_data(NOTIFY, f'{node.id},{node.ip}')

    def not_alone_notify(self, node: 'ChordNodeReference'):
        self._send_data(NOT_ALONE_NOTIFY, f'{node.id},{node.ip}')

    # Method to check if the predecessor is alive
    def check_node(self) -> bool:
        response = self._send_data(CHECK_NODE)
        if response != b'' and len(response.decode('utf-8')) > 0:
            # Node provide a response
            return True
        return False
    
    def lookup(self, id: int):
        # print('---------------------------------------------------------------')
        response = self._send_data(LOOKUP, str(id)).decode('utf-8').split(',')
        # print('---------------------------------------------------------------')
        # print('response:',response)
        return ChordNodeReference(response[1], self.port)
    