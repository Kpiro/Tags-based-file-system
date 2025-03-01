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

        try:
            self.writen_service.add_tags_to_files(file_list,tag_list,len_list,content_list)
            print('ya add tags to file')
            self.writen_service.add_files_to_tags(file_list,tag_list)
        except Exception as e:
            print('esta es e: ', e)
            return ErrorMSG(f'Files could not be added to the server: {e}')
        else:
            print('sucesssss')
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
            file_list = self.read_service.retrieve_files(tag_query)
            print('ya retrieve')
            print('file_list: ',file_list)
            if len(file_list)!=0:
                self.writen_service.add_tags_to_files(file_list,tag_list)
                print('ya add tags to file')
                self.writen_service.add_files_to_tags(file_list,tag_list)
        except Exception:
            return str(ErrorMSG('Tags could not be added'))+'\n'+str(FilesMSG(file_list))
        else:
            return str(SuccesMSG('Tags added successfully'))+'\n'+str(FilesMSG(file_list))


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
            print(f'🤨🤨 tags del delete file {tags}')
            self.writen_service.delete_files(files)
            self.writen_service.delete_files_from_tags(tags,files)
        except Exception:
            return str(ErrorMSG('Files could not be deleted'))+'\n'+str(FilesMSG(files))
        else:
            return str(SuccesMSG('Files deleted successfully'))+'\n'+str(FilesMSG(files))

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
            self.writen_service.delete_files_from_tags(tag_list,files)
        except Exception:
            return str(ErrorMSG('Tags could not be deleted'))+'\n'+str(FilesMSG(files))
        else:
            return str(SuccesMSG('Tags deleted successfully'))+'\n'+str(FilesMSG(files))

    def list_files(self,tag_query):
        """
        Endpoint para listar archivos:
        Se espera recibir el parámetro de consulta (?tag_query=...)
        """
        try:
            files = self.read_service.retrieve_files(tag_query)
        except Exception:
            return str(ErrorMSG('Files could not be listed'))+'\n'+str(FilesMSG(files))
        else:
            print('😍 listó')
            return str(SuccesMSG('Files listed successfully'))+'\n'+str(FilesMSG(files))
    
    def download_files(self,tag_query):
        file_names = self.read_service.retrieve_files(tag_query)
        file_contents, file_sizes = self.read_service.download_files(file_names)
        return file_names, file_sizes, file_contents


    # def download_file(self,file_name):
    #     try:
    #         file_content, file_size= self.read_service.download_file(file_name)
    #     except Exception:
    #         return ErrorMSG('File {file_name} could not be downloaded')
    #     else:
    #         return file_content,file_size

    def show(self):
        try:
            files,tags = self.read_service.retrieve_all_files()
        except Exception:
            return str(ErrorMSG('Files could not be listed'))
        else:
            return str(SuccesMSG('Files listed successfully'))+'\n'+str(FilesMSG(file_list=files,tag_list=tags))

        
