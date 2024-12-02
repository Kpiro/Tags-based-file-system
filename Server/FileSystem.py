from typing import Dict,List
import json
import uuid
import os
import re
import shutil
from utils_server import *


class TagFileSystem:
    def __init__(self, db_path, storage_path):
        self.db_path = db_path
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            # Si no existe, la crea
            os.makedirs(self.storage_path)
            print(f'Folder "{self.storage_path}" created successfully')
        self.load_db()

    def load_db(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    self.files = json.load(f)
                    self.files = {key: set(value) for key, value in self.files.items()}
            except:
                self.files:Dict[str,set[str]] = {}
        else:
            self.files:Dict[str,set[str]] = {}

    def save_db(self):
        with open(self.db_path, 'w') as f:
            # Convierte los valores de self.files a listas si son sets
            serializable_files = {key: list(value) if isinstance(value, set) else value for key, value in self.files.items()}
            json.dump(serializable_files, f, indent=4)



    def transform_query(self,input_query):
        try:
            transformed_query = re.sub(r'@(\w+)', r"'\1' in tags", input_query)
        except Error as e:
            raise e
        return transformed_query

    
    def add(self,num_files, tag_list:List[str], client_socket):

        for i in range(num_files):
            if client_socket.recv(1024).decode() != "OK":
                return 
            
            try:
                file_size1 = client_socket.recv(1024).decode()
                file_size = int(file_size1)
            except Exception as e:
                return str(Error(e))
            client_socket.send("OK".encode())

            try:
                file_name = client_socket.recv(1024).decode()
            except Exception as e:
                return str(Error(e))
            client_socket.send("OK".encode())
            
            if self.files.get(file_name):
                unique_id = str(uuid.uuid4())
                print(f"File {file_name} added with name {file_name+unique_id}")
                file_parts = file_name.split(".")
                file_name = file_parts[0] + unique_id + file_parts[1]
            destination_path = os.path.join(self.storage_path, file_name)
            with open(destination_path, "wb") as file:
                received_size = 0
                while received_size < file_size:
                    data = client_socket.recv(1024)
                    file.write(data)
                    received_size += len(data)
                print(f'File {file_name} received successfully.')
            self.files[file_name] = tag_list
        return str(Response("Files added successfully."))  
            

    def delete(self, tag_query):
        try:
            to_delete = [file for file, tags in self.files.items() if eval(self.transform_query(tag_query))]
        except:
            return str(InvalidQuery(tag_query))
        if len(to_delete) == 0:
            return str(NoFilesMatch(tag_query))
        for file_name in to_delete:
            destination_path = os.path.join(self.storage_path, file_name)
            try:
                os.remove(destination_path)
                print(f'File {file_name} deleted successfully')
            except Exception as e:
                return str(Error(e))
            del self.files[file_name]
        return str(Response("Files deleted successfully."))+str(MatchingFiles(to_delete))

    def list(self, tag_query):
        try:
            result = {file for file, tags in self.files.items() if eval(self.transform_query(tag_query))}
        except:
            return str(InvalidQuery(tag_query))
        if len(result) == 0:
            return str(NoFilesMatch(tag_query))
        return str(MatchingFiles(result))

    def add_tags(self, tag_query, tag_list):
        tag_list = set(tag_list)
        to_add_tags=[]
        for file, tags in self.files.items():
            try:
                if eval(self.transform_query(tag_query)):
                    self.files[file].update(tag_list)
                    to_add_tags.append(file)
            except:
                return str(InvalidQuery(tag_query))

        if len(to_add_tags)==0:
            return str(NoFilesMatch(tag_query))
        return str(Response(f'Tags {tag_list} added successfully'))+str(MatchingFiles(to_add_tags))
    
    def delete_tags(self, tag_query, tag_list):
        tag_list = set(tag_list)
        to_delete_tags=[]
        for file_name, tags in self.files.items():
            try:
                if eval(self.transform_query(tag_query)):
                    self.files[file_name].difference_update(tag_list)
                    to_delete_tags.append(file_name)
                    if len(self.files[file_name]) == 0:
                        destination_path = os.path.join(self.storage_path, file_name)
                        try:
                            os.remove(destination_path)
                            print(f'File {file_name} deleted successfully')
                        except Exception as e:
                            return str(Error(e))
                        del self.files[file_name]
            except:
                return str(InvalidQuery(tag_query))
        if len(to_delete_tags)==0:
            return str(NoFilesMatch(tag_query))
        return str(Response(f'Tags successfully removed from'))+str(MatchingFiles(to_delete_tags))

    
