import logging
import sys
import requests
import os
import json

from dotenv import load_dotenv
from pprint import pformat
import json
load_dotenv()

def search_channels(pages_to_search,google_api_key,q,order,search_type,page_token=None):
    """it invoke search in youtube bigdata v3 api. return the list of specifiy amount of channels

    Parameters: ()
        pages_to_search (int): Description of how many pages of calling search, 5 result /page
        google_api_key (str): google credential key for the api
        q(str): the keyword for searching
        order (str): option(date/rating/relevance/title/videoCount/viewCount)
        search_type (str): option(channel/playlist/video)
        page_token(str): can be used for nextPageToken
        ref: https://developers.google.com/youtube/v3/docs/search/list?apix_params=%7B%22part%22%3A%5B%22snippet%22%5D%2C%22q%22%3A%22crypto%22%2C%22type%22%3A%5B%22channel%22%5D%7D

    Returns:
    dict:{'items':[item1,item2]}
    for each item stands for tailered channel including
        keys: id,title,publishedAt

   """
    logging.info('fetch page: 1')
    payload=fetch_channels_page(google_api_key,q,order,search_type,page_token)
    all_items=payload['items']
    for i in range(pages_to_search-1):
        next_page_token=payload.get('nextPageToken')
        if next_page_token:
            logging.info(f'fetch page: {i+2}')
            payload=fetch_channels_page(google_api_key,q,order,search_type,next_page_token)
            all_items+=payload['items']
        else:
            logging.info('fetch pages stop here as no more')
    tailerd_payload={'items':
                    [{
                    'id': x['id']['channelId'],
                    'title':x['snippet']['title'],
                    'publishedAt':x['snippet']['publishedAt'],
                    } for x in all_items]}
    return tailerd_payload
    
def fetch_channels_page(google_api_key,q,order,search_type,page_token=None):
    """it invoke search in youtube bigdata v3 api. return single page info
    return:
    dict:response payload
    """
    response = requests.get(
        'https://www.googleapis.com/youtube/v3/search',
        params={
            'key': google_api_key,
            'part':'snippet',
            'q':q,
            'order':order,
            'type':search_type,
            'page_token':page_token,
        }  
    )
    payload=json.loads(response.text)

    return payload


def save_channels(input):
    """simple save input as json file """
    with open('./data_example/listof_tailered_channels.json', 'w') as file:
        json.dump(input, file, indent=4)
    print('json file done')

def main():
    logging.info('start')
    # config：
    pages_to_search=2
    google_api_key=os.getenv('google_api_key')
    q='bitcoin'
    order='relevance'
    search_type='channel'
    example=search_channels(
        pages_to_search,
        google_api_key,
        q,
        order,
        search_type,
        )
    save_channels(example)

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
