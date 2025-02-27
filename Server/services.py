from typing import List
from chord_node_reference import ChordNodeReference
from utils_server import calculate_hash
import json
import base64
class Service:
    def __init__(self,node):
        self.chord_ring: ChordNodeReference = node

    def find_owner(self, list_obj: List[str]) -> List[ChordNodeReference]:
        return [self.chord_ring.lookup(calculate_hash(obj)) for obj in list_obj]

class ReadService(Service):
    def __init__(self,node):
        super().__init__(node)

    def retrieve_files(self,tag_list):
        tags_owners = self.find_owner(tag_list)
        files = set()
        for owner, tag in zip(tags_owners, tag_list):
            ans = owner.get_files_from_tag(tag)
            print('get_files_from_tag: ',ans)
            if ans['state']=='Error':
                raise Exception(ans['message'])
            else:
                print(type(ans['files']))
                files.update(set(ans['files']))
        print('list: ',list(files))
        return list(files)
    
    def retrieve_tags(self,file_list):
        files_owners = self.find_owner(file_list)
        tags = set()
        for owner, file in zip(files_owners, file_list):
            ans = owner.get_tags_from_file(file)
            if ans['state']=='Error':
                raise Exception(ans['message'])
            else:
                tags.update(set(ans['tags']))
        return list(tags)
    def retrieve_all_files(self):
        files = []
        tags = []
        node = self.chord_ring
        while True:
            ans = node.get_all_files()
            if ans['state']=='Error':
                raise Exception(ans['message'])
            else:
                files+=ans['files']
                tags+=ans['tags']
            node = node.succ
            if node.id==self.chord_ring.id:
                break
        return files,tags

    

    
    def download_file(self,file_name):
        file_owner = self.find_owner([file_name])
        owner=file_owner[0]
        ans = owner.download_file(file_name)
        try:
            file_content = ans[0]
            file_size = ans[1]
        except:
            raise Exception(ans['message'])
        else:
            file_content,file_size

class WritenService(Service):
    def __init__(self,node):
        super().__init__(node)

    def add_tags_to_files(self,file_list,tag_list,len_list=None, content_list=None):
        file_owners = self.find_owner(file_list)

        if content_list and len_list:
            print('111111111111111111111')
            for owner, file, len, content in zip(file_owners, file_list, len_list, content_list):
                ans = owner.add_tags_to_file(file, tag_list,len, content)
                print('ans_for_service: ', ans)
                if ans['state']=='Error':
                    raise Exception(ans['message'])

        else:
            print('22222222222222222222222222222')
            for owner, file in zip(file_owners, file_list):
                ans = owner.add_tags_to_file(file, tag_list)
                if ans['state']=='Error':
                    raise Exception(ans['message'])
        
    def add_files_to_tags(self, file_list, tag_list):
        tag_owners = self.find_owner(tag_list)
        print('estoy aqui')
        for owner, tag in zip(tag_owners, tag_list):
            ans = owner.add_files_to_tag(tag, file_list)
            print('ya')
            if ans['state']=='Error':
                raise Exception(ans['message'])
    
    def delete_files(self,file_list):
        file_owners = self.find_owner(file_list)
        for owner, file in zip(file_owners, file_list):
            ans = owner.delete_file(file)
            if ans['state']=='Error':
                raise Exception(ans['message'])

    def delete_files_from_tags(self,tag_list,file_list):
        tag_owners = self.find_owner(tag_list)
        for owner, tag in zip(tag_owners, tag_list):
            ans = owner.delete_files_from_tag(tag,file_list)
            if ans['state']=='Error':
                raise Exception(ans['message'])

    def delete_tags_from_files(self,file_list,tag_list):
        files_owners = self.find_owner(file_list)
        for owner, file in zip(files_owners, file_list):
            ans = owner.delete_tags_from_file(file,tag_list)
            if ans['state']=='Error':
                raise Exception(ans['message'])



    
    

    