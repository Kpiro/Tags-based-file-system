from chord_node import ChordNode
from chord_node_reference import ChordNodeReference
from services import *
from utils_server import * 
class GatewayNode(ChordNode):

    # -----------------------------
    # Funciones simuladas de servicio
    # En un escenario real, estas funciones harían llamadas HTTP u otra
    # forma de comunicación con los microservicios correspondientes.
    # -----------------------------
    def __init__(self,ip,port = DEFAULT_NODE_PORT):
        super().__init__(ip,port)
        # chord_ring: ChordNodeReference = None
        self.read_service = ReadService(self.ref)
        self.writen_service = WritenService(self.ref) 

    def set_request(self,request):
        self.request = request

    # -----------------------------
    # Endpoints del Gateway
    # -----------------------------
    def add_files(self,file_list,tag_list,len_list = None,content_list=None):
        """
        Endpoint para añadir archivos:
        Recibe un JSON con los parámetros:
        {
            "file_list": [lista de archivos],
            "tag_list": [lista de etiquetas]
        } 
        """
        for content in content_list:
            print('content: ',content)
        try:
            self.writen_service.add_tags_to_files(file_list,tag_list,len_list,content_list)
            print('ya add tags to file')
            self.writen_service.add_files_to_tags(file_list,tag_list)
        except Exception:
            return ErrorMSG('Files could not be added to the server')
        else:
            return SuccesMSG('Files added successfully')

    def add_tags(self,tag_query,tag_list):
        """
        Endpoint para añadir etiquetas a archivos existentes:
        Recibe un JSON con los parámetros:
        {
            "tag_query": "consulta de etiquetas",
            "tag_list": [lista de etiquetas a añadir]
        }
        """

        try:
            files = self.read_service.retrieve_files(tag_query)
            if len(files)!=0:
                self.writen_service.add_files(files,tag_list)
        except Exception:
            return ErrorMSG('Tags could not be added')
        else:
            return SuccesMSG('Tags added successfully')


    def delete_files(self,tag_query):
        """
        Endpoint para eliminar archivos:
        Recibe un JSON con el parámetro:
        {
            "tag_query": "consulta de etiquetas"
        }
        """

        try:
            files = self.read_service.retrieve_files(tag_query)
            tags = self.read_service.retrieve_tags(files)
            self.writen_service.delete_files(files)
            self.writen_service.delete_files_from_tags(tags,files)
        except Exception:
            return ErrorMSG('Files could not be deleted')
        else:
            return SuccesMSG('Files deleted successfully')+'\n'+FilesMSG(files)

    def delete_tags(self,tag_query,tag_list):
        """
        Endpoint para eliminar etiquetas de archivos:
        Recibe un JSON con los parámetros:
        {
            "tag_query": "consulta de etiquetas",
            "tag_list": [lista de etiquetas a eliminar]
        }
        """
        try:
            files = self.read_service.retrieve_files(tag_query)
            self.writen_service.delete_tags_from_files(files,tag_list)
        except Exception:
            return ErrorMSG('Tags could not be deleted')
        else:
            return SuccesMSG('Tags deleted successfully')+'\n'+FilesMSG(files)

    def list_files(self,tag_query):
        """
        Endpoint para listar archivos:
        Se espera recibir el parámetro de consulta (?tag_query=...)
        """
        try:
            files = self.read_service.retrieve_files(tag_query)
        except Exception:
            return ErrorMSG('Files could not be listed')
        else:
            return SuccesMSG('Files listed successfully')+'\n'+FilesMSG(files)
    
    def download_file(self,file_name):
        try:
            file_content, file_size= self.read_service.download_file(file_name)
        except Exception:
            return ErrorMSG('File {file_name} could not be downloaded')
        else:
            return file_content,file_size

    def show(self):
        try:
            files,tags = self.read_service.retrieve_all_files()
        except Exception:
            return ErrorMSG('Files could not be listed')
        else:
            return SuccesMSG('Files listed successfully')+'\n'+FilesMSG(file_list=files,tag_list=tags)

        
