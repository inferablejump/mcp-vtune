# A wrapper to run vtune

import subprocess
import json
import xmltodict
import tempfile

ONEAPI_PATH = "C:\\Program Files (x86)\\Intel\\oneAPI\\setvars.bat" 

def run_with_oneapi_env(command, timeout=60):
    """Run a command with OneAPI environment sourced"""
    # Combine setvars.bat with the actual command in the same shell
    # capture the output of the command but not sourcing the environment
    full_command = f'"{ONEAPI_PATH}" && {command}'
    
    try:
        result = subprocess.run(
            full_command, 
            shell=True, 
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise
    except subprocess.TimeoutExpired as e:
        print(f"Command timed out after {timeout} seconds")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise

def vtune_report(report_dir: str):
    run_with_oneapi_env(f"vtune -report summary -result-dir {report_dir} -format xml -report-output {report_dir}\\summary.xml")
    raw_xml_report = open(f"{report_dir}\\summary.xml", "r").read()
    # convert xml to dict
    xml_dict = xmltodict.parse(raw_xml_report)
    # convert dict to json
    return json.dumps(xml_dict)

def run_hotspot_analysis(executable: str):
    """Run vtune hotspot analysis and return the report
    
    Args:
        executable: the executable to analyze

    Returns:
        The report in JSON format
    """
    tmp_output_dir = tempfile.mkdtemp()
    run_with_oneapi_env(f"vtune -collect hotspot -result-dir {tmp_output_dir} {executable}")
    print(tmp_output_dir)
    # return ("finished collecting")
    return vtune_report(tmp_output_dir)

# def run_memory_analysis(executable: str, output_dir: str):
#     source_oneapi()
#     subprocess.run(["vtune", "-collect", "memory-access", "-result-dir", output_dir, executable], shell=True)
#     return vtune_report(output_dir)

EXE = "C:\\Users\\ianss\\Desktop\\MyBinarySearch\\x64\\Debug\\MyBinarySearch.exe"
if __name__ == "__main__":
    # print("---")
    print(run_hotspot_analysis(EXE))
    # print(run_memory_analysis(EXE, "memory_report"))
