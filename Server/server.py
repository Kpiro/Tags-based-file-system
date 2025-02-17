import socket
import json
import sys
import threading
from FileSystem import TagFileSystem
from chord_node_reference import ChordNodeReference
from utils_server import *
from chord_node import ChordNode
from gateway_node import GatewayNode

class Server:

    def __init__(self,ip, port,known_node_ip=None, known_node_port=None):
        self.file_system = TagFileSystem("Server/data.json","Server/Storage")
        self.storage_path = "Server/Storage"
        self.node = GatewayNode(ip,int(port))

        threading.Thread(target=self.start_server, args=(ip,port)).start()
        if known_node_ip and known_node_port:
            threading.Thread(target=self.node.join, args=(ChordNodeReference(known_node_ip, known_node_port), )).start()
        else:
            threading.Thread(target=self.node.join).start()

    def start_server(self, ip, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((ip, 8005))
        server.listen(10)
        print(f"🚀 [SERVER] Running on {ip}:{port}")
        while True:
            client_socket, address = server.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, address)).start()

    def handle_client(self,client_socket, address):
        print(f"🔌 [CONNECTION] Client connected from {address}")
        try:
            while True:
                try:
                    request = client_socket.recv(1024).decode('utf-8')
                except:
                    self.file_system.save_db()
                    client_socket.close()
                    print(f"🔌🚫 [DISCONNECT] Client disconnected from {address}")
                    return
                # if not request:
                #     self.file_system.save_db()
                #     break
                response = self.process_request(request, client_socket)
                if response != None:
                    try:
                        client_socket.sendall(response.encode('utf-8'))
                    except:
                        client_socket.sendall(response)
                
        except Exception as e:
            print(e)
            client_socket.send(json.dumps({"error": str(e)}).encode('utf-8'))
            client_socket.close()
            print(f"🔌🚫 [DISCONNECT] Client disconnected from {address}")
            

    def process_request(self,request, client_socket):
        if request == 'show':
            client_socket.send('OK'.encode('utf-8'))
            return self.node.show()
        elif request == 'add-tags':
            client_socket.send('OK'.encode('utf-8'))
            tag_query = client_socket.recv(1024).decode('utf-8').split(',')
            client_socket.send('OK'.encode('utf-8'))
            tag_list = client_socket.recv(1024).decode('utf-8').split(',')
            return self.node.add_files(tag_query,tag_list)
        elif request == 'add-files':
            client_socket.send('OK'.encode('utf-8'))
            file_list = []
            len_list = []
            content_list = []
            file_name =''
            while True:
                file_info = client_socket.recv(1024).decode('utf-8')
                if file_info == 'end_file':
                    break
                
                file_info = file_info.split(',')
                file_name = file_info[0]
                file_size = file_info[1]
                file_list.append(file_name)
                len_list.append(file_size)
                # Variable para almacenar el archivo en memoria
                file_data = bytearray()  # Usamos bytearray para eficiencia en concatenación

                # Recibir el archivo en bloques
                received_size = 0
                while received_size < int(file_size):
                    data = client_socket.recv(1024)  # Recibir 1024 bytes
                    if not data:
                        break
                    file_data.extend(data)  # Agregar los datos a la variable
                    received_size += len(data)
                content_list.append(file_data)

                client_socket.send('OK'.encode('utf-8'))

            tag_list = client_socket.recv(1024).decode('utf-8').split('')
            return self.node.add_files(file_list,tag_list,len_list,content_list)


        elif request == 'delete-tags':
            client_socket.send('OK'.encode('utf-8'))
            tag_query = client_socket.recv(1024).decode('utf-8').split(',')
            client_socket.send('OK'.encode('utf-8'))
            tag_list = client_socket.recv(1024).decode('utf-8').split(',')
            return self.node.delete_tags(tag_query,tag_list)
        elif request == 'delete-files':
            client_socket.send('OK'.encode('utf-8'))
            tag_query = client_socket.recv(1024).decode('utf-8').split(',')
            return self.node.delete_files(tag_query)
        elif request == 'list':
            client_socket.send('OK'.encode('utf-8'))
            tag_query = client_socket.recv(1024).decode('utf-8').split(',')
            return self.node.list_files(tag_query)
        elif request == 'download':
            client_socket.send('OK'.encode('utf-8'))
            file_name = client_socket.recv(1024).decode('utf-8')
            file_content,file_size = self.node.download_file(file_name)
            client_socket.sendall(file_size).encode('utf-8')
            response = client_socket.recv(1024).decode('utf-8')
            if response != 'OK':
                return 'Error'
            return file_content



        
        




if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python server.py <IP> <PUERTO> -c [<NODO_CONOCIDO>]")
        sys.exit(1)

    # First node case
    elif len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        # Create node
        server = Server(ip, port)
        print(f"[IP]: {ip}")

    elif sys.argv[3] != '-c' or len(sys.argv) < 6:
        print("Uso: python server.py <IP> <PUERTO> -c [<NODO_CONOCIDO>]")
        sys.exit(1)       

    # Join node cases
    elif len(sys.argv) == 6:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        known_node_ip, known_node_port = sys.argv[4], int(sys.argv[5]) if len(sys.argv) > 3 else None

        server = Server(ip, port, known_node_ip, known_node_port)
        print(f"[IP]: {ip}")

    else:
        raise Exception("Incorrect params")

    


    

