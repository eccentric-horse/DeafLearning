from flask import session
from azure.data.tables import TableServiceClient, UpdateMode

import json
import os

connection_string = os.environ.get('STORAGE_CONNECTION_STRING')

def save_selected_questions(questions):
    if not connection_string:
        return
    
    question_encoded = json.dumps(questions)
    question_entity = {
        'PartitionKey': "pk",
        'RowKey': session.sid,
        'questions': question_encoded,
    }
    
    with TableServiceClient.from_connection_string(conn_str=connection_string) as table_service_client:
        table_client = table_service_client.get_table_client(table_name="logs")
        table_client.upsert_entity(mode=UpdateMode.MERGE, entity=question_entity)


def save_answer_data(question_data, answer_index, time_answered):
    
    if not connection_string:
        return
    
    with TableServiceClient.from_connection_string(conn_str=connection_string) as table_service_client:
        table_client = table_service_client.get_table_client(table_name="logs")
        
        try:
            entity = table_client.get_entity(partition_key="pk", row_key=session.sid)
        except:
            entity = {}

        answers = entity.get("answers", None)
        answer_entry = {
            "question": question_data,
            "answer_index": answer_index,
            "time_to_answer": time_answered 
        }

        answer_entity = {
            'PartitionKey': "pk",
            'RowKey': session.sid,
            'answers': json.dumps([answer_entry])
        }

        if answers:
            old_answers = json.loads(answers)
            old_answers.append(answer_entry)
            answer_entity['answers'] = json.dumps(old_answers)

        table_client.upsert_entity(mode=UpdateMode.MERGE, entity=answer_entity)

def save_chat_interaction(prompt, response):
    if not connection_string:
        return
    
    with TableServiceClient.from_connection_string(conn_str=connection_string) as table_service_client:
        table_client = table_service_client.get_table_client(table_name="logs")
        
        try:
            entity = table_client.get_entity(partition_key="pk", row_key=session.sid)
        except:
            entity = {}

        chat_log = entity.get("chat_log", None)
        chat_entry = {
            "prompt": prompt,
            "response": response,
        }

        chat_entity = {
            'PartitionKey': "pk",
            'RowKey': session.sid,
            'chat_log': json.dumps([chat_entry])
        }

        if chat_log:
            chat = json.loads(chat_log)
            chat.append(chat_entry)
            chat_entity['chat_log'] = json.dumps(chat)

        table_client.upsert_entity(mode=UpdateMode.MERGE, entity=chat_entity)
