import os
import subprocess
import time
import logging
import pytest
from src.stage1.db_connection import get_connection
from src.stage1.load_db_tables import load_channels_table, load_videos_table
from src.stage1.create_db_tables import create_tables
import datetime

logging.basicConfig()
logger = logging.getLogger("MyLogger")
logger.setLevel(logging.INFO)


database_credentials = {
    "RDS_USERNAME": "testuser",
    "RDS_PASSWORD": "testpass",
    "DS_DB_NAME": "testdb",
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


def test_load_videos_can_work(pg_container):
    conn = get_connection(database_credentials)
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
    video_conent = {
        "items": [
            {
                "id": "testId1",
                "title": "testTitle1",
                "videoPublishedAt": "2023-12-03T17:01:00Z",
                "videoId": "testVideoId1",
                "channel_id": "testChannelId1"
            },
            {
                "id": "testId2",
                "title": "testTitle2",
                "videoPublishedAt": "2023-12-01T18:09:35Z",
                "videoId": "testVideoId2",
                "channel_id": "testChannelId1"
            },
            {
                "id": "testId3",
                "title": "testTitle3",
                "videoPublishedAt": "2023-12-01T18:09:35Z",
                "videoId": "testVideoId3",
                "channel_id": "testChannelId2"
            },
        ]}
    create_tables(conn)
    load_channels_table(conn, channel_content)
    load_videos_table(conn, video_conent['items'])
    video_conent_result = conn.run("""select * from yt.videos""")
    assert video_conent_result == (
        [
            'testId1', 'testTitle1', datetime.datetime(
                2023, 12, 3, 17, 1), 'testVideoId1', 'testChannelId1'], [
            'testId2', 'testTitle2', datetime.datetime(
                2023, 12, 1, 18, 9, 35), 'testVideoId2', 'testChannelId1'], [
            'testId3', 'testTitle3', datetime.datetime(
                2023, 12, 1, 18, 9, 35), 'testVideoId3', 'testChannelId2'])
