# from src.dashboard import query_latest_videos
# from src.dashboard import query_latest_videos
# from src.dashboard import parse_filter_notification
# from src.dashboard import fetch_btc_bars
# from src.db_connection import get_connection
# from src.create_db_tables import create_tables, destroy_tables
# from src.load_db_tables import load_channels_table, load_videos_table

import subprocess
import time
import os
import json
import pytest

from dotenv import load_dotenv
load_dotenv()


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


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


# def test_query_latest_videso(pg_container):
#     conn = get_connection(
#     {
#         'RDS_USERNAME': 'testuser',
#         'RDS_HOSTNAME': 'localhost',
#         'RDS_DB_NAME': 'testdb',
#         'RDS_PORT': 5433,
#         'RDS_PASSWORD': 'testpass',
#     })
#     destroy_tables(conn)
#     create_tables(conn)
#     sample_ready_channels_list = read_json_file(
#         "test/sample_ready_channel_list.json")
#     load_channels_table(conn, sample_ready_channels_list)
#     notification = read_json_file('./test/sample_notification.json')
#     video_list = parse_filter_notification(conn, notification)
#     load_videos_table(conn, video_list)
#     result = query_latest_videos(conn)

#     from pprint import pprint
#     pprint(result)
#     assert 1==1

# def test_merge_query_to_btc_bars(pg_container):
#     conn = get_connection(
#         {
#             'RDS_USERNAME': os.getenv('RDS_USERNAME'),
#             'RDS_HOSTNAME': os.getenv('RDS_HOSTNAME'),
#             'RDS_DB_NAME': os.getenv('RDS_DB_NAME'),
#             'RDS_PORT': os.getenv('RDS_PORT'),
#             'RDS_PASSWORD': os.getenv('RDS_PASSWORD'),
#         }
#     )

#     result = merge_query_to_btc_bars(conn,'day','30')
#     assert result == 1

# def test_fetch_btc_bars():
#     result=fetch_btc_bars()
#     from pprint import pprint
#     pprint(result)
#     assert result==1

# def test_query_latest_videos():
#     conn = get_connection(
#         {
#             'RDS_USERNAME': os.getenv('RDS_USERNAME'),
#             'RDS_HOSTNAME': os.getenv('RDS_HOSTNAME'),
#             'RDS_DB_NAME': os.getenv('RDS_DB_NAME'),
#             'RDS_PORT': os.getenv('RDS_PORT'),
#             'RDS_PASSWORD': os.getenv('RDS_PASSWORD'),
#         }
#     )

#     result = query_latest_videos(conn)
#     assert result == 1
