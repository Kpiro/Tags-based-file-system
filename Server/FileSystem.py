from typing import Dict,List
import json
import uuid
import os
import re

class TagFileSystem:
    def __init__(self, db_path):
        self.db_path = db_path
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
        transformed_query = re.sub(r'@(\w+)', r"'\1' in tags", input_query)
        return transformed_query

    def add(self, files:List[str], tags:List[str]):

        tag_list = set(tags)
        for file_name in files:
            if self.files.get(file_name):
                unique_id = str(uuid.uuid4())
                print(f"File {file_name} added with name {file_name+unique_id}")
                file_name += unique_id
            self.files[file_name] = tag_list
        return {"RESPONSE": f"Files added successfully."}

    def delete(self, tag_query):
        to_delete = [file for file, tags in self.files.items() if eval(self.transform_query(tag_query))]
        if len(to_delete) == 0:
            return {"[ERROR]": f"No files match the query: {tag_query}"}
        for file in to_delete:
            del self.files[file]
        return {"RESPONSE:": f"Files deleted: {to_delete}"}

    def list(self, tag_query):
        result = {file for file, tags in self.files.items() if eval(self.transform_query(tag_query))}
        if len(result) == 0:
            return {"[ERROR]": f"No files match the query: {tag_query}"}
        return {"RESPONSE:": f"Files that match the query {result}" }

    def add_tags(self, tag_query, tag_list):
        tag_list = set(tag_list)
        query_sat = False
        for file, tags in self.files.items():
            if eval(self.transform_query(tag_query)):
                self.files[file].update(tag_list)
                query_sat = True
        if not query_sat:
            return {"[ERROR]": f"No files match the query: {tag_query}"}
        return {"RESPONSE:": f"Tags {tag_list} added to matching files."}
    
    def delete_tags(self, tag_query, tag_list):
        tag_list = set(tag_list)
        query_sat = False
        for file, tags in self.files.items():
            if eval(self.transform_query(tag_query)):
                self.files[file].difference_update(tag_list)
                if len(self.files[file]) == 0:
                    del self.files[file]
                query_sat = True
        if not query_sat:
            return {"[ERROR]": f"No files match the query: {tag_query}"}
        return {"RESPONSE:": f"Tags {tag_list} removed from matching files."}

    
