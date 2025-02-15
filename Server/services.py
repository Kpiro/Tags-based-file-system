from typing import List
from chord_node_reference import ChordNodeReference
from utils_server import calculate_hash

class Service:
    def __init__(self):
        self.chord_ring: ChordNodeReference = None

    def update_ring_reference(self, node: ChordNodeReference):
        self.chord_ring = node

    def find_owner(self, list_obj: List[str]) -> List[ChordNodeReference]:
        return [self.chord_ring.lookup(calculate_hash(obj)) for obj in list_obj]

class ReadService(Service):
    def __init__(self):
        super().__init__()

    def retrieve_files(self,tag_list):
        tags_owners = self.find_owner(tag_list)
        files = set()
        for owner, tag in zip(tags_owners, tag_list):
            files.union(set(owner.get_files_from_tag(tag)))
        return files

class WritenService(Service):
    def __init__(self):
        super().__init__()
    
    def add_files(self, file_list, tag_list):
        tags_owners = self.find_owner(tag_list)
        files_owners = self.find_owner(file_list)

        for owner, tag in zip(tags_owners, tag_list):
            owner.add_files_to_tag(tag, file_list)
        
        for owner, file in zip(files_owners, file_list):
            owner.add_tags_to_file(file, tag_list)




    
    

    