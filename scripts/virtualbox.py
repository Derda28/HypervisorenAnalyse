import subprocess
import time
import psutil
import logging
import sys
import threading

sys.path.append('C:\\Users\\Derda\\Documents\\Kerem-Bachelor\\Analysis-Hypervisors\\utils')
from file_handler import save_virtualbox_results

logging.basicConfig(
    filename="logs/virtualbox_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def start_virtualbox_vm(vm_name):
    try:
        logging.info(f"Starte VirtualBox-VM: {vm_name}")
        print(f"Starte VirtualBox-VM: {vm_name}")
        subprocess.run(["VBoxManage", "startvm", vm_name], check=True)
        logging.info("VirtualBox-VM erfolgreich gestartet.")
        print("VirtualBox-VM erfolgreich gestartet.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Fehler beim Starten der VirtualBox-VM: {e}")
        raise

def stop_virtualbox_vm(vm_name):
    try:
        logging.info(f"Stoppe VirtualBox-VM: {vm_name}")
        print(f"Stoppe VirtualBox-VM: {vm_name}")
        subprocess.run(["VBoxManage", "controlvm", vm_name, "acpipowerbutton"], check=True)
        logging.info("VirtualBox-VM erfolgreich gestoppt.")
        print("VirtualBox-VM erfolgreich gestoppt.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Fehler beim Stoppen der VirtualBox-VM: {e}")
        raise

def run_guest_workload(vm_name, script_name):
    """
    Führt ein Workload-Skript in der VM aus (synchron).
    """
    try:
        logging.info(f"Starte Workload {script_name} in VM {vm_name}")
        print(f"Starte Workload {script_name} in VM {vm_name}")
        result = subprocess.run([
            "VBoxManage", "guestcontrol", vm_name, "run",
            "--username", "kerem",
            "--password", "12345678",
            "--exe", "cmd.exe", "--", "/c", f"C:\\Users\\kerem\\Desktop\\{script_name}"
        ], check=False)
        if result.returncode != 0:
            logging.warning(f"{script_name} returned code {result.returncode}")
            print(f"Warnung: {script_name} returned non-zero code {result.returncode}")
    except Exception as e:
        logging.error(f"Fehler beim Ausführen von {script_name}: {e}")
        print(f"Fehler beim Ausführen von {script_name}: {e}")

def run_workloads(vm_name):
    """
    Führt die Workload-Skripte nacheinander aus (blocking).
    """
    workload_scripts = [
        "cpu_stress.bat",
        "memory_stress.bat",
        "disk_stress.bat"
    ]
    for script in workload_scripts:
        run_guest_workload(vm_name, script)


def monitor_metrics_continuous(results, stop_flag):
    """
    Sammelt fortlaufend Metriken in 'results', bis 'stop_flag' gesetzt wird.
    Ergebnisse: Liste von Dictionaries
    [
      {
       "time": <float>,
       "cpu": <float>,
       "memory": <float>,
       ...
      },
      ...
    ]
    """
    disk_initial = psutil.disk_io_counters()
    net_initial = psutil.net_io_counters()
    start_time = time.time()

    while not stop_flag.is_set():
        elapsed = time.time() - start_time
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_io_counters()
        net = psutil.net_io_counters()

        disk_read = disk.read_bytes - disk_initial.read_bytes
        disk_write = disk.write_bytes - disk_initial.write_bytes
        net_sent = net.bytes_sent - net_initial.bytes_sent
        net_recv = net.bytes_recv - net_initial.bytes_recv

        entry = {
            "time": elapsed,
            "cpu": cpu,
            "memory": memory,
            "disk_read_bytes": disk_read,
            "disk_write_bytes": disk_write,
            "net_bytes_sent": net_sent,
            "net_bytes_recv": net_recv
        }
        results.append(entry)

        # Minimal sleep to reduce CPU overhead
        # (We've already slept 1 second in cpu_percent(interval=1) above.)
        # If you'd prefer to poll more quickly, set interval=0 for cpu_percent
        # and do time.sleep(1) here.
    
    # end while
    logging.info("Metrics monitoring thread stopped.")


def run_virtualbox_test():
    vm_name = "Windows11"
    try:
        # 1) Start VM
        start_virtualbox_vm(vm_name)
        time.sleep(60)  # warte, bis die VM vollständig hochgefahren ist

        # 2) Start Monitoring Thread
        logging.info("Starte Performance-Monitoring.")
        print("Starte Performance-Monitoring.")
        results = []
        stop_flag = threading.Event()
        t = threading.Thread(target=monitor_metrics_continuous, args=(results, stop_flag))
        t.start()

        # 3) Run Workloads (this is blocking)
        run_workloads(vm_name)

        # 4) Stop Monitoring
        logging.info("Stoppe Performance-Monitoring.")
        print("Stoppe Performance-Monitoring.")
        stop_flag.set()
        t.join()  # wait for monitor thread to exit

        # 5) Save results
        save_virtualbox_results(results)

        # 6) Stop VM
        stop_virtualbox_vm(vm_name)
        logging.info("VirtualBox-Test abgeschlossen.")
        print("VirtualBox-Test abgeschlossen.")

    except Exception as e:
        logging.error(f"Fehler während des VirtualBox-Tests: {e}")
        print(f"Fehler während des VirtualBox-Tests: {e}")
