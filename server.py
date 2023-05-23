import subprocess
import json
import os
import shutil
import shlex
import asyncio
import logging
import time

class Server:
    def __init__(self):
        self.server_address = "127.0.0.1"
        self.server_port = 9999
        self.temp_strage_dir_path = "./temp-strage-dir/"
        self.reader = None
        self.writer = None
    
    def check_and_mkdir_for_strage_dir_path(self):
        if not os.path.exists(self.temp_strage_dir_path):
            os.mkdir(self.temp_strage_dir_path)
    
    async def create_server(self):
        server = await asyncio.start_server(self.accpet, self.server_address,self.server_port)
        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Serving on {addrs}')

        async with server:
            await server.serve_forever()
            
    async def accpet(self,reader,writer):
        print("socket created")
        self.reader = reader
        self.writer = writer
        
        try:
            while True:
                print("return True")
                menu_info =  await self.receive_menu_info()
                await self.check_video_exists(menu_info)
        
        except Exception as e:
            print("Error" + str(e))

        finally:
            self.sock.close()
            shutil.rmtree(self.temp_strage_dir_path)
            
    async def receive_menu_info(self):
        json_length = await self.protocol_extract_data_length_from_header()
        json_data = json.loads(await self.reader.read(json_length))
        
        print(json_data)
        return json_data
    
    async def protocol_extract_data_length_from_header(self):
        STREAM_RATE = 4
        return int.from_bytes(await self.reader.read(STREAM_RATE),"big")
        
    async def check_video_exists(self,menu_info):
        file_name_without_whitespace = "".join(menu_info["file_name"].split())
        file_name = self.temp_strage_dir_path + file_name_without_whitespace + menu_info["file_extension"]

        if os.path.exists(file_name):
            await self.replay_to_client("No need")
            await self.handle_convert_video(menu_info,file_name)
        else:
            await self.replay_to_client("need")
            cancel_event = asyncio.Event()
            await self.receive_video(menu_info,file_name,cancel_event)
        
            if cancel_event.is_set():
                print("キャンセルされた")
                self.delete_video(file_name)
            else:
                print("キャンセルされなかった")
                await self.handle_convert_video(menu_info,file_name)

    async def replay_to_client(self,message):
        message_bytes = message.encode("utf-8")

        header = self.protocol_make_header(len(message_bytes))
        self.writer.write(header)
        await self.writer.drain()
        self.writer.write(message_bytes)
        await self.writer.drain()
        print(message_bytes)
    
    def protocol_make_header(self,data_length):
        STREAM_RATE = 4
        return data_length.to_bytes(STREAM_RATE,"big")
        
    async def receive_video(self,menu_info,file_name,event):
        STREAM_RATE = 4096
        data_length = await self.protocol_extract_data_length_from_header()
        print(data_length)
        
        try:
            with open(file_name, "xb+") as video:
                while data_length > 0:
                    data = await self.reader.read(data_length if data_length <= STREAM_RATE else STREAM_RATE)
                    video.write(data)
                    data_length -= len(data)
                    # print(data_length)

                    if data == b"cancel":
                        print(data)
                        event.set()
                        break                    
            
        except FileExistsError:
            pass        

    async def handle_convert_video(self,menu_info,original_file_name):
        output_file_name = self.temp_strage_dir_path + self.create_output_file_name(menu_info)
        main_menu = menu_info["main_menu"]
        
        if main_menu == "compress":
            await self.compress_video(original_file_name,menu_info,output_file_name)
        elif main_menu == "resolution":
            await self.change_video_resolution(original_file_name,menu_info,output_file_name)
        elif main_menu == "aspect":
            await self.change_video_aspect(original_file_name,menu_info,output_file_name)
        elif main_menu == "audio":
            await self.video_to_mp3(original_file_name,output_file_name)
        elif main_menu == "gif":
            await self.video_to_gif(original_file_name,menu_info,output_file_name)
        
    def create_output_file_name(self,menu_info):
        original_file_name = "".join(menu_info["file_name"].split())
        main_menu = menu_info["main_menu"]
        
        if main_menu == "audio":
            file_extenstion = ".mp3"
        elif main_menu == "gif":
            file_extenstion = ".gif"
        elif main_menu == "webm":
            file_extenstion = ".webm"
        else:
            file_extenstion = menu_info["file_extension"]
        
        return f"{original_file_name}-{main_menu}{file_extenstion}"
    
    async def compress_video(self,original_file_name,menu_info,output_file_name):
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
        compress_command = f"ffmpeg -hide_banner -loglevel error -y -i {original_file_name} -c:v libx264 -crf {level} -preset medium -tune zerolatency -c:a copy {output_file_name}"
        await self.start_to_convert(compress_command,output_file_name)

    async def start_to_convert(self,ffmpeg_command,file_name):
        convert_process = subprocess.Popen(shlex.split(ffmpeg_command),stdin=subprocess.PIPE)
        monitor_process = await self.monitor_process(convert_process)
        
        if monitor_process:
            await self.report_to_end_converting(file_name,"done")
        else:
            await self.report_to_end_converting(file_name,"cancel")

    async def wait_for_process_to_cancel(self,convert_process):
        print("wait for user to cancel")
        try:
            cancel_message = "cancel".encode("utf-8")
            message = await self.reader.read(len(cancel_message))
            print(message.decode("utf-8"))
            
            if message.decode("utf-8") == "cancel":
                convert_process.communicate(str.encode("q"))
                return True
            
        except asyncio.CancelledError:
            pass

    async def monitor_process(self,process):
        print("monitor process.....")
        while process.poll() is None:
            try:
                cancel_task = await asyncio.wait_for(self.wait_for_process_to_cancel(process),timeout=0.001)
                if cancel_task:
                    return False
            except TimeoutError:
                pass

        print("process終了")
        return True

    async def change_video_resolution(self,original_file_name,menu_info,output_file_name):
        width = menu_info["option_menu"]["width"]
        height = menu_info["option_menu"]["height"]
        
        print("start to convert the video")
        
        change_resolution_command = f"ffmpeg -hide_banner -loglevel error -y -i {original_file_name} -filter:v scale={width}:{height} -c:a copy {output_file_name}"
        
        await self.start_to_convert(change_resolution_command,output_file_name) 

    async def change_video_aspect(self,original_file_name,menu_info,output_file_name):
        width = menu_info["option_menu"]["width"]
        height = menu_info["option_menu"]["height"]
        
        print("start to convert the video")

        change_aspect_command = f"ffmpeg -y -i {original_file_name}  -c copy -aspect {width}:{height} {output_file_name}"
    
        await self.start_to_convert(change_aspect_command,output_file_name)  

    async def video_to_mp3(self,original_file_name,output_file_name):
        print("start to convert the video")

        convert_to_mp3 = f"ffmpeg -y -i {original_file_name} -vn {output_file_name}"

        await self.start_to_convert(convert_to_mp3,output_file_name)
        
    async def video_to_gif(self,original_file_name,menu_info,output_file_name):
        start_time = menu_info["option_menu"]["start"]
        end_time = menu_info["option_menu"]["end"]

        print("start to convert the video")

        convert_to_gif = f"ffmpeg -ss {start_time} -y -i {original_file_name} -t {end_time} -r 5 {output_file_name}"

        await self.start_to_convert(convert_to_gif,output_file_name)
    
    async def report_to_end_converting(self,file_name,message):
        header = self.protocol_make_header(len(message))
        self.writer.write(header)
        await self.writer.drain()
        self.writer.write(message.encode("utf-8"))
        await self.writer.drain()
        
        if message == "done":
            await self.wait_for_pushing_download(file_name)
        
    async def wait_for_pushing_download(self,file_name):
        message_length = await self.protocol_extract_data_length_from_header()
        message = await self.reader.read(message_length)
        print("message is ; " + str(message.decode("utf-8") == "do"))
        
        if message.decode("utf-8") == "do":
            async with asyncio.TaskGroup() as tg:
                sending_video_task = tg.create_task(self.send_converted_video(file_name))
                monitor_task = tg.create_task(self.monitor_task(sending_video_task))
           
            if sending_video_task.cancelled():
                print("cancel downloading")
            else:
                print("done downloading")

        # self.delete_video(str(file_name))
            
    async def wait_for_task_to_cancel(self,task):
        print("wait for user to cancel")   
        try:
            cancel_message = "cancel".encode("utf-8")
            message = await self.reader.read(len(cancel_message))
            print(message.decode("utf-8"))
        
            if message.decode("utf-8") == "cancel":
                task.cancel()
                return True
            
        except asyncio.CancelledError:
            pass

    async def send_converted_video(self,file_name):
        print("Sending video...")
        STREAM_RATE = 4096
        
        try:
            with open(file_name, "rb") as video:
                video.seek(0, os.SEEK_END)
                data_size = video.tell()
                video.seek(0,0)
                header = self.protocol_make_header(data_size)
                self.writer.write(header)
                await self.writer.drain()
                
                data = video.read(4096)
                
                while data:
                    # print("sending...")
                    await asyncio.sleep(0.001)
                    self.writer.write(data)
                    await self.writer.drain()
                    data = video.read(4096)

        except asyncio.CancelledError:
            print("cancel sending video")

        except Exception as e:
            print("Error: " + str(e))

    async def monitor_task(self,monitoring_task):
        while not monitoring_task.done():
            try:
                cancel_task = await asyncio.wait_for(self.wait_for_task_to_cancel(monitoring_task),timeout=0.001)
                if cancel_task:
                    return False
            except TimeoutError:
                pass
        
        return True

    def delete_video(self,file_name):
        os.remove(file_name)
        ("Deleted...")
            
class Main():
    PYTHONASYNCIODEBUG = 1
    logging.basicConfig(level=logging.DEBUG)
    server = Server()
    server.check_and_mkdir_for_strage_dir_path()
    asyncio.run(server.create_server())

if __name__ == "__main__":
    Main()
    