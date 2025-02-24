import struct
from colorama import Fore, Back, Style, init
import socket
import json
from utils_client import *
import os

END_FILE = 30
END_FILES = 31
# Configuración del grupo multicast
MCAST_GRP = '224.0.0.1'
MCAST_PORT = 10000

# Inicializa colorama
init(autoreset=True)

class Client: 

    def __init__(self):
        self.storage_dir = "/app/Client/Storage"
        os.makedirs(self.storage_dir,exist_ok=True)
        # Descubrir el servidor mediante multicast
        server_info = self.discover_server()
        if server_info is None:
            print("No se encontró ningún servidor mediante multicast.")
            exit(1)
        else:
            print(f"Conectando al servidor en {server_info[0]}:{server_info[1]}")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_info[0], server_info[1]))

    def discover_server(self):
        """
        Envía un mensaje de descubrimiento multicast para encontrar el servidor.
        Retorna una tupla (ip, port) si se recibe respuesta o None si no.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.settimeout(20)
            ttl = struct.pack('b', 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            
            msg = "DISCOVER_SERVER"
            print("Enviando mensaje de descubrimiento multicast...")
            sock.sendto(msg.encode('utf-8'), (MCAST_GRP, MCAST_PORT))
            
            data, addr = sock.recvfrom(1024)
            print(f'Data {data}')
            response = data.decode('utf-8').strip()
            ip, port = response.split(',')
            return ip, int(port)
        except socket.timeout:
            print("No se recibió respuesta del descubrimiento multicast.")
            return None
        except Exception as e:
            print("Error en multicast discovery:", e)
            return None

    def show_menu(self):
        # Imprimir el menú con colores
        print(f"\n{Fore.BLUE}{Style.BRIGHT}[CLIENT MENU]{Style.RESET_ALL}")
        print(f'{Fore.CYAN}----------------{Style.RESET_ALL}')

        # Opción 1
        print(f"{Fore.BLUE}1. Add files with tags{Style.RESET_ALL}")
        print(f'{Fore.RED}e.a.: add --files D:/archivo.txt --tags importante, proyecto{Style.RESET_ALL}')
        print(f'{Fore.CYAN}--------------------------------------------------------------------{Style.RESET_ALL}')

        # Opción 2
        print(f"{Fore.BLUE}2. Delete files by tag query{Style.RESET_ALL}")
        print(f'{Fore.RED}e.a.: delete --query @casa and @Varadero or @LaHabana {Style.RESET_ALL}')
        print(f'{Fore.CYAN}--------------------------------------------------------------------{Style.RESET_ALL}')

        # Opción 3
        print(f"{Fore.BLUE}3. List files by tag query{Style.RESET_ALL}")
        print(f'{Fore.RED}e.a.: list --query @casa{Style.RESET_ALL}')
        print(f'{Fore.CYAN}--------------------------------------------------------------------{Style.RESET_ALL}')

        # Opción 4
        print(f"{Fore.BLUE}4. Add tags to files by tag query{Style.RESET_ALL}")
        print(f'{Fore.RED}e.a.: add --query @Varadero --tags felicidad, vacaciones{Style.RESET_ALL}')
        print(f'{Fore.CYAN}--------------------------------------------------------------------{Style.RESET_ALL}')

        # Opción 5
        print(f"{Fore.BLUE}5. Delete tags from files by tag query{Style.RESET_ALL}")
        print(f'{Fore.RED}e.a.: delete --query @Varadero --tags felicidad{Style.RESET_ALL}')
        print(f'{Fore.CYAN}--------------------------------------------------------------------{Style.RESET_ALL}')

        # Opción 6
        print(f"{Fore.BLUE}6. Exit{Style.RESET_ALL}")
        print(f'{Fore.RED}e.a.: exit{Style.RESET_ALL}')
        print(f'{Fore.CYAN}--------------------------------------------------------------------{Style.RESET_ALL}')

    def send_request(self,request):
        self.client_socket.send(request.encode('utf-8'))
        return self.client_socket.recv(1024).decode('utf-8')
    
    def parse_command(self,request):
        cmd =''
        try:
            cmd_parts = request.split(" ", 1)
            cmd = cmd_parts[0]
        except:
            cmd = request
        
        if cmd == "exit":
            self.client_socket.close()
            return
        elif cmd == "show":
            self.client_socket.send(cmd.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')
            return

        try:
            params = cmd_parts[1].split("--")
        except:
            print(InvalidCommandError(command))
        else:
            if cmd == "download":
                response = self.send_request(cmd)
                if response == 'OK':
                    param_file = params[0].split(' ')
                    if param_file[0]=='file':
                        file_name = param_file[1]
                        file_size = self.send_request(file_name)

                        file_path = os.path.join(self.storage_dir,file_name)
                        file_data = bytearray()
                        received_size = 0
                        while received_size < int(file_size):
                            data = self.client_socket.recv(1024)  # Recibir 1024 bytes
                            if not data:
                                break
                            file_data.extend(data)  # Agregar los datos a la variable
                            received_size += len(data)
                        with open(file_path, "wb") as dest_file:
                            dest_file.write(file_data)
                            print('File {file_name} downloaded succesfully')
                else:
                    print('Invalid')

            elif cmd == "list":
                param_query= params[0].split(' ')
                if param_query[0]=='query':
                    query = param_query[1]
                    response = self.send_request(cmd)
                    if response == 'OK':
                        response = self.send_request(query)
            elif cmd == "delete":
                param_query = params[0].split(' ')
                if param_query[0] == 'query':
                    query = param_query[1]
                else:
                    print('Invalid cmd')
                try: 
                    param_tags = params[1].split(' ')
                    if param_tags[0]=='tags':
                        tags = param_tags[1]
                    else:
                        print('Invalid cmd')
                except:
                    response = self.send_request('delete-files')
                    if response == 'OK':
                        response = self.send_request(query)
                else:
                    response = self.send_request('delete-tags')
                    if response == 'OK':
                        response = self.send_request(query)
                        if response == 'OK':
                            response = self.send_request(tags)

            elif cmd == "add":
                param_tags = params[2].split(' ')
                print(param_tags)
                if param_tags[0] == 'tags':
                    tags = param_tags[1]
                else:
                    print('Invalid cmd')
                    return
                param_0 = params[1].split(' ')
                if param_0[0]=='query':
                    query = param_0[1]
                    response = self.send_request('add-tags')
                    if response == 'OK':
                        response = self.send_request(query)
                        if response == 'OK':
                            response = self.send_request(tags)
                elif param_0[0]=='files':
                    files = param_0[1]
                    response = self.send_request('add-files')
                    if response == "OK":
                        file_path_list = files.split(',')
                        for file_path in file_path_list:
                            file_name = os.path.basename(file_path)
                            file_size = os.path.getsize(file_path)
                            response = self.send_request(f'{file_name},{file_size}')
                            if response == "OK":
                                with open(file_path, "rb") as source_file:
                                    self.client_socket.sendall(source_file.read())
                                    response = self.client_socket.recv(1024)
                                    if response != 'OK':
                                        print('Invalid')
                                        return
                            else:
                                print('Invalid')
                                return
                        response = self.send_request('end_file')
                        if response == 'OK':
                            response = self.send_request(tags)
                            print(response)
                            return
                    else:
                        print('Invalid')
                        return


            

        
    

if __name__ == "__main__":
    client = Client()
    client.show_menu()
    while True:
        command = input("Enter a command: ")
        client.parse_command(command)
        if command == "exit":
            print("🏃 Exiting...")
            break

