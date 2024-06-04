import autogen
import os
from githubtools import get_filechanges_and_comment

llm_config = {
    "config_list": [{"model": "gpt-3.5-turbo", "api_key": os.environ["OPENAI_API_KEY"]}],
}

def is_termination_msg(msg):
    return msg["content"] == "STOP!!!"

pr_update_github_agent = autogen.ConversableAgent(
    "github_agent",
    system_message="""You are Code generation assistant that helps user to read pull request comments. 
    You will select the right tool and handle the ask from the user?""",
    llm_config=llm_config,
    is_termination_msg=is_termination_msg,
    human_input_mode="TERMINATE"
)

human_proxy = autogen.ConversableAgent(
    "human_proxy",
    human_input_mode="ALWAYS",  # Never ask for human input.
)

# The user proxy agent is used for interacting with the assistant agent
# and executes tool calls.
user_proxy = autogen.ConversableAgent(
    name="User",
    is_termination_msg=lambda msg: msg.get("content") and "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
)

github_agent = autogen.ConversableAgent(
    "github_agent",
    system_message="You are the expert in github cli. When client asks about github cli, gives them useful information on how to use it?",
    llm_config=llm_config,
    is_termination_msg=is_termination_msg,
    human_input_mode="TERMINATE"
)

def get_unread_messages() -> list[str]:
    print('Executing get_unread_messages')
    return [
        "Hey team, just a reminder about the meeting at 3 PM today. See you there!",
        "Does anyone have the link to the latest project report? Thanks!",
        "Great job on the presentation yesterday! The client was really impressed.",
        "I'll be working remotely today. Please reach out on Slack if you need anything.",
        "Can someone review my PR? I need another set of eyes before merging.",
        "Happy Friday, everyone! 🎉 Any fun plans for the weekend?",
        "Heads up: The server will be down for maintenance tonight from 10 PM to 12 AM.",
        "Just a quick update: We've reached 80% of our monthly target. Keep up the good work!",
        "I'm stuck on a bug and could use some help. Anyone available for a quick call?",
        "Don't forget to submit your timesheets by the end of the day.",
        "Lunch is on me today! Any suggestions for where we should order from?",
        "The new feature deployment is scheduled for tomorrow. Please test your modules.",
        "Can we reschedule our 1:1 meeting? Something urgent came up.",
        "Congratulations to [Name] on their promotion to Senior Developer! 🎉",
        "Please review the updated project timeline and provide your feedback by EOD.",
        "We need volunteers for the upcoming hackathon. Who's interested?",
        "I'm looking for recommendations for a good book on project management. Any suggestions?",
        "Our next team-building activity is a virtual escape room. Hope to see you all there!",
        "Quick question: What's the best way to handle API rate limiting in our current setup?",
        "Thanks to everyone for your hard work this quarter. Let's keep the momentum going!"
    ]

# slack_agent = autogen.ConversableAgent(
#     "slack_agent",
#     system_message="You are helpful assistant that helps user to read slack messages. You will select the right tool and handle the ask from the user?",
#     llm_config=llm_config,
#     is_termination_msg=is_termination_msg,
#     human_input_mode="TERMINATE"
# )
# slack_agent.register_for_llm(
#     name="get_unread_messages",
#     description="Get unread message from slack from the current registered user"
# )(get_unread_messages)


github_agent = autogen.ConversableAgent(
    "github_agent",
    system_message="""You are Code generation assistant that helps user to read pull request comments. 
    You will select the right tool and handle the ask from the user?""",
    llm_config=llm_config,
    is_termination_msg=is_termination_msg,
    human_input_mode="TERMINATE"
)
github_agent.register_for_llm(
    name="get_filechanges_and_comment",
    description="Get latest PR changes and comments"
)(get_filechanges_and_comment)


def execute_github_pr_agent(comment: str) -> str:
    print(github_agent.last_message)
    return human_proxy.send(
        pr_update_github_agent,
        message="""You're a Code generation assistant, you have this review comment: '{github_agent.last_message.get("content")}' for your PR changes. 
       Please suggest 2 actions to address the comment."""
    )


github_agent.register_for_llm(
    name="execute_github_pr_agent",
    description="make the code changes to address PR comments"
)(execute_github_pr_agent)



human_proxy.register_for_execution(name="get_filechanges_and_comment")(get_filechanges_and_comment)


human_proxy.register_for_execution(name="execute_github_pr_agent")(execute_github_pr_agent)

human_proxy.initiate_chat(
    github_agent,
    message="What is new with my PR changes?"
)

