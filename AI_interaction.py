import openai
import os
from utitlities import ChatTemplate

guide = '''You are a Q&A bot. You provide short answers to questions.
For example:
Question: What does ASL stand for? American Sign Language.
Provide the answer to the following question:
Question: '''

def answer_question(question):
    chat = ChatTemplate({
        'messages': [{'role': 'user', 'content': guide + question}]})
    answer = chat.completion({}).choices[0].message.content
    return answer
