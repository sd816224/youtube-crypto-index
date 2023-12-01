import logging
import sys
import requests
import os
import json

from dotenv import load_dotenv
from pprint import pformat
load_dotenv()

def fetch_channels_page(google_api_key,part,q,order,search_type,page_token=None):
    response = requests.get(
        'https://www.googleapis.com/youtube/v3/search',
        params={
            'key': google_api_key,
            'part': part,
            'q':q,
            'order':order,
            'type':search_type,
        }  
    )
    payload=json.loads(response.text)
    logging.info(pformat(payload))
    return payload

def search_channels(pages_to_search,google_api_key,part,q,order,search_type,page_token=None):
    payload=fetch_channels_page(google_api_key=google_api_key,part=part,q=q,order=order,search_type=search_type)
    all_items=payload['items']
    for i in range(pages_to_search-1):
        next_page_token=payload.get('nextPageToken')
        payload=fetch_channels_page(google_api_key,part,q,order,search_type,next_page_token)
        all_items+=payload['items']

def main():
    logging.info('start')
    # config：
    pages_to_search=2
    google_api_key=os.getenv('google_api_key')
    part='snippet'
    q='bitcoin'
    order='relevance',
    search_type='channel'


    search_channels(
        pages_to_search,
        google_api_key,
        part,
        q,
        order,
        search_type,
        )


if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
