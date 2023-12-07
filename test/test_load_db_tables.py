# import os
# import subprocess
# import time
# import logging
# import pytest
# from pg8000 import DatabaseError, InterfaceError
# from docker_testing_db_fixture import pg_container
# from src.db_connection import get_connection
# from src.load_db_tables import load_channels_table

# logging.basicConfig()
# logger = logging.getLogger("MyLogger")
# logger.setLevel(logging.INFO)

# database_credentials = {
#             "RDS_USERNAME": "testuser",
#             "RDS_PASSWORD": "testpass",
#             "DS_DB_NAME": "testdb",
#             "RDS_HOSTNAME": "localhost",
#             "RDS_PORT": 5433,
#         }

# def test_load_channel_can_work(pg_container):
#     conn=get_connection(database_credentials)
#     conent=[
#     {
#         "id": "UC61jC9ggxeGu8HJ9Q_TxOGg",
#         "title": "BITCOIN",
#         "publishedAt": "2013-09-06T02:12:33Z",
#         "country": "CA",
#         "uploads_id": "UU61jC9ggxeGu8HJ9Q_TxOGg",
#         "statistics": {
#             "viewCount": "1424394",
#             "subscriberCount": "67200",
#             "hiddenSubscriberCount": False,
#             "videoCount": "218"
#         },
#         "status": {
#             "privacyStatus": "public",
#             "isLinked": True,
#             "longUploadsStatus": "longUploadsUnspecified",
#             "madeForKids": False
#         }
#     },
#     {
#         "id": "UC-0Hk4yjo7pfxrRq9vJke-Q",
#         "title": "BalkanTech Crypto",
#         "publishedAt": "2015-05-07T21:01:18Z",
#         "country": "RS",
#         "uploads_id": "UU-0Hk4yjo7pfxrRq9vJke-Q",
#         "statistics": {
#             "viewCount": "9151281",
#             "subscriberCount": "61800",
#             "hiddenSubscriberCount": False,
#             "videoCount": "818"
#         },
#         "status": {
#             "privacyStatus": "public",
#             "isLinked": True,
#             "longUploadsStatus": "longUploadsUnspecified",
#             "madeForKids": False
#         }
#     }]
#     load_channels_table(conn,conent)
#     assert 1==1
