from db_connection import get_connection
import json
from pprint import pprint
import os
from dotenv import load_dotenv

load_dotenv()  

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

output_json_file_name='./data_example/ready_channel_list.json'
content=read_json_file(output_json_file_name)
pprint(content)

conn = get_connection(
    {
        'RDS_USERNAME': os.getenv('RDS_USERNAME'),
        'RDS_HOSTNAME': os.getenv('RDS_HOSTNAME'),
        'DS_DB_NAME': os.getenv('DS_DB_NAME'),
        'RDS_PORT': os.getenv('RDS_PORT'),
        'RDS_PASSWORD': os.getenv('RDS_PASSWORD'),
    }
)