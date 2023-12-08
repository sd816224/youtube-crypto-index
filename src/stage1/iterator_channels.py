import sys
import os
sys.path.append(os.path.dirname(__file__))
from fetch_videos import fetch_videos  # noqa: E402
from load_db_tables import load_videos_table  # noqa: E402
import logging  # noqa: E402


logging.basicConfig()
logger = logging.getLogger("channels_iterator")
logger.setLevel(logging.INFO)


def channels_iterator(conn, google_api_key, maxResults_videos):
    '''
    This function iterators through yt.watch_channels table
    until all channels are marked a fetched.
    for each channel, it fetches all videos and load them into yt.videos table
    args:
        conn(class): pg connction instance
        google_api_key(string): google api key
        maxResults_videos(str):  maxresult/page option(0-50)
    '''
    upload_id = get_one_channel_id_from_db(conn)
    while upload_id is not None:

        all_videos = fetch_videos(google_api_key, upload_id, maxResults_videos)
    # save_json(all_videos, 'data_example/debug_stage1_fetch_videos_return.json') # noqa E501
    # all_videos = read_json_file('data_example/debug_stage1_fetch_videos_return.json')  # noqa E501
        load_videos_table(conn, all_videos['items'])
        mark_channel_fetched(conn, upload_id)
        upload_id = get_one_channel_id_from_db(conn)


def mark_channel_fetched(conn, channel_id):
    '''
    This function takes a channel_id and marks it as fetched.
    args:
        conn(class): pg connction instance
        channel_id(str): channel's uploads_id
    '''
    query = f'UPDATE yt.watch_channels SET videos_fetched = TRUE WHERE uploads_id = @@{channel_id}@@'  # noqa E501
    conn.run(query.replace('@@', "'"))
    conn.commit()
    logger.info(
        f"mark_channel_fetched: {channel_id} has been marked as fetched.")


def get_one_channel_id_from_db(conn):
    '''
    Connects to the watch_channels DB table, and
    returns one upload_ids with videos_fetched=FALSE.
    args:
        conn(class): pg connction instance
    '''
    uploads_id = conn.run('''SELECT uploads_id, channel_id
                                        FROM yt.watch_channels
                                        WHERE videos_fetched=FALSE
                           LIMIT 1 ''')  # join table to statistics and order by viewcount. # noqa E501
    if len(uploads_id) == 0:
        logger.info("there is no more channel un-fetched")
        return None
    logger.info(f"get_one_channel_id_from_db: channel_id: {uploads_id[0][1]}, list_id: {uploads_id[0][0]}") # noqa E501
    return uploads_id[0][0]
