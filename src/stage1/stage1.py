from list_channel import list_all_channels
from search_channels import search_channels
from create_db_tables import create_tables, check_tables, destroy_tables
from db_connection import get_connection
from load_db_tables import load_channels_table, load_status_table, load_statistics_table # noqa E501
from iterator_channels import channels_iterator
# from pprint import pprint
import logging
import sys
import os
import json
from dotenv import load_dotenv


def save_json(input, file_name):
    with open(file_name, 'w') as file:
        json.dump(input, file, indent=4)
    logger.info('json file done: %s', file_name)


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def stage1_lambda():
    # config
    reset_db_only = False
    work_on_remote_db = False
    channel_pages_to_search = 2
    q = 'bitcoin'
    maxResults_videos = '50'
    # config
    google_api_key = os.getenv('google_api_key')
    order = 'relevance'
    search_type = 'channel'
    logger.info('start')
    if work_on_remote_db:
        conn = get_connection(
            {
                'RDS_USERNAME': os.getenv('RDS_USERNAME'),
                'RDS_HOSTNAME': os.getenv('RDS_HOSTNAME'),
                'DS_DB_NAME': os.getenv('DS_DB_NAME'),
                'RDS_PORT': int(os.getenv('RDS_PORT')),
                'RDS_PASSWORD': os.getenv('RDS_PASSWORD'),
            }
        )
    else:
        conn = get_connection(
            {
                'RDS_USERNAME': 'testuser',
                'RDS_HOSTNAME': 'localhost',
                'DS_DB_NAME': 'testdb',
                'RDS_PORT': 5432,
                'RDS_PASSWORD': 'testpass',
            }
        )
    # config
    if reset_db_only:
        destroy_tables(conn)
        create_tables(conn)
        check_tables(conn)

        conn.close()
        logger.info('reset db done')
        return
    destroy_tables(conn)
    create_tables(conn)
    check_tables(conn)
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
    load_channels_table(conn, ready_channel_list)
    load_status_table(conn, ready_channel_list)
    load_statistics_table(conn, ready_channel_list)
    channels_iterator(conn, google_api_key, maxResults_videos)
    conn.close()


if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig()
    logger = logging.getLogger('stage1_lambda')
    logger.setLevel(logging.INFO)
    sys.exit(stage1_lambda())
