import os
import shutil
from git import Repo

# Clone into local directory
repo_url = input("Enter repo URL: ")
repo = Repo.clone_from(repo_url, "./cloned")

extensions = {
    ".cs", ".go", ".java", ".js", ".kt", ".kts", ".py", ".ts", ".c", ".cpp",
    ".cc", ".cxx", ".h", ".hpp", ".hh", ".hxx", ".jsx", ".rb", ".scala",
    ".swift", ".rs", ".php", ".tf", ".tfvars", ".hcl", ".generic", ".json",
    ".ex", ".exs", ".cls", ".trigger", ".dart"
}

# Create target directory
target_dir = os.path.abspath("./clonedf")
os.makedirs(target_dir, exist_ok=True)

# Walk the cloned repo
for root, dirs, files in os.walk("./cloned"):
    for file in files:
        _, ext = os.path.splitext(file)  # Gets extension ('' if no ext)
        if ext.lower() in extensions:
            src_path = os.path.join(root, file)
            dst_path = os.path.join(target_dir, file)

            # Ensure unique filename if duplicate
            base, extension = os.path.splitext(file)
            counter = 1
            while os.path.exists(dst_path):
                dst_path = os.path.join(target_dir, f"{base}_{counter}{extension}")
                counter += 1

            shutil.move(src_path, dst_path)

# Remove original cloned repo
shutil.rmtree(os.path.abspath("./cloned"))