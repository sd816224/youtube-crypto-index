# # import os
# # from pprint import pprint
# # from dotenv import load_dotenv
# # from pg8000 import DatabaseError
# # from db_connection import get_connection
# import logging
# # from fetch_videos import fetch_videos
# # from load_db_tables import load_videos_table

# # load_dotenv()

# logging.basicConfig()
# logger = logging.getLogger("channels_iterator")
# logger.setLevel(logging.INFO)




# def channels_iterator(conn,google_api_key,maxResults_videos):

#     # '''
#     # This function iterators through the table: yt.watch_channels.
#     # if:
#     #     videos have not been fetched, change column: videos_fetched to true
#     #     and yell (print that it's been changed)
#     # else:
#     #     leave the video_fetched alone. Default = []

#     # '''
#     upload_id=get_one_channel_id_from_db(conn)
#     while upload_id is not None:

#         all_videos=fetch_videos(google_api_key,upload_id,maxResults_videos)
#         from pprint import pprint
#         pprint(all_videos)
#         load_videos_table(conn,all_videos['items'])
#         mark_channel_fetched(conn, upload_id)
#         upload_id=get_one_channel_id_from_db(conn)
        

# def mark_channel_fetched(conn, channel_id):
#     '''
#     This function takes a channel_id and marks it as fetched.
#     '''
#     query = f'UPDATE yt.watch_channels SET videos_fetched = TRUE WHERE uploads_id = @@{channel_id}@@'
#     conn.run(query.replace('@@', "'"))
#     conn.commit()
#     logger.info(f"mark_channel_fetched: {channel_id} has been marked as fetched.")


# def get_one_channel_id_from_db(conn):
#     '''
#     Connects to the watch_channels DB table, and
#     returns one upload_ids with videos_fetched=FALSE.
#     '''
#     channel_id = conn.run('''SELECT uploads_id
#                                         FROM yt.watch_channels
#                                         WHERE videos_fetched=FALSE
#                            LIMIT 1 ''') # join table to statistics and order by viewcount.
#     if len(channel_id) == 0:
#         logger.info(f"there is no more channel un-fetched")
#         return None
#     logger.info(f"get_one_channel_id_from_db: {channel_id[0][0]}")
#     return channel_id[0][0]


# def fetch_videos(google_api_key, playlistId, maxResults, page_token=None):
#     """it invoke listitems in youtube bigdata v3 api. return all videos in the list

#     Parameters: ()
#         google_api_key (str): google credential key for the api
#         playlistId(str): the playlistId for searching. here is the channel uploadId
#         maxResults (str):  maxresult/page option(0-50)
#         page_token(str): can be used for nextPageToken

#         default part: snippet,id,contentDetails
#     Returns:
#     dict:{'items':[item1,item2]}
#     for each item stands for tailered channel including
#         keys: id,title,publishedAt

#    """ # noqa E501
#     logger.info('fetch page: 1')
#     payload = fetch_videos_page(
#         google_api_key,
#         playlistId,
#         maxResults,
#         page_token)
#     next_page_token = payload.get('nextPageToken')
#     all_items = payload['items']
#     page_no = 2
#     print(next_page_token)
#     while next_page_token:
#         logger.info(f'fetch page: {page_no}')
#         payload = fetch_videos_page(
#             google_api_key,
#             playlistId,
#             maxResults,
#             next_page_token)
#         next_page_token = payload.get('nextPageToken')
#         all_items += payload['items']
#         page_no += 1

#     tailerd_payload = {'items':
#                        [{
#                         'id': item['id'],
#                         'title': item['snippet']['title'],
#                         'videoPublishedAt': item['contentDetails']['videoPublishedAt'],# noqa E501
#                         'videoId': item['snippet']['resourceId']['videoId'],
#                         'channel_id': item['snippet']['channelId'],
#                         # 'description':item['snippet']['description'],
#                         } for item in all_items]}
#     return tailerd_payload


# def fetch_videos_page(google_api_key, playlistId, maxResults, pageToken=None):
#     """it invoke search in youtube bigdata v3 api. return single page info
#     return:
#     dict:response payload
#     """
#     try:
#         response = requests.get(
#             'https://www.googleapis.com/youtube/v3/playlistItems',
#             params={
#                 'key': google_api_key,
#                 'part': 'snippet,id,contentDetails',
#                 'playlistId': playlistId,
#                 'maxResults': maxResults,
#                 'pageToken': pageToken,
#             }
#         )
#         payload = json.loads(response.text)
#         if 'error' in payload:
#             logger.error('error in response: fetch_videos_page')
#             return None
#         return payload
#     except Exception as e:
#         logger.error(e)
#         return None
    

# def load_videos_table(conn, listof_videos):
#     """ query database.
#     insert listof_videos into yt.videos
#     """
#     cursor = conn.cursor()
#     query = 'INSERT INTO yt.videos (id, title, video_published_at, video_id, channel_id) VALUES (%s, %s, %s, %s, %s)'  # noqa E501
#     data = [
#         (
#             x['id'],
#             x['title'],
#             x['videoPublishedAt'],
#             x['videoId'],
#             x['channel_id']
#         )
#         for x in listof_videos]
#     try:
#         cursor.executemany(query, data)
#         print('load_videos_table done')
#     except Exception as e:
#         print(e)
#     conn.commit()
#     cursor.close()