import autogen
import os
import re

from sidekickpro_tools import apply_file_changes, get_filechanges_and_comment

config_list = [{"model": "llama3-70b-8192", "api_key": os.environ["GROQ_API_KEY"], "base_url": "https://api.groq.com/openai/v1"}]
# config_list = [{"model": "gpt-4", "api_key": os.environ["OPENAI_API_KEY"]}]
llm_config = {
    "config_list": config_list,
}

AGENT_ROUTING_PROMPT = """You are managing a group chat with the following agents: {agentlist}.
Each agent has a specific role:
- user: Handles human input. When you finish the task, returns to this role.
- github_agent: Handle github related task. It can generate batch based on the comments and diffs of other tool.

Based on the context of the current conversation and the roles of the agents, determine the most appropriate agent to handle the next message. Only return the role of the selected agent."""

GITHUB_AGENT_PROMPT = """
You are a GitHub agent. Your task is to review the comments and diffs on a specified pull request (PR) and generate a GitHub patch based on the feedback provided. Follow these steps meticulously:

1. Read Comments: Review all comments on the PR to understand the requested changes and feedback.
2. Analyze DiffExamine the diffs to comprehend the changes made and identify areas that need modification based on the feedback comments.
3. Generate PatchCreate a patch file that includes the necessary changes to ONLY address the feedback in the comments.

Requirements:
- Ensure the patch follows the repository's coding standards.
- Address all issues mentioned in the comments.
- Follow the instructions carefully and ensure the patch file is generated correctly based on the provided guidelines.

Output Format:
- Provide the patch in a .patch file format.
- Only generate the patch file and nothing else. Do not include summaries, explanations, or any additional text.
- Add a TERMINATE string at the end.

Example Patch Format:
diff –git a/diff_test.txt b/diff_test.txt
index 6b0c6cf..b37e70a 100644
— a/diff_test.txt
+++ b/diff_test.txt
@@ -1 +1 @@
-this is a git diff test example
+this is a diff example
"""


def is_termination_msg(msg):
    content = msg.get("content", "")

    return content and content.rstrip().endswith("TERMINATE")


github_agent = autogen.AssistantAgent(
    name="github_agent",
    system_message=GITHUB_AGENT_PROMPT,
    llm_config=llm_config,
    code_execution_config={
        "use_docker": False,
    },
)
github_agent.register_for_llm(
    name="get_filechanges_and_comment",
    description="Get latest PR changes and comments."
)(get_filechanges_and_comment)

user_proxy = autogen.UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    code_execution_config=False,
    is_termination_msg=is_termination_msg,
)
user_proxy.register_for_execution(name="get_filechanges_and_comment")(get_filechanges_and_comment)

group_chat = autogen.GroupChat(
    agents=[user_proxy, github_agent],
    messages=[],
    speaker_selection_method="auto",
    select_speaker_prompt_template=AGENT_ROUTING_PROMPT,
)
manager = autogen.GroupChatManager(
    name="manager",
    groupchat=group_chat,
    llm_config=llm_config,
    is_termination_msg=is_termination_msg,
)

print(">>>> Starting demo")

chat_results = user_proxy.initiate_chats(
    [
        {
            "recipient": manager,
            "message": "Get the latest comment in my pull request and apply the feedback based on the comment.",
            "clear_history": True,
            "silent": False,
            "summary_method": "reflection_with_llm",
        },
    ]
)

last_message = chat_results[-1].chat_history[-1]['content']
last_message = re.sub(r'TERMINATE\n?$', '', last_message)

pr_number = int(os.getenv('PR_NUMBER'))

BRANCH_NAME = os.getenv('BRANCH_NAME')
import subprocess



# Pull the latest changes from the remote repository
# command = ["git", "pull", "origin", BRANCH_NAME]
# process = subprocess.Popen(command, stdout=subprocess.PIPE)
# output, error = process.communicate()
# if error:
#     print(f"Error occurred while pulling: {error}")
# else:
#     print("Pull successful.")
# command = ["git", "checkout", f"origin/{BRANCH_NAME}"]
# process = subprocess.Popen(command, stdout=subprocess.PIPE)
# output, error = process.communicate()
# if error:
#     print(f"Error occurred while pulling: {error}")
# else:
#     print("Checkout branch successful.")


x = last_message
print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
print(x)
with open('file.patch', 'w') as f:
    f.write(last_message)



# Define the command to apply the patch
# command = ["git", "apply", "file.patch"]
command = "patch -p1 < file.patch"
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, error = process.communicate()
if error:
    print(f"Error occurred while applying patch: {error.decode()}")
else:
    print("Patch applied successfully.")


command = ["git", "commit", '-am " ^_^ ^_^ SidekickPro address comment"']
# Execute the command
process = subprocess.Popen(command, stdout=subprocess.PIPE)
output, error = process.communicate()
if error:
    print(f"Error occurred while commit: {error}")
else:
    print("commit applied successfully.")



command = ["git", "push", "origin", f"{BRANCH_NAME}"]
# Execute the command
process = subprocess.Popen(command, stdout=subprocess.PIPE)
output, error = process.communicate()
if error:
    print(f"Error occurred while push: {error}")
else:
    print("Push applied successfully.")

# apply_file_changes(pr_number, file_path: str, content: str, commit_message: str)
print(">>>> Success. hel0o")
exit(0)
