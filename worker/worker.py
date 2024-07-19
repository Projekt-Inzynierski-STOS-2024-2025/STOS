import os
import time

path = os.environ.get('FILES_PATH')

if not path:
    raise ValueError("PATH environment variable must be set.")

print(f"Worker working...")

time.sleep(10)

if os.path.isdir(path):
    for filename in os.listdir(path):
        print(filename)

    lock_file_path = os.path.join(path, '.lock')
    with open(lock_file_path, 'w') as lock_file:
        pass

print('Worker finished work')
