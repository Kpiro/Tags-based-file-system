from data_base import FileDataBase, TagDataBase
main_dir = "./Data_base"
import os
import socket
import json
from utils_server import recv_multiple_files,send_multiple_files, calculate_hash, is_between
from const import *
import threading

class DataManager:
    def __init__(self, ip, port = DEFAULT_DATA_PORT):
        self.db_ip = ip
        self.id = calculate_hash(ip)
        self.data_dir = os.path.join(main_dir,str(self.id))
        self.db_port = port
        
        os.makedirs(self.data_dir,exist_ok=True)

        self.my_files = FileDataBase(self.data_dir,'MyDB')
        self.pred_files = FileDataBase(self.data_dir,'PredDB')
        self.succ_files = FileDataBase(self.data_dir,'SuccDB')

        self.my_tags = TagDataBase(self.data_dir,'MyDB')
        self.pred_tags = TagDataBase(self.data_dir,'PredDB')
        self.succ_tags = TagDataBase(self.data_dir,'SuccDB')

        threading.Thread(target=self._recv, daemon=True).start()

    def _recv(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.db_ip, self.db_port))
        sock.listen(10)

        while True:
            conn, _ = sock.accept()
            data = conn.recv(1024).decode('utf-8')
            threading.Thread(target=self.handle_request, args=(conn, data)).start()

    #----------------------------------BASIC FUNCTION-------------------------------------------------------------

    # def clear_my_files(self):
    #     self.my_files.clear_data_base()
    # def clear_my_tags(self)
    #     self.my_tags.clear_data_base()
    # def clear_pred_files(self):
    #     self.pred_files.clear_data_base()
    # def clear_my_tags(self)
    #     self.pred_tags.clear_data_base()
    
    
    # ADD FILES OR TAGS
    def add_tags_to_my_file(self,file,tags):
        self.my_files.add_values_to_key(file,tags)
    def add_files_to_my_tag(self,tag,files):
        self.my_tags.add_values_to_key(tag,files)

    # def add_tags_to_pred_file(self,file,tags):
    #     self.pred_files.add_values_to_key(file,tags)
    
    # def add_tags_to_succ_file(self,file,tags):
    #     self.succ_files.add_values_to_key(file,tags)



    # def add_files_to_pred_tag(self,tag,files):
    #     self.pred_tags.add_values_to_key(tag,files)

    # def add_files_to_succ_tag(self,tag,files):
    #     self.succ_tags.add_values_to_key(tag,files)


    # REMOVE FILES FROM TAG OR TAGS FROM FILE
    
    def remove_tags_from_my_file(self,file,tags):
        self.my_files.remove_values_from_key(file,tags)
    
    def remove_files_from_my_tag(self,tag,files):
        self.my_tags.remove_values_from_key(tag,files)


    # def remove_tags_from_pred_file(self,file,tags):
    #     self.pred_files.remove_values_from_key(file,tags)
    
    # def remove_tags_from_succ_file(self,file,tags):
    #     self.succ_files.remove_values_from_key(file,tags)

    # def remove_files_from_pred_tag(self,tag,files):
    #     self.pred_tags.remove_values_from_key(tag,files)

    # def remove_files_from_succ_tag(self,tag,files):
    #     self.succ_tags.remove_values_from_key(tag,files)

    # DELETE FILE OR TAG
        
    def delete_my_file(self,file):
        self.my_files.delete_key(file)
    def delete_my_tag(self,tag):
        self.my_tags.delete_key(tag)

    # def delete_pred_file(self,file):
    #     self.pred_files.delete_key(file)

    # def delete_succ_file(self,file):
    #     self.succ_files.delete_key(file)



    # def delete_pred_tag(self,tag):
    #     self.pred_tags.delete_key(tag)

    # def delete_succ_tag(self,tag):
    #     self.succ_tags.delete_key(tag)

    # CHECK FILE OR TAG
        
    def check_my_file(self,file):
        self.my_files.check_key(file)
    def check_my_tag(self,tag):
        self.my_tags.check_key(tag)
    

    # GET FILE OR TAGS
        
    def get_tags_from_my_file(self,file):
        self.my_files.get_values(file)
    def get_files_from_my_tag(self,tag):
        self.my_tags.get_values(tag)

    # GET FILE OR TAGS
        
    def get_all_my_files(self):
        self.my_files.get_all_keys()
    def get_all_tags_in_my_files(self):
        self.my_files.get_all_values()

    def get_all_my_tags(self):
        self.my_tags.get_all_keys()
    def get_all_files_in_my_tags(self):
        self.my_tags.get_all_values()


    # READ AND WRITE A FILE
    def download_my_file(self,file):
        self.my_files.download_file(file)

    def upload_my_file(self,name,data):
        self.my_files.upload_file(name,data)

