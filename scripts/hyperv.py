import subprocess
import time
import psutil
import logging

logging.basicConfig(filename="logs/hyperv_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

def run_hyperv_test():
    try:
        logging.info("Hyper-V-Test gestartet")
        print("Microsoft Hyper-V wird gestartet...")
        # Starte eine VM mit Powershell
        subprocess.run(["powershell", "Start-VM -Name 'TestVM'"], check=True)
        print("Analyse gestartet.")
        logging.info("Analyse gestartet.")

        # Sammle Hardware-Metriken
        results = []
        start_time = time.time()
        while time.time() - start_time < 1500:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            results.append((cpu, memory))
        
        print("Analyse beendet.")
        logging.info("Analyse beendet.")

        # Stoppe die VM
        subprocess.run(["powershell", "Stop-VM -Name 'TestVM'"], check=True)

        # Ergebnisse speichern
        with open("data/hyperv_results.csv", "w") as file:
            file.write("CPU_Usage,Memory_Usage\n")
            file.writelines([f"{cpu},{mem}\n" for cpu, mem in results])
        logging.info("Ergebnisse gespeichert.")
    
    except Exception as e:
        logging.error(f"Fehler während des Hyper-V-Tests: {e}")
