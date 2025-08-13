import subprocess
import json
import os

def semgrep_analyze(directory_path, output_file, config_rules):
    
    print(f"analyzing files in '{directory_path}' with ruleset '{config_rules}'...")
    
    
    aggregated_results = {"results": [],"errors": [],"paths": {"_comment": f"Aggregated scan report for directory '{directory_path}'"}}
    
    files_to_scan = []
    for root, _, files in os.walk(directory_path):
        if any(part.startswith('.') for part in root.split(os.sep)):
            continue
        for file in files:
            files_to_scan.append(os.path.join(root, file))

    if not files_to_scan:
        print(f"No files found in '{directory_path}'. Skipping analysis for '{config_rules}'.")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(aggregated_results, f, indent=4)
        return

    is_first_scan = True

    for file_path in files_to_scan:
        print(f"  -> Scanning {file_path}...")
        command = ["semgrep", "scan", "--config", config_rules, "--json", file_path]
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')

            if result.returncode > 1:
                print(f"An error occurred while scanning '{file_path}'.")
                print(f"Return Code: {result.returncode}")
                print(f"Stderr:\n{result.stderr}")

            if not result.stdout.strip():
                continue

            current_output = json.loads(result.stdout)
            
            if is_first_scan:
                for key, value in current_output.items():
                    if key not in ["results", "errors", "paths"]:
                        aggregated_results[key] = value
                is_first_scan = False

            aggregated_results["results"].extend(current_output.get("results", []))
            aggregated_results["errors"].extend(current_output.get("errors", []))
            
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(aggregated_results, f, indent=4)
        
    issue_count = len(aggregated_results.get('results', []))
    print(f"\nAnalysis for '{config_rules}' complete. Found a total of {issue_count} issues across all files.")
    print(f"Aggregated results saved to '{output_file}'.")


target_directory = "test" 
output_directory = "result"

semgrep_configs = [
    "p/cwe-top-25",
    "p/r2c-security-audit",
    "p/owasp-top-ten",
    "p/secure-defaults"
]

os.makedirs(output_directory, exist_ok=True)
os.makedirs(target_directory, exist_ok=True)



for config in semgrep_configs:
    sanitized_config_name = config.replace('p/', '').replace('/', '_')
    
    output_filename = os.path.join(output_directory, f"{sanitized_config_name}_results.json")
    
    print(f"\nRunning analysis for: {config}")
    semgrep_analyze(target_directory, output_filename, config)
    print("-" * 50)

print("\nAll Semgrep analyses are complete.")


