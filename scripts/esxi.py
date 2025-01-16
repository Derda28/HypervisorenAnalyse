import time
import psutil  # Beispiel für Hardware-Metriken
import logging

# Logging einrichten
logging.basicConfig(filename="logs/esxi_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

def run_esxi_test():
    try:
        logging.info("ESXi-Test gestartet")
        print("VMware ESXi wird gestartet...")
        # Simuliere das Öffnen und Starten der VM
        time.sleep(1)  # Ersetze durch echte API-Aufrufe, z.B., um eine VM zu starten
        print("Analyse gestartet.")
        logging.info("Analyse gestartet.")

        # Sammle Hardware-Metriken
        results = []
        start_time = time.time()
        while time.time() - start_time < 1500:  # 25 Minuten
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            results.append((cpu, memory))
        
        print("Analyse beendet.")
        logging.info("Analyse beendet.")
        
        # Ergebnisse speichern
        with open("data/esxi_results.csv", "w") as file:
            file.write("CPU_Usage,Memory_Usage\n")
            file.writelines([f"{cpu},{mem}\n" for cpu, mem in results])
        logging.info("Ergebnisse gespeichert.")
    
    except Exception as e:
        logging.error(f"Fehler während des ESXi-Tests: {e}")
