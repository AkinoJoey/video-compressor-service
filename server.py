import socket
import subprocess
import json

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = "127.0.0.1"
        self.server_port = 9999
        
    def accpet(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.server_address, self.server_port))
        self.sock.listen(1)
        print("socket created")
        connect, address = self.sock.accept()
        print("Connected by", address)
        
        while True:
            menu_info =  self.receive_menu_info(connect)
            self.receive_video(connect,menu_info)

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
        file_name = "server-side-" + menu_info["file_name"] + menu_info["file_extension"]
        
        try:
            with open(file_name, "xb") as video:
                while data_length > 0:
                    data = connect.recv(STREAM_RATE if STREAM_RATE >= data_length else data_length)
                    video.write(data)
                    data_length -= len(data)
                    print(data_length)

            print("Done receiving video...")
            
        except FileExistsError:
            pass
            
        self.convert_video(file_name,connect)
        
    def convert_video(self,file_name,connect):
        level = 40

        print("start to convert the video")
        compress_command = f"ffmpeg -i {file_name} -c:v libx264 -crf {level} -preset medium -tune zerolatency -c:a copy {file_name}-{level}.mp4"
        
        subprocess.run(compress_command,shell=True)
        print("end converting")
        
        self.report_to_end_converting(connect,file_name)
    
    def report_to_end_converting(self,connect,file_name):
        message = "done"
        connect.sendall(message.encode("utf-8"))
        
        self.wait_for_pushing_download(connect,file_name)
        
    def wait_for_pushing_download(self,connect,file_name):
        STREAM_RATE = 4096
        
        while True:
            message = connect.recv(STREAM_RATE).decode("utf-8")
            if message == "download":
                self.send_converted_video(file_name,connect)
                break
        
    def send_converted_video(self,file_name,connect):
        print("Sending video...")
        
        with open(file_name, "rb") as video:
            data = video.read()
            STREAM_RATE = 4096
            connect.sendall(len(data).to_bytes(STREAM_RATE,"big"))
            connect.sendall(data)
            
        print("Done sending...")
        
            
class Main():
    server = Server()
    server.accpet()

if __name__ == "__main__":
    Main()
    
    
# ffmpeg -i usrs_original_video.mp4 -c:v libx264 -crf 40 -preset medium -tune zerolatency -c:a copy output-crf-40.mp4
# ffmpeg -i test.mp4 -c:v libx264 -crf 40 -preset medium -tune zerolatency -c:a copy output-crf-40.mp4
# ffmpeg -i test-1920x1080-30fps.mp4 -c:v libx264 -crf 28 -preset medium -tune zerolatency -c:a copy output-crf-28.mp4
