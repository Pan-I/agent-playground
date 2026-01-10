import yaml
from openai import OpenAI

with open('./prompts/prompt.yaml', 'r') as f:
    config = yaml.safe_load(f)
    original_prompt = config['user_goal']

client = OpenAI()

class AgentState:
    def __init__(self, goal: str):
        self.goal = goal
        self.thoughts = []
        self.done = False

def agent_step(state: AgentState) -> str:
    prompt = f"""
Goal: {state.goal}

Previous thoughts:
{state.thoughts}

What should be the next step?
If the task is complete, say "DONE".
Otherwise, describe the next action.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    return response.output_text.strip()

def run_agent(goal: str, max_steps=5):
    state = AgentState(goal)

    for step in range(max_steps):
        print(f"\n--- Step {step + 1} ---")
        thought = agent_step(state)
        print(thought)

        if "DONE" in thought.upper():
            state.done = True
            break

        state.thoughts.append(thought)

    return state

if __name__ == "__main__":
    run_agent(original_prompt)