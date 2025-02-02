import os
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

def load_results(file_path):
    """
    Lädt Ergebnisse aus einer CSV-Datei mit 7 Spalten:
      time, cpu, memory, disk_read_bytes, disk_write_bytes, net_bytes_sent, net_bytes_recv
    Gibt eine Liste von Dictionaries zurück:
      [
        {
          "time": <float>,
          "cpu": <float>,
          "memory": <float>,
          "disk_read_bytes": <float>,
          "disk_write_bytes": <float>,
          "net_bytes_sent": <float>,
          "net_bytes_recv": <float>
        },
        ...
      ]
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Datei {file_path} wurde nicht gefunden.")
    
    results = []
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        # Erste Zeile ist Header => überspringen
        for line in lines[1:]:
            row = line.strip().split(",")
            # Erwarten genau 7 Spalten
            if len(row) != 7:
                continue
            # Skip repeated header lines
            if (row[0].lower() == "time" or
                row[1].lower() == "cpu" or
                row[2].lower() == "memory"):
                continue
            try:
                entry = {
                    "time": float(row[0]),
                    "cpu": float(row[1]),
                    "memory": float(row[2]),
                    "disk_read_bytes": float(row[3]),
                    "disk_write_bytes": float(row[4]),
                    "net_bytes_sent": float(row[5]),
                    "net_bytes_recv": float(row[6])
                }
                results.append(entry)
            except ValueError:
                # Falls ein Feld kein Float ist => skip
                continue
    
    if not results:
        raise ValueError("Keine gültigen Daten gefunden oder nur Headerzeilen vorhanden.")
    
    return results

def set_dynamic_ylim(ax, max_val, factor=1.2, minimum=10):
    """
    Legt die Y-Grenze von 0 bis entweder (factor * max_val) oder 'minimum',
    je nachdem was größer ist. Dadurch wird die y-Achse höher,
    auch wenn die Daten sehr kleine Werte haben.
    """
    top = max(minimum, max_val * factor)
    ax.set_ylim(0, top)

def prepare_slide(hypervisor, csv_file):
    """
    Erstellt 3 Subplots für:
      1) CPU und Memory (Min/Max/Avg)
      2) Disk read/write (Min/Max/Avg)
      3) Net bytes sent/recv (Min/Max/Avg)
    Zeigt Marker + Annotation für Min/Max-Werte, eine gestrichelte Linie
    für den Durchschnitt, und vergrößert die Y-Achse via set_dynamic_ylim.
    """
    try:
        full_results = load_results(csv_file)
        if not full_results:
            raise ValueError("Keine gültigen Daten oder nur Headerzeilen vorhanden.")
        
        # Downsample: keep every 20th data point
        results = full_results[::100]
        
        times = [r["time"] for r in results]
        cpu_usage = [r["cpu"] for r in results]
        mem_usage = [r["memory"] for r in results]
        disk_read = [r["disk_read_bytes"] for r in results]
        disk_write = [r["disk_write_bytes"] for r in results]
        net_sent = [r["net_bytes_sent"] for r in results]
        net_recv = [r["net_bytes_recv"] for r in results]

        fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10, 8), sharex=True)

        # ------------------ 1) CPU + Memory ------------------
        axes[0].plot(times, cpu_usage, label="CPU (%)", marker='o', color='blue')
        axes[0].plot(times, mem_usage, label="Memory (%)", marker='x', color='orange')

        # CPU stats
        cpu_min = min(cpu_usage)
        cpu_max = max(cpu_usage)
        cpu_avg = sum(cpu_usage) / len(cpu_usage)
        idx_cpu_min = cpu_usage.index(cpu_min)
        idx_cpu_max = cpu_usage.index(cpu_max)

        axes[0].scatter(times[idx_cpu_min], cpu_min, color='blue', marker='v', s=100, zorder=5, label="CPU Min")
        axes[0].scatter(times[idx_cpu_max], cpu_max, color='blue', marker='^', s=100, zorder=5, label="CPU Max")
        axes[0].annotate(f"{cpu_min:.2f}", (times[idx_cpu_min], cpu_min),
                         xytext=(0, -15), textcoords="offset points",
                         ha='center', color='blue')
        axes[0].annotate(f"{cpu_max:.2f}", (times[idx_cpu_max], cpu_max),
                         xytext=(0, 10), textcoords="offset points",
                         ha='center', color='blue')
        axes[0].axhline(cpu_avg, color='blue', linestyle=':', label="CPU Avg")

        # Memory stats
        mem_min = min(mem_usage)
        mem_max = max(mem_usage)
        mem_avg = sum(mem_usage) / len(mem_usage)
        idx_mem_min = mem_usage.index(mem_min)
        idx_mem_max = mem_usage.index(mem_max)

        axes[0].scatter(times[idx_mem_min], mem_min, color='orange', marker='v', s=100, zorder=5, label="Mem Min")
        axes[0].scatter(times[idx_mem_max], mem_max, color='orange', marker='^', s=100, zorder=5, label="Mem Max")
        axes[0].annotate(f"{mem_min:.2f}", (times[idx_mem_min], mem_min),
                         xytext=(0, -15), textcoords="offset points",
                         ha='center', color='orange')
        axes[0].annotate(f"{mem_max:.2f}", (times[idx_mem_max], mem_max),
                         xytext=(0, 10), textcoords="offset points",
                         ha='center', color='orange')
        axes[0].axhline(mem_avg, color='orange', linestyle=':', label="Mem Avg")

        # Extend y-axis
        y_max_cpu_mem = max(cpu_max, mem_max)
        set_dynamic_ylim(axes[0], y_max_cpu_mem)  # ensures at least 10 or 1.2*x

        axes[0].set_ylabel("CPU/Mem (%)")
        axes[0].legend()
        axes[0].grid(True)

        # ------------------ 2) Disk read/write ------------------
        axes[1].plot(times, disk_read, label="Disk Read Bytes", marker='o', color='green')
        axes[1].plot(times, disk_write, label="Disk Write Bytes", marker='x', color='red')

        # Disk read stats
        dr_min = min(disk_read)
        dr_max = max(disk_read)
        dr_avg = sum(disk_read) / len(disk_read)
        idx_dr_min = disk_read.index(dr_min)
        idx_dr_max = disk_read.index(dr_max)

        axes[1].scatter(times[idx_dr_min], dr_min, color='green', marker='v', s=100, zorder=5, label="Read Min")
        axes[1].scatter(times[idx_dr_max], dr_max, color='green', marker='^', s=100, zorder=5, label="Read Max")
        axes[1].annotate(f"{dr_min:.2f}", (times[idx_dr_min], dr_min),
                         xytext=(0, -15), textcoords="offset points",
                         ha='center', color='green')
        axes[1].annotate(f"{dr_max:.2f}", (times[idx_dr_max], dr_max),
                         xytext=(0, 10), textcoords="offset points",
                         ha='center', color='green')
        axes[1].axhline(dr_avg, color='green', linestyle=':', label="Read Avg")

        # Disk write stats
        dw_min = min(disk_write)
        dw_max = max(disk_write)
        dw_avg = sum(disk_write) / len(disk_write)
        idx_dw_min = disk_write.index(dw_min)
        idx_dw_max = disk_write.index(dw_max)

        axes[1].scatter(times[idx_dw_min], dw_min, color='red', marker='v', s=100, zorder=5, label="Write Min")
        axes[1].scatter(times[idx_dw_max], dw_max, color='red', marker='^', s=100, zorder=5, label="Write Max")
        axes[1].annotate(f"{dw_min:.2f}", (times[idx_dw_min], dw_min),
                         xytext=(0, -15), textcoords="offset points",
                         ha='center', color='red')
        axes[1].annotate(f"{dw_max:.2f}", (times[idx_dw_max], dw_max),
                         xytext=(0, 10), textcoords="offset points",
                         ha='center', color='red')
        axes[1].axhline(dw_avg, color='red', linestyle=':', label="Write Avg")

        y_max_disk = max(dr_max, dw_max)
        set_dynamic_ylim(axes[1], y_max_disk)

        axes[1].set_ylabel("Disk Bytes")
        axes[1].legend()
        axes[1].grid(True)

        # ------------------ 3) Net bytes sent/recv --------------
        axes[2].plot(times, net_sent, label="Net Bytes Sent", marker='o', color='purple')
        axes[2].plot(times, net_recv, label="Net Bytes Recv", marker='x', color='brown')

        # Net sent stats
        ns_min = min(net_sent)
        ns_max = max(net_sent)
        ns_avg = sum(net_sent) / len(net_sent)
        idx_ns_min = net_sent.index(ns_min)
        idx_ns_max = net_sent.index(ns_max)

        axes[2].scatter(times[idx_ns_min], ns_min, color='purple', marker='v', s=100, zorder=5, label="Sent Min")
        axes[2].scatter(times[idx_ns_max], ns_max, color='purple', marker='^', s=100, zorder=5, label="Sent Max")
        axes[2].annotate(f"{ns_min:.2f}", (times[idx_ns_min], ns_min),
                         xytext=(0, -15), textcoords="offset points",
                         ha='center', color='purple')
        axes[2].annotate(f"{ns_max:.2f}", (times[idx_ns_max], ns_max),
                         xytext=(0, 10), textcoords="offset points",
                         ha='center', color='purple')
        axes[2].axhline(ns_avg, color='purple', linestyle=':', label="Sent Avg")

        # Net recv stats
        nr_min = min(net_recv)
        nr_max = max(net_recv)
        nr_avg = sum(net_recv) / len(net_recv)
        idx_nr_min = net_recv.index(nr_min)
        idx_nr_max = net_recv.index(nr_max)

        axes[2].scatter(times[idx_nr_min], nr_min, color='brown', marker='v', s=100, zorder=5, label="Recv Min")
        axes[2].scatter(times[idx_nr_max], nr_max, color='brown', marker='^', s=100, zorder=5, label="Recv Max")
        axes[2].annotate(f"{nr_min:.2f}", (times[idx_nr_min], nr_min),
                         xytext=(0, -15), textcoords="offset points",
                         ha='center', color='brown')
        axes[2].annotate(f"{nr_max:.2f}", (times[idx_nr_max], nr_max),
                         xytext=(0, 10), textcoords="offset points",
                         ha='center', color='brown')
        axes[2].axhline(nr_avg, color='brown', linestyle=':', label="Recv Avg")

        y_max_net = max(ns_max, nr_max)
        set_dynamic_ylim(axes[2], y_max_net)

        axes[2].set_ylabel("Net Bytes")
        axes[2].set_xlabel("Zeit (Sek.)")
        axes[2].legend()
        axes[2].grid(True)

        fig.suptitle(f"Performance-Metriken: {hypervisor}")

        # Speichern
        output_file = f"visualizations/graphs/{hypervisor.replace(' ', '_').lower()}_graph.png"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        fig.savefig(output_file)
        plt.close(fig)
        
        # Bild laden
        image = Image.open(output_file)
        photo = ImageTk.PhotoImage(image)
        slide = {"hypervisor": hypervisor, "type": "image", "content": photo}
        return slide

    except Exception as e:
        slide = {"hypervisor": hypervisor, "type": "text",
                 "content": f"Fehler für {hypervisor}:\n{str(e)}"}
        return slide

def show_results():
    """
    Öffnet ein neues Fenster, in dem die Ergebnisse als Slideshow angezeigt werden.
    """
    files = {
        "VMware ESXi": "data/esxi_results.csv",
        "Microsoft Hyper-V": "data/hyperv_results.csv",
        "VirtualBox": "data/virtualbox_results.csv",
        "vmware": "data/vmware_results.csv",
    }
    
    slides = []
    for hypervisor, csv_file in files.items():
        slide = prepare_slide(hypervisor, csv_file)
        slides.append(slide)
    
    if not slides:
        messagebox.showinfo("Ergebnisse", "Keine Ergebnisse verfügbar.")
        return

    slideshow_window = tk.Toplevel()
    slideshow_window.title("Ergebnisse - Slideshow")
    
    current_slide = [0]
    
    hypervisor_label = tk.Label(slideshow_window, text="", font=("Helvetica", 16))
    hypervisor_label.pack(pady=10)
    
    content_frame = tk.Frame(slideshow_window)
    content_frame.pack()
    
    content_label = tk.Label(content_frame)
    content_label.pack()
    
    nav_frame = tk.Frame(slideshow_window)
    nav_frame.pack(pady=10)
    
    def update_slide(index):
        slide = slides[index]
        hypervisor_label.config(text=slide["hypervisor"])
        if slide["type"] == "image":
            content_label.config(image=slide["content"], text="")
            content_label.image = slide["content"]
        else:
            content_label.config(text=slide["content"], image="")
    
    def prev_slide():
        if current_slide[0] > 0:
            current_slide[0] -= 1
            update_slide(current_slide[0])
    
    def next_slide():
        if current_slide[0] < len(slides) - 1:
            current_slide[0] += 1
            update_slide(current_slide[0])
    
    tk.Button(nav_frame, text="Vorherige", command=prev_slide).pack(side=tk.LEFT, padx=5)
    tk.Button(nav_frame, text="Nächste", command=next_slide).pack(side=tk.LEFT, padx=5)
    
    # Zeige erstes Slide
    update_slide(current_slide[0])
