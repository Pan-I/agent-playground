import json
import unittest

from script_files.llm_agent_scripts.agent import Agent


class MockLLM:
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0

    def complete(self, prompt):
        res = self.responses[self.call_count]
        self.call_count += 1
        return res


class TestAgentToolLoading(unittest.TestCase):
    def test_tool_loading(self):
        agent = Agent()
        self.assertIn('generate_ui_form', agent.tools)
        self.assertEqual(agent.tools['generate_ui_form']['schema'], {'fields': 'list'})

    def test_agent_uses_form_tool(self):
        mock_response = json.dumps({
            "type": "act",
            "tool": {
                "name": "generate_ui_form",
                "args": {
                    "fields": [
                        {"name": "email", "label": "Email Address", "type": "email"}
                    ]
                }
            }
        })
        # Second response to finish
        done_response = json.dumps({
            "type": "done",
            "content": "Form generated"
        })

        mock_llm = MockLLM([mock_response, done_response])
        agent = Agent(llm_provider=mock_llm)

        result = agent.run("Create a form for email")
        self.assertEqual(result, "Form generated")
        self.assertEqual(mock_llm.call_count, 2)


if __name__ == '__main__':
    unittest.main()
