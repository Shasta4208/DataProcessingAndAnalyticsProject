import os
import time

def get_files(file_path, first_run):
    files_to_process = []
    for root_dir, dirs, files in os.walk(file_path):
        for name in files:
            full_file_path = os.path.join(root_dir, name)
            if name.endswith('.xml') and os.path.getsize(full_file_path) > 0:
                file_mod_time = os.path.getmtime(full_file_path)
                if first_run or (time.time() - file_mod_time) <= 24 * 60 * 60:
                    files_to_process.append(full_file_path)
                else:
                    print(f"Skipping old file: {full_file_path}")
            else:
                print(f"Skipping empty or non-XML file: {full_file_path}")
    return files_to_process
