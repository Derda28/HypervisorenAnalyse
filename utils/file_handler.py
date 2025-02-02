import os

RESULTS_PATH = {
    "virtualbox": "data/virtualbox_results.csv",
    "vmware": "data/vmware_results.csv",
    "hyperv": "data/hyperv_results.csv",
    "esxi": "data/esxi_results.csv"
}

def save_virtualbox_results(results):
    """
    Speichert die Performance-Daten (als Liste von Dictionary-Einträgen)
    in die CSV-Datei 'data/virtualbox_results.csv'.
    """
    # Define the columns we expect, in the order we want them
    headers = ["time","cpu","memory","disk_read_bytes","disk_write_bytes","net_bytes_sent","net_bytes_recv"]
    
    # Convert each dictionary to a list in that order
    data_as_lists = []
    for entry in results:
        # If any key is missing, default to 0 or some fallback
        row = [
            entry.get("time", 0),
            entry.get("cpu", 0),
            entry.get("memory", 0),
            entry.get("disk_read_bytes", 0),
            entry.get("disk_write_bytes", 0),
            entry.get("net_bytes_sent", 0),
            entry.get("net_bytes_recv", 0)
        ]
        data_as_lists.append(row)
    
    # Now call the generic 'save_results' function
    save_results(RESULTS_PATH["virtualbox"], data_as_lists, headers=headers)


def save_vmware_results(results):
    """
    Nimmt eine Liste von Dictionaries wie:
    [
      {"time": 0.0, "cpu": 1.2, "memory": 42.5, ...},
      ...
    ]
    und speichert sie in data/vmware_results.csv
    """
    headers = ["time","cpu","memory","disk_read_bytes","disk_write_bytes","net_bytes_sent","net_bytes_recv"]

    data_as_lists = []
    for entry in results:
        row = [
            entry.get("time", 0),
            entry.get("cpu", 0),
            entry.get("memory", 0),
            entry.get("disk_read_bytes", 0),
            entry.get("disk_write_bytes", 0),
            entry.get("net_bytes_sent", 0),
            entry.get("net_bytes_recv", 0)
        ]
        data_as_lists.append(row)

    save_results(RESULTS_PATH["vmware"], data_as_lists, headers=headers)


def save_hyperv_results(results):
    headers = ["time","cpu","memory","disk_read_bytes","disk_write_bytes","net_bytes_sent","net_bytes_recv"]
    data_as_lists = []
    for r in results:
        row = [
            r.get("time",0),
            r.get("cpu",0),
            r.get("memory",0),
            r.get("disk_read_bytes",0),
            r.get("disk_write_bytes",0),
            r.get("net_bytes_sent",0),
            r.get("net_bytes_recv",0)
        ]
        data_as_lists.append(row)
    save_results(RESULTS_PATH["hyperv"], data_as_lists, headers=headers)


def save_esxi_results(data, headers=None):
    save_results(RESULTS_PATH["esxi"], data, headers)

def save_results(file_path, data, headers=None):
    """
    Speichert Ergebnisse in einer Datei.
    :param file_path: Pfad zur Datei.
    :param data: Liste von Listen (jeder Eintrag eine Zeile).
    :param headers: Kopfzeilen (Liste von Strings).
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        if headers:
            file.write(",".join(headers) + "\n")
        for row in data:
            file.write(",".join(map(str, row)) + "\n")

def load_results(file_path):
    """
    Lädt Ergebnisse aus einer Datei.
    :param file_path: Pfad zur Datei.
    :return: Liste von Zeilen als Listen.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Datei {file_path} wurde nicht gefunden.")
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    return [line.strip().split(",") for line in lines]
