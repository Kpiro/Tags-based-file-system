import socket
import threading
from chord_node_reference import ChordNodeReference
from utils_server import *
from const import * 

class ChordNode:
    def __init__(self, ip: str, port: int, m: int = 7):
        self.id = calculate_hash(f'{ip}:{str(port)}', m)
        self.ip = ip
        self.port = port
        self.ref = ChordNodeReference(self.ip, self.port)
        self.succ: ChordNodeReference = None  # Nodo sucesor
        self.predpred: ChordNodeReference = None # Nodo sucesor del sucesor
        self.pred: ChordNodeReference = None  # Nodo predecesor
        self.m = m # Número de bits
        self.finger_table = [ChordNodeReference]*self.m  # Tabla de finger
        self.files_data = {}  # Archivos de los que es responsable
        self.tags_data = {} # Etiquetas de la que es responsable

        # Start threads
        threading.Thread(target=self.start_chord_server, daemon=True).start()  

    # Method to find the predecessor of a given id
    def find_pred(self, id: int) -> 'ChordNodeReference':
        node = self
        while not inbetween(id, node.id, node.succ.id):
            node = node.succ
        return node.ref if isinstance(node, ChordNode) else node

    def lookup(self, id: int) -> 'ChordNodeReference':
        if self.id == id:
            return self.ref
        # If the id is in the interval (this node's ID, its successor's ID], return the successor.
        if inbetween(id, self.id, self.succ.id):
            return self.succ
        
        # Otherwise, find the closest preceding node in the finger table and ask it.
        for i in range(len(self.finger_table) - 1, -1, -1):
            if self.finger_table[i] and inbetween(self.finger_table[i].id, self.id, id):
                if self.finger_table[i].check_node():
                    return self.finger_table[i].lookup(id)
        
        return self.succ
    
    def not_alone_notify(self, node: 'ChordNodeReference'):
        print(f"[*] Node {node.ip} say I am not alone now, acting..")
        self.succ = node
        self.pred = node
        self.predpred = self.ref

        print(f"[*] end act...")
    
    # Method to join a Chord network using 'node' as an entry point
    def join(self, node: 'ChordNodeReference' = None):
        print("[*] Joining...")
        if node:
            if not node.check_node():
                raise Exception(f"There is no node using the address {node.ip}")
            
            self.pred = None
            self.predpred = None
            self.succ = node.lookup(self.id)

            # Second node joins to chord ring
            if self.succ.succ.id == self.succ.id:
                self.pred = self.succ
                self.predpred = self.ref
                # Notify node he is not alone
                self.succ.not_alone_notify(self.ref)
        else:
            self.succ = self.ref
            self.pred = None
            self.predpred = None

        print(f'Sucesor: {self.succ.ip}:{self.succ.port}')
        print("[*] end join")

    # Notify method to inform the node about another node
    def notify(self, node: 'ChordNodeReference'):
        print(f"[*] Node {node.ip} notified me, acting...")
        if node.id == self.id:
            pass
        else:
            if self.pred is None:
                self.pred = node
                self.predpred = node.pred
                
            # Check node still exists
            elif node.check_node():
                # Check if node is between my predecessor and me
                if inbetween(node.id, self.pred.id, self.id):
                    self.predpred = self.pred
                    self.pred = node
        print(f"[*] end act...")

    def request_handler(self, conn: socket, addr, data: list):
        data_resp = None
        option = int(data[0])

        if option == FIND_PREDECESSOR:
            target_id = int(data[1])
            data_resp = self.find_pred(target_id)

        elif option == LOOKUP:
            print('aqui')
            target_id = int(data[1])
            data_resp = self.lookup(target_id)

        elif option == GET_SUCCESSOR:
            data_resp = self.succ if self.succ else self.ref

        elif option == GET_PREDECESSOR:
            data_resp = self.pred if self.pred else self.ref

        elif option == NOTIFY:
            ip = data[2]
            self.notify(ChordNodeReference(ip, self.port))

        elif option == NOT_ALONE_NOTIFY:
            ip = data[2]
            self.not_alone_notify(ChordNodeReference(ip, self.port))

        elif option == CHECK_NODE:
            data_resp = self.ref

        # Send response
        if data_resp:
            response = f'{data_resp.id},{data_resp.ip}'.encode('utf-8')
            conn.sendall(response)
        conn.close()


    # Start server method to handle incoming requests
    def start_chord_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            s.listen(10)

            while True:
                conn, addr = s.accept()
                data = conn.recv(1024).decode('utf-8').split(',')

                threading.Thread(target=self.request_handler, args=(conn, addr, data)).start()
    