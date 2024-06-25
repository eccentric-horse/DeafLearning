import json
import random

# How many questions we pick for the video
total_questions = 3

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# list of choices
def chooseQuestions(file_list):
    json_files = {
        'transcript': 'static/transcript.json',
        'emotion': 'static/emotion.json',
        'movement': 'static/movement.json',
    }

    all_entries = []
    item_number = len(file_list)

    # Read the necessary files
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




'''
for entry in data:
    print(f"ID: {entry['ID']}")
    print(f"Transcript Reference: {entry['transcript_reference']}")
    print(f"Question: {entry['question']}")
    print(f"Time Stamp: {entry['time_stamp']}")
    print("Answers:")
    for answer in entry['answers']:
        print(f"  - Answer: {answer['answer']}, Correct: {answer['correct']}")
    print()
    '''