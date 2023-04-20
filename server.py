import socket

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = "127.0.0.1"
        self.server_port = 9999
        self.users_original_video = None
    
    def accpet(self):
        self.sock.bind((self.server_address, self.server_port))
        self.sock.listen(1)
        connect, address = self.sock.accept()
        print("Connected by", address)
        while True:
            data = connect.recv(1024)
            if data:
                print(f"Recevied {data.decode()}")
                connect.sendall(data)

                
            
class Main():
    server = Server()
    server.accpet()

if __name__ == "__main__":
    Main()