import os
import subprocess
import time
import logging
import pytest
import datetime
from unittest.mock import patch
from src.db_connection import get_connection
from src.load_db_tables import load_channels_table
from src.create_db_tables import create_tables
from src.iterator_channels import channels_iterator

logging.basicConfig()
logger = logging.getLogger("MyLogger")
logger.setLevel(logging.INFO)


database_credentials = {
    "RDS_USERNAME": "testuser",
    "RDS_PASSWORD": "testpass",
    "RDS_DB_NAME": "testdb",
    "RDS_HOSTNAME": "localhost",
    "RDS_PORT": 5433,
}


@pytest.fixture(scope="module")
def pg_container():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    compose_path = os.path.join(test_dir, "docker-compose-testonly.yaml")
    subprocess.run(
        ["docker", "compose", "-f", compose_path, "up", "-d"], check=False
    )  # noqa: E501
    try:
        max_attempts = 5
        for _ in range(max_attempts):
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "local-test-postgres",
                    "pg_isready",
                    "-h",
                    "localhost",
                    "-U",
                    "testdb",
                ],
                stdout=subprocess.PIPE,
                check=False,
            )
            if result.returncode == 0:
                break
            time.sleep(0.5)
        else:
            raise TimeoutError(
                """PostgreSQL container is not responding,
                cancelling fixture setup."""
            )
        yield
    finally:
        subprocess.run(
            ["docker", "compose", "-f", compose_path, "down"], check=False
        )  # noqa: E501


def mock_fetch_video(google_api_key, upload_id, maxResults_videos):
    mock_fetch_video_return = {
        "items": [
            {
                "id": f"testId1-{upload_id}",
                "title": "testTitle1",
                "videoPublishedAt": "2015-04-07T21:01:18Z",
                'videoId': 'testvideoId1',
                'list_id': upload_id
            },
            {
                "id": f"testId2-{upload_id}",
                "title": "testTitle2",
                "videoPublishedAt": "2015-03-07T21:01:18Z",
                'videoId': 'testvideoId2',
                'list_id': upload_id
            },
            {
                "id": f"testId3-{upload_id}",
                "title": "testTitle3",
                "videoPublishedAt": "2015-02-07T21:01:18Z",
                'videoId': 'testvideoId3',
                'list_id': upload_id
            }
        ]}
    return mock_fetch_video_return


# @patch('src.stage1.iterator_channels.fetch_videos',side_effect=mock_fetch_video)
def test_iterate_channels(pg_container):
    channel_content = [
        {
            "id": "testChannelId1",
            "title": "testTitle1",
            "publishedAt": "2015-02-07T21:01:18Z",
            "country": "GB",
            "uploads_id": "testUploadsId1",
            "statistics": {
                "viewCount": "1111",
                "subscriberCount": "1111",
                "hiddenSubscriberCount": False,
                "videoCount": "1111"
            },
            "status": {
                "privacyStatus": "public",
                "isLinked": True,
                "longUploadsStatus": "longUploadsUnspecified",
                "madeForKids": False
            }
        },
        {
            "id": "testChannelId2",
            "title": "testTitle2",
            "publishedAt": "2015-05-07T21:01:18Z",
            "country": "US",
            "uploads_id": "testUploadsId2",
            "statistics": {
                "viewCount": "2222",
                "subscriberCount": "2222",
                "hiddenSubscriberCount": False,
                "videoCount": "2222"
            },
            "status": {
                "privacyStatus": "public",
                "isLinked": True,
                "longUploadsStatus": "longUploadsUnspecified",
                "madeForKids": False
            }
        }]

    with patch('src.iterator_channels.fetch_videos', side_effect=mock_fetch_video): # noqa E501
        google_api_key = 'testkey'
        maxResults_videos = 'testMax'
        conn = get_connection(database_credentials)
        create_tables(conn)
        load_channels_table(conn, channel_content)
        # load_status_table(conn)
        channels_iterator(conn, google_api_key, maxResults_videos)

        updated_channels = conn.run('''SELECT * FROM yt.watch_channels''')
        assert updated_channels == (['testChannelId1',
                                     'testUploadsId1',
                                    'testTitle1',
                                     datetime.datetime(2015, 2, 7, 21, 1, 18),
                                     'GB',
                                     True,
                                     True],
                                    ['testChannelId2',
                                    'testUploadsId2',
                                     'testTitle2',
                                     datetime.datetime(2015, 5, 7, 21, 1, 18),
                                     'US',
                                     True,
                                     True])

        updated_videos = conn.run('''SELECT * FROM yt.videos''')
        assert updated_videos == (['testId1-testUploadsId1',
                                   'testTitle1',
                                  datetime.datetime(2015, 4, 7, 21, 1, 18),
                                  'testvideoId1',
                                   'testUploadsId1'],
                                  ['testId2-testUploadsId1',
                                  'testTitle2',
                                   datetime.datetime(2015, 3, 7, 21, 1, 18),
                                   'testvideoId2',
                                   'testUploadsId1'],
                                  ['testId3-testUploadsId1',
                                   'testTitle3',
                                   datetime.datetime(2015, 2, 7, 21, 1, 18),
                                   'testvideoId3',
                                   'testUploadsId1'],
                                  ['testId1-testUploadsId2',
                                   'testTitle1',
                                   datetime.datetime(2015, 4, 7, 21, 1, 18),
                                   'testvideoId1',
                                   'testUploadsId2'],
                                  ['testId2-testUploadsId2',
                                   'testTitle2',
                                   datetime.datetime(2015, 3, 7, 21, 1, 18),
                                   'testvideoId2',
                                   'testUploadsId2'],
                                  ['testId3-testUploadsId2',
                                   'testTitle3',
                                   datetime.datetime(2015, 2, 7, 21, 1, 18),
                                   'testvideoId3',
                                   'testUploadsId2'])
