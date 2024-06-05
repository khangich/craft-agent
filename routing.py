import os

import autogen

llm_config = {
    "config_list": [{"model": "gpt-3.5-turbo", "api_key": os.environ["OPENAI_API_KEY"]}],
}

AGENT_ROUTING_PROMPT = """You are managing a group chat with the following agents: {agentlist}.
Each agent has a specific role:
- user: Handles human input. When you finish the task, returns to this role.
- replier_agent: Responds to the user by converting outputs from other agents or functions into friendly, human-readable messages. It may be selected to respond to the output of other agents if the response is not clear.
- slack_agent: Handles Slack-related questions. For example, to retrieve messages or interact with Slack-specific functions.
- github_agent: Handles GitHub-related questions. For example, to manage pull requests, issues, and other GitHub interactions.

Based on the context of the current conversation and the roles of the agents, determine the most appropriate agent to handle the next message. Only return the role of the selected agent."""


def is_termination_msg(msg):
    return msg.get("content", "").find("TERMINATE") >= 0


def get_unread_messages() -> list[str]:
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
        "Congratulations to Tim on their promotion to Senior Developer! 🎉",
        "Please review the updated project timeline and provide your feedback by EOD.",
        "We need volunteers for the upcoming hackathon. Who's interested?",
        "I'm looking for recommendations for a good book on project management. Any suggestions?",
        "Our next team-building activity is a virtual escape room. Hope to see you all there!",
        "Quick question: What's the best way to handle API rate limiting in our current setup?",
        "Thanks to everyone for your hard work this quarter. Let's keep the momentum going!"
    ]


user_proxy = autogen.UserProxyAgent(
    name="user",
    system_message="Human admin",
    human_input_mode="ALWAYS",
    is_termination_msg=is_termination_msg,
    code_execution_config=False,
)
replier_agent = autogen.AssistantAgent(
    name="replier_agent",
    llm_config=llm_config,
    is_termination_msg=is_termination_msg,
    system_message="You are a helpful AI assistant designed to handle outputs from other functions effectively. Your task is to convert the output messages to a friendly human message",
)
slack_agent = autogen.AssistantAgent(
    "slack_agent",
    system_message="You are helpful slack assistant that helps user select the right tools to solve their problems",
    llm_config=llm_config,
    code_execution_config={
        "use_docker": False,
    },
)
autogen.agentchat.register_function(
    get_unread_messages,
    caller=slack_agent,
    executor=slack_agent,
    name="get_unread_messages",
    description="Get unread messages from slack from the current registered user"
)
github_agent = autogen.AssistantAgent(
    "github_agent",
    system_message="You are the helpful github assistant that helps user to solve their problems",
    llm_config=llm_config,
)
group_chat = autogen.GroupChat(
    agents=[user_proxy, replier_agent, github_agent, slack_agent],
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

user_proxy.initiate_chat(
    manager,
    message="what is the latest messages from Slack",
    max_turns=100
)
