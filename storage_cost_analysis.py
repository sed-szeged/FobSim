import os
from pandas import DataFrame
import time

times = [0]
sizes = [0]
run_time_seconds = 200


def run_storage_analysis():
    path = 'temporary'
    # initialize the size\
    total_size = 0
    # use the walk() method to navigate through directory tree
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            while True:
                try:
                    # use join to concatenate all the components of path
                    f = os.path.join(dirpath, name)
                    # use getsize to generate size in bytes and add it to the total size
                    total_size += os.path.getsize(f)
                    break
                except Exception as e:
                    time.sleep(0.01)
    return total_size


def upload_analysis():
    df = DataFrame({'Time': times, 'Size (bytes)': sizes})
    df.to_excel('Storage_analysis.xlsx', sheet_name='sheet1', index=False)


past_run_file_size = run_storage_analysis()
sizes[-1] = past_run_file_size
print("Storage analysis started.")
while True:
    current_file_size = run_storage_analysis()
    if current_file_size == sizes[-1]:
        time.sleep(1)
    else:
        for i in range(run_time_seconds):
            times.append(times[-1] + 1)
            sizes.append(current_file_size)
            time.sleep(1)
            current_file_size = run_storage_analysis()
        upload_analysis()
        break
