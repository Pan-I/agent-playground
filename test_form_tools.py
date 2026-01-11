import unittest

from script_files.tools import form_tools


class TestFormTools(unittest.TestCase):
    def test_generate_ui_form_basic(self):
        fields = [
            {"name": "username", "label": "Username", "type": "text"},
            {"name": "password", "label": "Password", "type": "password"}
        ]
        result = form_tools.generate_ui_form(fields)
        self.assertIn('<form>', result)
        self.assertIn('</form>', result)
        self.assertIn('label for="username">Username</label>', result)
        self.assertIn('input type="text" id="username" name="username"', result)
        self.assertIn('label for="password">Password</label>', result)
        self.assertIn('input type="password" id="password" name="password"', result)

    def test_generate_ui_form_empty(self):
        fields = []
        result = form_tools.generate_ui_form(fields)
        self.assertEqual(result, '<form>\n  <button type="submit">Submit</button>\n</form>')

    def test_generate_ui_form_invalid_type(self):
        # Should default to 'text' or handle it gracefully
        fields = [{"name": "age", "label": "Age", "type": "unknown"}]
        result = form_tools.generate_ui_form(fields)
        self.assertIn('type="text"', result)

    def test_generate_ui_form_missing_keys(self):
        fields = [{"name": "onlyname"}]
        result = form_tools.generate_ui_form(fields)
        self.assertIn('label for="onlyname">Onlyname</label>', result)
        self.assertIn('input type="text" id="onlyname" name="onlyname"', result)

        fields = [{"label": "Only Label"}]
        result = form_tools.generate_ui_form(fields)
        self.assertIn('label for="unnamed">Only Label</label>', result)
        self.assertIn('id="unnamed" name="unnamed"', result)


if __name__ == '__main__':
    unittest.main()
