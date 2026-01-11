from openai import OpenAI

class OpenAIProvider:
    def __init__(self, model="gpt-4.1-mini"):
        self.client = OpenAI()
        self.model = model

    def complete(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        return response.output_text.strip()

def get_llm_provider(provider_type="openai"):
    if provider_type == "openai":
        return OpenAIProvider()
    else:
        raise ValueError(f"Unsupported provider: {provider_type}")
