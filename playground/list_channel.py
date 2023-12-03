import logging
import sys
import requests
import os
import json

from dotenv import load_dotenv
from pprint import pformat
import json
import json
load_dotenv()

def list_all_channels(listof_channels,google_api_key):
    """it iterate the listof_channels and invoke lsit_channel api to get the detail. 
     export the channel list with detail, including:country, contendetails, statistics and status

    Parameters: ()
        listof_channels (dict): dict generated from search_channels function. contains primary target channels
        google_api_key (str): google credential key for the api

    Returns:
    dict:
   """
    new_list=[]
    for item in listof_channels['items']:
        channel_detail=list_channel(google_api_key,part='snippet,contentDetails,statistics,status',id=item['id'],page_token=None)
        item['country']=channel_detail['items'][0]['snippet']['country']
        item['contentDetails']=channel_detail['items'][0]['contentDetails']
        item['statistics']=channel_detail['items'][0]['statistics']
        item['status']=channel_detail['items'][0]['status']
        new_list.append(item)
    return new_list
    
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
    return payload

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def save_channels(input):
    with open('./data_example/ready_channel_list.json', 'w') as file:
        json.dump(input, file, indent=4)
    print('json file done')

def main():
    logging.info('start')
    # config：
    google_api_key=os.getenv('google_api_key')
    file_path = './data_example/listof_tailered_channels.json'
    listof_channels = read_json_file(file_path)
    ready_channel_list=list_all_channels(
        listof_channels,    
        google_api_key,
        )
    save_channels(ready_channel_list)

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
