import subprocess
import time
import psutil
import logging

logging.basicConfig(filename="logs/workstation_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

def run_workstation_test():
    try:
        logging.info("Workstation-Test gestartet")
        print("VMware Workstation wird gestartet...")
        # Simuliere das Öffnen und Starten der VM
        subprocess.run(["vmrun", "-T", "ws", "start", "C:\\Users\\Derda\\Documents\\Virtual Machines\\Windows 11 x64 (3)\\Windows 11 x64 (3).vmx"], check=True)
        print("Analyse gestartet.")
        logging.info("Analyse gestartet.")

        # Sammle Hardware-Metriken
        results = []
        start_time = time.time()
        while time.time() - start_time < 10:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            results.append((cpu, memory))
        
        print("Analyse beendet.")
        logging.info("Analyse beendet.")

        # Stoppe die VM
        subprocess.run(["vmrun", "-T", "ws", "stop", "C:\\Users\\Derda\\Documents\\Virtual Machines\\Windows 11 x64 (3)\\Windows 11 x64 (3).vmx"], check=True)

        # Ergebnisse speichern
        with open("data/workstation_results.csv", "w") as file:
            file.write("CPU_Usage,Memory_Usage\n")
            file.writelines([f"{cpu},{mem}\n" for cpu, mem in results])
        logging.info("Ergebnisse gespeichert.")
    
    except Exception as e:
        logging.error(f"Fehler während des Workstation-Tests: {e}")
