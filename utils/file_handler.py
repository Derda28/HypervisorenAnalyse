import os

def save_results(file_path, data, headers=None):
    """
    Speichert Ergebnisse in einer Datei.
    :param file_path: Pfad zur Datei.
    :param data: Liste von Zeilen, die gespeichert werden.
    :param headers: Optionale Kopfzeilen.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as file:
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
    with open(file_path, "r") as file:
        lines = file.readlines()
    return [line.strip().split(",") for line in lines]
