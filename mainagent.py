# Inserting code for coordinator agent using Microsoft Autogen library

from autogen_coordinator import CoordinatorAgent
from autogen_agents import GithubAgent, SlackAgent

def main():
    coordinator_agent = CoordinatorAgent()
    github_agent = GithubAgent()
    slack_agent = SlackAgent()

    while True:
        user_input = input("Enter your command: ")

        if user_input == "read pull requests":
            github_agent.read_pull_requests()
        elif user_input == "read comments":
            github_agent.read_comments()
        elif user_input == "read messages":
            slack_agent.read_messages()
        elif user_input == "summarize messages":
            slack_agent.summarize_messages()
        elif user_input == "exit":
            break
        else:
            print("Invalid command. Please try again.")

if __name__ == "__main__":
    main()
