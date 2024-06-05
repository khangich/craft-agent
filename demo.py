import autogen
import os
from sidekickpro_tools import get_filechanges_and_comment

llm_config = {
    "config_list": [{"model": "gpt-4", "api_key": os.environ["OPENAI_API_KEY"]}],
}


def is_termination_msg(msg):
    content = msg.get("content", "")

    return content and content.find("TERMINATE") >= 0


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

user = autogen.UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    code_execution_config=False,
    is_termination_msg=is_termination_msg,
)
user.register_for_execution(name="get_filechanges_and_comment")(get_filechanges_and_comment)

print(">>>> Starting demo")

chat_results = user.initiate_chats(
    [
        {
            "recipient": github_agent,
            "message": "What are the latest comments on my pull request",
            "clear_history": True,
            "silent": False,
            "summary_method": "reflection_with_llm",
        },
    ]
)

import pprint
import pdb
# pdb.set_trace()
# pprint.pprint(chat_results)
x = chat_results[-1].chat_history[-1]['content']
with open('file.patch', 'w') as f:
    f.write(x)
print(">>>> Success. Hello")
exit(1)
