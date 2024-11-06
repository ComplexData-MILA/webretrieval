import argparse
import subprocess
import json
import sys
import pandas as pd
import time
import threading
import os
import random

def handle_process(process):
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print("Error:", stderr.decode())
    


def main():
    parser = argparse.ArgumentParser(description="Collect news based on keywords.")
    parser.add_argument("-s", "--search_engine", default="DuckDuckGo", help="The select search engine to use to collect information"
                        +"Can select between DuckDuckGo and Google, default set to DuckDuckGo if not provided")
    parser.add_argument("-i", "--input_file", required=True, help="Input JSON file with the desired search keyword")
    parser.add_argument("-r", "--rpm", default=0.9 * 2_000, help="Requests per minute. Recommend setting this to slightly below your OpenAI limit.")
    parser.add_argument("-t", "--tpm", default=0.9 * 10_000_000, help="Maximum token limit per minute")
    parser.add_argument("-m", "--model", default="gpt-4o-mini", help="The GPT model that will be used")
    parser.add_argument("-o","--output_file", help="The file name of the output file, expect a JSON file. Input_file_name_output.json by default")
    args = parser.parse_args()

    if not args.output_file:
        base_name = os.path.splitext(args.input_file)[0]
        args.output_file = f"{base_name}.output.json"

    current_rp_count = 0
    current_tpm_count = 0
    df = pd.read_json(args.input_file, lines=True)
    last_reset_time = time.time()
    processes = []
    count = 0 
    df = df.sample(frac=1).reset_index(drop=True)


    
    for data in df.iterrows():
        actual = data[1]['verdict']
        statement = data[1]['text']
        if count >= 500: break
        current_time = time.time()
        if current_time - last_reset_time >= 60:
            last_reset_time = current_time
            current_rp_count = 0
            current_tpm_count = 0

        if current_rp_count > args.rpm or current_tpm_count > args.tpm:
            sleep_time = 60 - (time.time() - current_time)
            time.sleep(max(0, sleep_time))  # Ensures we don't sleep for a negative amount of time

        current_rp_count += 10  # this is max request count for 1 process
        current_tpm_count += 10000  # approximation for now, will change later in production environment

        time.sleep(10)
        process = subprocess.Popen([sys.executable, 'parallel.py', statement, args.search_engine, args.model, args.output_file, str(actual)], stdout=sys.stdout, stderr=subprocess.PIPE)
        process_thread = threading.Thread(target=handle_process, args=(process,))
        process_thread.start()
        processes.append((process, process_thread))

        count+=1
    for process, process_thread in processes:
        process_thread.join()  # Wait for all threads to complete

if __name__ == "__main__":
    main()
