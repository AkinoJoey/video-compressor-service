import socket
import subprocess

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = "127.0.0.1"
        self.server_port = 9999
        self.users_original_video = None
    
    def accpet(self):
        self.sock.bind((self.server_address, self.server_port))
        self.sock.listen(1)
        print("socket created")
        connect, address = self.sock.accept()
        print("Connected by", address)
        
        self.receive_original_video(connect)

    
    def receive_original_video(self,connect):
        data = connect.recv(1024)
        file_name = 'users_original_video'+'.mp4'
        
        try:
            with open(file_name, "wb") as video:
                while data:
                    video.write(data)
                    data = connect.recv(1024) 

            print("Done reading bytes..")
            
            self.convert_video(file_name)
            
        except Exception as e:
            print("Error" + str(e))
        
    def convert_video(self,file_name):
        level = 40

        print("start to convert the video")
        compress_command = f"ffmpeg -i {file_name} -c:v libx264 -crf {level} -preset medium -tune zerolatency -c:a copy output-crf-{level}.mp4"
        
        subprocess.run(compress_command,shell=True)
        print("end converting")
        
            
class Main():
    server = Server()
    server.accpet()

if __name__ == "__main__":
    Main()
    
    
# ffmpeg -i usrs_original_video.mp4 -c:v libx264 -crf 40 -preset medium -tune zerolatency -c:a copy output-crf-40.mp4
# ffmpeg -i test.mp4 -c:v libx264 -crf 40 -preset medium -tune zerolatency -c:a copy output-crf-40.mp4
# ffmpeg -i test-1920x1080-30fps.mp4 -c:v libx264 -crf 28 -preset medium -tune zerolatency -c:a copy output-crf-28.mp4
