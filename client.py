from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import socket
import os
import json
import threading
import re

class Client:
    def __init__(self):
        self.BUFFER_SIZE = 4096
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket_connecting = False
        self.server_address = "127.0.0.1"
        self.server_port = 9999
        self.file_path = None
        self.menu_info = {
            "file_name": None,
            "file_extension": None,
            "main_menu": None,
            "option_menu":None
        }
        
    def connect(self,conversion_event,connection_event,cancel_event):
        try:
            self.sock.connect((self.server_address, self.server_port))
            self.socket_connecting = True
            connection_event.set()
            self.send_menu_info(conversion_event,cancel_event)
            
        except ConnectionRefusedError:
            error_message = "サーバーに接続できません"
            ViewController.display_alert(error_message)
            conversion_event.set()
        
        except Exception as e:
            error_message = "Error: " + str(e)
            ViewController.display_alert(error_message)
            conversion_event.set()
            
    def send_menu_info(self,conversion_event,cancel_event):
        print("sending menu info ...")
        json_string = json.dumps(self.menu_info)
        self.sender(json_string)

        self.wait_for_sending_video(conversion_event,cancel_event)
    
    def sender(self,message):
        message_bytes = message.encode("utf-8")
        header = self.protocol_make_header(len(message_bytes))
        self.sock.sendall(header)
        self.sock.sendall(message_bytes)
    
    def protocol_make_header(self,data_length):
        STREAM_RATE = 4
        return data_length.to_bytes(STREAM_RATE,"big")
    
    def receiver(self):
        data_length = self.protocol_extract_data_length_from_header()
        data = self.sock.recv(data_length)
        
        return data.decode("utf-8")
    
    def protocol_extract_data_length_from_header(self):
        STREAM_RATE = 4
        return int.from_bytes(self.sock.recv(STREAM_RATE),"big")

    def wait_for_sending_video(self,conversion_event,cancel_event):
        message_from_server = self.receiver()

        if message_from_server == "need":
            self.send_video(conversion_event,cancel_event)
        elif message_from_server == "NO need":
            self.wait_to_convert(conversion_event,cancel_event)
        else:
            ViewController.display_alert("エラーが発生しました")
            conversion_event.set()
            cancel_event.set()
    
    def send_video(self,conversion_event,cancel_event):
        print("Sending video...")
        STREAM_RATE = 4096
        
        with open(self.file_path, "rb") as video:
            video.seek(0, os.SEEK_END)
            data_size = video.tell()
            video.seek(0,0)
            header = self.protocol_make_header(data_size)
            self.sock.sendall(header)
            
            data = video.read(STREAM_RATE)
            
            while data and not cancel_event.is_set():
                self.sock.send(data)
                data = video.read(STREAM_RATE)
        
        if cancel_event.is_set():
            print("Cancel to convert")
        else:
            print("Done sending...")
            self.wait_to_convert(conversion_event,cancel_event)
        
    def wait_to_convert(self,conversion_event,cancel_event):
        message = self.receiver()

        if message == "done":
            conversion_event.set()
        elif message == "cancel":
            pass
        elif message == "error":
            conversion_event.set()
            cancel_event.set()
            ViewController.display_alert("エラーが発生しました")
    
    def tell_server_want_to_download_or_not(self,download_event,cancel_event,do_or_not):
        self.sender(do_or_not)
        
        if do_or_not == "do":
            self.download_video(download_event,cancel_event)

    def download_video(self,download_event,cancel_event):
        STREAM_RATE = 4096
        data_length = self.protocol_extract_data_length_from_header()
        download_dir_path = os.path.join(os.getenv('USERPROFILE'), 'Downloads') if os.name  == "nt" else os.path.expanduser('~/Downloads')
        download_video_full_path_without_extension = os.path.join(download_dir_path,self.menu_info["file_name"])
        file_extension = self.get_new_file_extension()
        file_name =  self.check_for_same_name_and_rename(download_video_full_path_without_extension,file_extension)
        
        try:
            with open(file_name, "xb") as video:
                print("downloading video...")
                while data_length > 0 and not cancel_event.is_set():
                    data = self.sock.recv(data_length if data_length <= STREAM_RATE else STREAM_RATE)
                    video.write(data)
                    data_length -= len(data)
            
            if cancel_event.is_set():
                print("cancel to download...")
                
            else:
                print("Done downloading ...")
                ViewController.show_info("ダウンロードが完了しました。")
                download_event.set()

        except Exception as e:
            print("Download error:" + str(e))
            download_event.set()
    
    def get_new_file_extension(self):
        main_menu = self.menu_info["main_menu"]

        if main_menu == "audio":
            return ".mp3"
        elif main_menu == "gif":
            return ".gif"
        elif main_menu == "webm":
            return ".webm"
        else:
            return  self.menu_info["file_extension"]

    def check_for_same_name_and_rename(self,download_video_full_path_without_extension,file_extension):
        file_name = download_video_full_path_without_extension + file_extension
        number_for_file_name_overwrite = 1

        while os.path.isfile(file_name):
                file_name = download_video_full_path_without_extension + " " + str(f"({number_for_file_name_overwrite})") + file_extension
                number_for_file_name_overwrite += 1
                
        return file_name
    
    def tell_server_to_end_app(self):
        self.sender("end app")
        self.sock.close()
                
