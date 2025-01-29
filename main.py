import os
import shutil
import zipfile
from tkinter import Tk, Frame, filedialog, Button, Label, StringVar, Text
from tkinter.ttk import Progressbar
from datetime import datetime
from tqdm import tqdm
import time
import winreg

REG_PATH = r"Software\PackNMove"

class FileCompressor:
    def __init__(self, master):
        self.master = master
        self.master.title("PackNMove")
        self.master.geometry("600x400")

        self.source_folder = StringVar()
        self.dest_folder = StringVar()
        self.status_message = StringVar()

        self.load_config()

        self.container = Frame(master)
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        Label(self.container, text="來源資料夾:").grid(row=0, column=0, padx=5, pady=5)
        self.source_label = Label(self.container, textvariable=self.source_folder)
        self.source_label.grid(row=0, column=1, padx=5, pady=5)

        Button(self.container, text="瀏覽", command=self.browse_source).grid(row=0, column=2, padx=5, pady=5)

        Label(self.container, text="目標資料夾:").grid(row=1, column=0, padx=5, pady=5)
        self.dest_label = Label(self.container, textvariable=self.dest_folder)
        self.dest_label.grid(row=1, column=1, padx=5, pady=5)

        Button(self.container, text="瀏覽", command=self.browse_dest).grid(row=1, column=2, padx=5, pady=5)

        self.progress = Progressbar(self.container, orient='horizontal', length=400, mode='determinate')
        self.progress.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        Button(self.container, text="開始", command=self.start_compression).grid(row=3, column=1, pady=10)
        Button(self.container, text="重置", command=self.reset_folders).grid(row=4, column=1, pady=10)

        self.status_label = Label(self.container, textvariable=self.status_message)
        self.status_label.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

    def load_config(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                self.source_folder.set(winreg.QueryValueEx(key, "source_folder")[0])
                self.dest_folder.set(winreg.QueryValueEx(key, "dest_folder")[0])
        except FileNotFoundError:
            self.source_folder.set("")
            self.dest_folder.set("")

    def save_config(self):
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
            winreg.SetValueEx(key, "source_folder", 0, winreg.REG_SZ, self.source_folder.get())
            winreg.SetValueEx(key, "dest_folder", 0, winreg.REG_SZ, self.dest_folder.get())

    def browse_source(self):
        folder_selected = filedialog.askdirectory()
        self.source_folder.set(folder_selected)
        self.save_config()

    def browse_dest(self):
        folder_selected = filedialog.askdirectory()
        self.dest_folder.set(folder_selected)
        self.save_config()

    def reset_folders(self):
        self.source_folder.set("")
        self.dest_folder.set("")
        self.progress['value'] = 0
        self.status_message.set("")
        self.save_config()

    def start_compression(self):
        if not self.source_folder.get() or not self.dest_folder.get():
            self.status_message.set("警告: 請選擇來源和目標資料夾。")
            return

        self.compress_files(self.source_folder.get(), self.dest_folder.get())

    def compress_files(self, source_folder, dest_folder):
        start_time = time.time()
        files = os.listdir(source_folder)
        files = [os.path.join(source_folder, file) for file in files]
        file_groups = {}
        for file in files:
            mod_time = datetime.fromtimestamp(os.path.getmtime(file))
            mod_date = mod_time.strftime('%Y%m%d')
            if mod_date not in file_groups:
                file_groups[mod_date] = []
            file_groups[mod_date].append(file)

        total_files = len(files)
        self.progress['maximum'] = total_files
        processed_files = 0
        total_size = 0

        for mod_date, group_files in file_groups.items():
            archive_name = os.path.join(dest_folder, f"archive_{mod_date}.zip")
            with zipfile.ZipFile(archive_name, 'w') as archive:
                for file in tqdm(group_files, desc=f"正在壓縮 {mod_date}"):
                    archive.write(file, os.path.basename(file))
                    self.progress['value'] = processed_files + 1
                    self.master.update_idletasks()
                    total_size += os.path.getsize(file)
                    processed_files += 1

            for file in group_files:
                os.remove(file)

        end_time = time.time()
        elapsed_time = end_time - start_time
        stats_message = (f"PackNMove 成功完成！\n"
                         f"處理的檔案總數: {total_files}\n"
                         f"總大小: {total_size / (1024 * 1024 * 1024):.2f} GB\n"
                         f"用時: {elapsed_time:.2f} 秒")

        self.status_message.set(stats_message)

if __name__ == "__main__":
    root = Tk()
    app = FileCompressor(root)
    root.mainloop()
