import json
import socket
import threading
from chord_node_reference import ChordNodeReference
from utils_server import *
from const import * 
import time
from data_manager import DataManager
main_dir = "./Data_base"
import os

class ChordNode:
    def __init__(self, ip: str, port: int = DEFAULT_NODE_PORT, m: int = 7):
        self.id = calculate_hash(ip, m)
        self.ip = ip
        self.port = port
        self.ref = ChordNodeReference(self.ip, self.port)
        self.succ: ChordNodeReference = self.ref  # Nodo sucesor
        self.predpred: ChordNodeReference = None # Nodo sucesor del sucesor
        self.pred: ChordNodeReference = None  # Nodo predecesor
        self.m = m # Número de bits
        self.finger_table = [self.ref]*self.m  # Tabla de finger
        self.next = 0  # Finger table index to fix next
        self.data_manager = DataManager(self.ip)

        # Start threads
        threading.Thread(target=self.stabilize, daemon=True).start()
        threading.Thread(target=self.check_predecessor, daemon=True).start()
        threading.Thread(target=self.start_chord_server, daemon=True).start()  
        threading.Thread(target=self.fix_fingers, daemon=True).start()

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
    
    # Notify method to inform the node about another node
    def notify(self, node: 'ChordNodeReference'):
        print(f"[*] Node {node.ip} notified me, acting...")
        if node.id == self.id:
            pass
        else:
            if self.pred is None:
                self.pred = node
                self.predpred = node.pred
                pull_socket = get_socket(node.ip)
                pull_socket.sendall(f'{PUSH_MY_INFO}'.encode('utf-8'))
                self.data_manager.pull_data(owner_info=PRED_INFO,clean_info=True,conn=pull_socket)
                pull_socket.close()
                
            # Check node still exists
            elif node.check_node():
                # Check if node is between my predecessor and me
                if is_between(node.id, self.pred.id, self.id):
                    self.predpred = self.pred
                    self.pred = node

                    # Cuando entra un nodo entre mi predecesor y yo
                    # Delegar al nuevo nodo la información que ya no me pertenece
                    self.data_manager.delegate_data(self.pred.ip)

                    # 
                    pull_socket = get_socket(node.ip)
                    pull_socket.sendall(f'{PUSH_MY_INFO}'.encode('utf-8'))
                    self.data_manager.pull_data(owner_info=PRED_INFO,clean_info=True,conn=pull_socket)
                    pull_socket.close()

                    push_socket = get_socket(self.pred.ip)
                    push_socket.sendall(f'{PULL_PRED_INFO}'.encode('utf-8'))
                    resp = push_socket.recv(1024).decode('utf-8')
                    if resp != 'OK':
                        raise Exception("ACK negativo")
                    self.data_manager.push_data(owner_info=MY_INFO,clean_info=False,conn=push_socket)
                    push_socket.close()

                    push_socket = get_socket(self.succ.ip)
                    push_socket.sendall(f'{PULL_SUCC_INFO}'.encode('utf-8'))
                    resp = push_socket.recv(1024).decode('utf-8')
                    if resp != 'OK':
                        raise Exception("ACK negativo")
                    self.data_manager.push_data(owner_info=MY_INFO,clean_info=False,conn=push_socket)
                    push_socket.close()



                    
        print(f"[*] end act...")
    
    def reverse_notify(self, node: 'ChordNodeReference'):
        print(f"[*] Node {node.id} reversed notified me, acting...")
        self.succ = node
        print(f"[*] end act...")

    def not_alone_notify(self, node: 'ChordNodeReference'):
        print(f"[*] Node {node.ip} say I am not alone now, acting..")
        self.succ = node
        self.pred = node
        self.predpred = self.ref

        self.data_manager.delegate_data(self.pred.ip)

        swap_socket = get_socket(node.ip)
        swap_socket.sendall(f'{PUSH_MY_INFO}'.encode('utf-8'))
        self.data_manager.pull_data(owner_info=PRED_INFO,clean_info=True,conn=swap_socket)

        swap_socket.sendall(f'{PUSH_MY_INFO}'.encode('utf-8'))
        self.data_manager.pull_data(owner_info=SUCC_INFO,clean_info=True,conn=swap_socket)

        swap_socket.sendall(f'{PULL_PRED_INFO}'.encode('utf-8'))
        resp = swap_socket.recv(1024).decode('utf-8')
        if resp != 'OK':
            raise Exception("ACK negativo")
        self.data_manager.push_data(owner_info=MY_INFO,clean_info=False,conn=swap_socket)

        swap_socket.sendall(f'{PULL_SUCC_INFO}'.encode('utf-8'))
        resp = swap_socket.recv(1024).decode('utf-8')
        if resp != 'OK':
            raise Exception("ACK negativo")
        self.data_manager.push_data(owner_info=MY_INFO,clean_info=False,conn=swap_socket)

        swap_socket.close()

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

        print(f'Predecesor: ID -> {self.pred.id if self.pred != None else -1}, {self.pred.ip if self.pred != None else -1}:{self.pred.port if self.pred != None else -1}')
        print(f'Me: {self.id}')
        print(f'Sucesor: ID -> {self.succ.id}, {self.succ.ip}:{self.succ.port}')
        print("[*] end join")

    # Stabilize method to periodically verify and update the successor and predecessor
    def stabilize(self):
        while True:
            if self.succ.id != self.id:
                print('[⚖] Stabilizating...')

                # Check successor is alive before stabilization
                if self.succ.check_node():
                    x = self.succ.pred

                    if x.id != self.id:
                        
                        # Check is there is anyone between me and my successor
                        if x and inbetween(x.id, self.id, self.succ.id):
                            # Setearlo si no es el mismo
                            if x.id != self.succ.id:
                                self.succ = x

                                # Actualizar la información de x en self.rep_succ, porque self cambió de sucesor
                                pull_socket = get_socket(x.ip)
                                pull_socket.sendall(f'{PUSH_MY_INFO}'.encode('utf-8'))
                                self.data_manager.pull_data(owner_info=SUCC_INFO, clean_info=True,conn=pull_socket)
                                pull_socket.close()

                        # Notify mi successor
                        self.succ.notify(self.ref)

                        print(f'PredPred: ID -> {self.predpred.id if self.predpred != None else -1}, {self.predpred.ip if self.predpred != None else -1}:{self.predpred.port if self.predpred != None else -1}')
                        print(f'Predecesor: ID -> {self.pred.id if self.pred != None else -1}, {self.pred.ip if self.pred != None else -1}:{self.pred.port if self.pred != None else -1}')
                        print(f'Me: {self.id}')
                        print(f'Sucesor: ID -> {self.succ.id}, {self.succ.ip}:{self.succ.port}')
                        print('[⚖] end stabilize...')
                    else:
                        print(f'PredPred: ID -> {self.predpred.id if self.predpred != None else -1}, {self.predpred.ip if self.predpred != None else -1}:{self.predpred.port if self.predpred != None else -1}')
                        print(f'Predecesor: ID -> {self.pred.id if self.pred != None else -1}, {self.pred.ip if self.pred != None else -1}:{self.pred.port if self.pred != None else -1}')
                        print(f'Me: {self.id}')
                        print(f'Sucesor: ID -> {self.succ.id}, {self.succ.ip}:{self.succ.port}')
                        print("[⚖] 🟢 Already stable")

                    if self.pred and self.pred.check_node():
                        self.predpred = self.pred.pred

                else:
                    print("[⚖] I lost my successor, waiting for predecesor check...")

            time.sleep(10)

        # Fix fingers method to periodically update the finger table
    def fix_fingers(self):
        batch_size = 10
        while True:
            for _ in range(batch_size):
                try:
                    self.next += 1
                    if self.next >= self.m:
                        self.next = 0
                    self.finger[self.next] = self.lookup((self.id + 2 ** self.next) % 2 ** self.m)
                except Exception as e:
                    pass
            time.sleep(5)

    # Check predecessor method to periodically verify if the predecessor is alive
    def check_predecessor(self):
        while True:
            print("[*] Checking predecesor...")
            try:
                if self.pred and not self.pred.check_node():
                    print("[-] Predecesor failed")
                    two_nodes_failed = False

                    if self.predpred.check_node():
                        self.pred = self.predpred
                        self.predpred = self.predpred.pred

                    else:
                        self.pred = self.find_pred(self.predpred.id)
                        self.predpred = self.pred.pred
                        two_nodes_failed = True

                    if self.pred.id == self.id:
                        self.succ = self.ref
                        self.pred = None
                        self.predpred = None

                        if two_nodes_failed:
                            self.data_manager.assume_data(assume_predpred=self.ip)
                        else:
                            self.data_manager.assume_data()
                        continue

                    
                    self.pred.reverse_notify(self.ref)    

                    if two_nodes_failed:
                        self.data_manager.assume_data(assume_predpred=self.pred.ip) 
                    else:
                        self.data_manager.assume_data() 

                    swap_socket = get_socket(self.pred.ip)
                    swap_socket.sendall(f'{PUSH_MY_INFO}'.encode('utf-8'))
                    self.data_manager.pull_data(owner_info=PRED_INFO,clean_info=True,conn=swap_socket) 
                    
                    swap_socket.sendall(f'{PULL_SUCC_INFO}'.encode('utf-8'))
                    resp = swap_socket.recv(1024).decode('utf-8')
                    if resp != 'OK':
                        raise Exception("ACK negativo")
                    self.data_manager.push_data(owner_info=MY_INFO,clean_info=False,conn=swap_socket)
                    swap_socket.close()

                    push_socket = get_socket(self.succ.ip)
                    push_socket.sendall(f'{PULL_PRED_INFO}'.encode('utf-8'))
                    resp = push_socket.recv(1024).decode('utf-8')
                    if resp != 'OK':
                        raise Exception("ACK negativo")
                    self.data_manager.push_data(owner_info=MY_INFO,clean_info=False,conn=push_socket)
                    push_socket.close()


            except Exception as e:
                self.pred = None
                self.succ = self.ref

            time.sleep(10)
            pass

    def request_handler(self, conn: socket, addr, data: list):
        resp = None
        option = int(data[0])
        file_content = None

        if option == FIND_PREDECESSOR:
            target_id = int(data[1])
            node = self.find_pred(target_id)
            resp = {'state':'OK','id':node.id, 'ip':ip}

        elif option == LOOKUP:
            target_id = int(data[1])
            node = self.lookup(target_id)
            resp = {'state':'OK','id':node.id, 'ip': node.ip}

        elif option == GET_SUCCESSOR:
            node = self.succ if self.succ else self.ref
            resp = {'state':'OK','id':node.id,'ip':node.ip}

        elif option == GET_PREDECESSOR:
            node = self.pred if self.pred else self.ref
            resp = {'state':'OK','id':node.id, 'ip': node.ip}

        elif option == NOTIFY:
            ip = data[2]
            self.notify(ChordNodeReference(ip, self.port))
            resp = {'state':'OK'}

        elif option == REVERSE_NOTIFY:
            ip = data[2]
            self.reverse_notify(ChordNodeReference(ip, self.port))
            resp = {'state':'OK'}

        elif option == NOT_ALONE_NOTIFY:
            ip = data[2]
            self.not_alone_notify(ChordNodeReference(ip, self.port))
            resp = {'state':'OK'}

        elif option == CHECK_NODE:
            node = self.ref
            resp = {'state':'OK','id':node.id, 'ip': node.ip}

        elif option == ADD_TAGS_TO_FILE:
            file_name = data[1]
            tag_names = json.loads(data[2].replace("'", '"'))
            self.data_manager.add_tags_to_my_file(file_name,tag_names)
            resp = {'state':'OK'}

        elif option == ADD_TAGS_TO_FILE_UPLOAD:
            file_name = data[1]
            file_size = int(data[2])
            tag_names = json.loads(data[3].replace("'", '"'))

            if self.data_manager.check_my_file(file_name):
                resp = {'state': 'Error', 'message': f'File "{file_name}" is already in database'}
            
            else:
                self.data_manager.add_tags_to_my_file(file_name,tag_names)
                conn.sendall('OK'.encode('utf-8'))
                file_data = recv_file(file_size,conn)
                self.data_manager.upload_my_file(file_name,file_data)
                print('hizo upload')
                resp = {'state':'OK'}

        elif option == DOWNLOAD_FILE:
            file_name = data[1]
            file_content,file_size = self.data_manager.delete_my_file(file_name)
            conn.sendall(str(file_size).encode('utf-8'))
            response = conn.recv(1024).decode('utf-8')
            if response == 'OK':
                conn.sendall(file_content)
                return
        elif option == ADD_FILES_TO_TAG:
            tag_name = data[1]
            file_names = json.loads(data[2].replace("'", '"'))
            self.data_manager.add_files_to_my_tag(tag_name,file_names)
            resp = {'state':'OK'}

        elif option == GET_FILES_FROM_TAG:
            tag_name = data[1]
            files = self.data_manager.get_files_from_my_tag(tag_name)
            resp = {'state':'OK','files':files}

        elif option == DELETE_FILE:
            file_name = data[1]
            self.data_manager.delete_my_file(file_name)
            resp = {'state':'OK'}

        elif option == GET_TAGS_FROM_FILE:
            file_name = data[1]
            tags = self.data_manager.get_tags_from_my_file(file_name)
            resp = {'state':'OK','tags':tags}
                
        elif option == DELETE_FILES_FROM_TAG:
            tag_name = data[1]
            file_list = json.loads(data[2].replace("'", '"'))
            self.data_manager.remove_files_from_my_tag(tag_name,file_list)
            resp = {'state':'OK'}
        elif option == DELETE_TAGS_FROM_FILE:
            file_name = data[1]
            tag_list = json.loads(data[2].replace("'", '"'))
            self.data_manager.remove_tags_from_my_file(file_name,tag_list)
            resp = {'state':'OK'}
        elif option == GET_ALL_FILES:
            files = self.data_manager.get_all_my_files()
            tags = self.data_manager.get_all_tags_in_my_files()
            resp = {'state':'OK','files':files,'tags':tags}


        if resp:
            conn.sendall(json.dumps(resp).encode('utf-8'))

        conn.close()

    # Start server method to handle incoming requests
    def start_chord_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            s.listen(10)

            while True:
                conn, addr = s.accept()
                data = process_data(conn.recv(1024).decode('utf-8'))

                threading.Thread(target=self.request_handler, args=(conn, addr, data)).start()
                
    