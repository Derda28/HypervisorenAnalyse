import psutil

def get_cpu_usage():
    """Erfasst die CPU-Auslastung in Prozent."""
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    """Erfasst die Speicherauslastung in Prozent."""
    return psutil.virtual_memory().percent

def get_disk_usage():
    """Erfasst die Festplattenauslastung in Prozent."""
    return psutil.disk_usage('/').percent
