import os
import json
import xlsxwriter

from azure.data.tables import TableServiceClient
from datetime import timezone, timedelta

connection_string = os.environ.get('STORAGE_CONNECTION_STRING')
table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)

table_name = 'logs'
table_client = table_service_client.get_table_client(table_name=table_name)
entities = table_client.list_entities()

output_file_path = 'entities.xlsx'
workbook = xlsxwriter.Workbook(output_file_path)
worksheet = workbook.add_worksheet()

headers = []

def get_value(entity, field):
    if field == "timestamp":
        est_tz = timezone(timedelta(hours=-5), name="EST")
        return entity._metadata["timestamp"].astimezone(est_tz).isoformat()
    return entity[field]

row = 0
for entity_page in entities.by_page():
    for entity in entity_page:
        if not headers:
            headers = list(entity.keys()) + ["timestamp"]
            for col, header in enumerate(headers):
                worksheet.write(row, col, header)
            row += 1
        
        for col, key in enumerate(headers):
            value = get_value(entity, key)
            try:
                decoded_value = json.loads(value)
                worksheet.write(row, col, json.dumps(decoded_value))
            except (json.JSONDecodeError, TypeError):
                worksheet.write(row, col, value)
        row += 1

workbook.close()

print(f"Entities saved to {output_file_path}")
