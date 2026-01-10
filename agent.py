from openai import OpenAI

client = OpenAI()
print("Testing OpenAI...")

def run_agent(goal: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"You are an assistant. Your goal is: {goal}",
    )
    return response.output_text

if __name__ == "__main__":
    goal = "Explain what an agent loop is in one paragraph."
    output = run_agent(goal)
    print(goal)
    print(output)