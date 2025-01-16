import os
import matplotlib.pyplot as plt
from tkinter import messagebox


def load_results(file_path):
    """
    Läd Ergebnisse aus einer CSV-Datei.
    :param file_path: Pfad zur CSV-Datei.
    :return: Liste von (CPU, Memory) Werten.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Datei {file_path} wurde nicht gefunden.")

    results = []
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines[1:]:  # Überspringe die Kopfzeile
            cpu, memory = map(float, line.strip().split(","))
            results.append((cpu, memory))
    return results


def plot_results():
    """
    Lädt die Ergebnisse von allen Hypervisoren und zeigt sie in Diagrammen.
    """
    files = {
        "VMware ESXi": "data/esxi_results.csv",
        "Microsoft Hyper-V": "data/hyperv_results.csv",
        "VirtualBox": "data/virtualbox_results.csv",
        "VMware Workstation": "data/workstation_results.csv",
    }

    for hypervisor, file_path in files.items():
        try:
            results = load_results(file_path)
            cpu_usage = [res[0] for res in results]
            memory_usage = [res[1] for res in results]

            # Erstelle das Diagramm
            plt.figure(figsize=(10, 5))
            plt.plot(cpu_usage, label="CPU-Auslastung (%)", linestyle='-', marker='o')
            plt.plot(memory_usage, label="Speicherauslastung (%)", linestyle='--', marker='x')
            plt.title(f"Performance-Metriken: {hypervisor}")
            plt.xlabel("Zeit (in Sekunden)")
            plt.ylabel("Auslastung (%)")
            plt.legend()
            plt.grid(True)

            # Speichere das Diagramm
            output_file = f"visualizations/graphs/{hypervisor.replace(' ', '_').lower()}_graph.png"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            plt.savefig(output_file)
            plt.show()

        except FileNotFoundError:
            messagebox.showerror("Fehler", f"Ergebnisse für {hypervisor} wurden nicht gefunden.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {e}")


def show_results():
    """
    Öffnet ein Popup-Fenster, um die Ergebnisse der Visualisierung anzuzeigen.
    """
    try:
        plot_results()
    except Exception as e:
        messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {e}")
