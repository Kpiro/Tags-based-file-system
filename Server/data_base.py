import os
import json
main_dir = "./Data_base"
from utils_server import auto_save

class DataBase:
    def __init__(self,node_id,name) -> None:
        self.server_dir = os.path.join(main_dir,str(node_id))
        self.json_dir = os.path.join(self.server_dir,'Jsons')
        self.json_path = os.path.join(self.json_dir,name)
        self.create_dir()
        self.data:dict[str,set] 
        self.load_data_base()
    
    def create_dir(self):
        os.makedirs(self.server_dir,exist_ok=True)
        os.makedirs(self.json_dir,exist_ok=True)

    
    def load_data_base(self):
        try:
            with open(self.json_path, "r", encoding="utf-8") as file:
                self.data = {key: set(value) for key, value in json.load(file).items()}
        except :
            self.data = {} 


    def save_database(self):
        with open(self.json_path, "w", encoding="utf-8") as file:
            serializable_files = {key: list(value) if isinstance(value, set) else value for key, value in self.data.items()}
            json.dump(serializable_files, file, indent=4, ensure_ascii=False)

    # Write
    @auto_save
    def add_values_to_key(self, key, values):
        print(type(values))
        print('values: ',values)
        if key in self.data:
            self.data[key].update(set(values))
        else:
            self.data[key] = set(values)
    @auto_save
    def remove_values_from_key(self,key,values):
        if key in self.data:
            for value in values:
                self.data[key].remove(value)

        if len(self.data[key])==0:
            del self.data[key]

    @auto_save
    def delete_key(self,key):
        try:
            del self.data[key]
            return True
        except KeyError:
            return False

    def check_key(self,key):
        return key in self.data
    
    def get_values(self,key):
        return list(self.data[key])
       
    def get_all_keys(self):
        return list(self.data.keys())
    
    def get_all_values(self):
        return list(self.data.values())

class FileDataBase(DataBase):
    def __init__(self,node_id) -> None:
        super().__init__(node_id,name='files.json')
        self.storage_dir = os.path.join(self.server_dir,'Storage')
        os.makedirs(self.storage_dir,exist_ok=True)

    def delete_file_from_storage(self,key):
        file_path = os.path.join(self.storage_dir,key)
        try:
            os.remove(file_path)
        except:
            return False
        else:
            return True

    @auto_save
    def delete_key(self, key):
        if super().delete_key(key):
            return self.delete_file_from_storage(key)
        else:
            return False
        
    def upload_file(self,file_name,file_content):
        file_path = os.path.join(self.storage_dir,file_name)
        with open(file_path, "wb") as source_file:
            source_file.write(file_content)

    def download_file(self,file_name):
        file_path = os.path.join(self.storage_dir,file_name)
        file_size = os.path.getsize(file_path)
        with open(file_path, "rb") as source_file:
            return source_file.read(),file_size

    @auto_save    
    def remove_values_from_key(self,key,values):
        if key in self.data:
            for value in values:
                self.data[key].remove(value)

        if len(self.data[key])==0:
            del self.data[key]
            self.delete_file_from_storage(key)


class TagDataBase(DataBase):
    def __init__(self,node_id) -> None:
        super().__init__(node_id,name='tags.json')

