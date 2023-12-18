from dash import Dash, dcc, html
# from dash import Input, Output
# import dash_bootstrap_components as dbc
# import plotly.express as px
# import plotly.graph_objects as go
from db_connection import get_connection


# import pandas as pd
# import numpy as np
# import requests
from dotenv import load_dotenv
import os
load_dotenv()

app = Dash()
app.layout = html.Div([
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
        'DS_DB_NAME': os.getenv('DS_DB_NAME'),
        'RDS_PORT': os.getenv('RDS_PORT'),
        'RDS_PASSWORD': os.getenv('RDS_PASSWORD'),
    }
)


def query_latest_videos(conn):
    content = conn.run(
        'select title,video_published_at,video_id from yt.videos order by video_published_at desc limit 10') # noqa
    titles = [i[0] for i in content]
    published_at = [i[1].strftime("%Y-%m-%d %H:%M:%S") for i in content]
    video_id = [i[2] for i in content]
    return titles, published_at, video_id


# @app.callback(
#         Output('candles','figure'),
#         Output('count_up','children'),
#         Output('new_video_container','children'),
#         Input('page_refresh_interval','n_intervals')
#         )
# def update_figure(n_intervals):

#     url='https://www.bitstamp.net/api/v2/ohlc/btcusd/'
#     params={
#         'step':'60',
#         'limit':'30',
#         }
#     try:

#         data=requests.get(url,params=params).json()['data']['ohlc']
#         data=pd.DataFrame(data,columns=['timestamp','open','high','low','close'])
#         data.timestamp=data.timestamp.astype(int)
#         data.timestamp=pd.to_datetime(data.timestamp,unit='s')
#         candles=go.Figure(
#             data=[
#                 go.Candlestick(
#                     x=data.timestamp,
#                     open=data.open,
#                     high=data.high,
#                     low=data.low,
#                     close=data.close,
#                     )])
#         titles,published_at,video_id=query_latest_videos(conn)
#         video_links=[html.A(video_id,href=f"https://www.youtube.com/watch?v={video_id}",target="_blank") for video_id in video_id] # noqa
#         new_video_table = html.Table([
#         html.Caption("New uploaded Videos",style={"font-size": "28px", "font-weight": "bold"}), # noqa
#         html.Thead(html.Tr([ html.Th("published_at"), html.Th("titles"), html.Th("video_links")])), # noqa
#         html.Tbody([html.Tr([html.Td(a), html.Td(b), html.Td(c)]) for a,b,c in zip(published_at,titles,video_links)]) # noqa
#     ])
#     except Exception as e:
#         print(e)

#     return candles,n_intervals,new_video_table


if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0")
    # conn.close()
