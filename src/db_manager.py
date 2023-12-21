from list_channel import list_all_channels
from search_channels import search_channels
from create_db_tables import create_tables, check_tables, destroy_tables
from db_connection import get_connection
from load_db_tables import load_channels_table, load_status_table, load_statistics_table  # noqa E501
from iterator_channels import channels_iterator
# from pprint import pprint
import logging
import sys
import os
import json
from dotenv import load_dotenv

logging.basicConfig()
logger = logging.getLogger('stage1_lambda')
logger.setLevel(logging.INFO)


def save_json(input, file_name):
    with open(file_name, 'w') as file:
        json.dump(input, file, indent=4)
    logger.info('json file done: %s', file_name)


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def main():
    load_dotenv()
    # config
    reset_db_only = False
    db_init = False
    work_on_remote_db = True
    channel_pages_to_search = 40
    q = 'bitcoin'
    maxResults_channels = '50'
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
                'RDS_DB_NAME': os.getenv('RDS_DB_NAME'),
                'RDS_PORT': int(os.getenv('RDS_PORT')),
                'RDS_PASSWORD': os.getenv('RDS_PASSWORD'),
            }
        )
    else:
        conn = get_connection(
            {
                'RDS_USERNAME': 'testuser',
                'RDS_HOSTNAME': 'localhost',
                'RDS_DB_NAME': 'testdb',
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
    if db_init:
        destroy_tables(conn)
        create_tables(conn)
        check_tables(conn)
        channel_list_primary = search_channels(
            channel_pages_to_search,
            google_api_key,
            q,
            order,
            search_type,
            maxResults_channels,
        )
        logger.info('search_channels done')
        ready_channel_list = list_all_channels(
            channel_list_primary,
            google_api_key,
        )
        logger.info('list_channels done')
        load_channels_table(conn, ready_channel_list)
        load_status_table(conn, ready_channel_list)
        load_statistics_table(conn, ready_channel_list)
        logger.info('load channges&status&statistics done')
    channels_iterator(conn, google_api_key, maxResults_videos)
    logger.info('load videos done')
    conn.close()


if __name__ == '__main__':
    logging.basicConfig()
    logger = logging.getLogger('stage1_lambda')
    logger.setLevel(logging.INFO)
    sys.exit(main())
