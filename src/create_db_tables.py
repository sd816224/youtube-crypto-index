import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig()
logger = logging.getLogger('create_db_tables')
logger.setLevel(logging.INFO)


def create_tables(conn):
    # try:
    conn.run("""CREATE SCHEMA IF NOT EXISTS yt;""")
    logger.info('create schema')

    conn.run("""CREATE TABLE IF NOT EXISTS yt.watch_channels(
                        id INT PRIMARY KEY NOT NULL,
                        channel_id VARCHAR NOT NULL,
                        uploads_id VARCHAR NOT NULL,
                        title VARCHAR NOT NULL,
                        published_at TIMESTAMP NOT NULL,
                        country VARCHAR NOT NULL,
                        statistic_id INT NOT NULL,
                        status_id INT NOT NULL,
                        watch_status BOOLEAN DEFAULT true
                      );
                      CREATE TABLE IF NOT EXISTS yt.statistics(
                        id SERIAL PRIMARY KEY,
                        view_count INT NOT NULL,
                        subscriber_count INT NOT NULL,
                        hidden_subscriber_count BOOLEAN NOT NULL,
                        video_count INT NOT NULL
                      );
                      CREATE TABLE IF NOT EXISTS yt.status(
                        id INT PRIMARY KEY NOT NULL,
                        privacy_status VARCHAR NOT NULL,
                        is_linked BOOLEAN NOT NULL,
                        long_uploads_status VARCHAR NOT NULL
                      );
                      """)
    logger.info(
        'create table: yt.watch_channels/statistics/status  [column_name,dadta_type]') # noqa

    result = conn.run("""
                        SELECT column_name,data_type FROM information_schema.columns
                        WHERE table_schema = 'yt'
                        AND table_name = 'watch_channels';
                """) # noqa E501

    logger.info(result)
    result = conn.run("""
                        SELECT column_name,data_type FROM information_schema.columns
                        WHERE table_schema = 'yt'
                        AND table_name = 'statistics';
                """)  # noqa E501

    logger.info(result)
    result = conn.run("""
                        SELECT column_name,data_type FROM information_schema.columns
                        WHERE table_schema = 'yt'
                        AND table_name = 'status';
                """)  # noqa E501
    logger.info(result)


def check_tables(conn):
    result = conn.run("""
                        SELECT * FROM information_schema.tables
                        WHERE table_schema = 'yt'
                """)
    logger.info('yt.watch_channels: [column_name,dadta_type]')
    logger.info(result)


def destroy_tables(conn):
    conn.run('DROP TABLE IF EXISTS yt.watch_channels;')
    logger.info('destroy yt.watch_channels table')
    # result = conn.run('DROP SCHEMA IF EXISTS yt;')
    # logger.info('destroy yt schema')
