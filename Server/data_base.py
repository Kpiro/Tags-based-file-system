import os
import json
main_dir = ""
class DataBase:
    def __init__(self,node_id,name) -> None:
        self.data_dir = os.path.join(main_dir,node_id)
        self.create_dir()
        self.data_path = os.path.join(self.data_dir,name)
        self.data = {}
    
    def create_dir(self):
        os.makedirs(self.data_path,exist_ok=True)

    def read_database(self):
        with open(self.data_path, "r", encoding="utf-8") as file:
            self.data = json.load(self.data_path)

    def save_database(self):
        with open(self.data_path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    def add_values_to_key(self,key,values):
        self.data[key]+=values

    def remove_values_from_key(self,key,values):
        self.data[key]-=values
        if len(self.data[key])==0:
            del self.data[key]

    def check_key(self,key):
        return self.data.get(key)
    
    def get_values(self,key):
        return self.data[key]
    
    def delete_key(self,key):
        try:
            del self.data[key]
            return True
        except KeyError:
            return False




# class DataBase:
#     def __init__(self,node_id) -> None:
#         data_path = os.path.join(main_dir,node_id)
#         os.makedirs(data_path,exist_ok=True)
#         self.files = {}
#         self.tags = {}
    
#     def add_tags_to_file(self,file_name,tags_names):
#         self.files[file_name]+=tags_names

#     def add_tags_to_file(self,tag_name,files_names):
#         self.tags[tag_name]+=files_names

#     def remove_tags_from_file(self,tag_name,files_names):
#         self.tags[tag_name]-=files_names
#     def add_tags_to_file(self,tag_name,files_names):
#         self.tags[tag_name]+=files_names

    

#     def check_tag(self,tag_name):
#         return self.tags.get(tag_name)
    
#     def check_file(self,file_name):
#         return self.files.get(file_name)


