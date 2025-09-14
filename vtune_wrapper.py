# A wrapper to run vtune

import subprocess
import json
import xmltodict
import tempfile
import os
import sys
ONEAPI_PATH = "C:\\Program Files (x86)\\Intel\\oneAPI\\setvars.bat" 

def run_with_oneapi_env(command, timeout=60):
    """Run a command with OneAPI environment sourced"""
    # Use os.system with a temporary batch file to avoid quote issues
    import tempfile
    
    # Create a temporary batch file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as f:
        f.write(f'@echo off\n')
        f.write(f'call "{ONEAPI_PATH}"\n')
        f.write(f'{command}\n')
        batch_file = f.name
    
    try:
        # Run the batch file
        result = subprocess.run(
            [batch_file],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        # print(f"Command failed: {e}", file=sys.stderr)
        # print(f"stdout: {e.stdout}", file=sys.stderr)
        # print(f"stderr: {e.stderr}", file=sys.stderr)
        raise
    except subprocess.TimeoutExpired as e:
        # print(f"Command timed out after {timeout} seconds", file=sys.stderr)
        # print(f"stdout: {e.stdout}", file=sys.stderr)
        # print(f"stderr: {e.stderr}", file=sys.stderr)
        raise
    finally:
        # Clean up the temporary batch file
        try:
            os.unlink(batch_file)
        except:
            pass

def vtune_report(report_dir: str):
    # Generate the XML report
    # print(f"Generating report from directory: {report_dir}", file=sys.stderr)
    try:
        output = run_with_oneapi_env(f"vtune -report summary -result-dir {report_dir} -format xml -report-output {report_dir}\\summary.xml")
        # print(f"vtune report command output: {output}", file=sys.stderr)
    except Exception as e:
        pass
        # print(f"vtune report command failed: {e}", file=sys.stderr)
    
    # Check if the XML report was created successfully
    summary_xml_path = f"{report_dir}\\summary.xml"
    # print(f"Looking for XML report at: {summary_xml_path}", file=sys.stderr)
    # print(f"File exists: {os.path.exists(summary_xml_path)}", file=sys.stderr)
    
    if not os.path.exists(summary_xml_path):
        # print("XML report not found, creating fallback...", file=sys.stderr)
        # If vtune failed to create the report, create an empty XML structure
        empty_xml = '<?xml version="1.0" encoding="UTF-8"?><report><summary><message>No data available</message></summary></report>'
        with open(summary_xml_path, "w") as f:
            f.write(empty_xml)
    
    # Read and parse the XML report
    with open(summary_xml_path, "r") as f:
        raw_xml_report = f.read()
    
    # print(f"XML report content length: {len(raw_xml_report)}", file=sys.stderr)
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
    # print(f"Starting hotspot analysis for: {executable}", file=sys.stderr)
    # print(f"Output directory: {tmp_output_dir}", file=sys.stderr)
    
    try:
        output = run_with_oneapi_env(f"vtune -collect hotspot -result-dir {tmp_output_dir} {executable}", timeout=120)
        # print(f"vtune collect command output: {output}", file=sys.stderr)
    except Exception as e:
        # print(f"vtune collect command failed: {e}", file=sys.stderr)
        pass
    
    # print(tmp_output_dir, file=sys.stderr)
    # return ("finished collecting")
    return vtune_report(tmp_output_dir)

def test_vtune_installation():
    """Test if vtune is properly installed and accessible"""
    try:
        output = run_with_oneapi_env("vtune --version", timeout=10)
        print(f"vtune version: {output}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"vtune not accessible: {e}", file=sys.stderr)
        return False

EXE = "C:\\Users\\ianss\\Desktop\\MyBinarySearch\\x64\\Debug\\MyBinarySearch.exe"
if __name__ == "__main__":
    print("Testing vtune installation...", file=sys.stderr)
    if test_vtune_installation():
        print("vtune is accessible, running analysis...", file=sys.stderr)
        print(run_hotspot_analysis(EXE), file=sys.stderr)
    else:
        print("vtune is not accessible. Please check your Intel oneAPI installation.", file=sys.stderr)
    # print(run_memory_analysis(EXE, "memory_report"))
