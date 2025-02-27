import ipaddress
import socket
import json
import sys
import struct
import threading
from chord_node_reference import ChordNodeReference
from utils_server import *
from chord_node import ChordNode
from gateway_node import GatewayNode

class Server:

    def __init__(self,ip, port = DEFAULT_SERVER_PORT, known_node_ip=None):
        self.ip = ip
        self.storage_path = "Server/Storage"
        self.node = GatewayNode(ip)

        # Iniciar hilo para responder descubrimientos multicast (para conexión cliente–servidor)
        # threading.Thread(target=self.multicast_listener, daemon=True).start()
        # Iniciar el servidor TCP para clientes (por ejemplo, en puerto DEFAULT_SERVER_PORT, ej. 8005)
        threading.Thread(target=self.start_server, args=(ip,port)).start()
        if known_node_ip:
            threading.Thread(target=self.node.join, args=(ChordNodeReference(known_node_ip), )).start()
        else:
            threading.Thread(target=self.node.join).start()

    def multicast_listener(self):
        """
        Se une al grupo multicast para escuchar peticiones de descubrimiento de clientes.
        Cuando recibe "DISCOVER_SERVER", responde con la IP y puerto (del servidor TCP de clientes).
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('', MCAST_PORT))
        except Exception as e:
            print(f"Error al enlazar multicast listener en server: {e}")
            return
        
        # Unirse al grupo multicast
        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        print(f"[*] Server multicast listener iniciado en {MCAST_GRP}:{MCAST_PORT}")
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                print(f'Recibiendo data multicast {data}')
                msg = data.decode('utf-8').strip()
                if msg == "DISCOVER_SERVER":
                    # Responde con la IP del servidor y el puerto de conexión a clientes (por ejemplo, DEFAULT_SERVER_PORT)
                    response = f"{self.ip},{DEFAULT_SERVER_PORT}"
                    print(f"[*] Recibí DISCOVER_SERVER de {addr}. Respondiendo con {response}")
                    sock.sendto(response.encode('utf-8'), addr)
            except Exception as e:
                print(f"Error en multicast listener del server: {e}")

    def start_server(self, ip, port = DEFAULT_SERVER_PORT):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((ip, port))
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
                    client_socket.close()
                    print(f"🔌🚫 [DISCONNECT] Client disconnected from {address}")
                    return
                # if not request:
                #     self.file_system.save_db()
                #     break
                response = self.process_request(request, client_socket)
                if response != None:
                    try:
                        client_socket.sendall(str(response).encode('utf-8'))
                    except:
                        client_socket.sendall(response)
                
        except Exception as e:
            print(e)
            client_socket.send(json.dumps({"error": str(e)}).encode('utf-8'))
            client_socket.close()
            print(f"🔌🚫 [DISCONNECT] Client disconnected from {address}")
            

    def process_request(self,request, client_socket):
        if request == 'show':
            return self.node.show()
        elif request == 'add-tags':
            client_socket.send('OK'.encode('utf-8'))
            tag_query = [query.strip() for query in client_socket.recv(1024).decode('utf-8').split(',')]
            print('tag_query: ',tag_query)
            client_socket.send('OK'.encode('utf-8'))
            tag_list = [tag.strip() for tag in client_socket.recv(1024).decode('utf-8').split(',')]
            print('tag_list: ',tag_list)
            return self.node.add_tags(tag_query,tag_list)
        elif request == 'add-files':
            client_socket.send('OK'.encode('utf-8'))
            file_list = []
            len_list = []
            content_list = []
            file_name =''
            while True:
                file_info = client_socket.recv(1024).decode('utf-8')
                client_socket.send('OK'.encode('utf-8'))
                if file_info == 'end_file':
                    break
                
                file_info = file_info.split(',')
                file_name = file_info[0]
                file_size = int(file_info[1])
                file_list.append(file_name)
                len_list.append(file_size)
                # Variable para almacenar el archivo en memoria
                file_data = bytearray()  # Usamos bytearray para eficiencia en concatenación

                # Recibir el archivo en bloques
                received_size = 0
                print('file_size_server: ',file_size )
                while received_size < file_size:
                    print('received_size: ',received_size)
                    data = client_socket.recv(1024)  # Recibir 1024 bytes
                    if not data:
                        break
                    file_data.extend(data)  # Agregar los datos a la variable
                    received_size += len(data)
                content_list.append(file_data)

                client_socket.send('OK'.encode('utf-8'))

            tag_arg = client_socket.recv(1024).decode('utf-8')
            tag_list = [tag.strip() for tag in tag_arg.split(',')]
            return self.node.add_files(file_list,tag_list,len_list,content_list)


        elif request == 'delete-tags':
            client_socket.send('OK'.encode('utf-8'))
            tag_query = [query.strip() for query in client_socket.recv(1024).decode('utf-8').split(',')]
            client_socket.send('OK'.encode('utf-8'))
            tag_list = [tag.strip() for tag in client_socket.recv(1024).decode('utf-8').split(',')]
            return self.node.delete_tags(tag_query,tag_list)
        elif request == 'delete-files':
            client_socket.send('OK'.encode('utf-8'))
            tag_query = [query.strip() for query in client_socket.recv(1024).decode('utf-8').split(',')]
            return self.node.delete_files(tag_query)
        elif request == 'list':
            client_socket.send('OK'.encode('utf-8'))
            tag_query = [query.strip() for query in client_socket.recv(1024).decode('utf-8').split(',')]
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
    # Get ip from current server
    # ip = socket.gethostbyname(socket.gethostname()) 
    ip = "127.0.0.1"
    # First node case
    if len(sys.argv) == 1:

        # Create node
        server = Server(ip)
        print(f"[IP]: {ip}")     

    # Join node cases using especific ip addres
    elif len(sys.argv) == 3:
        flag = sys.argv[1]

        if flag == '-c':
            target_ip = sys.argv[2]
            try:
                ipaddress.ip_address(target_ip)
            except:
                raise Exception(f"{target_ip} cannot be interpreted as an IP address")

            server = Server(ip, known_node_ip=target_ip)
            print(f"[IP]: {ip}")
        else:
            raise Exception(f"Missing flag: {flag} does not exist")

    else:
        raise Exception("Incorrect params")

    


    

