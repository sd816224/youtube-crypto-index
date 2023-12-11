import logging
import requests
import json

logging.basicConfig()
logger = logging.getLogger('search_channels')
logger.setLevel(logging.INFO)


def search_channels(
        pages_to_search,
        google_api_key,
        q,
        order,
        search_type,
        maxResults_channels,
        page_token=None):
    """it invoke search in youtube bigdata v3 api
    return the list of specifiy amount of channels

    Parameters: ()
        # pages_to_search (int): Description of how many pages of calling search, 5 result /page #noqa
        google_api_key (str): google credential key for the api
        q(str): the keyword for searching
        order (str): option(date/rating/relevance/title/videoCount/viewCount)
        search_type (str): option(channel/playlist/video)
        maxResults_channels (str): max result per page. dafeult 5. option(0-50)
        page_token(str): can be used for nextPageToken
        # ref: https://developers.google.com/youtube/v3/docs/search/list?apix_params=%7B%22part%22%3A%5B%22snippet%22%5D%2C%22q%22%3A%22crypto%22%2C%22type%22%3A%5B%22channel%22%5D%7D # noqa

    Returns:
    dict:{'items':[item1,item2]}
    for each item stands for tailered channel including
        keys: id,title,publishedAt

   """
    logger.info('fetch page: 1')
    payload = fetch_channels_page(
        google_api_key, q, order, search_type, maxResults_channels, page_token)
    all_items = payload['items']
    for i in range(pages_to_search - 1):
        next_page_token = payload.get('nextPageToken')
        if next_page_token:
            logger.info(f'fetch page: {i + 2}')
            payload = fetch_channels_page(
                google_api_key,
                q,
                order,
                search_type,
                maxResults_channels,
                next_page_token)
            all_items += payload['items']
        else:
            logger.info('fetch pages stop here as no more')
    tailerd_payload = {'items':
                       [{
                           'id': x['id']['channelId'],
                           'title': x['snippet']['title'],
                        'publishedAt': x['snippet']['publishedAt'],
                        } for x in all_items]}
    return tailerd_payload


def fetch_channels_page(
        google_api_key,
        q,
        order,
        search_type,
        maxResults_channels,
        page_token=None):
    """it invoke search in youtube bigdata v3 api. return single page info
    return:
    dict:response payload
    """
    try:
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/search',
            params={
                'key': google_api_key,
                'part': 'snippet',
                'q': q,
                'order': order,
                'type': search_type,
                'maxResults': maxResults_channels,
                'page_token': page_token,
            }
        )
        payload = json.loads(response.text)
        if 'error' in payload:
            logger.error('error in response: fetch_channels_page')
            return None
        return payload

    except Exception as e:
        logger.error(e)
        return None
