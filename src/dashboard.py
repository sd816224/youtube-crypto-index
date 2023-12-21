from dash import Dash, html
from dash import dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc
from dash import Input, Output
import plotly.graph_objects as go
from load_db_tables import load_videos_table
from db_connection import get_connection
from dotenv import load_dotenv
import datetime as dt
import pandas as pd
import requests
import logging
import sys
import os
import json
import flask
from flask import Flask, request
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from xml.parsers.expat import ExpatError
import xmltodict
src_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(src_path)


src_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(src_path)

# import numpy as np
load_dotenv()
conn = get_connection(
    {
        'RDS_USERNAME': os.getenv('RDS_USERNAME'),
        'RDS_HOSTNAME': os.getenv('RDS_HOSTNAME'),
        'RDS_DB_NAME': os.getenv('RDS_DB_NAME'),
        'RDS_PORT': os.getenv('RDS_PORT'),
        'RDS_PASSWORD': os.getenv('RDS_PASSWORD'),
    }
)

app_flask = Flask(__name__)
app_dash = Dash(
    __name__,
    server=app_flask,
    external_stylesheets=[
        dbc.themes.DARKLY])


@app_flask.route('/plotly_dashboard')
def render_dashboard():
    return flask.redirect('/dash')


app = DispatcherMiddleware(app_flask, {
    '/dash': app_dash.server,
})


def query_latest_videos(conn):
    content = conn.run(
        'select title,video_published_at,video_id from yt.videos order by video_published_at desc limit 50')  # noqa
    titles = [i[0] for i in content]
    published_at = [i[1].strftime("%Y-%m-%d %H:%M:%S") for i in content]
    video_list = [i[2] for i in content]
    video_links = [
        f'[{item}](https://www.youtube.com/watch?v={item})' for item in video_list]  # noqa
    df = pd.DataFrame(
        {
            'published_at': published_at,
            'title': titles,
            'video_link': video_links
        })
    return df.to_dict('records')


def create_dropdown(option, id):
    return html.Div(
        [
            html.Label(id),
            dcc.Dropdown(option, option[0], id=id, clearable=False)
        ]
    )


tblcols = [
    {'name': 'published_at', 'id': 'published_at'},
    {'name': 'title', 'id': 'title'},
    {'name': 'video_link', 'id': 'video_link', 'presentation': 'markdown'},
]

app_dash.layout = html.Div([
    html.H1('Youtube-Crypto-Index (YCI)', style={"font-size": "65px", "font-weight": "bold"}), # noqa
    dbc.Row(
        dbc.Col(
            html.H2("Latest cryptocurrency-related videos", style={"font-size": "28px", "font-weight": "bold"}), # noqa
            width={"offset": 3},
        )
    ),
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id="new_video_container",
                data=query_latest_videos(conn),
                columns=tblcols,
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'
                    },
                style_data={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white',
                        'whiteSpace': 'normal'
                    },
                page_size=10,
                page_current=0,
            ),
        ], width=8),
    ]),
    html.Div([
        create_dropdown(['day', 'hour'], id='timeframe'),
        create_dropdown(['30', '60', '120', '240', '480'], id='bar_nums'),
    ],style={'display': 'flex', 'margin': 'auto', 'justify-content': 'flex-start'}, # noqa
    ),
    dcc.Graph(id='candles'),
    dcc.Graph(id='index'),
    dcc.Interval(id='page_refresh_interval', interval=5000),
    html.H1(id='count_up')
])


@app_dash.callback(
    Output('count_up', 'children'),
    Output('candles', 'figure'),
    Output('index', 'figure'),
    Output('new_video_container', 'data'),
    Input('page_refresh_interval', 'n_intervals'),
    Input('timeframe', 'value'),
    Input('bar_nums', 'value'),
)
def update_figure(n_intervals, timeframe, bar_nums):
    try:
        data = merge_query_to_btc_bars(conn, timeframe, bar_nums)
        candles = go.Figure(
            data=[
                go.Candlestick(
                    x=data.timestamp,
                    open=data.open,
                    high=data.high,
                    low=data.low,
                    close=data.close,
                )])
        candles.update_layout(
            xaxis_rangeslider_visible=False,
            height=400, width=1000,
            title_text="BTC/USD",
            template='plotly_dark',
        )

        index = px.line(x=data.timestamp, y=data['count'], height=300)
        index.update_layout(
            height=300, width=1000,
            title_text="YCI",
            template='plotly_dark',
        )

    except Exception as e:
        print(e)

    # return candles,index, n_intervals, new_video_table
    return n_intervals, candles, index, query_latest_videos(conn)


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
        # document_prefix = str(dt.datetime.now())[:16]
        # file_name = f'./feed_example/notification_{document_prefix}.json'
        # save_json(xml_dict, file_name)
        # logger.info('notification saved to json file')

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


def merge_query_to_btc_bars(conn, timeframe, bar_nums):
    query = f"""
            select * from (select
            date_trunc('{timeframe}',video_published_at) as interval_up,
            count(video_id) as count
            from yt.videos
            group by interval_up
            order by interval_up desc) prim_table
            where interval_up > NOW()-interval '{bar_nums} {timeframe.upper()}';
        """ # noqa E501
    content = conn.run(query)
    df = pd.DataFrame({
        "timestamp": [i[0] for i in content],
        'count': [i[1] for i in content]
    }
    )
    btc_df = fetch_btc_bars(timeframe, bar_nums)
    merged_df = pd.merge(df, btc_df, on='timestamp', how='right').fillna(0)
    return merged_df


def fetch_btc_bars(timeframe, bar_nums):
    interval_dict = {
        'minute': 60,
        'hour': 3600,
        'day': 86400
    }

    url = 'https://www.bitstamp.net/api/v2/ohlc/btcusd/'
    params = {
        'step': interval_dict[timeframe],
        'limit': int(bar_nums),
    }
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
    return data


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
