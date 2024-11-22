import socket
import json
import re

# Base de datos de archivos en memoria
x = ["vacaciones","verano","calor"]
file_system = {"img1.jpg":set(x),"img2.jpg":set(x), "text.txt":set(x), "img4.png":set(["Varadero","verano"]),"img5.png":set(["Varadero","provincia"]),"img6.png":set(["Cienfuegos","provincia"]) }

def transform_query(input_query):
    # Reemplaza todas las ocurrencias de @tag por 'tag' in tags
    transformed_query = re.sub(r'@(\w+)', r"'\1' in tags", input_query)
    # print(f"Transformed data: {transformed_query}")
    return transformed_query

def process_request(command, payload):
    global file_system

    if command == "add":
        # Agregar archivos con etiquetas
        file_list = payload['file_list']
        tag_list = set(payload['tag_list'])
        if len(tag_list)!=len(payload['tag_list']):
                return {"error": f"Duplicated tags found"}
        for file_name in file_list:
            if file_system.get(file_name):
                return {"error": f"File {file_name} already exists."}
            else:
                file_system[file_name] = tag_list
        return {"message": f"Files {file_list} added successfully."}

    elif command == "delete":
        # Eliminar archivos que cumplan la consulta
        tag_query = payload['tag_query']
        to_delete = [file for file, tags in file_system.items() if eval(transform_query(tag_query))]

        if len(to_delete) == 0:
            return {"error": f"No files match the query: {tag_query}"}

        for file in to_delete:
            del file_system[file]
        return {"message": f"Files deleted: {to_delete}"}

    elif command == "list":
        print('aaaa')
        # Listar archivos según la consulta
        tag_query = payload['tag_query']
        result = {file: tags for file, tags in file_system.items() if eval(transform_query(tag_query))}
        if len(result) == 0:
            return {"error": f"No files match the query: {tag_query}"}
        return {"result": list(result)}

    elif command == "add-tags":
        # Agregar etiquetas a archivos que cumplan la consulta
        tag_query = payload['tag_query']
        tag_list = set(payload['tag_list'])
        if len(tag_list)!=len(payload['tag_list']):
            return {"error": f"Duplicated tags found"}
        query_sat = False
        for file, tags in file_system.items():
            if eval(transform_query(tag_query)):
                file_system[file].update(tag_list)
                query_sat = True
        if not query_sat:
            return {"error": f"No files match the query: {tag_query}"}
        return {"message": f"Tags {tag_list} added to matching files."}

    elif command == "delete-tags":
        # Eliminar etiquetas de archivos según la consulta
        tag_query = payload['tag_query']
        tag_list = set(payload['tag_list'])
        if len(tag_list)!=len(payload['tag_list']):
            return {"error": f"Duplicated tags found"}
        query_sat = False
        for file, tags in file_system.items():
            if eval(transform_query(tag_query)):
                file_system[file].difference_update(tag_list)
                if len(file_system[file])==0:
                    del file_system[file]
                
                query_sat = True
        
        if not query_sat:
            return {"error": f"No files match the query: {tag_query}"}
        return {"message": f"Tags {tag_list} removed from matching files."}

    else:
        return {"error": "Unknown command"}

def start_server():
    host = "0.0.0.0"
    port = 5000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)

    print(f"[SERVER] Running on {host}:{port}")
    while True:
        client_socket, address = server.accept()
        print(f"[CONNECTION] Client connected from {address}")

        while True:
            try:
                # Recibir datos del cliente
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break

                request = json.loads(data)
                command = request.get("command")
                payload = request.get("payload", {})

                # Procesar comando
                response = process_request(command, payload)

                # Enviar respuesta
                client_socket.send(json.dumps(response).encode('utf-8'))

            except Exception as e:
                print(f"[ERROR] {e}")
                client_socket.send(json.dumps({"error": str(e)}).encode('utf-8'))

        client_socket.close()
        print(f"[DISCONNECT] Client disconnected")

if __name__ == "__main__":
    start_server()