#----------------------------------REPLICATION FUNCTIONs-------------------------------------------------------------

    def push_data(self,owner_info: int = MY_INFO,clean_info: bool = False, conn: socket.socket = None):
        if owner_info == MY_INFO:
           tags = self.my_tags
           files = self.my_files
        elif owner_info == PRED_INFO:
            tags = self.pred_tags
            files = self.pred_files
        else:
            tags = self.succ_tags
            files = self.succ_files
        # Send tags
        conn.sendall(json.dumps(tags.data).encode('utf-8'))

        resp = conn.recv(1024).decode('utf-8')
        if resp != f"OK":
            raise Exception("ACK negativo")

        # Send files
        conn.sendall(json.dumps(files.data).encode('utf-8'))

        resp = conn.recv(1024).decode('utf-8')
        if resp != "OK":
            raise Exception("ACK negativo")
        send_multiple_files(files.get_all_keys(),files.download_file,conn)
        
    def pull_data(self, owner_info: int = MY_INFO, clean_info: bool = False, conn: socket.socket = None):
        
        if clean_info:
            if owner_info == PRED_INFO:
                self.pred_files.clear_data_base()
                self.pred_tags.clear_data_base()
            elif owner_info == SUCC_INFO:
                self.succ_files.clear_data_base()
                self.succ_tags.clear_data_base()

        # Receive tags
        tags_json = json.loads(conn.recv(1024).decode('utf-8'))
        conn.sendall('OK'.encode('utf-8'))

        # Receive files
        files_json = json.loads(conn.recv(1024).decode('utf-8'))

        conn.sendall('OK'.encode('utf-8'))
        

        if owner_info == PRED_INFO:
            self.pred_tags.merge_data(tags_json)
            self.pred_files.merge_data(files_json)
        elif owner_info == SUCC_INFO:
            self.succ_tags.merge_data(tags_json)
            self.succ_files.merge_data(files_json)
        elif owner_info == MY_INFO:
            self.my_tags.merge_data(tags_json)
            self.my_files.merge_data(files_json)
        name_list,_, content_list = recv_multiple_files()

        for name, content in zip(name_list,content_list):
            if owner_info == PRED_INFO:
                self.pred_files.upload_file(name,content)
                # Overwrite replicated tags and files
            elif owner_info == SUCC_INFO:
                self.succ_files.upload_file(name,content)
            elif owner_info == MY_INFO:
                self.my_files.upload_file(name,content)
        print(f"[📥] {len(files_json.items())} tags assumed from predpred")
        print(f"[📥] {len(tags_json.items())} files assumed from predpred")

    # Function to delegate data to the new incoming owner
    def delegate_data(self, new_owner_ip: str):
        print(f"[📤] Delegating data to {new_owner_ip}")
        i_t = 0
        i_f = 0

        new_owner_id = calculate_hash(new_owner_ip)
        my_id = calculate_hash(self.db_ip)

        tags_to_delegate = {}
        for k, v in self.get_all_my_tags():
            tag_hash = calculate_hash(k)
            if not is_between(tag_hash, new_owner_id, my_id):
                tags_to_delegate[k] = v
                i_t+=1

        files_to_delegate = {}
        for k, v in self.get_all_my_files():
            file_name_hash = calculate_hash(k)
            if not is_between(file_name_hash, new_owner_id, my_id):
                files_to_delegate[k] = v
                i_f+=1

        # Send corresponding data to new owner
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((new_owner_ip, self.db_port))
            s.sendall(f"{PULL_MY_INFO}".encode('utf-8'))
            
            resp = s.recv(1024).decode('utf-8')
            if resp != 'OK':
                raise Exception("ACK negativo")

            s.sendall(json.dumps(tags_to_delegate).encode('utf-8'))

            resp = s.recv(1024).decode('utf-8')
            if resp != 'OK':
                raise Exception("ACK negativo")

            s.sendall(json.dumps(files_to_delegate).encode('utf-8'))

            resp = s.recv(1024).decode('utf-8')
            if resp!= 'OK':
                raise Exception("ACK negativo")
            
            send_multiple_files(files_to_delegate,self.download_my_file,s)
            
            s.close()

        print(f"[📤] {i_t} tags delegated")
        print(f"[📤] {i_f} files delegated")

        # Delete not corresponding data
        for k, _ in tags_to_delegate.items():
            self.delete_my_tag(k)
        for k, _ in files_to_delegate.items():
            self.delete_my_file(k)

    # Function to assume data from old failed owner
    def assume_data(self, assume_predpred: str = None):
        print(f"[📥] Assuming predecesor data")

        # Assume replicated tags
        self.my_tags.merge_data(self.pred_tags.data)
        print(f"[📥] {len(self.pred_tags.data.items())} tags assumed from predecesor")
        self.pred_tags.clear_data_base()

        self.my_files.merge_data(self.pred_files.data)
        print(f"[📥] {len(self.pred_files.data.items())} files assumed from predecesor")
        for file_name in self.pred_files.get_all_keys():
            file_content, _ = self.pred_files.download_file(file_name)
            self.my_files.upload_file(file_name,file_content)
        self.pred_files.clear_data_base()

        # Assume predpred data
        if assume_predpred:
            if assume_predpred == self.db_ip:
                # Assume replicated tags
                self.my_tags.merge_data(self.succ_tags.data)
                print(f"[📥] {len(self.succ_tags.data.items())} tags assumed from prepred")
                self.succ_tags.clear_data_base()

                self.my_files.merge_data(self.succ_files.data)
                print(f"[📥] {len(self.succ_files.data.items())} files assumed from prepred")
                for file_name in self.succ_files.get_all_keys():
                    file_content, _ = self.succ_files.download_file(file_name)
                    self.my_files.upload_file(file_name,file_content)
                self.succ_files.clear_data_base()

            else:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((assume_predpred, self.db_port))

                    # Ask for replicated data
                    s.sendall(f"{PUSH_SUCC_INFO}".encode('utf-8'))

                    self.pull_data(owner_info=MY_INFO,clean_info=False,conn=s)
                    s.close()


    def handle_request(self, conn, request):
        # Send all my stored data
        if request == f"{PUSH_MY_INFO}":
            self.push_data(owner_info=MY_INFO,clean_info=False,conn = conn)
        elif request == f"{PUSH_PRED_INFO}":
            self.push_data(owner_info=PRED_INFO,clean_info=False,conn = conn)
        elif request == f"{PUSH_SUCC_INFO}":
            self.push_data(owner_info=SUCC_INFO,clean_info=False,conn = conn)

        elif request == f"{PULL_MY_INFO}":
            conn.sendall('OK'.encode('utf-8'))
            self.pull_data(owner_info=MY_INFO,clean_info=False,conn=conn)
        elif request == f"{PULL_PRED_INFO}":
            conn.sendall('OK'.encode('utf-8'))
            self.pull_data(owner_info=PRED_INFO,clean_info=True,conn=conn)
        elif request == f"{PULL_SUCC_INFO}":
            conn.sendall('OK'.encode('utf-8'))
            self.pull_data(owner_info=SUCC_INFO,clean_info=True,conn=conn)
     