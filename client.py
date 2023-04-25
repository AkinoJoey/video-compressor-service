from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import socket
import os
import json


class Client:
    def __init__(self):
        self.BUFFER_SIZE = 4096

        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server_address = "127.0.0.1"
        self.server_port = 9999
        self.file_path = None
        self.file_name = None
        self.file_extension = None
        self.main_menu = None
        self.option_menu = None
    
    def create_menu_info_json(self):
        menu_info = {
            "file_name": self.file_name,
            "file_extension": self.file_extension,
            "main_menu": self.main_menu,
            "option_menu":self.option_menu
        }

        return json.dumps(menu_info)
    
    def send_menu_info(self,json_file):
        print("sending menu info ...")
        DATA_SIZE_SENDING_PER_ONE = 4
        json_file_bytes = json_file.encode("utf-8")
        self.sock.sendall(len(json_file_bytes).to_bytes(DATA_SIZE_SENDING_PER_ONE),"big")
        
    def connect(self):
        self.sock.connect((self.server_address, self.server_port))

        menu_info_json = self.create_menu_info_json()
        self.send_menu_info(menu_info_json)

        # print("Sending video..")
        
        # with open(self.file_path, "rb") as video:
        #     buffer = video.read()
        #     self.sock.sendall(buffer)
            
        # print("Done sending..")


class ViewController:
    def __init__(self,client):
        self.root = Tk()
        self.client = client
        self.file_name = StringVar()

    def create_main_manu_page(self):
        # rootの構成
        # サイズを決める
        self.root.geometry("620x220")
        #　リサイズをFalseに設定 
        self.root.resizable(False, False)
        self.root.title("Main Menu")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # mainframeの作成
        mainframe = ttk.Frame(self.root)
        mainframe.grid(column=0, row=0,sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        mainframe.rowconfigure(1, weight=1)
        
        # 上半分のフレーム
        upper_half_frame = ttk.Frame(mainframe,borderwidth=2, relief='solid')
        upper_half_frame.grid(column=0, row=0,sticky=(N, W, E, S))
        upper_half_frame.columnconfigure(0, weight=1)
        upper_half_frame.rowconfigure(0, weight=1)
        
        # 下半分のフレーム
        lower_half_frame = ttk.Frame(mainframe,borderwidth=2, relief='solid')
        lower_half_frame.grid(column=0,row=1,sticky=(N, W, E, S))
        lower_half_frame.columnconfigure(0, weight=1)
        lower_half_frame.columnconfigure(1, weight=1)
        lower_half_frame.columnconfigure(2, weight=1)
        lower_half_frame.columnconfigure(3, weight=1)
        lower_half_frame.columnconfigure(4, weight=1)
        lower_half_frame.rowconfigure(0, weight=1)
        
        # 動画選択ボタン
        upload_btn_frame = ttk.Frame(upper_half_frame)
        upload_btn_frame.grid(column=0, row=0,sticky=(N,W,E,S))
        upload_btn_frame.columnconfigure(0,weight=1)
        upload_btn_frame.rowconfigure(0,weight=2)
        upload_btn_frame.rowconfigure(1,weight=1)
        ttk.Button(upload_btn_frame, text="選択" ,command=lambda: self.prompt_video_file()).grid(column=0, row=0,sticky=S)

        # 選択した動画名の表示部分
        file_name_label = ttk.Label(upload_btn_frame, textvariable=self.file_name)
        file_name_label.grid(column=0, row=1,sticky=N)
        
        # 圧縮ボタンの部分
        compress_frame = ttk.Frame(lower_half_frame)
        compress_frame.grid(column=0, row=0)
        compress_frame.columnconfigure(0, weight=1)
        compress_frame.rowconfigure(0, weight=1)
        ttk.Button(compress_frame,text="圧縮",command=lambda: [self.create_compress_option_display(),self.set_main_menu("圧縮")]).grid(column=0, row=0)
        
        # # 解像度ボタンの部分
        resolution_frame = ttk.Frame(lower_half_frame)
        resolution_frame.grid(column=1, row=0)
        ttk.Button(resolution_frame,text="解像度").grid(column=0, row=0)
        
        # # 縦横比ボタンの部分
        ratio_frame = ttk.Frame(lower_half_frame)
        ratio_frame.grid(column=2, row=0)
        ttk.Button(ratio_frame,text="縦横比").grid(column=0, row=0)
        
        # # to Audioボタンの部分
        to_audio_frame = ttk.Frame(lower_half_frame)
        to_audio_frame.grid(column=3, row=0)
        ttk.Button(to_audio_frame,text="to Audio").grid(column=0, row=0)
        
        # # GIF WEBMボタンの部分
        gif_webm_frame = ttk.Label(lower_half_frame)
        gif_webm_frame.grid(column=4, row=0)
        ttk.Button(gif_webm_frame, text="to GIF or WEBM").grid(column=0, row=0)

        self.root.mainloop()
    
    def prompt_video_file(self):
        file_path = filedialog.askopenfilename(
            title = "動画ファイルを選択",
            initialdir= "./"
        )

        # 拡張子なしのファイル名
        file_name_with_extension = os.path.basename(file_path)
        file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]
        file_extension = os.path.splitext(file_name_with_extension)[1]

        self.set_file_path(file_path)
        self.set_file_name(file_name_without_extension)
        self.set_file_extension(file_extension)
        self.display_file_name(file_name_with_extension)

    def set_file_path(self, file_path):
        self.client.file_path = file_path
        
    def set_file_name(self,file_name):
        self.client.file_name = file_name
    
    def set_file_extension(self,file_extension):
        self.client.file_extension = file_extension
    
    def display_file_name(self, file_name):
        self.file_name.set(file_name)
    
    def create_compress_option_display(self):
        # option_windowの作成
        option_window = Toplevel(self.root)
        option_window.title("圧縮する")
        option_window.geometry("420x220")
        option_window.resizable(False,False)
        option_window.columnconfigure(0, weight=1)
        option_window.rowconfigure(0, weight=1)

        # mainframeの作成
        mainframe = ttk.Frame(option_window)
        mainframe.grid(column=0, row=0,sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        mainframe.rowconfigure(1, weight=1)
        mainframe.rowconfigure(2, weight=1)
        mainframe.rowconfigure(3, weight=1)
        mainframe.rowconfigure(4, weight=1)

        # 圧縮レベルのラベル部分
        ttk.Label(mainframe,text="圧縮レベル").grid(column=0,row=0)

        # radio button
        compress_level = StringVar()
        high = ttk.Radiobutton(mainframe, text="high", variable=compress_level, value="high")
        high.grid(column=0,row=1)
        middle = ttk.Radiobutton(mainframe, text="middle", variable=compress_level, value="middle")
        middle.grid(column=0, row=2)
        low = ttk.Radiobutton(mainframe, text="low", variable=compress_level, value="low")
        low.grid(column=0, row=3)

        # start button
        ttk.Button(mainframe, text="start",command=lambda:[self.set_option_menu(compress_level.get()),self.start_to_convert()]).grid(column=0, row=4)

        # main manuの操作ができないように設定して、フォーカスを新しいウィンドウに移す
        option_window.grab_set()
        option_window.focus_set()
    
    def set_main_menu(self, main_menu):
        self.client.main_menu = main_menu
        
    def set_option_menu(self, option_menu):
        self.client.option_menu = option_menu

    def start_to_convert(self):
        self.client.create_menu_info_json()

class Main():
    client = Client()
    view_con = ViewController(client)
    view_con.create_main_manu_page()

    
if __name__ == "__main__":
    Main()