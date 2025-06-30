import platform
import psutil
import subprocess
import json

def get_host_info() -> str:
    """get host information

    Returns:
        str: the host information in JSON string
    """
    info: dict[str, str] = {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "memory_gb": str(round(psutil.virtual_memory().total / (1024**3), 2)),
    }

    cpu_count = psutil.cpu_count(logical=True)
    if cpu_count is None:
        info["cpu_count"] = "-1"
    else:
        info["cpu_count"] = str(cpu_count)
    
    try:
        cpu_model = subprocess.check_output(
            ["wmic", "cpu", "get", "name", "/value"], 
            shell=True
        ).decode().strip()
        
        # Parse the output - wmic returns "Name=Intel Core i7-..." format
        for line in cpu_model.split('\n'):
            if line.startswith('Name='):
                info["cpu_model"] = line.split('=', 1)[1].strip()
                break
        else:
            info["cpu_model"] = "Unknown"
    except Exception:
        info["cpu_model"] = "Unknown"

    return json.dumps(info, indent=4)

if __name__ == '__main__':
    print(get_host_info())