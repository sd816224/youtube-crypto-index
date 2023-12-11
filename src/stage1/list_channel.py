import logging
import requests
import json

logging.basicConfig()
logger = logging.getLogger('list_channel')
logger.setLevel(logging.INFO)


def list_all_channels(listof_channels, google_api_key):
    """it iterate the channel_list_primary
    invoke list_channel api to get the detail.
    export the channel list with detail
    including:country, contendetails, statistics and status

    Parameters: ()
        # listof_channels (dict): dict generated from search_channels function. contains primary target channels # noqa
        google_api_key (str): google credential key for the api

    Returns:
    list: [{chanel1_detail},{chanel3_detail},{chanel2_detail}]
   """

    new_list = []
    for item in listof_channels['items']:
        channel_detail = list_channel_detail(
            google_api_key,
            part='snippet,contentDetails,statistics,status',
            id=item['id'],
            page_token=None)
        item['country'] = channel_detail['items'][0]['snippet'].get('country')
        item['uploads_id'] = channel_detail['items'][0]['contentDetails']['relatedPlaylists']['uploads'] # noqa
        item['statistics'] = channel_detail['items'][0]['statistics']
        item['status'] = channel_detail['items'][0]['status']
        new_list.append(item)
    return new_list


def list_channel_detail(google_api_key, part, id, page_token=None):
    """it invoke search in youtube bigdata v3 api. return channel detail
    return:
    dict:response payload
    """
    try:
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/channels',
            params={
                'key': google_api_key,
                'part': part,
                'id': id,
                'page_token': page_token,
            }
        )
        payload = json.loads(response.text)
        if 'error' in payload:
            logger.error('error in response: list_channel_detail')
            return None
        return payload
    except Exception as e:
        logger.error(e)
        return None
