from colorama import Fore, Back, Style, init
import socket
import json
from Utils.utils import *


# Inicializa colorama
init(autoreset=True)

class Client: 

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("10.0.11.254", 5000))

    def show_menu(self):
        # Imprimir el menú con colores
        print(f"\n{Fore.BLUE}{Style.BRIGHT}[CLIENT MENU]{Style.RESET_ALL}")
        print(f'{Fore.CYAN}----------------{Style.RESET_ALL}')

        # Opción 1
        print(f"{Fore.BLUE}1. Add files with tags{Style.RESET_ALL}")
        print(f'{Fore.RED}e.a.: tagger add --file archivo.txt --tags importante, proyecto{Style.RESET_ALL}')
        print(f'{Fore.CYAN}--------------------------------------------------------------------{Style.RESET_ALL}')

        # Opción 2
        print(f"{Fore.BLUE}2. Delete files by tag query{Style.RESET_ALL}")
        print(f'{Fore.RED}e.a.: tagger delete --query @casa and @Varadero or @LaHabana {Style.RESET_ALL}')
        print(f'{Fore.CYAN}--------------------------------------------------------------------{Style.RESET_ALL}')

        # Opción 3
        print(f"{Fore.BLUE}3. List files by tag query{Style.RESET_ALL}")
        print(f'{Fore.RED}e.a.: tagger list --query "size>10MB"{Style.RESET_ALL}')
        print(f'{Fore.CYAN}--------------------------------------------------------------------{Style.RESET_ALL}')

        # Opción 4
        print(f"{Fore.BLUE}4. Add tags to files by tag query{Style.RESET_ALL}")
        print(f'{Fore.RED}e.a.: tagger add --query "type=pdf" --tags "lectura"{Style.RESET_ALL}')
        print(f'{Fore.CYAN}--------------------------------------------------------------------{Style.RESET_ALL}')

        # Opción 5
        print(f"{Fore.BLUE}5. Delete tags from files by tag query{Style.RESET_ALL}")
        print(f'{Fore.RED}e.a.: tagger delete --query "created<2020" --tags "duplicado"{Style.RESET_ALL}')
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
            # parsed_response = json.loads(response)
            # key, value = list(parsed_response.items())[0]
            # print(f'{key} {value}')

        except Exception as e:
            print(f"[ERROR] {e}")

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

        # print(f'parts: {parts}')

        try:
            params = parts[1].split("--")
        except:
            print(InvalidCommandError(command))
            return
        # print(f'params: {params}')

        json_request = "{"

        for i in range(1,len(params)):
            args = params[i].split(" ",1)
            if len(args)!=2:
                print(InvalidCommandError(command))
                return

            if i== len(params)-1:
                json_request+=f'"{args[0]}": "{args[1]}"'
                json_request+="}"
            else:
                json_request+=f'"{args[0]}": "{args[1]}",'

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

