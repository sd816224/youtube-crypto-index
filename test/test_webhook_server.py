from src.webhook_server import parse_filter_notification
from src.db_connection import get_connection
from src.create_db_tables import create_tables, destroy_tables
from src.load_db_tables import load_channels_table, load_videos_table
import time_machine
import pytest
import subprocess
import time
import os
import json


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


@time_machine.travel("2023-12-14 00:00:00")
def test_parse_filter_notification_all_new_uploads(pg_container):

    conn = get_connection(
        {
            'RDS_USERNAME': 'testuser',
            'RDS_HOSTNAME': 'localhost',
            'DS_DB_NAME': 'testdb',
            'RDS_PORT': 5433,
            'RDS_PASSWORD': 'testpass',
        })
    create_tables(conn)
    sample_ready_channels_list = read_json_file(
        "test/sample_ready_channel_list.json")
    load_channels_table(conn, sample_ready_channels_list)
    notification = read_json_file('./test/sample_notification.json')
    result = parse_filter_notification(conn, notification)
    assert result == [{'id': 'test_video_id_1-2023-Dec-14 00:00:00',
                       'list_id': 'UU_test_id3',
                      'title': 'test_title1',
                       'videoId': 'test_video_id_1',
                       'videoPublishedAt': '2023-12-14T03:00:03+00:00'},
                      {'id': 'test_video_id_2-2023-Dec-14 00:00:00',
                      'list_id': 'UU_test_id3',
                       'title': 'test_title2',
                       'videoId': 'test_video_id_2',
                       'videoPublishedAt': '2023-12-14T01:00:12+00:00'},
                      {'id': 'test_video_id_3-2023-Dec-14 00:00:00',
                      'list_id': 'UU_test_id3',
                       'title': 'test_title3',
                       'videoId': 'test_video_id_3',
                       'videoPublishedAt': '2023-12-13T23:00:44+00:00'},
                      {'id': 'test_video_id_4-2023-Dec-14 00:00:00',
                       'list_id': 'UU_test_id3',
                       'title': 'test_title4',
                       'videoId': 'test_video_id_4',
                       'videoPublishedAt': '2023-12-13T21:00:27+00:00'},
                      {'id': 'test_video_id_5-2023-Dec-14 00:00:00',
                       'list_id': 'UU_test_id3',
                       'title': 'test_title5',
                       'videoId': 'test_video_id_5',
                       'videoPublishedAt': '2023-12-13T19:00:14+00:00'}]
    conn.close()


def test_parse_filter_notification_if_video_exists(pg_container):
    conn = get_connection(
        {
            'RDS_USERNAME': 'testuser',
            'RDS_HOSTNAME': 'localhost',
            'DS_DB_NAME': 'testdb',
            'RDS_PORT': 5433,
            'RDS_PASSWORD': 'testpass',
        })
    destroy_tables(conn)
    create_tables(conn)
    sample_ready_channels_list = read_json_file(
        "test/sample_ready_channel_list.json")
    load_channels_table(conn, sample_ready_channels_list)
    notification = read_json_file('./test/sample_notification.json')
    video_list = parse_filter_notification(conn, notification)
    load_videos_table(conn, video_list)
    result = parse_filter_notification(conn, notification)
    assert result == []
    conn.close()


def test_parse_filter_notification_get_name_changing_feed(pg_container):
    conn = get_connection(
        {
            'RDS_USERNAME': 'testuser',
            'RDS_HOSTNAME': 'localhost',
            'DS_DB_NAME': 'testdb',
            'RDS_PORT': 5433,
            'RDS_PASSWORD': 'testpass',
        })
    destroy_tables(conn)
    create_tables(conn)
    sample_ready_channels_list = read_json_file(
        "test/sample_ready_channel_list.json")
    load_channels_table(conn, sample_ready_channels_list)
    notification = read_json_file('./test/sample_notification.json')
    video_list = parse_filter_notification(conn, notification)
    load_videos_table(conn, video_list)
    name_changing_feed = read_json_file(
        './test/sample_notification_change_name_feed.json')
    result = parse_filter_notification(conn, name_changing_feed)
    assert result == []
    conn.close()


def test_parse_filter_notification_deletion_feed(pg_container):
    conn = get_connection(
        {
            'RDS_USERNAME': 'testuser',
            'RDS_HOSTNAME': 'localhost',
            'DS_DB_NAME': 'testdb',
            'RDS_PORT': 5433,
            'RDS_PASSWORD': 'testpass',
        })
    destroy_tables(conn)
    create_tables(conn)
    sample_ready_channels_list = read_json_file(
        "test/sample_ready_channel_list.json")
    load_channels_table(conn, sample_ready_channels_list)
    notification = read_json_file('./test/sample_notification.json')
    video_list = parse_filter_notification(conn, notification)
    load_videos_table(conn, video_list)
    name_changing_feed = read_json_file(
        './test/sample_notification_deletion_feed.json')
    result = parse_filter_notification(conn, name_changing_feed)
    assert result == []
    conn.close()
