import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig()
logger = logging.getLogger('create_db_tables')
logger.setLevel(logging.INFO)


def create_tables(conn):
    """ query database.
    create 1 schema :
      yt
    create 3 tables:
      watch_channels
      statistics
      status
    """
    conn.run("""CREATE SCHEMA IF NOT EXISTS yt;""")
    logger.info('create schema')

    conn.run("""
                      CREATE TABLE IF NOT EXISTS yt.statistics(
                        id SERIAL PRIMARY KEY,
                        view_count INT NOT NULL,
                        subscriber_count INT NOT NULL,
                        hidden_subscriber_count BOOLEAN NOT NULL,
                        video_count INT NOT NULL
                      );
                      CREATE TABLE IF NOT EXISTS yt.status(
                        id INT PRIMARY KEY ,
                        privacy_status VARCHAR NOT NULL,
                        is_linked BOOLEAN NOT NULL,
                        long_uploads_status VARCHAR NOT NULL
                      );
                      CREATE TABLE IF NOT EXISTS yt.watch_channels(
                        channel_id VARCHAR PRIMARY KEY,
                        uploads_id VARCHAR NOT NULL,
                        title VARCHAR NOT NULL,
                        published_at TIMESTAMP NOT NULL,
                        country VARCHAR NOT NULL,
                        statistic_id INT,
                        status_id INT,
                        watch_status BOOLEAN DEFAULT true,
                        videos_fetched BOOLEAN DEFAULT false,
                        FOREIGN KEY (statistic_id) REFERENCES yt.statistics(id), 
                        FOREIGN KEY (status_id) REFERENCES yt.status(id)
                      );
                      CREATE TABLE IF NOT EXISTS yt.videos(
                        id VARCHAR PRIMARY KEY,
                        title VARCHAR NOT NULL,
                        video_published_at TIMESTAMP NOT NULL,
                        video_id VARCHAR NOT NULL,
                        channel_id VARCHAR NOT NULL,
                        FOREIGN KEY (channel_id) REFERENCES yt.watch_channels(channel_id)      
                      );
                      """)  # noqa E501
    conn.commit()
    result = conn.run("""
                        SELECT column_name,data_type FROM information_schema.columns
                        WHERE table_schema = 'yt'
                        AND table_name = 'watch_channels';
                """)  # noqa E501
    logger.info('watch_channels:')
    logger.info(result)
    result = conn.run("""
                        SELECT column_name,data_type FROM information_schema.columns
                        WHERE table_schema = 'yt'
                        AND table_name = 'statistics';
                """)  # noqa E501
    logger.info('statistics:')
    logger.info(result)
    result = conn.run("""
                        SELECT column_name,data_type FROM information_schema.columns
                        WHERE table_schema = 'yt'
                        AND table_name = 'status';
                """)  # noqa E501
    logger.info('status:')
    logger.info(result)
    result = conn.run("""
                        SELECT column_name,data_type FROM information_schema.columns
                        WHERE table_schema = 'yt'
                        AND table_name = 'videos';
                """)  # noqa E501
    logger.info('videos:')
    logger.info(result)


def check_tables(conn):
    """ query database.
    check tables in yt schema: logger column name and data type
    """
    result = conn.run("""
                        SELECT * FROM information_schema.tables
                        WHERE table_schema = 'yt'
                """)
    # conn.commit()
    logger.info('yt.watch_channels: [column_name,data_type]')
    logger.info(result)


def destroy_tables(conn):
    """ query database.
    delete all 3 tables and schema
    """
    conn.run('DROP TABLE IF EXISTS yt.videos;')
    logger.info('destroy yt.videos table')

    conn.run('DROP TABLE IF EXISTS yt.watch_channels;')
    logger.info('destroy yt.watch_channels table')

    conn.run('DROP TABLE IF EXISTS yt.statistics;')
    logger.info('destroy yt.statistics table')

    conn.run('DROP TABLE IF EXISTS yt.status;')
    logger.info('destroy yt.status table')

    conn.run('DROP SCHEMA IF EXISTS yt;')
    logger.info('destroy yt schema')

    conn.commit()
