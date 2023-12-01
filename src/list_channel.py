import logging
import sys
import requests
import os
import json

from dotenv import load_dotenv
from pprint import pformat
import json
load_dotenv()

# def list_channel(google_api_key,part,id,page_token=None):
#     """it invoke search in youtube bigdata v3 api. return the list of specifiy amount of channels

#     Parameters: ()
#         pages_to_search (int): Description of how many pages of calling search, 5 result /page
#         google_api_key (str): google credential key for the api
#         q(str): the keyword for searching
#         order (str): option(date/rating/relevance/title/videoCount/viewCount)
#         search_type (str): option(channel/playlist/video)
#         page_token(str): can be used for nextPageToken
#         ref: https://developers.google.com/youtube/v3/docs/search/list?apix_params=%7B%22part%22%3A%5B%22snippet%22%5D%2C%22q%22%3A%22crypto%22%2C%22type%22%3A%5B%22channel%22%5D%7D

#     Returns:
#     int: list of object

#    """
#     payload=fetch_channels_page(google_api_key,q,page_token=None)
#     all_items=payload['items']
#     for i in range(pages_to_search-1):
#         next_page_token=payload.get('nextPageToken')
#         if next_page_token:
#             payload=fetch_channels_page(google_api_key,q,order,search_type,next_page_token)
#             all_items+=payload['items']
#         else:
#             logging.info('fetch pages stop here as no more')
#     return all_items
    
def list_channel(google_api_key,part,id,page_token=None):
    response = requests.get(
        'https://www.googleapis.com/youtube/v3/channels',
        params={
            'key': google_api_key,
            'part':part,
            'id':id,
            'page_token':page_token,
        }  
    )
    payload=json.loads(response.text)
    print(pformat(payload))
    return payload


def save_channels(input_list):
    """save the list of channels into json file as:
    {'items':[item1,item2]}
    """
    # json_content={'items':input_list}
    with open('./data_example/single_list_channel_result.json', 'w') as file:
        json.dump(input_list, file, indent=4)
    print('json file done')

def main():
    logging.info('start')
    # config：
    google_api_key=os.getenv('google_api_key')
    part='snippet,contentDetails,statistics,status'
    id='UC-0Hk4yjo7pfxrRq9vJke-Q'
    example=list_channel(
        google_api_key,
        part,
        id,
        )
    save_channels(example)
if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
