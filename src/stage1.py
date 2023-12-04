from list_channel import list_all_channels
from search_channels import search_channels
from create_db_tables import create_tables, check_tables, destroy_tables
from db_connection import get_connection
from pprint import pprint
import logging
import sys
import os
from dotenv import load_dotenv


def stage1_lambda():
    # config
    logger.info('start')
    channel_pages_to_search = 2
    google_api_key = os.getenv('google_api_key')
    q = 'bitcoin'
    order = 'relevance'
    search_type = 'channel'
    reset_db = False
    conn = get_connection(
        {
            'RDS_USERNAME': os.getenv('RDS_USERNAME'),
            'RDS_HOSTNAME': os.getenv('RDS_HOSTNAME'),
            'DS_DB_NAME': os.getenv('DS_DB_NAME'),
            'RDS_PORT': os.getenv('RDS_PORT'),
            'RDS_PASSWORD': os.getenv('RDS_PASSWORD'),
        }
    )
    # config
    if reset_db:
        destroy_tables(conn)
        logger.info('reset db done')
        return

    channel_list_primary = search_channels(
        channel_pages_to_search,
        google_api_key,
        q,
        order,
        search_type,
    )

    ready_channel_list = list_all_channels(
        channel_list_primary,
        google_api_key,
    )

    pprint(ready_channel_list)

    create_tables(conn)
    check_tables(conn)
    conn.close()


if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig()
    logger = logging.getLogger('stage1_lambda')
    logger.setLevel(logging.INFO)
    sys.exit(stage1_lambda())


# def read_json_file(file_path):
#     with open(file_path, 'r') as file:
#         data = json.load(file)
#     return data

# def save_channels(input):
#     with open('./data_example/ready_channel_list.json', 'w') as file:
#         json.dump(input, file, indent=4)
#     print('json file done')
