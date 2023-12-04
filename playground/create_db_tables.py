from db_connection import get_connection
import logging
import os
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig()
logger = logging.getLogger('create_db_tables')
logger.setLevel(logging.INFO)


conn=get_connection(
    {
        'RDS_USERNAME': os.getenv('RDS_USERNAME'),
        'RDS_HOSTNAME': os.getenv('RDS_HOSTNAME'),
        'DS_DB_NAME': os.getenv('DS_DB_NAME'),
        'RDS_PORT': os.getenv('RDS_PORT'),
        'RDS_PASSWORD': os.getenv('RDS_PASSWORD'),
    }
)

def create_tables(conn):

    # try:
    conn.run(f"""
                      CREATE SCHEMA IF NOT EXISTS yt;
                      """)
    logger.info('create schema')
    
    conn.run(f"""
                      CREATE TABLE IF NOT EXISTS yt.watch_channels(
                        id SERIAL PRIMARY KEY,
                        date DATE,
                        open NUMERIC,
                        high NUMERIC,
                        low NUMERIC,
                        close NUMERIC,
                        volume NUMERIC,
                        market_cap NUMERIC
                      );
                      """)
    logger.info('create table: yt.watch_channels [column_name,dadta_type]')

    result=conn.run(f"""
                        SELECT column_name,data_type FROM information_schema.columns
                        WHERE table_schema = 'yt'
                        AND table_name = 'watch_channels';
                """)
    logger.info(result)




def check_table(conn):
    result=conn.run(f"""
                        SELECT column_name,data_type FROM information_schema.columns
                        WHERE table_schema = 'yt'
                        AND table_name = 'watch_channels';
                """)
    logger.info('yt.watch_channels: [column_name,dadta_type]')
    logger.info(result)

def destroy_tables(conn):
    conn.run('DROP TABLE IF EXISTS yt.watch_channels;')
    logger.info('destroy yt.watch_channels table')
    result = conn.run('DROP SCHEMA IF EXISTS yt;')
    logger.info('destroy yt schema')


create_tables(conn)
# check_table(conn)
# destroy_tables(conn)


conn.close()