from src.sub_manager import get_channel_list
from src.sub_manager import load_subscription_table
from src.sub_manager import health_check
from src.db_connection import get_connection
from src.create_db_tables import create_tables, destroy_tables
from src.load_db_tables import load_channels_table
from unittest.mock import patch, Mock
import pytest
import subprocess
import time
import os
import json
import datetime
import time_machine


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


with open('./test/sample_health_response.html') as f:
    test_response = f.read()


@pytest.fixture
def mock_response():
    with patch('src.sub_manager.requests.get') as mock_get:
        response = Mock()
        mock_get.return_value = response
        response.text = test_response
        yield mock_get


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def test_health_check(mock_response):
    callback_url = 'test_url'
    channel_id = 'test_id'
    health_report = health_check(callback_url, channel_id)
    assert health_report == {
        'Aggregate statistics': '0 delivery request(s) per second to '
        '7ad0-86-1-59-63.ngrok-free.app,\n'
        '        0% errors',
        'Callback URL': 'https://7ad0-86-1-59-63.ngrok-free.app/feed',
        'Expiration time': 'Sat, 16 Dec 2023 18:23:12 +0000',
        'Last delivery error': 'n/a',
        'Last subscribe request': 'Mon, 11 Dec 2023 18:23:12 +0000',
        'Last successful verification': 'Mon, 11 Dec 2023 18:23:13 +0000',
        'Last unsubscribe request': 'n/a',
        'Last verification error': 'n/a',
        'State': 'verified',
        'channel_id': 'test_id'}  # noqa: E501


def test_get_channel_list_init_list(pg_container):
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
    channel_list = get_channel_list(conn)
    assert 'UC_test_id1' in channel_list
    assert 'UC_test_id2' in channel_list
    assert 'UC_test_id3' in channel_list
    assert 'UC_test_id4' in channel_list
    assert 'UC_test_id5' in channel_list
    conn.close()


def test_load_subscription_table(pg_container):
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
    health_report_aggregate = read_json_file(
        "test/sample_aggregate_health_report.json")
    load_subscription_table(conn, health_report_aggregate)
    result_channel_id = conn.run('select channel_id from yt.subscription;')
    result_state = conn.run('select state from yt.subscription;')
    result_callback_url = conn.run('select callback_URL from yt.subscription;')
    result_last_successful_verification = conn.run(
        'select Last_successful_verification from yt.subscription;')
    result_expiration_time = conn.run(
        'select expiration_time from yt.subscription;')
    assert result_channel_id == (
        ['UC_test_id1'],
        ['UC_test_id2'],
        ['UC_test_id3'],
        ['UC_test_id4'],
        ['UC_test_id5'])
    assert result_state == (
        ['verified'],
        ['verified'],
        ['verified'],
        ['verified'],
        ['verified'])
    assert result_callback_url == (
        ['https://7ad0-86-1-59-63.ngrok-free.app/feed'],
        ['https://7ad0-86-1-59-63.ngrok-free.app/feed'],
        ['https://7ad0-86-1-59-63.ngrok-free.app/feed'],
        ['https://7ad0-86-1-59-63.ngrok-free.app/feed'],
        ['https://7ad0-86-1-59-63.ngrok-free.app/feed'])
    assert result_expiration_time == (
        [datetime.datetime(2023, 12, 13, 22, 22, 22)],
        [datetime.datetime(2023, 12, 17, 17, 21, 27)],
        [datetime.datetime(2023, 12, 17, 17, 21, 27)],
        [datetime.datetime(2023, 12, 17, 17, 21, 28)],
        [datetime.datetime(2023, 12, 17, 17, 21, 30)])
    assert result_last_successful_verification == (
        [datetime.datetime(2023, 12, 13, 0, 0, 1)],
        [datetime.datetime(2023, 12, 12, 17, 21, 28)],
        [datetime.datetime(2023, 12, 12, 17, 21, 29)],
        [datetime.datetime(2023, 12, 12, 17, 21, 29)],
        [datetime.datetime(2023, 12, 12, 17, 21, 32)],
    )
    conn.close()


@time_machine.travel("2023-12-13 21:23:22")
def test_get_channel_list_expire_list(pg_container):
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
    health_report_aggregate = read_json_file(
        "test/sample_aggregate_health_report.json")
    load_subscription_table(conn, health_report_aggregate)
    channel_list = get_channel_list(conn)
    assert channel_list == ['UC_test_id1']
    conn.close()


@time_machine.travel("2023-12-13 07:23:22")
def test_get_channel_list_expire_list_multiple_renew(pg_container):
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
    health_report_aggregate = read_json_file(
        "test/sample_aggregate_health_report_multiple_renew.json")
    load_subscription_table(conn, health_report_aggregate)
    channel_list = get_channel_list(conn)

    from pprint import pprint
    result = conn.run('select * from yt.subscription;')
    pprint(result)

    assert channel_list == ['UC_test_id2']
    conn.close()
