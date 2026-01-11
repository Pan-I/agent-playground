from script_files.tools import workflow_tools
from script_files.llm_agent_scripts import agent


def main():
    agent.run_agent(workflow_tools.original_prompt)

if __name__ == "__main__":
    main()