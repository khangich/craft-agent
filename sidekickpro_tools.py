from github import Github
from github.InputGitTreeElement import InputGitTreeElement
import base64
import os
# Replace 'your_access_token' with your actual GitHub access token
import os
from autogen import ConversableAgent
from typing import Annotated, Literal
from github import Auth
from github import Github
from github import GithubIntegration
import requests

class Config:
    def __init__(self):
        self.USERNAME = os.getenv('USERNAME')
        self.API_TOKEN = os.getenv('API_TOKEN')
        self.REPO = os.getenv('REPO')

    def validate(self):
        if not all([self.USERNAME, self.API_TOKEN, self.REPO]):
            raise ValueError("One or more environment variables are missing. Please ensure USERNAME, API_TOKEN, and REPO are set.")


auth = Auth.Token(Config().API_TOKEN)
g = Github(auth=auth)
if not g.get_user().login:
    print("not login")

def _get_diff_content(diff_url):
    response = requests.get(diff_url)
    if response.status_code == 200:
        return response.text
    else:
        return None
    
def get_recent_pull_request():
    return 9

def get_pull_request_comment():
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {Config().API_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    url = f"https://api.github.com/repos/{Config().REPO}/pulls/{get_recent_pull_request()}/comments"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(response)
        return None

def get_filechanges_and_comment() -> str:
    repo = g.get_repo(f"{Config().REPO}")
    pr = repo.get_pull(get_recent_pull_request())
    # print("body = ", pr.body)
    # print("comments = ", pr.comments)
    # print("change files ", pr.changed_files)
    # print("diff_url ", pr.diff_url)
    content = _get_diff_content(pr.diff_url)
    comments = get_pull_request_comment()
    comments = " ".join([c["body"] for c in comments])
    # print(">>> pr.comments = ", comments)
    # comments = "do not exit(1), please print success message at the end"
    return f"{comments} : {content}"


def apply_file_changes(pr_number: int, file_path: str, content: str, commit_message: str) -> bool:
    g = Github(os.environ["API_TOKEN"])
    repo = g.get_repo(f"{Config().REPO}")
    # Get the pull request
    pull_request = repo.get_pull(pr_number)
    # Get the branch name from the pull request
    branch_name = pull_request.head.ref
    # Get the latest commit on the branch
    latest_commit = repo.get_branch(branch_name).commit
    # Create a new blob (file) in the repository
    # file_path = 'readme_new.txt'
    # content = 'This is the new content for the file'
    content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    blob = repo.create_git_blob(content_encoded, 'base64')
    # Create a tree element
    tree_element = InputGitTreeElement(path=file_path, mode='100644', type='blob', sha=blob.sha)
    # Create a new tree
    base_tree = repo.get_git_tree(sha=latest_commit.sha)
    new_tree = repo.create_git_tree([tree_element], base_tree)
    new_commit = repo.create_git_commit(commit_message, new_tree, [latest_commit.commit])
    # Update the reference to point to the new commit
    ref = repo.get_git_ref(f"heads/{branch_name}")
    ref.edit(new_commit.sha)

    print(f"Commit created and added to PR #{pr_number}")
    return True