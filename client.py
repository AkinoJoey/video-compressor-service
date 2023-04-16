from tkinter import *
from tkinter import ttk


class View:
    
    def __init__(self,root):
        # rootの構成
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
        
        # アップロードボタン
        upload_btn_frame = ttk.Frame(upper_half_frame,borderwidth=2, relief='solid')
        upload_btn_frame.grid(column=0, row=0)
        ttk.Button(upload_btn_frame, text="Upload").grid(column=0, row=0)
        
        # 圧縮ボタンの部分
        compress_frame = ttk.Frame(lower_half_frame,borderwidth=2, relief='solid')
        compress_frame.grid(column=0, row=0,sticky=(N, W, E, S))
        ttk.Label(compress_frame, text="圧縮").grid(column=0, row=0)
        ttk.Button(compress_frame).grid(column=0, row=1)
        
        # # 解像度ボタンの部分
        # resolution_frame = ttk.Frame(lower_half_frame)
        # resolution_frame.grid(column=1, row=1)
        # ttk.Label(resolution_frame, text="解像度").grid(column=0, row=0)
        # ttk.Button(resolution_frame).grid(column=0, row=1)
        
        # # 縦横比ボタンの部分
        # ratio_frame = ttk.Frame(lower_half_frame)
        # ratio_frame.grid(column=2, row=1)
        # ttk.Label(ratio_frame, text="縦横比").grid(column=0, row=0)
        # ttk.Button(ratio_frame).grid(column=0, row=1)
        
        # # to Audioボタンの部分
        # to_audio_frame = ttk.Frame(lower_half_frame)
        # to_audio_frame.grid(column=3, row=1)
        # ttk.Label(to_audio_frame, text="to Audio").grid(column=0, row=0)
        # ttk.Button(to_audio_frame).grid(column=0, row=1)
        
        # # GIF WEBMボタンの部分
        # gif_webm_frame = ttk.Label(lower_half_frame)
        # gif_webm_frame.grid(column=4, row=1)
        # ttk.Label(gif_webm_frame, text="GIF or WEBM").grid(column=0, row=0)
        # ttk.Button(gif_webm_frame).grid(column=0, row=1)
        
        
        # コンテンツフレーム内に含まれるすべてのウィジェットにパディングを追加
        # for child in mainframe.winfo_children(): 
        #     child.grid_configure(padx=5, pady=5)
            
class FeetToMeters:

    def __init__(self, root):
        
        # タイトルの作成
        root.title("Feet to Meters")

        # コンテンツフレームの作成
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
       
        # フィート数を入力するウィジェットを作成
        self.feet = StringVar()
        feet_entry = ttk.Entry(mainframe, width=7, textvariable=self.feet)
        feet_entry.grid(column=2, row=1, sticky=(W, E))
        self.meters = StringVar()

        # 変換後のmetersを表示する部分を作成
        ttk.Label(mainframe, textvariable=self.meters).grid(column=2, row=2, sticky=(W, E))
        
        #　calculateのボタンを作成
        ttk.Button(mainframe, text="Calculate", command=self.calculate).grid(column=3, row=3, sticky=W)

        # その他の文字の部分を作成
        ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
        ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
        ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

        # コンテンツフレーム内に含まれるすべてのウィジェットにパディングを追加
        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        # エントリウィジェットにフォーカスを当てて入力しやすくする
        feet_entry.focus()
        
        # returnキーとcalculateボタンをbindして操作性を高める
        root.bind("<Return>", self.calculate)
        
    def calculate(self, *args):
        try:
            value = float(self.feet.get())
            self.meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)
        except ValueError:
            pass


# メインアプリケーションウィンドウの設定
root = Tk()

# サイズを決める
root.geometry("620x220")

#　リサイズをFalseに設定 
root.resizable(False, False)
# FeetToMeters(root)
View(root)

# rootをループしてウィジェットを常時表示する
root.mainloop()