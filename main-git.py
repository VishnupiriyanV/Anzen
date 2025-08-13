import os
import shutil
from git import Repo

# Clone into local directory
repo_url = input()
repo = Repo.clone_from(repo_url, "./test")

extensions = [".cs", ".go", ".java", ".js", ".kt", 
".kts", ".py", ".ts", ".c", ".cpp", ".cc", 
".cxx", ".h", ".hpp", ".hh", ".hxx", ".jsx", 
".rb", ".scala", ".swift", ".rs", ".php", 
".tf", ".tfvars", ".hcl", ".generic", 
".json", ".ex", ".exs", ".cls", ".trigger", ".dart"]

# Create testf dir
os.makedir("./testf")

# Traversing the cloned directory
for root, dirs, files in os.walk("."):
     for file in files:
      name, ext = file.splitext(".")
      if "." + ext in extensions:
         path = os.path.abspath(file)
         shutil.move(path, )
