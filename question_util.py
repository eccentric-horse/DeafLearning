import json
import pickle
import random
import re

# might want to migrate away from this as it could be security risk 
# when paired with pickle, depends on how the session cookie is signed...
from flask import session 
from utilities import ChatTemplate

# How many questions we pick for the video
total_questions = 3

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def choose_questions(file_list):
    json_files = {
        'transcript': 'static/transcript.json',
        'emotion': 'static/emotion.json',
        'movement': 'static/movement.json',
    }

    all_entries = []
    item_number = len(file_list)

    for file_key in file_list:
        file_data = read_json(json_files[file_key])
        all_entries.append(file_data)

    if item_number == 1:
        # If only one file, pick all entries from this file
        entries_to_pick = [total_questions]
    else:
        # Calculate how to distribute the entries evenly
        entries_per_file = total_questions // item_number
        remainder = total_questions % item_number
        
        entries_to_pick = [entries_per_file] * item_number
        for i in range(remainder):
            entries_to_pick[i] += 1

    selected_entries = []
    for i, file_data in enumerate(all_entries):
        selected_entries.extend(random.sample(file_data, entries_to_pick[i]))
    
    return selected_entries

def get_chat_template():
    template = None
    if session.get('template'):
        template = pickle.loads(session['template'])
    else:
        template = ChatTemplate.from_file('question_types.json')
    return template

def update_chat_template(template):
    session['template'] = pickle.dumps(template)

def get_question_types(prompt):
    chat_template = get_chat_template()
    chat_template.template['messages'].append({'role': 'user', 'content': prompt})
    message = chat_template.completion({}).choices[0].message
    pattern = r'QUESTIONS(.*)DONE'
    result = None

    if 'DONE' in message.content:
        # Apply the provided regex pattern to extract desired information
        # Return the extracted information, stripped of leading and trailing whitespace
        result = re.search(pattern, message.content, 
                           re.DOTALL).group(1).strip().split(" "), True
    else:
        # if we are not done update the template
        chat_template.template['messages'].append({'role': message.role, 'content': message.content})
        result = f'{message.content}', False

    update_chat_template(chat_template)

    return result