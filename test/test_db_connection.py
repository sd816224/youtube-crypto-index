import os
import subprocess
import time
import logging
import pytest
from pg8000 import DatabaseError, InterfaceError
from src.db_connection import get_connection

logger = logging.getLogger("MyLogger")
logger.setLevel(logging.INFO)


@pytest.fixture(scope="module")
def pg_container():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    compose_path = os.path.join(test_dir, "docker-compose.yaml")
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
                    "local-postgres",
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


def test_get_connection_returns_correct_log_when_successful_con(
    pg_container, caplog
):  # noqa: E501
    """
    This test should return the correct log in CloudWatch,
    when passed correct details to establish connection with the database.

    Requirements:
        dictionary object with required database credentials:
        user, host, port, database, and password.
    """
    with caplog.at_level(logging.INFO):
        database_credentials = {
            "RDS_USERNAME": "testuser",
            "RDS_PASSWORD": "testpass",
            "DS_DB_NAME": "testdb",
            "RDS_HOSTNAME": "localhost",
            "RDS_PORT": 5432,
        }
        get_connection(database_credentials)
        assert (
            "Connection to database has been established."
            in caplog.text  # noqa: E501
        )


def test_get_connection_with_interface_error_no_user(pg_container):
    """
    Testing for a InterfaceError. When passed incorrect user,
    should return InterfaceError message.
    """
    with pytest.raises(InterfaceError):
        database_credentials = {
            "RDS_USERNAME": "",
            "RDS_PASSWORD": "testpass",
            "DS_DB_NAME": "testdb",
            "RDS_HOSTNAME": "localhost",
            "RDS_PORT": 5433,
        }
        get_connection(database_credentials)


def test_get_connection_with_interface_error_no_host(pg_container):
    """
    Testing for a InterfaceError. When passed incorrect host,
    should return InterfaceError message.
    """
    with pytest.raises(InterfaceError):
        database_credentials = {
            "RDS_USERNAME": "testuser",
            "RDS_PASSWORD": "testpass",
            "DS_DB_NAME": "testdb",
            "RDS_HOSTNAME": "incorrect-host",
            "RDS_PORT": 5433,
        }
        get_connection(database_credentials)


def test_for_interface_error_when_provided_incorrect_port(pg_container):
    """
    Testing for a InterfaceError. When passed incorrect port,
    should return InterfaceError log.
    """
    with pytest.raises(InterfaceError):
        database_credentials = {
            "RDS_USERNAME": "testuser",
            "RDS_PASSWORD": "testpass",
            "DS_DB_NAME": "testdb",
            "RDS_HOSTNAME": "localhost",
            "RDS_PORT": 1000,
        }
        get_connection(database_credentials)


def test_get_connection_with_database_error_incorrect_database_name(
    pg_container,
):  # noqa: E501
    """
    Testing for a DatabaseError.
    When passed incorrect database name
    should return DatabaseError.
    """
    with pytest.raises(DatabaseError):
        database_credentials = {
            "RDS_USERNAME": "testuser",
            "RDS_PASSWORD": "testpass",
            "DS_DB_NAME": "wrong-db-name",
            "RDS_HOSTNAME": "localhost",
            "RDS_PORT": 5432,
        }
        get_connection(database_credentials)


def test_get_connection_with_database_error_incorrect_password(pg_container):
    """
    Testing for a DatabaseError.
    When passed incorrect details, should return DatabaseError.
    """
    with pytest.raises(DatabaseError):
        database_credentials = {
            "RDS_USERNAME": "testuser",
            "RDS_PASSWORD": "wrong-password",
            "DS_DB_NAME": "testdb",
            "RDS_HOSTNAME": "localhost",
            "RDS_PORT": 5432,
        }
        get_connection(database_credentials)
