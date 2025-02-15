from flask import Flask, request, jsonify

app = Flask(__name__)
from chord_node_reference import ChordNodeReference
from services import *

# -----------------------------
# Funciones simuladas de servicio
# En un escenario real, estas funciones harían llamadas HTTP u otra
# forma de comunicación con los microservicios correspondientes.
# -----------------------------

chord_ring: ChordNodeReference = None
read_service = ReadService()
writen_service = WritenService() 

def service_add(file_list, tag_list):
    # Lógica para copiar los archivos y asignar las etiquetas
    # Ejemplo: requests.post("http://servicio-escritura/add", json={...})
    print(f"Service Add llamado con archivos: {file_list} y etiquetas: {tag_list}")
    return {"status": "success", "message": "Archivos añadidos", "files": file_list, "tags": tag_list}

def service_delete(tag_query):
    # Lógica para eliminar archivos según el tag_query
    print(f"Service Delete llamado con query: {tag_query}")
    return {"status": "success", "message": "Archivos eliminados", "tag_query": tag_query}

def service_list(tag_query):
    # Lógica para obtener la lista de archivos según el tag_query
    print(f"Service List llamado con query: {tag_query}")
    # Ejemplo de respuesta con archivos dummy
    dummy_files = [
        {"filename": "archivo1.txt", "tags": ["tag1", "tag2"]},
        {"filename": "archivo2.txt", "tags": ["tag2", "tag3"]}
    ]
    return {"status": "success", "files": dummy_files}

def service_add_tags(tag_query, tag_list):
    # Lógica para añadir etiquetas a los archivos que cumplen con tag_query
    print(f"Service Add Tags llamado con query: {tag_query} y etiquetas: {tag_list}")
    return {"status": "success", "message": "Etiquetas añadidas", "tag_query": tag_query, "tags_added": tag_list}

def service_delete_tags(tag_query, tag_list):
    # Lógica para eliminar etiquetas de los archivos que cumplen con tag_query
    print(f"Service Delete Tags llamado con query: {tag_query} y etiquetas: {tag_list}")
    return {"status": "success", "message": "Etiquetas eliminadas", "tag_query": tag_query, "tags_removed": tag_list}

# -----------------------------
# Endpoints del Gateway
# -----------------------------

@app.route('/add', methods=['POST'])
def add_files():
    """
    Endpoint para añadir archivos:
    Recibe un JSON con los parámetros:
    {
        "files_list": [lista de archivos],
        "tags_list": [lista de etiquetas]
    } 
    """
    data = request.get_json()
    if not data or "file_list" not in data or "tag_list" not in data:
        return jsonify({"status": "error", "message": "Parámetros inválidos. Se requieren file_list y tag_list"}), 400
    
    file_list = data["file_list"]
    tag_list = data["tag_list"]
    writen_service.add_files(file_list, tag_list)
    return jsonify('OK'), 200

@app.route('/add-tags',methods = ['POST'])
def add_tags():
    """
    Endpoint para añadir etiquetas a archivos existentes:
    Recibe un JSON con los parámetros:
    {
        "tag_query": "consulta de etiquetas",
        "tag_list": [lista de etiquetas a añadir]
    }
    """
    data = request.get_json()
    if not data or "tag_query" not in data or "tag_list" not in data:
        return jsonify({"status": "error", "message": "Parámetros inválidos. Se requieren tag_query y tag_list"}), 400
    
    tag_query = data["tag_query"]
    tag_list = data["tag_list"]

    files = read_service.retrieve_files(tag_query)
    if len(files)!=0:
        writen_service.add_files(files,tag_list)

    return jsonify('OK'), 200

@app.route('/delete', methods=['DELETE'])
def delete_files():
    """
    Endpoint para eliminar archivos:
    Recibe un JSON con el parámetro:
    {
        "tag_query": "consulta de etiquetas"
    }
    """
    data = request.get_json()
    if not data or "tag_query" not in data:
        return jsonify({"status": "error", "message": "Parámetro inválido. Se requiere tag_query"}), 400
    
    tag_query = data["tag_query"]
    result = service_delete(tag_query)
    return jsonify(result), 200

@app.route('/list', methods=['GET'])
def list_files():
    """
    Endpoint para listar archivos:
    Se espera recibir el parámetro de consulta (?tag_query=...)
    """
    tag_query = request.args.get("tag_query")
    if not tag_query:
        return jsonify({"status": "error", "message": "Se requiere el parámetro tag_query en la query string"}), 400

    result = service_list(tag_query)
    return jsonify(result), 200


@app.route('/delete-tags', methods=['DELETE'])
def delete_tags():
    """
    Endpoint para eliminar etiquetas de archivos:
    Recibe un JSON con los parámetros:
    {
        "tag_query": "consulta de etiquetas",
        "tag_list": [lista de etiquetas a eliminar]
    }
    """
    data = request.get_json()
    if not data or "tag_query" not in data or "tag_list" not in data:
        return jsonify({"status": "error", "message": "Parámetros inválidos. Se requieren tag_query y tag_list"}), 400
    
    tag_query = data["tag_query"]
    tag_list = data["tag_list"]
    result = service_delete_tags(tag_query, tag_list)
    return jsonify(result), 200

# -----------------------------
# Ejecución de la aplicación
# -----------------------------

if __name__ == '__main__':
    # Ejecutamos el gateway en el puerto 5000 en modo debug
    app.run(debug=True, port=5000)
    
