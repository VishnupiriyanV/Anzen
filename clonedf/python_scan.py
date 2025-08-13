#Works only for Python
import subprocess
import os

input_file = "vuln_scanners/test_program.py"

output_file = "bandit_report.csv"

def run_bandit(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"E]error: File not Found")
        return

    command = ["bandit", "-r", input_file, "-o", output_file, "-f", "csv"]

    try:
        res = subprocess.run(command, capture_output=True, text=True)
        print(res.stdout)
        
    except FileNotFoundError:
        print("error: 'bandit' command not found.")
    except subprocess.CalledProcessError as e:
        print(f"error during bandit analysis: {e}")
        print(e.stderr)

run_bandit(input_file, output_file)
