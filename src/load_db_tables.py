
def load_channels_table(conn, channels_content):
    """ query database.
    insert ready_channel_list into yt.watch_channels
    """
    cursor = conn.cursor()
    query = 'INSERT INTO yt.watch_channels (channel_id, uploads_id, title, published_at, country) VALUES (%s, %s, %s, %s, %s)'  # noqa E501
    data = [
        (x['id'],
         x['uploads_id'],
            x['title'],
            x['publishedAt'],
            x['country']) for x in channels_content]
    try:
        cursor.executemany(query, data)
        print('query done')
    except Exception as e:
        print(e)
    conn.commit()
    cursor.close()


def load_videos_table(conn, channels_content):
    """ query database.
    insert listof_videos into yt.videos
    """
    cursor = conn.cursor()
    query = 'INSERT INTO yt.videos (id, title, video_published_at, video_id, channel_id) VALUES (%s, %s, %s, %s, %s)'  # noqa E501
    data = [
        (
            x['id'],
            x['title'],
            x['videoPublishedAt'],
            x['videoId'],
            x['channel_id']
        )
        for x in channels_content]

    try:
        cursor.executemany(query, data)
        print('query done')
    except Exception as e:
        print(e)
    conn.commit()
    cursor.close()


#######
# def read_json_file(file_path):
#     with open(file_path, 'r') as file:
#         data = json.load(file)
#     return data


# channel_json_file_name = './data_example/ready_channel_list.json'
# channel_content = read_json_file(channel_json_file_name)

# video_json_file_name = './data_example/listof_videos.json'
# video_content = read_json_file(video_json_file_name)['items']

# conn = get_connection(
#     {
#         'RDS_USERNAME': 'testuser',
#         'RDS_HOSTNAME': 'localhost',
#         'DS_DB_NAME': 'testdb',
#         'RDS_PORT': 5432,
#         'RDS_PASSWORD': 'testpass',
#     }
# )
# load_channels_table(conn, channel_content)
# load_videos_table(conn, video_content)
