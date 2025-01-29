import os
import time

os.makedirs("test_files", exist_ok=True)

file_details = [
    ("file1.txt", "This is the first file."),
    ("file2.txt", "This is the second file."),
    ("file3.txt", "This is the third file.")
]

for filename, content in file_details:
    with open(os.path.join("test_files", filename), "w") as file:
        file.write(content)

now = time.time()
mod_times = [now, now - 86400, now - 172800]

for (filename, _), mod_time in zip(file_details, mod_times):
    os.utime(os.path.join("test_files", filename), (mod_time, mod_time))

print("Three files with different modification times have been created in the 'test_files' directory.")
