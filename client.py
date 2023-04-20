from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import socket

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server_address = "127.0.0.1"
        self.server_port = 9999
        self.original_video = None

    def connect(self):
        test_string = "this is test."
        self.sock.connect((self.server_address, self.server_port))
        self.sock.sendall(test_string.encode("utf-8"))
        data = self.sock.recv(1024)
        print("Recevid", data.decode())

class View:
    def __init__(self,root):
        self.root = root
        
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
        
        # アップロードボタン
        upload_btn_frame = ttk.Frame(upper_half_frame)
        upload_btn_frame.grid(column=0, row=0)
        ttk.Button(upload_btn_frame, text="Upload" ,command=filedialog.askopenfilename).grid(column=0, row=0)
        
        # 圧縮ボタンの部分
        compress_frame = ttk.Frame(lower_half_frame)
        compress_frame.grid(column=0, row=0)
        compress_frame.columnconfigure(0, weight=1)
        compress_frame.rowconfigure(0, weight=1)
        ttk.Button(compress_frame,text="圧縮",command=self.make_compress_option_display).grid(column=0, row=0)
        
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
        ttk.Button(gif_webm_frame, text="GIF WEBM").grid(column=0, row=0)

    def make_compress_option_display(self):
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
        ttk.Button(mainframe, text="start").grid(column=0, row=4)

        # main manuの操作ができないように設定して、フォーカスを新しいウィンドウに移す
        option_window.grab_set()
        option_window.focus_set()
    




class Main():
    # メインアプリケーションウィンドウの設定
    root = Tk()
    # FeetToMeters(root)
    View(root)
    # rootをループしてウィジェットを常時表示する
    root.mainloop()

    # client = Client()
    # client.connect()

if __name__ == "__main__":
    Main()