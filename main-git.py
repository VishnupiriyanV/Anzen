import os
import sys
import shutil
from git import Repo
import subprocess
import json

def main():
    # Get repository URL from command line argument
    if len(sys.argv) != 2:
        print("Usage: python main-git.py <repository_url>")
        sys.exit(1)
    
    repo_url = sys.argv[1]
    
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

    try:
        # Clone into local directory
        print(f"Cloning repository: {repo_url}")
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
        file_count = 0
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
                    file_count += 1

        print(f"Filtered {file_count} source code files")

        # Remove original cloned repo
        shutil.rmtree(cloned_dir)

        # Run Semgrep
        print("Running Semgrep scan...")
        cmd = ["semgrep", "--config", "auto", filtered_dir, "--json", "--quiet"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Save JSON output
        with open(output_file, "w") as f:
            json.dump(json.loads(result.stdout), f, indent=2)
            
        print(f"Scan complete. Results saved to {output_file}")
        
        # Clean up filtered directory
        shutil.rmtree(filtered_dir)
        
    except Exception as e:
        print(f"Error during scanning: {str(e)}")
        # Clean up on error
        for path in [cloned_dir, filtered_dir]:
            if os.path.exists(path):
                shutil.rmtree(path)
        sys.exit(1)

if __name__ == "__main__":
    main()