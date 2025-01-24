import json
from jinja2 import Environment, FileSystemLoader

def main():
    # 1. Load questions from the JSON file.
    with open('questions.json', 'r') as file:
        data = json.load(file)

    # 2. Set up a Jinja environment pointing to the current directory (.)
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('prompt_template.jinja')

    # 3. Render the template with the questions from the JSON.
    rendered_prompt = template.render(questions=data['questions'])

    # 4. Print or otherwise process the rendered prompt.
    print(rendered_prompt)

if __name__ == "__main__":
    main()
