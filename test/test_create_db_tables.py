import os
import subprocess
import time
import logging
import pytest
from src.stage1.db_connection import get_connection
from src.stage1.create_db_tables import create_tables, destroy_tables

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


def test_create_tables_create_tables_with_correct_columns(pg_container):
    conn = get_connection(database_credentials)
    destroy_tables(conn)
    create_tables(conn)
    table_names = conn.run("""
                        SELECT table_name FROM information_schema.tables
                        WHERE table_schema = 'yt'
                """)
    watch_channels_columns = conn.run("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_schema = 'yt'
                        AND table_name = 'watch_channels';
                """)
    statistics_columns = conn.run("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_schema = 'yt'
                        AND table_name = 'statistics';
                """)
    status_columns = conn.run("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_schema = 'yt'
                        AND table_name = 'status';
                """)
    videos_columns = conn.run("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_schema = 'yt'
                        AND table_name = 'videos';
                """)

    assert table_names == (
        ['watch_channels'],
        ['statistics'],
        ['status'],
        ['videos'])
    assert watch_channels_columns == (
        ['channel_id'],
        ['uploads_id'],
        ['title'],
        ['published_at'],
        ['country'],
        ['watch_status'],
        ['videos_fetched'])
    assert statistics_columns == (
        ['channel_id'],
        ['view_count'],
        ['subscriber_count'],
        ['hidden_subscriber_count'],
        ['video_count'])
    assert status_columns == (
        ['channel_id'],
        ['privacy_status'],
        ['is_linked'],
        ['long_uploads_status'])
    assert videos_columns == (
        ['id'],
        ['title'],
        ['video_published_at'],
        ['video_id'],
        ['list_id'])


def test_delete_tables_can_work(pg_container):
    conn = get_connection(database_credentials)
    destroy_tables(conn)
    table_names = conn.run("""
                        SELECT table_name FROM information_schema.tables
                        WHERE table_schema = 'yt'
                """)
    assert table_names == ()
