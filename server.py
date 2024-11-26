import socket
import json
import re
import threading

# Base de datos de archivos en memoria
x = ["vacaciones","verano","calor"]
file_system = {"img1.jpg":set(x),"img2.jpg":set(x), "text.txt":set(x), "img4.png":set(["Varadero","verano"]),"img5.png":set(["Varadero","provincia"]),"img6.png":set(["Cienfuegos","provincia"]) }

def transform_query(input_query):
    transformed_query = re.sub(r'@(\w+)', r"'\1' in tags", input_query)
    return transformed_query

def process_request(command, payload):
    global file_system
    if command == "add":
        file_list = payload['file_list']
        tag_list = set(payload['tag_list'])
        if len(tag_list) != len(payload['tag_list']):
            return {"error": "Duplicated tags found"}
        for file_name in file_list:
            if file_system.get(file_name):
                return {"error": f"File {file_name} already exists."}
            else:
                file_system[file_name] = tag_list
        return {"message": f"Files {file_list} added successfully."}
    elif command == "delete":
        tag_query = payload['tag_query']
        to_delete = [file for file, tags in file_system.items() if eval(transform_query(tag_query))]
        if len(to_delete) == 0:
            return {"error": f"No files match the query: {tag_query}"}
        for file in to_delete:
            del file_system[file]
        return {"message": f"Files deleted: {to_delete}"}
    elif command == "list":
        tag_query = payload['tag_query']
        result = {file: tags for file, tags in file_system.items() if eval(transform_query(tag_query))}
        if len(result) == 0:
            return {"error": f"No files match the query: {tag_query}"}
        return {"result": list(result)}
    elif command == "add-tags":
        tag_query = payload['tag_query']
        tag_list = set(payload['tag_list'])
        if len(tag_list) != len(payload['tag_list']):
            return {"error": "Duplicated tags found"}
        query_sat = False
        for file, tags in file_system.items():
            if eval(transform_query(tag_query)):
                file_system[file].update(tag_list)
                query_sat = True
        if not query_sat:
            return {"error": f"No files match the query: {tag_query}"}
        return {"message": f"Tags {tag_list} added to matching files."}
    elif command == "delete-tags":
        tag_query = payload['tag_query']
        tag_list = set(payload['tag_list'])
        if len(tag_list) != len(payload['tag_list']):
            return {"error": "Duplicated tags found"}
        query_sat = False
        for file, tags in file_system.items():
            if eval(transform_query(tag_query)):
                file_system[file].difference_update(tag_list)
                if len(file_system[file]) == 0:
                    del file_system[file]
                query_sat = True
        if not query_sat:
            return {"error": f"No files match the query: {tag_query}"}
        return {"message": f"Tags {tag_list} removed from matching files."}
    else:
        return {"error": "Unknown command"}

def handle_client(client_socket, address):
    print(f"[CONNECTION] Client connected from {address}")
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            request = json.loads(data)
            command = request.get("command")
            payload = request.get("payload", {})
            response = process_request(command, payload)
            client_socket.send(json.dumps(response).encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] {e}")
        client_socket.send(json.dumps({"error": str(e)}).encode('utf-8'))
    finally:
        client_socket.close()
        print(f"[DISCONNECT] Client disconnected from {address}")

def start_server():
    host = "0.0.0.0"
    port = 5000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[SERVER] Running on {host}:{port}")

    while True:
        client_socket, address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()

if __name__ == "__main__":
    start_server()