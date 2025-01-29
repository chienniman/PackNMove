import os
import shutil
import zipfile
from tkinter import Tk, filedialog, Button, Label, StringVar, messagebox
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

        self.source_folder = StringVar()
        self.dest_folder = StringVar()

        self.load_config()

        Label(master, text="Source Folder:").grid(row=0, column=0, padx=5, pady=5)
        self.source_label = Label(master, textvariable=self.source_folder)
        self.source_label.grid(row=0, column=1, padx=5, pady=5)

        Button(master, text="Browse", command=self.browse_source).grid(row=0, column=2, padx=5, pady=5)

        Label(master, text="Destination Folder:").grid(row=1, column=0, padx=5, pady=5)
        self.dest_label = Label(master, textvariable=self.dest_folder)
        self.dest_label.grid(row=1, column=1, padx=5, pady=5)

        Button(master, text="Browse", command=self.browse_dest).grid(row=1, column=2, padx=5, pady=5)

        self.progress = Progressbar(master, orient='horizontal', length=400, mode='determinate')
        self.progress.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        Button(master, text="Start", command=self.start_compression).grid(row=3, column=1, pady=10)

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

    def start_compression(self):
        if not self.source_folder.get() or not self.dest_folder.get():
            messagebox.showwarning("Warning", "Please select both source and destination folders.")
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
                for file in tqdm(group_files, desc=f"Compressing {mod_date}"):
                    archive.write(file, os.path.basename(file))
                    self.progress['value'] = processed_files + 1
                    self.master.update_idletasks()
                    total_size += os.path.getsize(file)
                    processed_files += 1

            for file in group_files:
                os.remove(file)

        end_time = time.time()
        elapsed_time = end_time - start_time
        stats_message = (f"PackNMove completed successfully!\n"
                         f"Total files processed: {total_files}\n"
                         f"Total size: {total_size / (1024 * 1024):.2f} MB\n"
                         f"Time: {elapsed_time:.2f} seconds")

        messagebox.showinfo("Info", stats_message)

if __name__ == "__main__":
    root = Tk()
    app = FileCompressor(root)
    root.mainloop()
