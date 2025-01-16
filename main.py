import tkinter as tk
from tkinter import messagebox
import threading
from visualization.plot_results import show_results

# Importiere die Automatisierungsskripte
from scripts.esxi import run_esxi_test
from scripts.hyperv import run_hyperv_test
from scripts.virtualbox import run_virtualbox_test
from scripts.workstation import run_workstation_test

# GUI erstellen
app = tk.Tk()
app.title("Hypervisor Automatisierung")

tk.Button(app, text="VMWare ESXi", command=lambda: threading.Thread(target=run_esxi_test).start()).pack(pady=10)
tk.Button(app, text="Microsoft Hyper-V", command=lambda: threading.Thread(target=run_hyperv_test).start()).pack(pady=10)
tk.Button(app, text="VirtualBox", command=lambda: threading.Thread(target=run_virtualbox_test).start()).pack(pady=10)
tk.Button(app, text="VMWare Workstation", command=lambda: threading.Thread(target=run_workstation_test).start()).pack(pady=10)
tk.Button(app, text="Ergebnisse anzeigen", command=show_results).pack(pady=20)

app.mainloop()