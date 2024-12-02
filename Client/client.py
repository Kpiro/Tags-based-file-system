from colorama import Fore, Back, Style, init
import socket
import json
from utils_client import *
import os


# Inicializa colorama
init(autoreset=True)

class Client: 

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("10.0.11.2", 5000))
        self.FILE_PATH = "/app/Client/client_files"

    def show_menu(self):
        # Imprimir el menú con colores
        print(f"\n{Fore.BLUE}{Style.BRIGHT}[CLIENT MENU]{Style.RESET_ALL}")
        print(f'{Fore.CYAN}----------------{Style.RESET_ALL}')

        # Opción 1
        print(f"{Fore.BLUE}1. Add files with tags{Style.RESET_ALL}")
        print(f'{Fore.RED}e.a.: add --file D:/archivo.txt --tags importante, proyecto{Style.RESET_ALL}')
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


    
    def send_request(self,command, payload):
        try:
            # Crear y enviar la solicitud
            request = {"command": command, "payload": payload}
            self.client_socket.send(json.dumps(request).encode('utf-8'))

            # Recibir respuesta
            response = self.client_socket.recv(1024).decode('utf-8')
            print(response)

        except Exception as e:
            print(Error(e))

    def send_files(self,files):

            for file in files:

                file_path = os.path.join(self.FILE_PATH, file)
                try:
                    file_size = os.path.getsize(file_path)
                except FileNotFoundError:
                    print(InvalidPathError(file_path))
                    self.client_socket.send(str(InvalidPathError(file_path)).encode())
                    return
                if not os.path.isfile(file_path):
                    self.client_socket.send(str(InvalidPathError(file_path)).encode())
                    print(InvalidPathError(file_path))
                    return
                else:
                    self.client_socket.send("OK".encode())
                
                # Enviar información del archivo
                self.client_socket.send(f"{file_size}".encode())
                response = self.client_socket.recv(1024).decode()
                
                if response != "OK":
                    print(response)
                    return
                
                file_name = os.path.basename(file_path)

                self.client_socket.send(file_name.encode())
                response = self.client_socket.recv(1024).decode()

                if response != "OK":
                    print(response)
                    return
                
                # Enviar archivo
                with open(file_path, "rb") as file:
                    while chunk := file.read(1024):
                        self.client_socket.send(chunk)
            print(self.client_socket.recv(1024).decode())

    def parse_command(self,command):

        if command == "exit":
            self.client_socket.close()
            return
        elif command == "show":
            s=""
            s+="{"
            s+="}"
            self.send_request("show",s)
            return

        try:
            parts = command.split(" ", 1)
        except:
            print(InvalidCommandError(command))
            return

        try:
            params = parts[1].split("--")
        except:
            print(InvalidCommandError(command))
            return
        
        json_request = "{"

        isAddFile = False
        for i in range(1,len(params)):
            args = params[i].split(" ",1)
            if len(args)!=2:
                print(InvalidCommandError(command))
                return

            if i== len(params)-1:
                json_request+=f'"{args[0]}": "{args[1]}"'
                json_request+="}"
            else:
                if args[0]=="file":
                    if parts[0] == "add":
                        isAddFile = True
                    files=[x.strip() for x in args[1].split(",")]
                    json_request+=f'"{args[0]}": "{len(files)}",'
                else:
                    json_request+=f'"{args[0]}": "{args[1]}",'

        if isAddFile:
            try:
                # Crear y enviar la solicitud
                request = {"command": parts[0], "payload": json_request}
                self.client_socket.send(json.dumps(request).encode('utf-8'))
            except Exception as e:
                print(Error(e))
                return
            cmd_recv = self.client_socket.recv(1024).decode('utf-8')
            if cmd_recv=="Command received":
                self.send_files(files)
            else:
                print(cmd_recv)
                return
        else:
            self.send_request(parts[0],json_request)
            

        
    

if __name__ == "__main__":
    client = Client()
    client.show_menu()
    while True:
        command = input("Enter a command: ")
        client.parse_command(command)
        if command == "exit":
            print("🏃 Exiting...")
            break

