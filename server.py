import socket
import subprocess
import json
import sys
import os
import shutil

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = "127.0.0.1"
        self.server_port = 9999
        self.temp_strage_dir_path = "./temp-strage-dir/"
    
    def check_and_mkdir_for_strage_dir_path(self):
        if not os.path.exists(self.temp_strage_dir_path):
            os.mkdir(self.temp_strage_dir_path)
            
    def accpet(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.server_address, self.server_port))
        self.sock.listen(1)
        print("socket created")
        connect, address = self.sock.accept()
        print("Connected by", address)
        
        try:
            while True:
                menu_info =  self.receive_menu_info(connect)
                self.receive_video(connect,menu_info)
        
        except Exception as e:
            print("Error" + str(e))

        finally:
            self.sock.close()
            shutil.rmtree(self.temp_strage_dir_path)
            
    def receive_menu_info(self,connect):
        DATA_SIZE = 4
        json_length = int.from_bytes(connect.recv(DATA_SIZE),"big")
        json_data = json.loads(connect.recv(json_length))
        
        print(json_data)
        return json_data
    
    def receive_video(self,connect,menu_info):
        STREAM_RATE = 4096
        data_length = int.from_bytes(connect.recv(STREAM_RATE),"big")
        print(data_length)
        original_file_name = self.temp_strage_dir_path + menu_info["file_name"] + menu_info["file_extension"]
        
        try:
            with open(original_file_name, "xb+") as video:
                while data_length > 0:
                    data = connect.recv(data_length if data_length <= STREAM_RATE else STREAM_RATE)
                    video.write(data)
                    data_length -= len(data)
                    print(data_length)

            print("Done receiving video...")
            
        except FileExistsError:
            pass
        
            
        self.convert_video(connect,menu_info,original_file_name)
        
    def convert_video(self,connect,menu_info,original_file_name):
        output_file_name = self.temp_strage_dir_path + self.create_output_file_name(menu_info)
        main_menu = menu_info["main_menu"]
        
        if main_menu == "compress":
            self.compress_video(original_file_name,menu_info,output_file_name)
        
        print("end converting")
        
        self.report_to_end_converting(connect,output_file_name)
    
    def create_output_file_name(self,menu_info):
        original_file_name = menu_info["file_name"]
        main_menu = menu_info["main_menu"]
        option_menu = menu_info["option_menu"]
        file_extenstion = menu_info["file_extension"]
        
        return f"{original_file_name}-{main_menu}-{option_menu}{file_extenstion}"
    
    def compress_video(self,original_file_name,menu_info,output_file_name):
        option_menu = menu_info["option_menu"]
        high = 40
        middle = 34
        low = 28
        
        if option_menu == "high":
            level = high
        elif option_menu == "middle":
            level = middle
        else:
            level = low
            
        print("start to convert the video")
        compress_command = f"ffmpeg -n -i {original_file_name} -c:v libx264 -crf {level} -preset medium -tune zerolatency -c:a copy {output_file_name}"

        subprocess.run(compress_command,shell=True)
    
    def report_to_end_converting(self,connect,file_name):
        message = "done"
        connect.sendall(message.encode("utf-8"))
        
        self.wait_for_pushing_download(connect,file_name)
        
    def wait_for_pushing_download(self,connect,file_name):
        STREAM_RATE = 4096
        
        while True:
            message = connect.recv(STREAM_RATE).decode("utf-8",errors='ignore')
            if message == "download":
                self.send_converted_video(file_name,connect)
                break
        
    def send_converted_video(self,file_name,connect):
        print("Sending video...")
        STREAM_RATE = 4096
        
        with open(file_name, "rb") as video:
            video.seek(0, os.SEEK_END)
            data_size = video.tell()
            video.seek(0,0)
            connect.sendall(data_size.to_bytes(STREAM_RATE,"big"))
            
            data = video.read(4096)
            
            while data:
                print("sending...")
                connect.send(data)
                data = video.read(4096)
            
        print("Done sending...")
        
            
class Main():
    server = Server()
    server.check_and_mkdir_for_strage_dir_path()
    server.accpet()

if __name__ == "__main__":
    Main()
    