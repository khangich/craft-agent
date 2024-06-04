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
        self.GITHUB_API_TOKEN = os.getenv('GITHUB_API_TOKEN')
        self.REPO = os.getenv('REPO')

    def validate(self):
        if not all([self.USERNAME, self.GITHUB_API_TOKEN, self.REPO]):
            raise ValueError("One or more environment variables are missing. Please ensure USERNAME, GITHUB_API_TOKEN, and REPO are set.")


auth = Auth.Token(Config().GITHUB_API_TOKEN)
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
    return 234

def get_filechanges_and_comment():
    repo = g.get_repo(f"{Config().REPO}")
    pr = repo.get_pull(get_recent_pull_request())
    # print("body = ", pr.body)
    # print("comments = ", pr.comments)
    # print("change files ", pr.changed_files)
    # print("diff_url ", pr.diff_url)
    content = _get_diff_content(pr.diff_url)
    return pr.comments, content

def pr_prompt(comment: str, content: str):
    prompt = f"You're a Code generation assistant, you have this review comment: '{comment}' for your PR changes: '{content}'. Please suggest 2 actions to address the comment."
    return prompt

get_filechanges_and_comment()

