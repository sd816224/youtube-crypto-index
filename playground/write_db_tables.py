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
channel_id='UCi7RBPfTtRkVchV6qO8PUzg'
conn = get_connection(
    {
        'RDS_USERNAME': os.getenv('RDS_USERNAME'),
        'RDS_HOSTNAME': os.getenv('RDS_HOSTNAME'),
        'DS_DB_NAME': os.getenv('DS_DB_NAME'),
        'RDS_PORT': os.getenv('RDS_PORT'),
        'RDS_PASSWORD': os.getenv('RDS_PASSWORD'),
    }
)

def wirte_channels_table_db(conn,channels_content):
    """ query database. 
    insert ready_channel_list into yt.watch_channels
    """
    cursor = conn.cursor()
    query ='INSERT INTO yt.watch_channels (channel_id, uploads_id, title, published_at, country) VALUES (%s, %s, %s, %s, %s)'
    data=[
        (x['id'],x['uploads_id'],x['title'],x['publishedAt'],x['country']) for x in channels_content
    ]
    cursor.executemany(query, data)
    conn.commit()
    cursor.close()
    conn.close()

