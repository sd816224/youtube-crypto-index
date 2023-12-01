import logging
import sys
import requests
from dotenv import load_dotenv
import os
import json
from pprint import pformat
from flask import Flask, request
load_dotenv()

def fetch_playlist_items_page(google_api_key, youtube_playlist_id,page_token=None):
    response=requests.get('https://www.googleapis.com/youtube/v3/playlistItems',params={
        "key":google_api_key,
        "playlistId":youtube_playlist_id,
        "part":'contentDetails',
        'pageToken':page_token,
        })
    payload=json.loads(response.text)
    logging.debug('got %s',payload)
    return payload

def fetch_playlist_items(google_api_key,youtube_playlist_id,page_token=None):
    payload = fetch_playlist_items_page(google_api_key,youtube_playlist_id,page_token)
    yield from payload['items']
    next_page_token=payload.get('nextPageToken')

    if next_page_token is not None:
        yield from fetch_playlist_items(google_api_key,youtube_playlist_id,next_page_token)



def fetch_video_page(google_api_key, video_id,page_token=None):
    response=requests.get('https://www.googleapis.com/youtube/v3/videos',params={
        "key":google_api_key,
        "id":video_id,
        "part":'snippet,statistics',
        'pageToken':page_token,
        })
    payload=json.loads(response.text)
    logging.debug('got %s',payload)
    return payload

def fetch_videos(google_api_key,video_id,page_token=None):
    payload = fetch_video_page(google_api_key,video_id,page_token)
    yield from payload['items']
    next_page_token=payload.get('nextPageToken')

    if next_page_token is not None:
        yield from fetch_videos(google_api_key,video_id,next_page_token)

def summarize_video(video):
    return {
        'video_id':video['id'],
        'title':video['snippet']['title'],
        'likes':int(video['statistics'].get('likeCount',0)),
        'views':int(video['statistics'].get('viewCount',0)),
        'comments':int(video['statistics'].get('commentCount',0)),
    }

def on_delivery(err,record):
    pass

def fetch_search(google_api_key,page_token=None):
    response=requests.get('https://www.googleapis.com/youtube/v3/search',params={
        "key":google_api_key,
        "q":'crypto',
        "type":'channel',
        'part':'snippet',
        'pageToken':page_token,
        })
    payload=json.loads(response.text)
    logging.debug('got %s',payload)
    return payload

def main():
    logging.info('Start')
    kafka_config={
        'bootstrap.servers':os.getenv('kafka_bootstrap_servers'),
        'security.protocol':'sasl_ssl',
        'sasl.mechanism':'PLAIN',
        'sasl.username':os.getenv('kafka_username'),
        'sasl.password':os.getenv('kafka_password'),
    }
    # producer= SerializingProducer(kafka_config)
    google_api_key=os.getenv('google_api_key')
    youtube_playlist_id=os.getenv('youtube_playlist_id')

    fetch_search(google_api_key)

    # for video_item in fetch_playlist_items(google_api_key,youtube_playlist_id):
    #     video_id=video_item['contentDetails']['videoId']
    #     for video in fetch_videos(google_api_key,video_id):
    #         logging.info(pformat(summarize_video(video)))        

    #         producer.produce(
    #             topic='youtube_videos',
    #             key=video_id,
    #             value=value,
    #             on_delivery=on_delivery,
            
    #         )




if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())



