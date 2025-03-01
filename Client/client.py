import struct
import threading
import time
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
DEFAULT_CLIENT_PORT = 10002

class Client: 

    def __init__(self):
        self.storage_dir = "/app/Client/Storage"
        os.makedirs(self.storage_dir, exist_ok=True)
        self.local_ip = socket.gethostbyname(socket.gethostname())
        self.client_socket = None
        self.is_connected = False

        threading.Thread(target=self.discover_server).start()  
        threading.Thread(target=self.send_message_multicast).start()
        threading.Thread(target=self.main_func).start()

    def discover_server(self):
        # Crear un socket TCP para recibir respuesta de servidores
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind(('', DEFAULT_CLIENT_PORT))  
        tcp_socket.listen(5)

        print(f"[*] Cliente escuchando en {self.local_ip}:{DEFAULT_CLIENT_PORT}")

        # Esperar conexiones TCP de servidores
        while True:
            try:
                conn, addr = tcp_socket.accept()
                tcp_socket.settimeout(5)  # Espera un tiempo por respuestas
                data = conn.recv(1024).decode('utf-8')
                server_ip, server_port = data.split(',')
                print(f"Servidor encontrado: {server_ip}:{server_port}")
                conn.close()
                break
            except socket.timeout:
                print(f'[*] No se pudo conectar a ningún servidor')
                break 

        # Conectar al primer servidor encontrado
        print(f"Conectando al servidor en {server_ip}:{server_port}")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_ip, int(server_port)))

        self.is_connected = True

    def send_message_multicast(self):
        """
        Envía un mensaje multicast con la IP y puerto TCP del cliente.
        """
        try:
            # Enviar mensaje multicast
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.settimeout(5)
            ttl = struct.pack('b', 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

            msg = f"DISCOVER_SERVER,{self.local_ip},{DEFAULT_CLIENT_PORT}"
            print("Enviando mensaje de descubrimiento multicast...")
            sock.sendto(msg.encode('utf-8'), (MCAST_GRP, MCAST_PORT))

            sock.close()
        except Exception as e:
            print("Error en multicast discovery:", e)

    def main_func(self):
        timeout = 10  # Tiempo máximo de espera en segundos
        start_time = time.time()

        while not self.is_connected:
            if time.time() - start_time > timeout:
                print("Tiempo de espera agotado, no se pudo conectar.")
                break  # Sal del bucle si se supera el tiempo límite
            time.sleep(0.5)  # Espera antes de volver a intentar

        if self.is_connected:
            self.show_menu()
            while True:
                command = input("Enter a command: ")
                client.parse_command(command)
                if command == "exit":
                    print("🏃 Exiting...")
                    break

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
            print('cmd_parts: ',cmd_parts)
            cmd = cmd_parts[0]
        except:
            cmd = request
        
        if cmd == "exit":
            self.client_socket.close()
            return
        elif cmd == "show":
            self.client_socket.send(cmd.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')
            print(response)
            return

        try:
            params = [param.strip() for param in cmd_parts[1].split("--")]
            print('params: ',params)
        except:
            # print(InvalidCommandError(command))
            pass
        else:
            if cmd == "download":
                response = self.send_request(cmd)
                if response == 'OK':
                    param_query = params[1].split(' ',1)
                    if param_query[0]=='query':
                        query = param_query[1]
                        response = self.send_request(query)
                        

                        while True:
                            print('response: ', response)
                            if response == 'end-file':
                                break
                            file_info = response.split(',',1)
                            file_name = file_info[0]
                            file_size = int(file_info[1])
                            self.client_socket.send('OK'.encode('utf-8'))
                            file_path = os.path.join(self.storage_dir,file_name)
                            file_data = bytearray()
                            received_size = 0
                            while received_size < file_size:
                                data = self.client_socket.recv(1024)  # Recibir 1024 bytes
                                if not data:
                                    break
                                file_data.extend(data)  # Agregar los datos a la variable
                                received_size += len(data)
                            response = self.send_request('OK')

                            with open(file_path, "wb") as dest_file:
                                dest_file.write(file_data)
                                print(f'File {file_name} downloaded succesfully')

                        print(f'All files were downloaded succesfully in {self.storage_dir}')

            elif cmd == "list":
                param_query= params[1].split(' ',1)
                if param_query[0]=='query':
                    query = param_query[1]
                    response = self.send_request(cmd)
                    if response == 'OK':
                        response = self.send_request(query)
                        print(response)
            elif cmd == "delete":
                param_query = params[1].split(' ',1)
                if param_query[0] == 'query':
                    query = param_query[1]
                else:
                    print('Invalid cmd')
                try: 
                    param_tags = params[2].split(' ',1)
                    if param_tags[0]=='tags':
                        tags = param_tags[1]
                    else:
                        print('Invalid cmd')
                except:
                    response = self.send_request('delete-files')
                    if response == 'OK':
                        response = self.send_request(query)
                        print(response)
                else:
                    response = self.send_request('delete-tags')
                    if response == 'OK':
                        response = self.send_request(query)
                        if response == 'OK':
                            response = self.send_request(tags)
                            print(response)

            elif cmd == "add":
                param_tags = params[2].split(' ',1)
                print(param_tags)
                if param_tags[0] == 'tags':
                    tags = param_tags[1]
                else:
                    print('Invalid cmd')
                    return
                param_0 = params[1].split(' ',1)
                if param_0[0]=='query':
                    query = param_0[1]
                    response = self.send_request('add-tags')
                    if response == 'OK':
                        response = self.send_request(query)
                        if response == 'OK':
                            response = self.send_request(tags)
                            print(response)
                elif param_0[0]=='files':
                    files = param_0[1]
                    response = self.send_request('add-files')
                    print(response)
                    if response == "OK":
                        file_path_list = [file_path.strip() for file_path in files.split(',')]
                        for file_path in file_path_list:
                            file_name = os.path.basename(file_path)
                            file_size = os.path.getsize(file_path)
                            print(f'file_info: {file_name} -- {file_size}' )
                            response = self.send_request(f'{file_name},{file_size}')
                            print(response)
                            if response == "OK":
                                with open(file_path, "rb") as source_file:
                                    self.client_socket.sendall(source_file.read())
                                    response = self.client_socket.recv(1024).decode('utf-8')
                                    print(response)
                                    if response != 'OK':
                                        print('Invalid')
                                        return
                            else:
                                print('Invalid')
                                return
                        response = self.send_request('end-file')
                        print('😍 es ok?', response)
                        if response == 'OK':
                            response = self.send_request(tags)
                            print(response)
                            return
                    else:
                        print('Invalid')
                        return

            

        
    

if __name__ == "__main__":
    client = Client()

