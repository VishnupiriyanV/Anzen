import subprocess

def run_command(cmd):
    subprocess.call(cmd, shell=True) # CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
