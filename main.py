import os
import time
from threading import Thread
from multiprocessing import Process, Queue, current_process
from collections import defaultdict

# Sample setup for demonstration (file names and content are mocked)
# Let's create some temporary files
base_path = "/mnt/data/test_files"
os.makedirs(base_path, exist_ok=True)

# Create 5 sample text files
sample_contents = [
    "This is a test file with Python and threading.",
    "Another file with multiprocessing and keywords.",
    "Searching keywords in many files can be fun.",
    "Python can handle threads and processes.",
    "This file has no keywords at all."
]
file_paths = []

for i, content in enumerate(sample_contents):
    file_path = os.path.join(base_path, f"file_{i+1}.txt")
    with open(file_path, "w") as f:
        f.write(content)
    file_paths.append(file_path)

# Keywords to search
keywords = ["Python", "threading", "multiprocessing", "keywords"]

# Helper for threading
def search_in_files_thread(file_list, keywords, result_dict):
    for file_path in file_list:
        try:
            with open(file_path, "r") as f:
                content = f.read()
            for keyword in keywords:
                if keyword in content:
                    result_dict.setdefault(keyword, []).append(file_path)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

# Helper for multiprocessing
def search_in_files_process(file_list, keywords, queue):
    result = defaultdict(list)
    for file_path in file_list:
        try:
            with open(file_path, "r") as f:
                content = f.read()
            for keyword in keywords:
                if keyword in content:
                    result[keyword].append(file_path)
        except Exception as e:
            print(f"{current_process().name} error reading {file_path}: {e}")
    queue.put(dict(result))

# Threading version
def run_threading_version(file_paths, keywords):
    start = time.time()
    threads = []
    result = {}

    # Split files between 2 threads
    mid = len(file_paths) // 2
    file_chunks = [file_paths[:mid], file_paths[mid:]]

    for chunk in file_chunks:
        t = Thread(target=search_in_files_thread, args=(chunk, keywords, result))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    end = time.time()
    return result, end - start

# Multiprocessing version
def run_multiprocessing_version(file_paths, keywords):
    start = time.time()
    processes = []
    queue = Queue()
    final_result = defaultdict(list)

    # Split files between 2 processes
    mid = len(file_paths) // 2
    file_chunks = [file_paths[:mid], file_paths[mid:]]

    for chunk in file_chunks:
        p = Process(target=search_in_files_process, args=(chunk, keywords, queue))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    while not queue.empty():
        result = queue.get()
        for k, v in result.items():
            final_result[k].extend(v)

    end = time.time()
    return dict(final_result), end - start

import pandas as pd

if __name__ == "__main__":
    thread_result, thread_time = run_threading_version(file_paths, keywords)
    process_result, process_time = run_multiprocessing_version(file_paths, keywords)

    print("Threading result:", thread_result)
    print("Threading time:", thread_time)

    print("Multiprocessing result:", process_result)
    print("Multiprocessing time:", process_time)

    df = pd.DataFrame({
        "Method": ["Threading", "Multiprocessing"],
        "Time (s)": [thread_time, process_time],
        "Results": [thread_result, process_result]
    })

    print("\n--- Підсумкова таблиця ---")
    print(df)