class ViewController:
    def __init__(self,client):
        self.root = Tk()
        self.client = client
        self.file_name_for_display = StringVar()
        self.root.protocol("WM_DELETE_WINDOW",self.end_app)

    def end_app(self):
        if self.client.socket_connecting:
            self.client.tell_server_to_end_app()
            self.root.destroy()
        else:
            self.root.destroy()

    @staticmethod
    def display_alert(error_msg):
        messagebox.showerror(title="error",message=error_msg)

    @staticmethod
    def show_info(msg):
        messagebox.showinfo(message=msg)
            
    def create_main_menu_page(self):
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
        upper_half_frame = ttk.Frame(mainframe)
        upper_half_frame.grid(column=0, row=0,sticky=(N, W, E, S))
        upper_half_frame.columnconfigure(0, weight=1)
        upper_half_frame.rowconfigure(0, weight=1)
        
        # 下半分のフレーム
        lower_half_frame = ttk.Frame(mainframe)
        lower_half_frame.grid(column=0,row=1,sticky=(N, W, E, S))
        lower_half_frame.columnconfigure(0, weight=1)
        lower_half_frame.columnconfigure(1, weight=1)
        lower_half_frame.columnconfigure(2, weight=1)
        lower_half_frame.rowconfigure(0, weight=1)
        lower_half_frame.rowconfigure(1, weight=1)
        
        # 動画選択ボタン
        upload_btn_frame = ttk.Frame(upper_half_frame)
        upload_btn_frame.grid(column=0, row=0,sticky=(N,W,E,S))
        upload_btn_frame.columnconfigure(0,weight=1)
        upload_btn_frame.rowconfigure(0,weight=2)
        upload_btn_frame.rowconfigure(1,weight=1)
        ttk.Button(upload_btn_frame,cursor='hand2',text="選択" ,command=self.prompt_video_file).grid(column=0, row=0,sticky=S)

        # 選択した動画名の表示部分
        file_name_label = ttk.Label(upload_btn_frame, textvariable=self.file_name_for_display)
        file_name_label.grid(column=0, row=1,sticky=N)
        
        # 圧縮ボタンの部分
        compress_frame = ttk.Frame(lower_half_frame)
        compress_frame.grid(column=0, row=0)
        compress_frame.columnconfigure(0, weight=1)
        compress_frame.rowconfigure(0, weight=1)
        ttk.Button(compress_frame,text="圧縮",cursor='hand2',command=lambda:[
            self.confirm_selected_video("compress"),
            self.set_main_menu_dict("compress")
            ]).grid(column=0, row=0)
        
        # # 解像度ボタンの部分
        resolution_frame = ttk.Frame(lower_half_frame)
        resolution_frame.grid(column=1, row=0)
        ttk.Button(resolution_frame,cursor='hand2',text="解像度",command=lambda:[
            self.confirm_selected_video("resolution"),
            self.set_main_menu_dict("resolution")
        ]).grid(column=0, row=0)
        
        # # 縦横比ボタンの部分
        ratio_frame = ttk.Frame(lower_half_frame)
        ratio_frame.grid(column=2, row=0)
        ttk.Button(ratio_frame,text="縦横比",cursor='hand2',command=lambda:[
            self.confirm_selected_video("aspect"),
            self.set_main_menu_dict("aspect")
            ]).grid(column=0, row=0)
        
        # # to Audioボタンの部分
        to_audio_frame = ttk.Frame(lower_half_frame)
        to_audio_frame.grid(column=0, row=1)
        ttk.Button(to_audio_frame,text="To Audio",cursor='hand2',command=lambda:[
            self.confirm_selected_video("audio"),
            self.set_main_menu_dict("audio")
        ]).grid(column=0, row=0)
        
        # # WEBMボタンの部分
        gif_webm_frame = ttk.Label(lower_half_frame)
        gif_webm_frame.grid(column=1, row=1)
        ttk.Button(gif_webm_frame, text="To GIF",cursor='hand2',command=lambda:[
            self.confirm_selected_video("gif"),
            self.set_main_menu_dict("gif")
        ]).grid(column=0, row=0)

        # # WEBMボタンの部分
        gif_webm_frame = ttk.Label(lower_half_frame)
        gif_webm_frame.grid(column=2, row=1)
        ttk.Button(gif_webm_frame, text="To WEBM",cursor='hand2',command=lambda:[
            self.confirm_selected_video("webm"),
            self.set_main_menu_dict("webm")
            ]).grid(column=0, row=0)

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
        self.set_file_name_dict(file_name_without_extension)
        self.set_file_extension_dict(file_extension)
        self.display_file_name(file_name_with_extension)
        
    def confirm_selected_video(self,selected_main_menu):
        if self.file_name_for_display.get() == "":
            ViewController.display_alert("ファイルを選択してください")
        else:
            if selected_main_menu == "compress":
                self.create_compress_option_window()
            elif selected_main_menu == "resolution":
                self.create_resolution_option_window()
            elif selected_main_menu == "aspect":
                self.create_aspect_option_window()
            elif selected_main_menu == "audio":
                self.create_audio_option_window()
            elif selected_main_menu == "gif":
                self.create_gif_webm_option_window()
            elif selected_main_menu == "webm":
                self.create_gif_webm_option_window()
    
    def set_main_menu_dict(self, main_menu):
        self.client.menu_info["main_menu"] = main_menu

    def set_file_path(self, file_path):
        self.client.file_path = file_path
        
    def set_file_name_dict(self,file_name):
        self.client.menu_info["file_name"] = file_name
    
    def set_file_extension_dict(self,file_extension):
        self.client.menu_info["file_extension"] = file_extension
    
    def display_file_name(self, file_name):
        self.file_name_for_display.set(file_name)
 
    def create_compress_option_window(self):
        # option_windowの作成
        option_window = self.create_new_window("圧縮レベル")

        # mainframeの作成
        mainframe = ttk.Frame(option_window)
        mainframe.grid(column=0, row=0,sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        mainframe.rowconfigure(1, weight=1)
        mainframe.rowconfigure(2, weight=1)
        mainframe.rowconfigure(3, weight=1)

        # radio button
        compress_level = StringVar(value="middle")
        high = ttk.Radiobutton(mainframe,cursor='hand2',text="high", variable=compress_level, value="high")
        high.grid(column=0,row=0)
        middle = ttk.Radiobutton(mainframe,cursor='hand2',text="middle", variable=compress_level, value="middle")
        middle.grid(column=0, row=1)
        low = ttk.Radiobutton(mainframe,cursor='hand2',text="low", variable=compress_level, value="low")
        low.grid(column=0, row=2)

        # start button
        ttk.Button(mainframe,cursor='hand2',text="start",command=lambda:[
            self.set_option_menu_dict(compress_level.get()),
            self.start_to_convert(option_window)
            ]).grid(column=0, row=3)

        # main menuの操作ができないように設定して、フォーカスを新しいウィンドウに移す
        option_window.grab_set()
        option_window.focus_set()
    
    def create_new_window(self,title):
        option_window = Toplevel(self.root)
        option_window.title(title)
        option_window.geometry("420x220")
        option_window.resizable(False,False)
        option_window.columnconfigure(0, weight=1)
        option_window.rowconfigure(0, weight=1)
        
        return option_window
    
    def set_option_menu_dict(self, option_menu):
        self.client.menu_info["option_menu"] = option_menu

    def start_to_convert(self,option_window):
        option_window.destroy()
        conversion_event = threading.Event()
        cancel_event = threading.Event()
        cancel_for_callback = self.handle_to_cancel
        progressbar_window =  self.create_progressbar("変換中",cancel_event,cancel_for_callback,"変換を中止してよろしいですか？",conversion_event)
       
        if self.client.socket_connecting:
            connecting_thread = threading.Thread(target=self.client.send_menu_info,args=[conversion_event,cancel_event])
            connecting_thread.start()
            wait_for_conversion_thread = threading.Thread(target=self.wait_for_conversion,args=[progressbar_window,conversion_event,cancel_event])
            wait_for_conversion_thread.start()
        else:
            connection_event = threading.Event()
            connect_thread = threading.Thread(target=self.client.connect,args=[conversion_event,connection_event,cancel_event])
            connect_thread.start()
            
            wait_for_conversion_thread = threading.Thread(target=self.wait_for_conversion,args=[progressbar_window,conversion_event,cancel_event,connection_event])
            wait_for_conversion_thread.start()
    
    def handle_to_cancel(self,msg,main_event,cancel_event):
        answer = messagebox.askyesno(message=msg)

        if answer:
            self.client.sender("cancel")
            cancel_event.set()
            main_event.set()
    
    def wait_for_conversion(self,window,conversion_event,cancel_event,connection_event=None):
        if not connection_event is None:
            connection_event.wait()
        
        conversion_event.wait()
        window.destroy()
        
        if not cancel_event.is_set():
            self.create_download_window()
        
    def create_resolution_option_window(self):
        option_window = self.create_new_window("解像度")

        mainframe = ttk.Frame(option_window)
        mainframe.grid(column=0, row=0,sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=9)
        mainframe.columnconfigure(1, weight=1)
        mainframe.columnconfigure(2, weight=9)
        mainframe.rowconfigure(0, weight=1)
        mainframe.rowconfigure(1, weight=1)
        mainframe.rowconfigure(2, weight=1)
        mainframe.rowconfigure(3, weight=1)
        mainframe.rowconfigure(4, weight=1)

        format_label = ttk.Label(mainframe, text="フォーマット")
        format_label.grid(column=0, row=0,columnspan=3,sticky=S)

        format_combobox = ttk.Combobox(mainframe,cursor='hand2',justify=CENTER,state="readonly",width=10)
        format_combobox['values'] = ("720p","1080p","WQHD","4K","8K","カスタム")
        format_combobox.current(0)
        format_combobox.grid(column=0,row=1,columnspan=3)
        format_combobox.bind('<<ComboboxSelected>>',lambda event:self.change_resolution(event,width,height,width_entry,height_entry))
        
        resolution_label = ttk.Label(mainframe, text="解像度")
        resolution_label.grid(column=0, row=2,columnspan=3,sticky=S)

        width = StringVar(value="1280")
        height = StringVar(value="720")
        
        check_num_wrapper = (self.root.register(self.check_num),'%P',0,5)

        width_entry = ttk.Entry(mainframe,textvariable=width,width=6,state="disable",validate="key",validatecommand=check_num_wrapper)
        width_entry.grid(column=0,row=3,sticky=E)

        height_entry = ttk.Entry(mainframe,textvariable=height,width=6,state="disable",validate="key",validatecommand=check_num_wrapper)
        height_entry.grid(column=2,row=3,sticky=W)
        x = ttk.Label(mainframe, text= "x")
        x.grid(column=1,row=3)
        
        ttk.Button(mainframe, text="start",cursor='hand2',command=lambda:[
            self.check_not_blank(width.get(),height.get(),option_menu={"width": width.get(),"height": height.get()},option_window=option_window)
            ]).grid(column=0, row=4,columnspan=3)
        
        option_window.grab_set()
        option_window.focus_set()
        
    def change_resolution(self,event,width,height,width_entry,height_entry):
        current_value = event.widget.get()

        if current_value == "720p":
            width.set("1280")
            height.set("720")
            self.set_state_of_option(width_entry,height_entry,"disable")

        elif current_value == "1080p":
            width.set("1920")
            height.set("1080")
            self.set_state_of_option(width_entry,height_entry,"disable")

        elif current_value == "WQHD":
            width.set("2560")
            height.set("1440")
            self.set_state_of_option(width_entry,height_entry,"disable")

        elif current_value == "4K":
            width.set("4096")
            height.set("2160")
            self.set_state_of_option(width_entry,height_entry,"disable")

        elif current_value == "8K":
            width.set("7680")
            height.set("4320")
            self.set_state_of_option(width_entry,height_entry,"disable")

        else:
            self.set_state_of_option(width_entry,height_entry,"normal")   
    
    def set_state_of_option(self,width_entry,height_entry,state):
        width_entry.configure(state=state)
        height_entry.configure(state=state)
    
    def check_num(self,newval,min,max):
        pattern = f'^\\d{{{min},{max}}}$'
        return re.match(pattern,newval) is not None

    def check_not_blank(self,*entry,option_menu,option_window):
        for value in entry:
            if value == "":
                ViewController.display_alert("値を入力してください")
                return
        
        self.set_option_menu_dict(option_menu)
        self.start_to_convert(option_window)
        
    def create_aspect_option_window(self):
        option_window = self.create_new_window("アスペクト比")

        mainframe = ttk.Frame(option_window)
        mainframe.grid(column=0, row=0,sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=9)
        mainframe.columnconfigure(1, weight=1)
        mainframe.columnconfigure(2, weight=9)
        mainframe.rowconfigure(0,weight=1)
        mainframe.rowconfigure(1,weight=1)
        
        width = StringVar(value="16")
        height = StringVar(value="9")

        check_num_wrapper = (self.root.register(self.check_num),'%P',0,2)
        
        width_entry = ttk.Entry(mainframe,textvariable=width,width=6,state="normal",justify=CENTER,validate='key',validatecommand=check_num_wrapper)
        width_entry.grid(column=0,row=0,sticky=(E,S))
        
        height_entry = ttk.Entry(mainframe,textvariable=height,width=6,state="normal",justify=CENTER,validate='key',validatecommand=check_num_wrapper)
        height_entry.grid(column=2,row=0,sticky=(W,S))

        colon = ttk.Label(mainframe, text= ":")
        colon.grid(column=1,row=0,sticky=S)
        
        ttk.Button(mainframe, text="start",cursor='hand2',command=lambda:[
            self.check_not_blank(width.get(),height.get(),option_menu={"width": width.get(),"height": height.get()},option_window=option_window)
            ]).grid(column=0, row=1,columnspan=3)
        
        option_window.grab_set()
        option_window.focus_set()
    
    def create_audio_option_window(self):
        option_window = self.create_new_window("To Audio")

        mainframe = ttk.Frame(option_window)
        mainframe.grid(column=0, row=0,sticky=(N, W, E, S))
        mainframe.columnconfigure(0,weight=1)
        mainframe.rowconfigure(0,weight=1)

        ttk.Button(mainframe, text="start",cursor="hand2",command=lambda:[
            self.set_option_menu_dict("-"),
            self.start_to_convert(option_window)
        ]).grid(column=0,row=0)

        option_window.grab_set()
        option_window.focus_set()

    def create_gif_webm_option_window(self):
        option_window = self.create_new_window("時間範囲を指定")

        mainframe = ttk.Frame(option_window)
        mainframe.grid(column=0, row=0,sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=9)
        mainframe.columnconfigure(1, weight=1)
        mainframe.columnconfigure(2, weight=9)
        mainframe.rowconfigure(0, weight=1)
        mainframe.rowconfigure(1, weight=1)

        start_frame = ttk.Frame(mainframe)
        start_frame.grid(column=0,row=0,sticky=(S,E))
        start_frame.columnconfigure(0,weight=9)
        start_frame.columnconfigure(1,weight=1)
        start_frame.columnconfigure(2,weight=9)
        start_frame.columnconfigure(3,weight=1)
        start_frame.columnconfigure(4,weight=9)
        start_frame.rowconfigure(0,weight=1)

        end_frame = ttk.Frame(mainframe)
        end_frame.grid(column=2,row=0,sticky=(S,W))
        end_frame.columnconfigure(0,weight=9)
        end_frame.columnconfigure(1,weight=1)
        end_frame.columnconfigure(2,weight=9)
        end_frame.columnconfigure(3,weight=1)
        end_frame.columnconfigure(4,weight=9)
        end_frame.rowconfigure(0,weight=1)

        start_hh = StringVar(value="00")
        start_mm = StringVar(value="00")
        start_ss = StringVar(value="00")

        end_hh = StringVar(value="00")
        end_mm = StringVar(value="00")
        end_ss = StringVar(value="00")
        
        colon_1 = ttk.Label(start_frame,text=":")
        colon_1.grid(column=1,row=0)
        colon_2 = ttk.Label(start_frame,text=":")
        colon_2.grid(column=3,row=0)
        colon_3 = ttk.Label(end_frame,text=":")
        colon_3.grid(column=1,row=0)
        colon_4 = ttk.Label(end_frame,text=":")
        colon_4.grid(column=3,row=0)

        wave = ttk.Label(mainframe,text="~")
        wave.grid(column=1,row=0,sticky=S)

        check_time_wrapper = (self.root.register(self.check_num),'%P',0,2)
        start_hh_entry = ttk.Entry(start_frame, textvariable=start_hh,width=3,justify=CENTER,validate='key',validatecommand=check_time_wrapper)
        start_hh_entry.grid(column=0, row=0,sticky=(S,E))
        start_mm_entry = ttk.Entry(start_frame, textvariable=start_mm,width=3,justify=CENTER,validate='key',validatecommand=check_time_wrapper)
        start_mm_entry.grid(column=2,row=0,sticky=S)
        start_ss_entry = ttk.Entry(start_frame,textvariable=start_ss,width=3,justify=CENTER,validate='key',validatecommand=check_time_wrapper)
        start_ss_entry.grid(column=4,row=0,sticky=(S,W))

        end_hh_entry = ttk.Entry(end_frame, textvariable=end_hh,width=3,justify=CENTER,validate='key',validatecommand=check_time_wrapper)
        end_hh_entry.grid(column=0, row=0,sticky=(S,W))
        end_mm_entry = ttk.Entry(end_frame, textvariable=end_mm,width=3,justify=CENTER,validate='key',validatecommand=check_time_wrapper)
        end_mm_entry.grid(column=2,row=0,sticky=S)
        end_ss_entry = ttk.Entry(end_frame,textvariable=end_ss,width=3,justify=CENTER,validate='key',validatecommand=check_time_wrapper)
        end_ss_entry.grid(column=4,row=0,sticky=(S,E))
        
        ttk.Button(mainframe, text="start",cursor="hand2",command=lambda:[
            self.check_not_blank(start_hh.get(),start_mm.get(),start_ss.get(),end_hh.get(),end_mm.get(),end_ss.get(),
                                 option_menu={
                                    "start":f"{start_hh.get()}:{start_mm.get()}:{start_ss.get()}",
                                    "end":f"{end_hh.get()}:{end_mm.get()}:{end_ss.get()}"
                                             },
                                 option_window=option_window)
        ]).grid(column=0,row=1,columnspan=3)

        option_window.grab_set()
        option_window.focus_set()

    def create_progressbar(self,title,cancel_event,callback_for_canceling,title_when_cancel,main_event):
        processing_window = self.create_new_window(title)

        mainframe = ttk.Frame(processing_window,padding=50)
        mainframe.grid(column=0, row=0,sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        
        progressbar = ttk.Progressbar(mainframe,length=200,orient=HORIZONTAL,mode='indeterminate')
        progressbar.grid(column=0,row=0)
        progressbar.start(10)
        print("display progress bar....")
        
        # closeボタンを押した時に閉じる
        processing_window.protocol("WM_DELETE_WINDOW",func=lambda:[callback_for_canceling(title_when_cancel,main_event,cancel_event)])
                                                                                                               
        return processing_window
        
    def create_download_window(self):       
        download_window = self.create_new_window("処理完了")
        mainframe = ttk.Frame(download_window)
        mainframe.grid(column=0, row=0,sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        cancel_event = threading.Event()
        download_event = threading.Event()
        request_download_thread  = threading.Thread(target=self.client.tell_server_want_to_download_or_not,args=[download_event,cancel_event,"do"])
        
        # closeボタンを押した場合、ダウンロードが必要ないことをサーバーに伝える
        download_window.protocol("WM_DELETE_WINDOW",func=lambda:[
            self.check_if_cancel_downloading("ダウンロードを終了しますか？",download_event,cancel_event,download_window)
        ])
        
        ttk.Button(mainframe, text="Download",command=lambda:[
            download_window.destroy(),
            request_download_thread.start(),
            self.start_to_download(cancel_event,download_event)
            ]).grid(column=0, row=0)

    def check_if_cancel_downloading(self,msg,download_event,cancel_event,window):
        answer = messagebox.askyesno(message=msg)
        
        if answer:
            self.client.tell_server_want_to_download_or_not(download_event,cancel_event,"not")
            window.destroy()
        
    def start_to_download(self,cancel_event,download_event):
        callback_for_canceling = self.handle_to_cancel
        progressbar_window = self.create_progressbar("ダウンロード中",cancel_event,callback_for_canceling,"ダウンロードを中止しますか？",download_event)
        
        wait_for_downloading_thread = threading.Thread(target=self.wait_for_downloading,args=[progressbar_window,download_event])
        wait_for_downloading_thread.start()
        
    def wait_for_downloading(self,window,downloading_event):
        downloading_event.wait()
        print("destroy open window")
        window.destroy()

class Main():
    client = Client()
    view_con = ViewController(client)
    view_con.create_main_menu_page()

    
if __name__ == "__main__":
    Main()