import logging
from load_db_tables import load_videos_table
from db_connection import get_connection
import xmltodict
from xml.parsers.expat import ExpatError
from flask import Flask, request
import flask
import json
import datetime as dt
import sys
import os
from dotenv import load_dotenv

# from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

src_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(src_path)

from dash import Dash,html
from dash import dcc
from dash import Input, Output
# import dash_bootstrap_components as dbc
# import plotly.express as px
import plotly.graph_objects as go
from db_connection import get_connection

import pandas as pd
# import numpy as np
import requests
from dotenv import load_dotenv
import os
load_dotenv()


app_flask = Flask(__name__)
app_dash = Dash(__name__,server=app_flask)

@app_flask.route('/plotly_dashboard') 
def render_dashboard():
    return flask.redirect('/dash')

app = DispatcherMiddleware(app_flask, {
    '/dash': app_dash.server,
})

app_dash.layout = html.Div([
    html.H1('Youtube-Crypto-Index'),
    html.Div(id="new_video_container"),
    dcc.Graph(id='candles'),
    dcc.Interval(id='page_refresh_interval', interval=2000),
    html.H1(id='count_up'),
])
conn = get_connection(
    {
        'RDS_USERNAME': os.getenv('RDS_USERNAME'),
        'RDS_HOSTNAME': os.getenv('RDS_HOSTNAME'),
        'RDS_DB_NAME': os.getenv('RDS_DB_NAME'),
        'RDS_PORT': os.getenv('RDS_PORT'),
        'RDS_PASSWORD': os.getenv('RDS_PASSWORD'),
    }
)

def query_latest_videos(conn):
    content = conn.run(
        'select title,video_published_at,video_id from yt.videos order by video_published_at desc limit 20')  # noqa
    titles = [i[0] for i in content]
    published_at = [i[1].strftime("%Y-%m-%d %H:%M:%S") for i in content]
    video_id = [i[2] for i in content]
    return titles, published_at, video_id


@app_dash.callback(
    Output('candles', 'figure'),
    Output('count_up', 'children'),
    Output('new_video_container', 'children'),
    Input('page_refresh_interval', 'n_intervals')
)
def update_figure(n_intervals):

    url = 'https://www.bitstamp.net/api/v2/ohlc/btcusd/'
    params = {
        'step': '60',
        'limit': '30',
    }
    try:

        data = requests.get(url, params=params).json()['data']['ohlc']
        data = pd.DataFrame(
            data,
            columns=[
                'timestamp',
                'open',
                'high',
                'low',
                'close'])
        data.timestamp = data.timestamp.astype(int)
        data.timestamp = pd.to_datetime(data.timestamp, unit='s')
        candles = go.Figure(
            data=[
                go.Candlestick(
                    x=data.timestamp,
                    open=data.open,
                    high=data.high,
                    low=data.low,
                    close=data.close,
                )])
        titles, published_at, video_id = query_latest_videos(conn)
        video_links = [html.A(video_id, href=f"https://www.youtube.com/watch?v={video_id}", target="_blank") for video_id in video_id]  # noqa
        new_video_table = html.Table([
        html.Caption("New uploaded Videos", style={"font-size": "28px", "font-weight": "bold"}),  # noqa
        html.Thead(html.Tr([html.Th("published_at"), html.Th("titles"), html.Th("video_links")])),  # noqa
        html.Tbody([html.Tr([html.Td(a), html.Td(b), html.Td(c)]) for a, b, c in zip(published_at, titles, video_links)])])# noqa
    except Exception as e:
        print(e)

    return candles, n_intervals, new_video_table


@app_flask.route('/feed', methods=['GET', 'POST'])
def webhook():
    print('>>>>>>>>>>>>coming to backend<<<<<<<<<<<<<<<<<')
    load_dotenv()
    # config
    # path_name
    work_on_remote_db = True

    challenge = request.args.get('hub.challenge')
    if challenge:
        return challenge
    try:
        xml_dict = xmltodict.parse(request.data)

        # Save the dictionary to a JSON file

        document_prefix = str(dt.datetime.now())[:16]
        file_name = f'./feed_example/notification_{document_prefix}.json'
        save_json(xml_dict, file_name)
        logger.info('notification saved to json file')

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

        listof_videos = parse_filter_notification(conn, xml_dict)
        logger.info('listof_videos parsed: %s', listof_videos)
        if listof_videos:
            load_videos_table(conn, listof_videos)
            logger.info('load_videos_table done')

        conn.close()

    except (ExpatError, LookupError):
        return "", 403

    return "", 204


def save_json(input, file_name):
    with open(file_name, 'w') as file:
        json.dump(input, file, indent=4)
    logger.info('json file done: %s', file_name)


def video_not_exists(conn, video_id):
    '''check if video already exists in the db
    args:
        conn(obj): db connection
        video_id(str): video id
    return:
        True if video not exists in the db
        False if video does already exist in the db
    '''
    result = conn.run(f"SELECT * FROM yt.videos WHERE video_id='{video_id}'")
    return True if len(result) == 0 else False


def parse_filter_notification(conn, notification):
    '''parse the notification json.
    filter out the videos that already exists in the db.
    return a list of videos to be inserted into the db
    args:
        conn(obj): db connection
        notification(dict): notification json
    return:
        videos_insertion_content(list):
        list of video objects to be inserted into the db
    '''

    """ entry in the notification feed is
    list if multiple result.
    dict if single result.
    channel_id starts by UC and list id starts by UU.
    the following looksthe same"""
    videos_ = notification['feed'].get('entry')
    videos_insertion_content = []
    if isinstance(videos_, list):
        for video in videos_:
            # skip if video already exists
            if not video_not_exists(conn, video['yt:videoId']):
                logger.info('video loading skipped as its already exists in the db: %s', video['yt:videoId'])  # noqa E501
                continue
            video_row = {
                'id': video['yt:videoId'] + dt.datetime.now().strftime("-%Y-%b-%d %H:%M:%S"),  # noqa E501
                'title': video['title'],
                'videoPublishedAt': video['published'],
                'videoId': video['yt:videoId'],
                # replace UC with UU to get the list id
                'list_id': video['yt:channelId'].replace('UC', 'UU', 1)
            }
            videos_insertion_content.append(video_row)
        return videos_insertion_content
    elif isinstance(videos_, dict) and video_not_exists(conn, videos_['yt:videoId']):  # noqa E501
        video_row = {
            'id': videos_['yt:videoId'] + dt.datetime.now().strftime("-%Y-%b-%d %H:%M:%S"),  # noqa E501
            'title': videos_['title'],
            'videoPublishedAt': videos_['published'],
            'videoId': videos_['yt:videoId'],
            # replace UC with UU to get the list id
            'list_id': videos_['yt:channelId'].replace('UC', 'UU', 1)
        }
        videos_insertion_content.append(video_row)
        return videos_insertion_content
    else:
        logger.info('video loading skipped as exist/not valid')
        return []


if __name__ == '__main__':
    """
    dashboard nevery write db. read only.
    dashboard nevery write db. read only.
    dashboard nevery write db. read only.
    dashboard nevery write db. read only.
    dashboard nevery write db. read only.
    dashboard nevery write db. read only.
    """
    logging.basicConfig()
    logger = logging.getLogger('dashboard')
    logger.setLevel(logging.WARN)

    run_simple('0.0.0.0', 8050, app, use_reloader=True, use_debugger=True)
    # conn.close()
