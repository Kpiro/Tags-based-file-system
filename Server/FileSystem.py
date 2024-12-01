from typing import Dict,List
import json
import uuid
import os
import re
import shutil
from Utils.utils import *


class TagFileSystem:
    def __init__(self, db_path, storage_path):
        self.db_path = db_path
        self.storage_path = storage_path
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

    def add(self, files:List[str], tags:List[str]):

        tag_list = set(tags)
        for file_path in files:
            
            file_name = os.path.basename(file_path)
            
            if self.files.get(file_name):
                unique_id = str(uuid.uuid4())
                print(f"File {file_name} added with name {file_name+unique_id}")
                file_parts = file_name.split(".")
                file_name = file_parts[0] + unique_id + file_parts[1]
            if not os.path.isfile(file_path):
                return str(InvalidPathError(file_path))
            destination_path = os.path.join(self.storage_path, file_name)
            try:
                shutil.copy(file_path, destination_path)
            except Exception as e:
                return str(FailCopy(file_path))
            self.files[file_name] = tag_list
        return str(Response("Files added successfully."))

    def delete(self, tag_query):
        try:
            to_delete = [file for file, tags in self.files.items() if eval(self.transform_query(tag_query))]
        except:
            return str(InvalidQuery(tag_query))
        if len(to_delete) == 0:
            return str(NoFilesMatch(tag_query))
        for file in to_delete:
            del self.files[file]
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
        for file, tags in self.files.items():
            try:
                if eval(self.transform_query(tag_query)):
                    self.files[file].difference_update(tag_list)
                    to_delete_tags.append(file)
                    if len(self.files[file]) == 0:
                        del self.files[file]
            except:
                return str(InvalidQuery(tag_query))
        if len(to_delete_tags)==0:
            return str(NoFilesMatch(tag_query))
        return str(Response(f'Tags successfully removed from'))+str(MatchingFiles(to_delete_tags))

    
