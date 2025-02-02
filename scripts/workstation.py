import subprocess
import time
import psutil
import logging
import sys
import threading

# Adjust path if needed so Python can find file_handler with save_vmware_results
sys.path.append('C:\\Users\\Derda\\Documents\\Kerem-Bachelor\\Analysis-Hypervisors\\utils')
from file_handler import save_vmware_results

logging.basicConfig(
    filename="logs/workstation_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def start_workstation_vm(vm_path):
    """Startet eine VMware Workstation-VM."""
    try:
        logging.info(f"Starte VMware Workstation-VM: {vm_path}")
        print(f"Starte VMware Workstation-VM: {vm_path}")
        subprocess.run(["vmrun", "-T", "ws", "start", vm_path], check=True)
        logging.info("VMware Workstation-VM erfolgreich gestartet.")
        print("VMware Workstation-VM erfolgreich gestartet.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Fehler beim Starten der VMware Workstation-VM: {e}")
        raise

def stop_workstation_vm(vm_path):
    """Stoppt eine VMware Workstation-VM."""
    try:
        logging.info(f"Stoppe VMware Workstation-VM: {vm_path}")
        print(f"Stoppe VMware Workstation-VM: {vm_path}")
        subprocess.run(["vmrun", "-T", "ws", "stop", vm_path], check=True)
        logging.info("VMware Workstation-VM erfolgreich gestoppt.")
        print("VMware Workstation-VM erfolgreich gestoppt.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Fehler beim Stoppen der VMware Workstation-VM: {e}")
        raise

def run_guest_workload(vm_path, script_name):
    """
    Führt ein Workload-Skript (z.B. cpu_stress.bat) in der VMware Workstation-VM aus (synchron).
    Die Skripte liegen in der VM (Gast). Passen Sie Pfade, Gastnutzer, etc. an.
    """
    try:
        logging.info(f"Starte Workload {script_name} in VM {vm_path}")
        print(f"Starte Workload {script_name} in VM {vm_path}")
        # Example: if your batch files are on the guest's Desktop under user 'haltd'
        # Adjust -gu (username), -gp (password), path to the script, etc.
        result = subprocess.run([
            "vmrun", "-T", "ws",
            "-gu", "haltd",
            "-gp", "Verpissdichbillgates81",
            "runProgramInGuest",
            vm_path,
            "C:\\Windows\\System32\\cmd.exe",
            "--", "/c", f"C:\\Users\\haltd\\Desktop\\{script_name}"
        ], check=False)
        if result.returncode != 0:
            logging.warning(f"{script_name} returned code {result.returncode}")
            print(f"Warnung: {script_name} returned non-zero code {result.returncode}")
    except Exception as e:
        logging.error(f"Fehler beim Ausführen von {script_name}: {e}")
        print(f"Fehler beim Ausführen von {script_name}: {e}")

def run_workloads(vm_path):
    """
    Führt mehrere Workloads nacheinander aus (cpu_stress.bat, memory_stress.bat, disk_stress.bat).
    """
    workload_scripts = [
        "cpu_stress.bat",
        "memory_stress.bat",
        "disk_stress.bat"
    ]
    for script in workload_scripts:
        run_guest_workload(vm_path, script)

def monitor_metrics_continuous(results, stop_flag):
    """
    Sammelt fortlaufend Metriken in 'results', bis 'stop_flag' gesetzt wird.
    Jedes Sample enthält: time, cpu, memory, disk_read_bytes, disk_write_bytes, net_bytes_sent, net_bytes_recv.
    """
    disk_initial = psutil.disk_io_counters()
    net_initial = psutil.net_io_counters()
    start_time = time.time()

    while not stop_flag.is_set():
        elapsed = time.time() - start_time
        # 1 second sample
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

    logging.info("Metrics monitoring thread stopped.")

def run_workstation_test():
    """
    Führt einen kompletten Test für VMware Workstation durch, ähnlich wie im VirtualBox-Skript:
    1) Start VM
    2) Start Monitoring
    3) Run CPU/Memory/Disk workloads in Guest
    4) Stop Monitoring
    5) Save results
    6) Stop VM
    """
    vm_path = "C:\\Users\\Derda\\Documents\\Virtual Machines\\Windows 11 x64 (3)\\Windows 11 x64 (3).vmx"

    try:
        # 1) Start VM
        start_workstation_vm(vm_path)
        time.sleep(60)  # Warte 60 Sekunden, bis die VM hochgefahren ist

        # 2) Start Monitoring (in Hintergrund-Thread)
        logging.info("Starte Performance-Monitoring für VMware Workstation.")
        print("Starte Performance-Monitoring für VMware Workstation.")
        results = []
        stop_flag = threading.Event()
        monitor_thread = threading.Thread(target=monitor_metrics_continuous, args=(results, stop_flag))
        monitor_thread.start()

        # 3) Run the workloads (cpu/memory/disk stress) sequentially
        run_workloads(vm_path)

        # 4) Stop Monitoring
        logging.info("Stoppe Performance-Monitoring.")
        print("Stoppe Performance-Monitoring.")
        stop_flag.set()
        monitor_thread.join()  # warten, bis Thread beendet ist

        # 5) Save results
        # We assume 'save_vmware_results' can handle a list of dicts
        # If not, convert to a list-of-lists or CSV lines accordingly.
        save_vmware_results(results)

        # 6) Stop VM
        stop_workstation_vm(vm_path)
        logging.info("VMware Workstation-Test abgeschlossen.")
        print("VMware Workstation-Test abgeschlossen.")

    except Exception as e:
        logging.error(f"Fehler während des VMware Workstation-Tests: {e}")
        print(f"Fehler während des VMware Workstation-Tests: {e}")
