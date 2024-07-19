import os
import shutil
import time

input_path = os.getenv('INPUT_PATH')
output_path = os.getenv('OUTPUT_PATH')

if not input_path or not output_path:
    raise ValueError("Both INPUT_PATH and OUTPUT_PATH environment variables must be set.")

os.makedirs(output_path, exist_ok=True)

print(f"Worker working...")

time.sleep(10)

for filename in os.listdir(input_path):
    full_file_name = os.path.join(input_path, filename)
    if os.path.isfile(full_file_name):
        shutil.copy(full_file_name, output_path)


print('Worker finished work')
