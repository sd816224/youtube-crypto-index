from list_channel import list_all_channels
from search_channels import search_channels
from pprint import pprint
import logging
import sys
import os
from dotenv import load_dotenv
load_dotenv()


def stage1_lambda():
    # config
    logging.info('start')
    channel_pages_to_search = 2
    google_api_key = os.getenv('google_api_key')
    q = 'bitcoin'
    order = 'relevance'
    search_type = 'channel'

    # config

    channel_list_primary = search_channels(
        channel_pages_to_search,
        google_api_key,
        q,
        order,
        search_type,
    )
    pprint(channel_list_primary)
    ready_channel_list = list_all_channels(
        channel_list_primary,
        google_api_key,
    )

    pprint(ready_channel_list)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(stage1_lambda())


# def read_json_file(file_path):
#     with open(file_path, 'r') as file:
#         data = json.load(file)
#     return data

# def save_channels(input):
#     with open('./data_example/ready_channel_list.json', 'w') as file:
#         json.dump(input, file, indent=4)
#     print('json file done')
