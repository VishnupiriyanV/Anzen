from git import Repo

# Clone into local directory
repo_url = input()
repo = Repo.clone_from(repo_url, "./test")