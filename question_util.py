import json
import pickle
import random
import re

# might want to migrate away from this as it could be security risk 
# when paired with pickle, depends on how the session cookie is signed...
from flask import session 
from utilities import ChatTemplate
from itertools import cycle
from pprint import pprint

# Number of questions we pick for the video
total_questions = 10

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def choose_questions(file_list):  
    video_duration=900000 # video duration 15 minutes
    json_files = {
        'transcript': 'static/transcript.json',
        'emotion': 'static/emotion.json',
        'movement': 'static/movement.json',
    }

    # Read and sort entries from each file
    all_entries = {}
    for file_key in file_list:
        file_data = read_json(json_files[file_key])
        for question in file_data:
            question['question_type'] = file_key
        all_entries[file_key] = sorted(file_data, key=lambda x: x['time_stamp'])
    
    interval = video_duration / total_questions
    # prepare to track how many questions have been selected from each file
    selected_counts = {key: 0 for key in file_list}
    
    selected_entries = []
    start_time = 0
    relax_selection = False

    while len(selected_entries) < total_questions:
        if start_time + interval >= video_duration:
            # if we made it all the way through and we haven't 
            # selected enough questions relax the buckets the questions
            # can be chosen from
            start_time = 0
            relax_selection = True

        end_time = start_time + interval
        
        # collect available questions from each file within the current interval
        available_entries = {key: [entry for entry in all_entries[key] if start_time <= entry['time_stamp'] < end_time] for key in file_list}
        # determine which file to select from next (cycling through the files)
        for file_key in file_list:
            if available_entries[file_key] and (relax_selection or selected_counts[file_key] < total_questions // len(file_list)):
                selected_entry = random.choice(available_entries[file_key])
                selected_entries.append(selected_entry)
                all_entries[file_key].remove(selected_entry)  # remove selected entry to avoid picking it again
                selected_counts[file_key] += 1
                print(f"Selected question '{selected_entry['ID']}' from file '{file_key}'")
                break
        start_time = end_time
    
    #pprint(selected_entries)
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