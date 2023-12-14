import logging
import requests
import json

logging.basicConfig()
logger = logging.getLogger('fetch_videos')
logger.setLevel(logging.INFO)


def fetch_videos(google_api_key, playlistId, maxResults, page_token=None):
    """it invoke listitems in youtube bigdata v3 api. return all videos in the list

    Parameters: ()
        google_api_key (str): google credential key for the api
        playlistId(str): the playlistId for searching. here is the channel uploadId
        maxResults (str):  maxresult/page option(0-50)
        page_token(str): can be used for nextPageToken

        default part: snippet,id,contentDetails
    Returns:
    dict:{'items':[item1,item2]}
    for each item stands for tailered channel including
        keys: id,title,publishedAt

   """ # noqa E501
    logger.info('fetch page: 1')
    payload = fetch_videos_page(
        google_api_key,
        playlistId,
        maxResults,
        page_token)
    next_page_token = payload.get('nextPageToken')
    all_items = payload['items']
    page_no = 2
    while next_page_token:
        logger.info(f'fetch page: {page_no}')
        payload = fetch_videos_page(
            google_api_key,
            playlistId,
            maxResults,
            next_page_token)
        next_page_token = payload.get('nextPageToken')
        all_items += payload['items']
        page_no += 1

    tailerd_payload = {'items':
                       [{
                        'id': item['id'],
                        'title': item['snippet']['title'],
                        'videoPublishedAt': item['contentDetails']['videoPublishedAt'],# noqa E501
                        'videoId': item['snippet']['resourceId']['videoId'],
                        'list_id': item['snippet']['playlistId'],
                        # 'description':item['snippet']['description'],
                        } for item in all_items]}
    return tailerd_payload


def fetch_videos_page(google_api_key, playlistId, maxResults, pageToken=None):
    """it invoke search in youtube bigdata v3 api. return single page info
    return:
    dict:response payload
    """
    try:
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/playlistItems',
            params={
                'key': google_api_key,
                'part': 'snippet,id,contentDetails',
                'playlistId': playlistId,
                'maxResults': maxResults,
                'pageToken': pageToken,
            }
        )
        payload = json.loads(response.text)
        if 'error' in payload:
            logger.error('error in response: fetch_videos_page')
            return None
        return payload
    except Exception as e:
        logger.error(e)
        return None
