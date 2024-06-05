import autogen
import os
from sidekickpro_tools import apply_file_changes, get_filechanges_and_comment

# config_list = [{"model": "llama3-70b-8192", "api_key": os.environ["GROQ_API_KEY"], "base_url": "https://api.groq.com/openai/v1"}]
config_list = [{"model": "gpt-4", "api_key": os.environ["OPENAI_API_KEY"], "temperature": 0}]
llm_config = {
    "config_list": config_list,
}

AGENT_ROUTING_PROMPT = """You are managing a group chat with the following agents: {agentlist}.
Each agent has a specific role:
- user: Handles human input. When you finish the task, returns to this role.
- replier_agent: Responds to the user by converting outputs from other agents or functions into friendly, human-readable messages. It may be selected to respond to the output of other agents if the response is not clear.
- slack_agent: Handles Slack-related questions. For example, to retrieve messages or interact with Slack-specific functions.
- github_agent: Handles GitHub-related questions. For example, to manage pull requests, issues, and other GitHub interactions.

Based on the context of the current conversation and the roles of the agents, determine the most appropriate agent to handle the next message. Only return the role of the selected agent."""

GITHUB_AGENT_PROMPT = """
You are a GitHub agent. Your task is to review the comments and diffs on a specified pull request (PR) and generate a GitHub patch based on the feedback provided. Follow these steps meticulously:

1. Read Comments: Review all comments on the PR to understand the requested changes and feedback.
2. Analyze DiffExamine the diffs to comprehend the changes made in the PR and identify areas that need modification based on the comments.
3. Generate PatchCreate a patch file that includes the necessary changes to address the feedback in the comments and any code improvements identified from the diff analysis.

Requirements:
- Ensure the patch follows the repository's coding standards.
- Address all issues mentioned in the comments.
- Optimize code where necessary for performance and readability.

Output Format:
- Provide the patch in a .patch file format.
- Only generate the patch file and nothing else. Do not include summaries, explanations, or any additional text.
- Add TERMINATE string at the end.

Example Patch Format:
diff –git a/diff_test.txt b/diff_test.txt
index 6b0c6cf..b37e70a 100644
— a/diff_test.txt
+++ b/diff_test.txt
@@ -1 +1 @@
-this is a git diff test example
+this is a diff example

Follow the instructions carefully and ensure the patch file is generated correctly based on the provided guidelines.
"""


def is_termination_msg(msg):
    content = msg.get("content", "")

    return content and content.find("TERMINATE") >= 0


replier_agent = autogen.AssistantAgent(
    name="replier_agent",
    llm_config=llm_config,
    max_consecutive_auto_reply=2,
    is_termination_msg=is_termination_msg,
    system_message="You are a helpful AI assistant designed to handle outputs from other functions effectively. Your task is to convert the output messages to a friendly human message",
)
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
    agents=[user_proxy, replier_agent, github_agent],
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

x = chat_results[-1].chat_history[-1]['content']
print(x)
with open('file.patch', 'w') as f:
    f.write(x)

# pr_number = int(os.getenv('PR_NUMBER'))
# import subprocess
# # Define the command to apply the patch
# command = ["git", "apply", "file.patch"]
# # Execute the command
# process = subprocess.Popen(command, stdout=subprocess.PIPE)
# output, error = process.communicate()
# if error:
#     print(f"Error occurred while applying patch: {error}")
# else:
#     print("Patch applied successfully.")
#     print("Patch applied successfully. output = ", output, " error = ", error)


# # Add the changes
# command = ["git", "add", "."]
# process = subprocess.Popen(command, stdout=subprocess.PIPE)
# output, error = process.communicate()
# if error:
#     print(f"Error occurred while adding changes: {error}")
# else:
#     print("Changes added successfully.")

# command = ["git", "commit", '-am "address comment"']
# # Execute the command
# process = subprocess.Popen(command, stdout=subprocess.PIPE)
# output, error = process.communicate()
# if error:
#     print(f"Error occurred while commit: {error}")
# else:
#     print("commit applied successfully. output = ", output, " error = ", error)

# BRANCH_NAME = os.getenv('BRANCH_NAME')
# print(f"branch name {BRANCH_NAME}")
# command = ["git", "push", f"origin {BRANCH_NAME}"]
# # Execute the command
# process = subprocess.Popen(command, stdout=subprocess.PIPE)
# output, error = process.communicate()
# if error:
#     print(f"Error occurred while push: {error}")
# else:
#     print("push applied successfully. output = ", output, " error = ", error)

# apply_file_changes(pr_number, file_path: str, content: str, commit_message: str)
print(">>>> Success. Helo")print("a")
