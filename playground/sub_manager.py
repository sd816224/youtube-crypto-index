import requests
import xmltodict
import xmltojson
import html_to_json
import logging
from pprint import pprint
import json
from db_connection import get_connection
import time

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


def health_check(callback_url,channel_id):
    '''check subscription health. expirey date
    ''' 
    headers={
        "authority": "pubsubhubbub.appspot.com",
        "cache-control": "max-age=0",
        "origin": "https://pubsubhubbub.appspot.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
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
        'https://pubsubhubbub.appspot.com/subscription-details', headers=headers, params=params
    )
    json_ = html_to_json.convert(response.text)
    column_names=[x['_value'] for x in json_['html'][0]['body'][0]['section'][0]['dl'][0]['dt']]
    values=[x['_value'] for x in json_['html'][0]['body'][0]['section'][0]['dl'][0]['dd']]
    health_report={}
    for i,j in zip(column_names,values):
        health_report[i]=j
    health_report['channel_id']=channel_id
    save_json(health_report, "feed_example/health_report.json")
    return health_report
    

def sub_to_channel(callback_url,channel_id):
    '''request subscription to channel
    ''' 
    headers={
        "authority": "pubsubhubbub.appspot.com",
        "cache-control": "max-age=0",
        "origin": "https://pubsubhubbub.appspot.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "referer": "https://pubsubhubbub.appspot.com/subscribe",
        "accept-language": "en-US,en;q=0.9",
}

    data = {
        "hub.callback": callback_url,
        "hub.topic": f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}",
        "hub.verify": "async",
        "hub.mode": "subscribe",
        "hub.verify_token": "",
        "hub.secret": "",
    }

    response = requests.post('https://pubsubhubbub.appspot.com/subscribe', headers=headers, data=data)
    logger.info('%s subscription request status>>> %s',channel_id,response.status_code)





def get_channel_list(conn):
    '''
    get channel list which are not subscribed ever or expiring within 1 hour

    arg: 
        conn(class): pg connction instance
    returnL
        list of string(list)
    '''
    # find all channels which are not subscribed ever
    query='''
            SELECT wc.channel_id FROM yt.watch_channels wc 
            LEFT JOIN 
            yt.subscription sub
            ON wc.channel_id =sub.channel_id
            WHERE sub.channel_id is null; '''
    channel_list=conn.run(query)
    
    # find all channels expire within 1 hour
    # query2='''
    #     '''

    print([item[0] for item in channel_list])
    return [item[0] for item in channel_list]


def load_subscription_table(conn,health_report_aggregate):
    cursor = conn.cursor()
    query = 'INSERT INTO yt.subscription (channel_id, callback_URL, state, Last_successful_verification,expiration_time,Last_subscribe_request,Last_unsubscribe_request,Last_verification_error,Last_delivery_error,aggregate_statistics) VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s)'  # noqa E501
    data = [
        (x['channel_id'],
         x['Callback URL'],
         x['State'],
         None if x['Last successful verification']=='n/a' else x['Last successful verification'],
         None if x['Expiration time']=='n/a' else x['Expiration time'],
         None if x['Last subscribe request']=='n/a' else x['Last subscribe request'],
         None if x['Last unsubscribe request']=='n/a' else x['Last unsubscribe request'],
         x['Last verification error'],
         x['Last delivery error'],
         x['Aggregate statistics'],
        ) for x in health_report_aggregate]
    print(data)
    try:
        cursor.executemany(query, data)
        print('load_subcription_table done')
    except Exception as e:
        print(e)
    conn.commit()
    cursor.close()



def sub_manager(conn,callback_url):
    '''triggered every 1hour.
    renew subscription and channel in channel_list which expiring within 1 hour.
    '''
    channel_list=get_channel_list(conn) 
    health_report_aggregate=[]
    i=1
    for channel_id in channel_list:
        logger.info('%s/%s',i,len(channel_list))
        sub_to_channel(callback_url,channel_id)

    time.sleep(100)
    for channel_id in channel_list:
        # sub_to_channel(callback _url,channel_id)
        print(channel_id)
        health_report_aggregate.append(health_check(callback_url,channel_id))
    
    save_json(health_report_aggregate,"feed_example/health_report_aggregate.json")

    print('agg json saved')
    load_subscription_table(conn,health_report_aggregate)


conn = get_connection(
    {
        'RDS_USERNAME': 'testuser',
        'RDS_HOSTNAME': 'localhost',
        'DS_DB_NAME': 'testdb',
        'RDS_PORT': 5432,
        'RDS_PASSWORD': 'testpass',
    })
callback_url='https://7ad0-86-1-59-63.ngrok-free.app/feed'
sub_manager(conn,callback_url)
# get_channel_list(conn)
# health_report_aggregate=read_json_file("feed_example/health_report_aggregate.json")
# load_subscription_table(conn,health_report_aggregate)


# callback_url='https://7ad0-86-1-59-63.ngrok-free.app/feed'
# channel_id='UC30CiUvwTY9dV6FUkPeh2iQ'
# report=health_check(callback_url,channel_id)
# pprint(report)