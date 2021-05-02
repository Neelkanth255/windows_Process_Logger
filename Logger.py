import psutil
from datetime import datetime
import pandas as pd
import schedule
import time
import os


# GET Process Information #
def get_processes_info():
    processes = []

    for process in psutil.process_iter():
        with process.oneshot():
            try:
                pid = process.pid
            except:
                print("Process ID didnt get retrived")

            if pid == 0:
                continue

            name = process.name()
            try:
                create_time = datetime.fromtimestamp(process.create_time())
            except OSError:
                create_time = datetime.fromtimestamp(psutil.boot_time())

            try:
                cores = len(process.cpu_affinity())
            except psutil.AccessDenied:
                cores = 0

            cpu_usage = process.cpu_percent()
            status = process.status()


            try:
                nice = int(process.nice())
            except psutil.AccessDenied:
                nice = 0

            try:
                memory_usage = process.memory_full_info().uss
            except psutil.AccessDenied:
                memory_usage = 0


            io_counters = process.io_counters()
            read_bytes = io_counters.read_bytes
            write_bytes = io_counters.write_bytes
            n_threads = process.num_threads()

            try:
                username = process.username()
            except psutil.AccessDenied:
                username = "N/A"

            # Creating Dictionary of all Process Info and Appending it in a list in each iteration

            processes.append({
                'pid': pid, 'name': name, 'create_time': create_time,
                'cores': cores, 'cpu_usage': cpu_usage, 'status': status, 'nice': nice,
                'memory_usage': memory_usage, 'read_bytes': read_bytes, 'write_bytes': write_bytes,
                'n_threads': n_threads, 'username': username,
            })

    return processes



# Creating Data Frame with the List of Process Dictionary

def construct_dataframe(processes):
    df = pd.DataFrame(processes)
    df.set_index('pid', inplace=True)
    df.sort_values("memory_usage", inplace=True, ascending=True)
    df['memory_usage'] = df['memory_usage'].apply(get_size)
    df['write_bytes'] = df['write_bytes'].apply(get_size)
    df['read_bytes'] = df['read_bytes'].apply(get_size)
    df['create_time'] = df['create_time'].apply(datetime.strftime, args=("%Y-%m-%d %H:%M:%S",))
    columns = "name,cpu_usage,memory_usage,read_bytes,write_bytes,status,create_time,nice,n_threads,cores"
    df = df[columns.split(",")] #
    return df


def get_size(bytes):
    """
    Returns size of bytes in a nice format
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024



if __name__ == "__main__":

    col = "pid,name,cpu_usage,memory_usage,read_bytes,write_bytes,status,create_time,nice,n_threads,cores"
    df1 = pd.DataFrame(columns=col.split(","))
    df1.to_csv("C:\\Users\\STXAHDLP078\\Documents\\Python Projects\\test\\result.csv",index=False)

    # Calling get_processes_info() & construct_dataframe(processes)
    def execute():
        processes = get_processes_info()
        df = construct_dataframe(processes)
        print(df.to_string())
        df.to_csv("C:\\Users\\STXAHDLP078\\Documents\\Python Projects\\test\\result.csv", mode='a', header=False)


    execute()


    schedule.every(10).seconds.do(execute)

    while 1:
        schedule.run_pending()
        time.sleep(1)

