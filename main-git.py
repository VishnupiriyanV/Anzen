import os
import shutil
from git import Repo
import subprocess, json

# Paths
cloned_dir = "./cloned"
filtered_dir = "./clonedf"
output_file = "semgrep_results.json"

# Clean up from previous runs
for path in [cloned_dir, filtered_dir, output_file]:
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

# Clone into local directory
repo_url = input("Enter repo URL: ").strip()
Repo.clone_from(repo_url, cloned_dir)

# Extensions to keep
extensions = {
    ".cs", ".go", ".java", ".js", ".kt", ".kts", ".py", ".ts", ".c", ".cpp",
    ".cc", ".cxx", ".h", ".hpp", ".hh", ".hxx", ".jsx", ".rb", ".scala",
    ".swift", ".rs", ".php", ".tf", ".tfvars", ".hcl", ".generic", ".json",
    ".ex", ".exs", ".cls", ".trigger", ".dart"
}

# Create target directory
os.makedirs(filtered_dir, exist_ok=True)

# Move matching files
for root, _, files in os.walk(cloned_dir):
    for file in files:
        _, ext = os.path.splitext(file)
        if ext.lower() in extensions:
            src_path = os.path.join(root, file)
            dst_path = os.path.join(filtered_dir, file)

            # Handle duplicate names
            base, extension = os.path.splitext(file)
            counter = 1
            while os.path.exists(dst_path):
                dst_path = os.path.join(filtered_dir, f"{base}_{counter}{extension}")
                counter += 1

            shutil.move(src_path, dst_path)

# Remove original cloned repo
shutil.rmtree(cloned_dir)

# Run Semgrep
cmd = ["semgrep", "--config", "auto", filtered_dir, "--json"]
result = subprocess.run(cmd, capture_output=True, text=True, check=True)

# Save JSON output
with open(output_file, "w") as f:
    json.dump(json.loads(result.stdout), f, indent=2)

print(f"Scan complete. Results saved to {output_file}")