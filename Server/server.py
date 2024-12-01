import socket
import json
import re
import threading
from Server.FileSystem import TagFileSystem
from Utils.utils import *

class Server:

    def __init__(self,db_path, storage_path):
        self.file_system = TagFileSystem(db_path,storage_path)
        self.storage_path = storage_path

    def start_server(self):
        host = "0.0.0.0"
        port = 5000

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)
        print(f"🚀 [SERVER] Running on {host}:{port}")


        while True:
            client_socket, address = server.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_thread.start()
    
    def handle_client(self,client_socket, address):
        print(f"🔌 [CONNECTION] Client connected from {address}")
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    print("Va a guardar la bd")
                    self.file_system.save_db()
                    break
                request = json.loads(data)
                command = request.get("command")
                payload = request.get("payload", {})
                response = self.process_request(command, json.loads(payload))
                client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"[ERROR] {e}")
            client_socket.send(json.dumps({"error": str(e)}).encode('utf-8'))
            self.file_system.save_db()
            client_socket.close()
            print(f"[DISCONNECT] Client disconnected from {address}")
            

    def process_request(self,command, payload):

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
                    return self.file_system.add(files=[x.strip() for x in payload["file"].split(",")],tags=[x.strip() for x in payload["tags"].split(",")])
                elif payload.get("query"):
                    return self.file_system.add_tags(tag_query=payload["query"],tag_list=[x.strip() for x in payload["tags"].split(",")])
        else:
            return str(InvalidCommandError(command))





if __name__ == "__main__":
    server = Server("Server\data.json", "Server\Storage")
    server.start_server()