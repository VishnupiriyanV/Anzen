import os
import shutil
import sys
from git import Repo
import subprocess
import json
import argparse
import stat # Added for file permissions

# Paths
cloned_dir = "./cloned"
filtered_dir = "./clonedf"
output_file = "semgrep_results.json"

# Define the error handler for shutil.rmtree
def handle_remove_readonly(func, path, exc_info):
    """
    Error handler for shutil.rmtree.
    If the error is due to a read-only file, it attempts to change
    the file's permissions and re-run the function.
    """
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        try:
            func(path)
        except Exception as e:
            print(f"Error re-attempting remove on '{path}': {e}")
            raise # Re-raise if changing permissions didn't help
    else:
        raise # Re-raise original exception if not a permission issue

def get_args():
    parser = argparse.ArgumentParser(description="Clones a Git repository and runs a Semgrep scan.")
    parser.add_argument("--repo_url", required=True, help="URL of the Git repository to scan.")
    return parser.parse_args()

def main():
    # Parse command-line arguments using argparse
    args = get_args()
    repo_url = args.repo_url # <--- THIS IS THE KEY CHANGE

    print(f"Starting scan for repository: {repo_url}")

    # Clean up from previous runs with error handling
    for path in [cloned_dir, filtered_dir, output_file]:
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path, onerror=handle_remove_readonly)
                    print(f"Cleaned up existing directory: {path}")
                else:
                    os.remove(path)
                    print(f"Cleaned up existing file: {path}")
            except Exception as e:
                print(f"Warning: Error during initial cleanup of '{path}' in main-git.py: {e}")
                # Do not exit, try to proceed with cloning if cleanup failed.
                # The primary cleanup is still handled by app.py's finally block.

    # Clone into local directory
    try:
        Repo.clone_from(repo_url, cloned_dir)
        print(f"Successfully cloned {repo_url} into {cloned_dir}")
    except Exception as e:
        print(f"Error cloning repository {repo_url}: {e}")
        sys.exit(1) # Exit if cloning fails, as subsequent steps depend on it

    # Extensions to keep
    extensions = {
        ".cs", ".go", ".java", ".js", ".kt", ".kts", ".py", ".ts", ".c", ".cpp",
        ".cc", ".cxx", ".h", ".hpp", ".hh", ".hxx", ".jsx", ".rb", ".scala",
        ".swift", ".rs", ".php", ".tf", ".tfvars", ".hcl", ".generic", ".json",
        ".ex", ".exs", ".cls", ".trigger", ".dart"
    }

    # Create target directory
    os.makedirs(filtered_dir, exist_ok=True)
    print(f"Created filtered directory: {filtered_dir}")

    # Move matching files
    files_moved = 0
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
                files_moved += 1
    print(f"Moved {files_moved} relevant files to {filtered_dir}")

    # Run Semgrep
    cmd = ["semgrep", "--config", "auto", filtered_dir, "--json"]
    print(f"Running Semgrep command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Save JSON output
        with open(output_file, "w") as f:
            json.dump(json.loads(result.stdout), f, indent=2)
        print(f"Scan complete. Results saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Semgrep scan failed with error (Return Code: {e.returncode}):")
        print(f"Semgrep Stdout: {e.stdout}")
        print(f"Semgrep Stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'semgrep' command not found. Please ensure Semgrep is installed and in your PATH.")
        print("You can usually install it with: pip install semgrep")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding Semgrep JSON output: {e}")
        print(f"Semgrep raw stdout: {result.stdout}")
        print(f"Semgrep raw stderr: {result.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    main()
