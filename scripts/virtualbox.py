import subprocess
import time
import psutil
import logging

logging.basicConfig(filename="logs/virtualbox_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

def run_virtualbox_test():
    try:
        logging.info("VirtualBox-Test gestartet")
        print("VirtualBox wird gestartet...")
        # Starte eine VM mit VBoxManage
        subprocess.run(["VBoxManage", "startvm", "Windows11", "--type", "headless"], check=True)
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
        subprocess.run(["VBoxManage", "controlvm", "Windows11", "poweroff"], check=True)

        # Ergebnisse speichern
        with open("data/virtualbox_results.csv", "w") as file:
            file.write("CPU_Usage,Memory_Usage\n")
            file.writelines([f"{cpu},{mem}\n" for cpu, mem in results])
        logging.info("Ergebnisse gespeichert.")
    
    except Exception as e:
        logging.error(f"Fehler während des VirtualBox-Tests: {e}")
