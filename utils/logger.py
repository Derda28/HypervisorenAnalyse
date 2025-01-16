import logging
import os

def setup_logger(log_file):
    """
    Initialisiert den Logger für das angegebene Log-File.
    :param log_file: Pfad zur Log-Datei.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger()
