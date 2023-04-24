from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import socket


class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server_address = "127.0.0.1"
        self.server_port = 9999
        self.file_name = "test.mp4"
        self.BUFFER_SIZE = 4096
        
    def connect(self):
        self.sock.connect((self.server_address, self.server_port))
        
        print("Sending video..")
        
        with open(self.file_name, "rb") as video:
            buffer = video.read()
            self.sock.sendall(buffer)
            
        print("Done sending..")


class View:
    @staticmethod
    def create_main_manu_page():
        root = Tk()
        
        # rootの構成
        # サイズを決める
        root.geometry("620x220")
        #　リサイズをFalseに設定 
        root.resizable(False, False)
        root.title("Main Menu")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # mainframeの作成
        mainframe = ttk.Frame(root)
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
        upload_btn_frame.grid(column=0, row=0)
        ttk.Button(upload_btn_frame, text="ファイルを選択" ,command=filedialog.askopenfilename).grid(column=0, row=0)
        
        # 圧縮ボタンの部分
        compress_frame = ttk.Frame(lower_half_frame)
        compress_frame.grid(column=0, row=0)
        compress_frame.columnconfigure(0, weight=1)
        compress_frame.rowconfigure(0, weight=1)
        ttk.Button(compress_frame,text="圧縮",command=lambda: View.make_compress_option_display(root)).grid(column=0, row=0)
        
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

        root.mainloop()
    
    @staticmethod
    def make_compress_option_display(root):
        # option_windowの作成
        option_window = Toplevel(root)
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
        ttk.Button(mainframe, text="start").grid(column=0, row=4)

        # main manuの操作ができないように設定して、フォーカスを新しいウィンドウに移す
        option_window.grab_set()
        option_window.focus_set()

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view


class Main():
    View.create_main_manu_page()
    client = Client()


if __name__ == "__main__":
    Main()