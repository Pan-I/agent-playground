def generate_ui_form(fields: list[dict]) -> str:
    """
    Generates an HTML form from a list of field specifications.
    Each field is a dict with 'name', 'label', and 'type'.
    """
    allowed_types = ['text', 'number', 'email', 'password']
    form_lines = ['<form>']

    for field in fields:
        name = field.get('name', 'unnamed')
        label = field.get('label', name.capitalize())
        f_type = field.get('type', 'text')

        if f_type not in allowed_types:
            f_type = 'text'

        form_lines.append(f'  <div>')
        form_lines.append(f'    <label for="{name}">{label}</label>')
        form_lines.append(f'    <input type="{f_type}" id="{name}" name="{name}">')
        form_lines.append(f'  </div>')

    form_lines.append('  <button type="submit">Submit</button>')
    form_lines.append('</form>')
    return '\n'.join(form_lines)
