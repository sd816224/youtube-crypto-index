import requests
import html_to_json
import logging
import json
import time
import datetime
import sys
import os
from dotenv import load_dotenv
src_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(src_path)
from db_connection import get_connection  # noqa E402

logging.basicConfig()
logger = logging.getLogger("sub_manager")
logger.setLevel(logging.INFO)


def save_json(input, file_name):
    with open(file_name, 'w') as file:
        json.dump(input, file, indent=4)
    logger.info('json file done: %s', file_name)


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def health_check(callback_url, channel_id):
    '''check subscription health. expirey date
    args:
        callback_url(str): callback_url of webhook server
        channel_id(str): channel id
    return:
        health_report(dict): health report of the channel
    '''
    headers = {
        "authority": "pubsubhubbub.appspot.com",
        "cache-control": "max-age=0",
        "origin": "https://pubsubhubbub.appspot.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # noqa E501
        "referer": "https://pubsubhubbub.appspot.com/subscribe",
        "accept-language": "en-US,en;q=0.9",
    }
    params = (
        ('hub.callback', callback_url),
        ('hub.topic',
         f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"),
        ('hub.secret', ''),
    )
    response = requests.get(
        'https://pubsubhubbub.appspot.com/subscription-details',
        headers=headers,
        params=params)
    json_ = html_to_json.convert(response.text)
    column_names = [x['_value'] for x in json_['html']
                    [0]['body'][0]['section'][0]['dl'][0]['dt']]
    values = [x['_value'] for x in json_['html'][0]
              ['body'][0]['section'][0]['dl'][0]['dd']]
    health_report = {}
    for i, j in zip(column_names, values):
        health_report[i] = j
    health_report['channel_id'] = channel_id
    # save_json(health_report, "feed_example/health_report.json")
    return health_report


def sub_to_channel(callback_url, channel_id):
    '''request subscription to channel
    args:
        callback_url(str): callback_url of webhook server
        channel_id(str): channel id
    '''
    headers = {
        "authority": "pubsubhubbub.appspot.com",
        "cache-control": "max-age=0",
        "origin": "https://pubsubhubbub.appspot.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # noqa E501
        "referer": "https://pubsubhubbub.appspot.com/subscribe",
        "accept-language": "en-US,en;q=0.9",
    }

    data = {
        "hub.callback": callback_url,
        "hub.topic": f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}",  # noqa E501
        "hub.verify": "async",
        "hub.mode": "subscribe",
        "hub.verify_token": "",
        "hub.secret": "",
    }

    response = requests.post(
        'https://pubsubhubbub.appspot.com/subscribe',
        headers=headers,
        data=data)
    logger.info(
        '%s subscription request status>>> %s',
        channel_id,
        response.status_code)


def get_channel_list(conn):
    '''
    get channel list which are not subscribed ever or expiring within 1 hour

    arg:
        conn(class): pg connction instance
    return:
        list of string(list)
    '''
    # find never-subscripted channels
    query = '''
            SELECT wc.channel_id FROM yt.watch_channels wc
            LEFT JOIN
            yt.subscription sub
            ON wc.channel_id =sub.channel_id
            WHERE sub.channel_id is null; '''
    channel_list = conn.run(query)
    init_channel_list = [item[0] for item in channel_list]
    logger.info('%s of init_channel_list', len(init_channel_list))

    # find already-subscripted channels expire within 1 hour
    now = datetime.datetime.now()
    one_hour_future = now + datetime.timedelta(hours=1)
    time_line_str = one_hour_future.strftime("%Y-%b-%d %H:%M:%S")

    query2 = f'''
    select * from (
    select * , ROW_NUMBER() over (partition by channel_id order by expiration_time DESC) as row_num
    from yt.subscription s ) subquery
    where row_num =1 and expiration_time < '{time_line_str}'
    '''  # noqa E501
    channel_list2 = conn.run(query2)
    expire_channel_list = [item[0] for item in channel_list2]
    logger.info('%s of expire_channel_list', len(expire_channel_list))
    total_sub_list = init_channel_list + expire_channel_list
    return total_sub_list


def load_subscription_table(conn, health_report_aggregate):
    '''
    load health reports to subscription table
    arg:
        conn(class): pg connction instance
        health_report_aggregate(list): aggregate list of health reports
    '''
    cursor = conn.cursor()
    query = '''
    INSERT INTO yt.subscription 
    (channel_id, callback_URL, state, Last_successful_verification,expiration_time,
    Last_subscribe_request,Last_unsubscribe_request,Last_verification_error,
    Last_delivery_error,aggregate_statistics) 
    VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s)'''  # noqa E501
    data = [
        (x['channel_id'],
         x['Callback URL'],
         x['State'],
         None if x['Last successful verification'] == 'n/a' else x['Last successful verification'],  # noqa E501
         None if x['Expiration time'] == 'n/a' else x['Expiration time'],
         None if x['Last subscribe request'] == 'n/a' else x['Last subscribe request'],  # noqa E501
         None if x['Last unsubscribe request'] == 'n/a' else x['Last unsubscribe request'],  # noqa E501
         x['Last verification error'],
         x['Last delivery error'],
         x['Aggregate statistics'],
         ) for x in health_report_aggregate]
    try:
        cursor.executemany(query, data)
        print('load_subcription_table done')
    except Exception as e:
        print(e)
    conn.commit()
    cursor.close()


def sub_manager():
    '''triggered every 1hour.
    renew subscription and channel in channel_list which expiring within 1 hour.
    wait 100s and reload health check report.
    '''  # noqa E501
    load_dotenv()
    # config
    callback_url = 'https://bdc4-86-1-59-63.ngrok-free.app/feed'
    work_on_remote_db = True
    try:
        if work_on_remote_db:
            conn = get_connection(
                {
                    'RDS_USERNAME': os.getenv('RDS_USERNAME'),
                    'RDS_HOSTNAME': os.getenv('RDS_HOSTNAME'),
                    'RDS_DB_NAME': os.getenv('RDS_DB_NAME'),
                    'RDS_PORT': int(os.getenv('RDS_PORT')),
                    'RDS_PASSWORD': os.getenv('RDS_PASSWORD'),
                }
            )
        else:
            conn = get_connection(
                {
                    'RDS_USERNAME': 'testuser',
                    'RDS_HOSTNAME': 'localhost',
                    'RDS_DB_NAME': 'testdb',
                    'RDS_PORT': 5432,
                    'RDS_PASSWORD': 'testpass',
                }
            )

        channel_list = get_channel_list(conn)
        i = 1
        if len(channel_list) > 0:
            for channel_id in channel_list:
                logger.info(
                    '%s/%s : %s subscription',
                    i,
                    len(channel_list),
                    channel_id)
                i += 1
                sub_to_channel(callback_url, channel_id)
            logger.info('subscription done. cool down 100s')
            time.sleep(100)
            health_report_aggregate = []
            for channel_id in channel_list:
                logger.info('%s append health report', channel_id)
                health_report_aggregate.append(
                    health_check(callback_url, channel_id))

            load_subscription_table(conn, health_report_aggregate)
            logger.info('load_subscription_table done')
        else:
            logger.info('no channel to subscribe..')
        conn.close()

    except Exception as e:
        logger.error(e)
        logger.error('sub_manager failed')


if __name__ == '__main__':
    logging.basicConfig()
    logger = logging.getLogger('sub_manager_lambda')
    logger.setLevel(logging.INFO)

    # i = 1
    # while True:
    #     sub_manager()
    #     logger.info(f'sub_manager run {i} times. pause 1 hour')
    #     time.sleep(3600)
    #     i += 1

    sub_manager()
