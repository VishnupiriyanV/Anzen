import subprocess
import json
import os
import sys

def semgrep_analyze(directory_path, output_file, config_rules):
    """
    Analyzes a directory using Semgrep with a specific ruleset and saves the results.
    This corrected version runs Semgrep once per directory, which is much more efficient.
    """
    print(f"Analyzing directory '{directory_path}' with ruleset '{config_rules}'...")

    # Semgrep can scan a directory directly. No need to walk the file tree in Python.
    command = [
        "semgrep",
        "scan",
        "--config", config_rules,
        "--json",          # Output results in JSON format
        directory_path     # The target directory to scan
    ]

    try:
        # Execute the Semgrep command once for the entire directory.
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False  # Don't raise an exception on non-zero exit codes
        )

        # Semgrep exit codes: 0 = no findings, 1 = findings found, >1 = error
        if result.returncode > 1:
            print(f"An error occurred while scanning '{directory_path}'. See details below.", file=sys.stderr)
            print(f"Return Code: {result.returncode}", file=sys.stderr)
            print(f"Stderr:\n{result.stderr}", file=sys.stderr)
            return # Stop processing this config if an error occurs

        # Load the JSON output to count issues and ensure it's valid.
        try:
            scan_results = json.loads(result.stdout)
        except json.JSONDecodeError:
            print("Error: Semgrep did not return valid JSON.", file=sys.stderr)
            print(f"Raw output:\n{result.stdout}", file=sys.stderr)
            return
            
        # Write the complete JSON output to the file.
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scan_results, f, indent=4)
        
        # Count the number of issues found from the results.
        issue_count = len(scan_results.get('results', []))
        print(f"Analysis complete. Found a total of {issue_count} issues.")
        print(f"Full report saved to '{output_file}'.")

    except FileNotFoundError:
        print("\nError: 'semgrep' command not found.", file=sys.stderr)
        print("Please ensure Semgrep is installed and available in your system's PATH.", file=sys.stderr)
        sys.exit(1) # Exit the script if Semgrep isn't installed.
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


def main():
    """
    Main function to orchestrate the Semgrep analysis workflow.
    """
    target_directory = "test"
    output_directory = "result"

    # A list of Semgrep registry configurations to use for scanning.
    semgrep_configs = [
        "p/cwe-top-25",
        "p/r2c-security-audit",
        "p/owasp-top-ten",
        "p/secure-defaults"
    ]

    # Ensure the target and output directories exist.
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(target_directory, exist_ok=True)
    
    # --- Main analysis loop ---
    for config in semgrep_configs:
        # Sanitize the config name for a clean filename (e.g., 'p/owasp-top-ten' -> 'owasp-top-ten')
        sanitized_config_name = config.split('/')[-1]
        output_filename = os.path.join(output_directory, f"{sanitized_config_name}_results.json")
        
        print("-" * 50)
        print(f"Running analysis for ruleset: {config}")
        semgrep_analyze(target_directory, output_filename, config)

    print("-" * 50)
    print("\n✅ All Semgrep analyses are complete.")


if __name__ == "__main__":
    main()