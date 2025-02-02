import subprocess
import time
import psutil
import logging
import sys
import threading

# Adjust path if needed so Python can find 'file_handler' with 'save_hyperv_results'
sys.path.append('C:\\Users\\Derda\\Documents\\Kerem-Bachelor\\Analysis-Hypervisors\\utils')

from file_handler import save_hyperv_results

logging.basicConfig(
    filename="logs/hyperv_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def start_hyperv_vm(vm_name):
    """Startet eine Hyper-V-VM."""
    try:
        logging.info(f"Starte Hyper-V-VM: {vm_name}")
        print(f"Starte Hyper-V-VM: {vm_name}")
        # Use PowerShell Start-VM
        subprocess.run(["powershell", "-Command", f"Start-VM -Name \"{vm_name}\""], check=True)
        logging.info("Hyper-V-VM erfolgreich gestartet.")
        print("Hyper-V-VM erfolgreich gestartet.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Fehler beim Starten der Hyper-V-VM: {e}")
        raise

def stop_hyperv_vm(vm_name):
    """Stoppt eine Hyper-V-VM."""
    try:
        logging.info(f"Stoppe Hyper-V-VM: {vm_name}")
        print(f"Stoppe Hyper-V-VM: {vm_name}")
        # Use PowerShell Stop-VM
        subprocess.run(["powershell", "-Command", f"Stop-VM -Name \"{vm_name}\" -Force"], check=True)
        logging.info("Hyper-V-VM erfolgreich gestoppt.")
        print("Hyper-V-VM erfolgreich gestoppt.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Fehler beim Stoppen der Hyper-V-VM: {e}")
        raise

def run_guest_workload(vm_name, script_name):
    """
    Führt ein Workload-Skript in der Hyper-V-VM aus (synchron) via PowerShell Invoke-Command.
    """
    try:
        logging.info(f"Starte Workload {script_name} in Hyper-V-VM: {vm_name}")
        print(f"Starte Workload {script_name} in Hyper-V-VM: {vm_name}")

        # We'll define a multiline PowerShell command using triple-quoted string.
        # This helps avoid confusion with braces in an f-string.
        ps_command = f"""
$cred = New-Object System.Management.Automation.PSCredential 'haltdeinefresselassmichuberspringen@outlook.de', 
    (ConvertTo-SecureString 'Verpissdichbillgates81' -AsPlainText -Force)

Invoke-Command -VMName '{vm_name}' -Credential $cred -ScriptBlock {{
    try {{
        Start-Process -FilePath 'C:\\Users\\haltd\\Desktop\\{script_name}' -ErrorAction Stop -Wait
        Write-Output 'Batch-Datei erfolgreich ausgeführt.'
    }} catch {{
        Write-Output "Fehler: $($_)"
    }}
}}
"""

        # Now run that PowerShell command
        result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_command], check=False)

        if result.returncode != 0:
            logging.warning(f"{script_name} returned code {result.returncode}")
            print(f"Warnung: {script_name} returned non-zero code {result.returncode}")

    except Exception as e:
        logging.error(f"Fehler beim Ausführen von {script_name}: {e}")
        print(f"Fehler beim Ausführen von {script_name}: {e}")


def run_workloads(vm_name):
    """
    Führt mehrere Workloads nacheinander aus (cpu_stress.bat, memory_stress.bat, disk_stress.bat).
    Passen Sie ggf. die Pfade an den Gast an.
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
    Jeder Eintrag: {
      "time": <float>,
      "cpu": <float>,
      "memory": <float>,
      "disk_read_bytes": <int>,
      "disk_write_bytes": <int>,
      "net_bytes_sent": <int>,
      "net_bytes_recv": <int>
    }
    """
    disk_initial = psutil.disk_io_counters()
    net_initial = psutil.net_io_counters()
    start_time = time.time()

    while not stop_flag.is_set():
        elapsed = time.time() - start_time
        # 1-second sample
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_now = psutil.disk_io_counters()
        net_now = psutil.net_io_counters()

        disk_read = disk_now.read_bytes - disk_initial.read_bytes
        disk_write = disk_now.write_bytes - disk_initial.write_bytes
        net_sent = net_now.bytes_sent - net_initial.bytes_sent
        net_recv = net_now.bytes_recv - net_initial.bytes_recv

        entry = {
            "time": elapsed,
            "cpu": cpu_percent,
            "memory": memory_percent,
            "disk_read_bytes": disk_read,
            "disk_write_bytes": disk_write,
            "net_bytes_sent": net_sent,
            "net_bytes_recv": net_recv
        }
        results.append(entry)

    logging.info("Metrics monitoring thread stopped.")

def run_hyperv_test():
    """
    Führt einen kompletten Test für eine Hyper-V-VM durch, analog zu VirtualBox/Workstation:
    1) Start VM
    2) Start Monitoring Thread
    3) Run CPU/Memory/Disk workloads in Guest
    4) Stop Monitoring
    5) Save results
    6) Stop VM
    """
    vm_name = "Kerem"  # Your Hyper-V VM name

    try:
        # 1) Start VM
        start_hyperv_vm(vm_name)
        time.sleep(60)  # Warte, bis die VM vollständig hochgefahren ist

        # 2) Start Monitoring
        logging.info("Starte Performance-Monitoring für Hyper-V.")
        print("Starte Performance-Monitoring für Hyper-V.")
        results = []
        stop_flag = threading.Event()
        monitor_thread = threading.Thread(target=monitor_metrics_continuous, args=(results, stop_flag))
        monitor_thread.start()

        # 3) Run the workloads (cpu, memory, disk stress) sequentially
        run_workloads(vm_name)

        # 4) Stop Monitoring
        logging.info("Stoppe Performance-Monitoring.")
        print("Stoppe Performance-Monitoring.")
        stop_flag.set()
        monitor_thread.join()  # warten, bis Thread beendet ist

        # 5) Save results
        # We assume 'save_hyperv_results' can handle a list of dictionaries:
        # [
        #   {"time":..., "cpu":..., "memory":..., "disk_read_bytes":..., "disk_write_bytes":..., "net_bytes_sent":..., "net_bytes_recv":...},
        #   ...
        # ]
        from file_handler import save_hyperv_results
        save_hyperv_results(results)

        # 6) Stop VM
        stop_hyperv_vm(vm_name)

        logging.info("Hyper-V-Test abgeschlossen.")
        print("Hyper-V-Test abgeschlossen.")

    except Exception as e:
        logging.error(f"Fehler während des Hyper-V-Tests: {e}")
        print(f"Fehler während des Hyper-V-Tests: {e}")
