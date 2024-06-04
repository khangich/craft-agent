
class GithubTools:
    def __init__(self, author):
        self.author = author

    def read_recent_pull_request(self):
        import requests
        url = f"https://api.github.com/repos/{self.author}/pulls"
        response = requests.get(url)
        if response.status_code == 200:
            pull_requests = response.json()
            if pull_requests:
                recent_pull_request = pull_requests[0]
                return recent_pull_request
            else:
                print("No recent pull requests found for this author.")
                return None
        else:
            print("Failed to fetch pull requests.")
            return None
        
    def get_pr_file_changes(self, username, repo, pr):
        import requests
        response = requests.get(f"https://api.github.com/repos/{username}/{repo}/pulls/{pr}/files")
        if response.status_code == 200:
            files_changed = response.json()
            pr_files = [elem['filename'] for elem in files_changed]
            return pr_files
        else:
            print("Failed to fetch file changes.")
            return None
        
    def get_pr_comments(self, username, repo, pr):
        import requests
        headers = {"Accept": "application/vnd.github-commitcomment.text+json"}
        response = requests.get(f"https://api.github.com/repos/{username}/{repo}/pulls/{pr}/comments", headers=headers)
        if response.status_code == 200:
            comments = response.json()
            return comments
        else:
            print("Failed to fetch comments.")
            return None

    def pull_all_diff(self):
        # Code to pull all the diff from the recent PR
        pass

    def send_prompt_to_openai(self, file_changes_content):
        # Code to send a prompt to OpenAI with the context as the file changes content
        pass


# ght = GithubTools("princeton-nlp")
# # f = ght.get_pr_file_changes("princeton-nlp", "SWE-agent", 497)
# # print(f)

# # f = ght.get_pr_file_changes("princeton-nlp", "SWE-agent", 234)
# f = ght.get_pr_comments("princeton-nlp", "SWE-agent", 234)
# print(f)


import os

from autogen import ConversableAgent


from typing import Annotated, Literal

Operator = Literal["+", "-", "*", "/"]


def calculator(a: int, b: int, operator: Annotated[Operator, "operator"]) -> int:
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        return int(a / b)
    else:
        raise ValueError("Invalid operator")
    

# Let's first define the assistant agent that suggests tool calls.
assistant = ConversableAgent(
    name="Assistant",
    system_message="You are a helpful AI assistant. "
    "You can help with simple calculations. "
    "Return 'TERMINATE' when the task is done.",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": os.environ["OPENAI_API_KEY"]}]},
)

# The user proxy agent is used for interacting with the assistant agent
# and executes tool calls.
user_proxy = ConversableAgent(
    name="User",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
)

# Register the tool signature with the assistant agent.
assistant.register_for_llm(name="calculator", description="A simple calculator")(calculator)

# Register the tool function with the user proxy agent.
user_proxy.register_for_execution(name="calculator")(calculator)

chat_result = user_proxy.initiate_chat(assistant, message="What is (44232 + 13312 / (232 - 32)) * 5?")


# print("Keys in the dictionary:")
# for d in dict0:
#     for key in d.keys():
#         print(key)




# pr_files = [elem['filename'] for elem in dict0]
# print(pr_files)