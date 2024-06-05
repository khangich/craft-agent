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
    return 1


def get_pull_request_comment():
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {Config().API_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    url = f"https://api.github.com/repos/{Config().REPO}/pulls/{get_recent_pull_request()}/comments"
    print(">>> url = ", url)
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

get_filechanges_and_comment()

