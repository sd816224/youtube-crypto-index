import logging
from load_db_tables import load_videos_table
from db_connection import get_connection
import xmltodict
from xml.parsers.expat import ExpatError
from flask import Flask, request
import json
import datetime as dt
import sys
import os

src_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(src_path)


app = Flask(__name__)

logging.basicConfig()
logger = logging.getLogger('create_db_tables')
logger.setLevel(logging.INFO)


@app.route('/feed', methods=['GET', 'POST'])
def webhook():
    challenge = request.args.get('hub.challenge')
    if challenge:
        return challenge
    try:
        xml_dict = xmltodict.parse(request.data)

        # Save the dictionary to a JSON file
        document_prefix = str(dt.datetime.now())[:16]
        with open(f'./feed_example/notification_{document_prefix}.json', 'w') as json_file:  # noqa E501
            json.dump(xml_dict, json_file, indent=4)
        logger.info('notification saved to json file')

        conn = get_connection(
            {
                'RDS_USERNAME': 'testuser',
                'RDS_HOSTNAME': 'localhost',
                'DS_DB_NAME': 'testdb',
                'RDS_PORT': 5432,
                'RDS_PASSWORD': 'testpass', })

        listof_videos = parse_filter_notification(conn, xml_dict)
        logger.info('listof_videos parsed: %s', listof_videos)
        if listof_videos:
            load_videos_table(conn, listof_videos)
            logger.info('load_videos_table done')

        conn.close()

    except (ExpatError, LookupError):
        return "", 403

    return "", 204


def video_not_exists(conn, video_id):
    '''check if video already exists in the db
    args:
        conn(obj): db connection
        video_id(str): video id
    return:
        True if video not exists in the db
        False if video does already exist in the db
    '''
    result = conn.run(f"SELECT * FROM yt.videos WHERE video_id='{video_id}'")
    return True if len(result) == 0 else False


def parse_filter_notification(conn, notification):
    '''parse the notification json.
    filter out the videos that already exists in the db.
    return a list of videos to be inserted into the db
    args:
        conn(obj): db connection
        notification(dict): notification json
    return:
        videos_insertion_content(list):
        list of video objects to be inserted into the db
    '''

    """ entry in the notification feed is
    list if multiple result.
    dict if single result.
    channel_id starts by UC and list id starts by UU.
    the following looksthe same"""
    videos_ = notification['feed'].get('entry')
    videos_insertion_content = []
    if isinstance(videos_, list):
        for video in videos_:
            # skip if video already exists
            if not video_not_exists(conn, video['yt:videoId']):
                logger.info('video loading skipped as its already exists in the db: %s', video['yt:videoId'])  # noqa E501
                continue
            video_row = {
                'id': video['yt:videoId'] + dt.datetime.now().strftime("-%Y-%b-%d %H:%M:%S"), # noqa E501
                'title': video['title'],
                'videoPublishedAt': video['published'],
                'videoId': video['yt:videoId'],
                # replace UC with UU to get the list id
                'list_id': video['yt:channelId'].replace('UC', 'UU', 1)
            }
            videos_insertion_content.append(video_row)
        return videos_insertion_content
    elif isinstance(videos_, dict) and video_not_exists(conn, videos_['yt:videoId']): # noqa E501
        video_row = {
            'id': videos_['yt:videoId'] + dt.datetime.now().strftime("-%Y-%b-%d %H:%M:%S"), # noqa E501
            'title': videos_['title'],
            'videoPublishedAt': videos_['published'],
            'videoId': videos_['yt:videoId'],
            # replace UC with UU to get the list id
            'list_id': videos_['yt:channelId'].replace('UC', 'UU', 1)
        }
        videos_insertion_content.append(video_row)
        return videos_insertion_content
    else:
        logger.info('video loading skipped as exist/not valid')
        return []


if __name__ == '__main__':
    app.run()
