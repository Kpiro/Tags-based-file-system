import socket
import json
import sys
import threading
from FileSystem import TagFileSystem
from utils_server import *
from chord_node import ChordNode

class Server:

    def __init__(self,ip, port):
        self.file_system = TagFileSystem("Server\data.json","Server\Storage")
        self.storage_path = "Server\Storage"
        self.node = ChordNode(ip,int(port))

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ip, port))
        server.listen(5)
        print(f"🚀 [SERVER] Running on {ip}:{port}")


        while True:
            client_socket, address = server.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_thread.start()
    
    def handle_client(self,client_socket, address):
        print(f"🔌 [CONNECTION] Client connected from {address}")
        try:
            while True:
                try:
                    data = client_socket.recv(1024).decode('utf-8')
                except:
                    self.file_system.save_db()
                    client_socket.close()
                    print(f"🔌🚫 [DISCONNECT] Client disconnected from {address}")
                    return
                if not data:
                    self.file_system.save_db()
                    break
                request = json.loads(data)
                command = request.get("command")
                payload = request.get("payload", {})
                response = self.process_request(command, json.loads(payload), client_socket)
                if response != None:
                    client_socket.send(response.encode('utf-8'))
                
        except Exception as e:
            print(Error(e))
            client_socket.send(json.dumps({"error": str(e)}).encode('utf-8'))
            self.file_system.save_db()
            client_socket.close()
            print(f"🔌🚫 [DISCONNECT] Client disconnected from {address}")
            

    def process_request(self,command, payload, client_socket):

        if command == "show":
            return str(StorageFiles(self.file_system.files))

        elif command == "delete":   
            if payload.get('query'):
                if payload.get("tags"):
                    return self.file_system.delete_tags(tag_query=payload["query"],tag_list=[x.strip() for x in payload["tags"].split(",")])
                return self.file_system.delete(tag_query=payload["query"])
                
            
        elif command == "list":
            if payload.get('query'):
                return self.file_system.list(tag_query=payload["query"])
        elif command == "add":
            if payload.get("tags"):
                if payload.get("file"):
                    client_socket.send("Command received".encode('utf-8'))
                    return self.file_system.add(num_files=int(payload["file"]),tag_list=[x.strip() for x in payload["tags"].split(",")], client_socket=client_socket)
                elif payload.get("query"):
                    return self.file_system.add_tags(tag_query=payload["query"],tag_list=[x.strip() for x in payload["tags"].split(",")])
        else:
            return str(InvalidCommandError(command))





if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python server.py <IP> <PUERTO> [<NODO_CONOCIDO>]")
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    # known_node = sys.argv[3] if len(sys.argv) > 3 else None
    server = Server(ip, port)