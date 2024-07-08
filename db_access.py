from azure.data.tables import TableServiceClient

import os
import json

connection_string = os.environ.get('STORAGE_CONNECTION_STRING')

table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)

table_name = 'logs'
table_client = table_service_client.get_table_client(table_name=table_name)
entities = table_client.list_entities()
output_file_path = 'entities.json'

with open(output_file_path, 'w') as file:
    file.write('[')
    for entity in entities:
        processed_entity = {}
        for key, value in entity.items():
            try:
                if key in ['chat_log', 'questions', 'answers', 'survey']:
                    processed_entity[key] = json.loads(value)
                else:
                    processed_entity[key] = value
            except (TypeError, ValueError):
                processed_entity[key] = value
        json.dump(processed_entity, file)
        file.write(',')
    file.write(']')
file.close()
