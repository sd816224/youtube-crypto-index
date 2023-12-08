
def load_channels_table(conn, listof_channels):
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
            x['country']) for x in listof_channels]
    try:
        cursor.executemany(query, data)
        print('load_channels_table done')
    except Exception as e:
        print(e)
    conn.commit()
    cursor.close()


def load_statistics_table(conn, listof_channels):
    """ query database.
    insert data into yt.statistics
    """
    cursor = conn.cursor()
    query = 'INSERT INTO yt.statistics (channel_id, view_count, subscriber_count, hidden_subscriber_count, video_count) VALUES (%s, %s, %s, %s, %s)'  # noqa E501
    data = [
        (x['id'],
         x['statistics']['viewCount'],
            x['statistics']['subscriberCount'],
            x['statistics']['hiddenSubscriberCount'],
            x['statistics']['videoCount']) for x in listof_channels]
    try:
        cursor.executemany(query, data)
        print('load_sstatistics_table done')
    except Exception as e:
        print(e)
    conn.commit()
    cursor.close()


def load_status_table(conn, listof_channels):
    """ query database.
    insert data into yt.status
    """
    cursor = conn.cursor()
    query = 'INSERT INTO yt.status (channel_id, privacy_status, is_linked, long_uploads_status) VALUES (%s, %s, %s, %s)'  # noqa E501
    data = [
        (x['id'],
         x['status']['privacyStatus'],
            x['status']['isLinked'],
            x['status']['longUploadsStatus']) for x in listof_channels]
    try:
        cursor.executemany(query, data)
        print('load_status_table done')
    except Exception as e:
        print(e)
    conn.commit()
    cursor.close()


def load_videos_table(conn, listof_videos):
    """ query database.
    insert listof_videos into yt.videos
    """
    cursor = conn.cursor()
    query = 'INSERT INTO yt.videos (id, title, video_published_at, video_id, list_id) VALUES (%s, %s, %s, %s, %s)'  # noqa E501
    data = [
        (
            x['id'],
            x['title'],
            x['videoPublishedAt'],
            x['videoId'],
            x['list_id']
        )
        for x in listof_videos]

    try:
        cursor.executemany(query, data)
        print('load_videos_table done')
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
