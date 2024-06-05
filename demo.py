from typing import Literal

from pydantic import BaseModel, Field
from typing_extensions import Annotated

import autogen
from autogen.cache import Cache
import autogen
import os
from githubtools import get_filechanges_and_comment

llm_config = {
    "config_list": [{"model": "gpt-4", "api_key": os.environ["OPENAI_API_KEY"]}],
}


github_agent = autogen.AssistantAgent(
    name="github_agent",
    llm_config=llm_config,
    code_execution_config=False,
)
github_agent.register_for_llm(
    name="get_filechanges_and_comment",
    description="Get latest PR changes and comments. You are also a code asisstant, you can suggest code changes."
)(get_filechanges_and_comment)


# writer = autogen.AssistantAgent(
#     name="writer",
#     llm_config=llm_config,
#     system_message="""
#         You are a professional writer, known for
#         your insightful and engaging articles.
#         You transform complex concepts into compelling narratives.
#         Reply "TERMINATE" in the end when everything is done.
#         """,
# )

user = autogen.UserProxyAgent(
    name="User",
    human_input_mode="ALWAYS",  # ask human for input at each step
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
)
user.register_for_execution(name="get_filechanges_and_comment")(get_filechanges_and_comment)

chat_results = user.initiate_chats(
    [
        {
            "recipient": github_agent,
            "message": "What are the latest comments on my pull request",
            "clear_history": True,
            "silent": False,
            "summary_method": "reflection_with_llm",
        },
        # {
        #     "recipient": writer,
        #     "message": "",
        # },
    ]
)
print("success")