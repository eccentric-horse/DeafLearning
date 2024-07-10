import json
import pickle
import random
import re

# might want to migrate away from this as it could be security risk 
# when paired with pickle, depends on how the session cookie is signed...
from flask import session 
from utilities import ChatTemplate
from itertools import cycle
from db_util import save_chat_interaction

# Number of questions we pick for the video
total_questions = 10

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def choose_questions(question_types):  
    video_duration=900000 # video duration 15 minutes
    json_files = {
        'transcript': 'static/transcript.json',
        'emotion': 'static/emotion.json',
        'visual': 'static/visual.json',
    }

    # if for some reason we ask for more questions than are available
    # just stop looking
    total_avail_questions = 0

    # Read and sort entries from each file
    all_entries = {}
    for q_type in question_types:
        file_data = read_json(json_files[q_type])
        for question in file_data:
            question['question_type'] = q_type
            total_avail_questions += 1

        all_entries[q_type] = sorted(file_data, key=lambda x: x['time_stamp'])

        for index, entry in enumerate(all_entries[q_type]):
            entry['order'] = index + 1

    interval = video_duration / total_questions
    # prepare to track how many questions have been selected from each file
    selected_counts = {key: 0 for key in question_types}
    
    selected_entries = []
    start_time = 0
    relax_selection = False

    while len(selected_entries) < total_questions and total_avail_questions > 0:
        end_time = start_time + interval

        if end_time > video_duration:
            # if we made it all the way through and we haven't 
            # selected enough questions relax the buckets the questions
            # can be chosen from and reset the time interval
            start_time = 0
            end_time = interval
            relax_selection = True

        # collect available questions from each file within the current interval
        available_entries = {key: [entry for entry in all_entries[key] if start_time <= entry['time_stamp'] < end_time] for key in question_types}
        #print(available_entries, len(selected_entries), all_entries["emotion"])
        # determine which file to select from next (cycling through the files)
        for q_type in question_types:
            type_bucket_not_full = selected_counts[q_type] < total_questions // len(question_types)
            if available_entries[q_type] and (relax_selection or type_bucket_not_full):
                selected_entry = random.choice(available_entries[q_type])
                selected_entries.append(selected_entry)
                all_entries[q_type].remove(selected_entry)  # remove selected entry to avoid picking it again
                selected_counts[q_type] += 1
                total_avail_questions -= 1
                print(f"Selected question '{selected_entry['ID']}' for question_type '{q_type}'")
                break
        start_time = end_time

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

    save_chat_interaction(prompt, message.content)

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