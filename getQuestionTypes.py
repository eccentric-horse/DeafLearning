import re
from utitlities import ChatTemplate

# Define a function named 'step' which takes two arguments:
# 1. template_file: the path to a file containing a chat template
# 2. pattern: a regular expression pattern used for extracting information from the chat
def step(template_file, pattern):
    chat_template = ChatTemplate.from_file(template_file)
    print(chat_template.template['messages'][-1]['content'])
    while True:
        prompt = input('Student: ')
        # Store to memory as chat context / history
        chat_template.template['messages'].append({'role': 'user', 'content': prompt})

        # Generate a response based on the updated chat template
        message = chat_template.completion({}).choices[0].message
        # Check if the message content contains 'DONE'
        if 'DONE' in message.content:
            # Apply the provided regex pattern to extract desired information
            # Return the extracted information, stripped of leading and trailing whitespace
            return re.search(pattern, message.content, re.DOTALL).group(1).strip() 

        print(f'{message.content}')
        # Store to memory as chat context / history
        chat_template.template['messages'].append({'role': message.role, 'content': message.content})

def get_question_types():
    return step('questionTypes.json', r'QUESTIONS(.*)DONE').split(" ")

questions = get_question_types()

print("here is your info")
print(questions)