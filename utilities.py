import copy
import json
import openai
import os
import re

openai.api_key = os.environ['OPENAI_API_KEY']

def insert_params(string, **kwargs):
    pattern = r"{{(.*?)}}"
    matches = re.findall(pattern, string)
    for match in matches:
        replacement = kwargs.get(match.strip())
        if replacement is not None:
            string = string.replace("{{" + match + "}}", replacement)
    return string
 

class Template:
    """
    This tool reads prompt template, replace the customizable values,
    and returns a completion model.

    Attributes:
    - template (dict): The template content.

    Methods:
    - __init__(template): Initializes the Template object with the provided template.
    - from_file(template_file): Creates a Template object from a JSON file.
    - completion(parameters): Generates a completion using the template and provided parameters.
    """
    def __init__(self, template):
        self.template = template

    def from_file(template_file):
        with open(template_file, 'r') as f:
            template = json.load(f)

        return Template(template)

    def completion(self, parameters):
        instance = copy.deepcopy(self.template)
        instance['prompt'] = insert_params(instance['prompt'], **parameters)

        return openai.completions.create(
            model='gpt-3.5-turbo-instruct',
            **instance)


class ChatTemplate:
    """
    This tool reads prompt template, replace the customizable values,
    and returns a chat completion model.

    Attributes:
    - template (dict): The chat template content.

    Methods:
    - __init__(template): Initializes the ChatTemplate object with the provided template.
    - from_file(template_file): Creates a ChatTemplate object from a JSON file.
    - completion(parameters): Generates a completion using the chat template and provided parameters.
    """
    def __init__(self, template):
        self.template = template

    def from_file(template_file):
        with open(template_file, 'r') as f:
            template = json.load(f)

        return ChatTemplate(template)

    def completion(self, parameters):
        instance = copy.deepcopy(self.template)
        for item in instance['messages']:
            item['content'] = insert_params(item['content'], **parameters)

        return openai.chat.completions.create(
            model='gpt-4o',
            **instance)
    