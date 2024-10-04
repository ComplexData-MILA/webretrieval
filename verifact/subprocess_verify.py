import subprocess
import json
import sys
import pandas as pd
import time
import threading

rpm = int(0.9 * 30_000)  # requests per minute
tpm = int(0.9 * 150_000_000)  # tokens per minute, probably will never reach

current_rp_count = 0
current_tpm_count = 0
input_file_path = "fact.json"
df = pd.read_json(input_file_path, lines=True)
last_reset_time = time.time()

def handle_process(process):
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print("Error:", stderr.decode())
    else:
        print(stdout.decode())

processes = []
for statement in df["statement"]:
    current_time = time.time()
    if current_time - last_reset_time >= 60:
        last_reset_time = current_time
        current_rp_count = 0
        current_tpm_count = 0

    if current_rp_count > rpm or current_tpm_count > tpm:
        sleep_time = 60 - (time.time() - current_time)
        time.sleep(max(0, sleep_time))  # Ensures we don't sleep for a negative amount of time

    current_rp_count += 10  # this is max request count for 1 process
    current_tpm_count += 5000  # approximation for now, will change later in production environment

    process = subprocess.Popen([sys.executable, 'parallel.py', statement], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process_thread = threading.Thread(target=handle_process, args=(process,))
    process_thread.start()
    processes.append((process, process_thread))

for process, process_thread in processes:
    process_thread.join()  # Wait for all threads to complete
