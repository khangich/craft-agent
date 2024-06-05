from github import Github
from github.InputGitTreeElement import InputGitTreeElement
import base64
import os
# Replace 'your_access_token' with your actual GitHub access token
access_token = 'your_access_token'

# Authenticate with GitHub
g = Github(os.environ["API_TOKEN"])

# Replace 'your_repo_owner' and 'your_repo_name' with the actual repository owner and name
repo_owner = "khangich"
repo_name = 'craft-agent'

# Replace 'pr_number' with the actual pull request number
pr_number = 5

# Get the repository
repo = g.get_repo(f"{repo_owner}/{repo_name}")

# Get the pull request
pull_request = repo.get_pull(pr_number)

# Get the branch name from the pull request
branch_name = pull_request.head.ref

# Get the latest commit on the branch
latest_commit = repo.get_branch(branch_name).commit

# Create a new blob (file) in the repository
file_path = 'readme_new.txt'
content = 'This is the new content for the file'
content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
blob = repo.create_git_blob(content_encoded, 'base64')

# Create a tree element
tree_element = InputGitTreeElement(path=file_path, mode='100644', type='blob', sha=blob.sha)

# Create a new tree
base_tree = repo.get_git_tree(sha=latest_commit.sha)
new_tree = repo.create_git_tree([tree_element], base_tree)

# Create a new commit
commit_message = 'Your commit message'
new_commit = repo.create_git_commit(commit_message, new_tree, [latest_commit.commit])

# Update the reference to point to the new commit
ref = repo.get_git_ref(f"heads/{branch_name}")
ref.edit(new_commit.sha)

print(f"Commit created and added to PR #{pr_number}")