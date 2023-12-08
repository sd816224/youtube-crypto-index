# import time

# def iteratr_channels():

#     # select channel from db. until no more video_fetched is false
#     # result= select query limit = 1.
#     # while result not None:


#     for i in range(10):
#         print('get the channel **********', i)
#         video_list=search_video()  #pass 1 channel_id everytime into search_video. let it work.
#         write_video(video_list)
    

# def search_video(): # 
#     print('search_video from api')
#     return ['video1', 'video2', 'video3']

# def write_video(video_list):
#     print('write_video to db',video_list)

# iteratr_channels()

import requests
headers={
        "authority": "pubsubhubbub.appspot.com",
        "cache-control": "max-age=0",
        "origin": "https://pubsubhubbub.appspot.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "referer": "https://pubsubhubbub.appspot.com/subscribe",
        "accept-language": "en-US,en;q=0.9",
    }
params = (
        ('hub.callback', 'https://8ac3-86-1-59-63.ngrok-free.app'),
        ('hub.topic','https://www.youtube.com/xml/feeds/videos.xml?channel_id=UC30CiUvwTY9dV6FUkPeh2iQ'),
        ('hub.secret', ''),
    )

response = requests.get(
            'https://pubsubhubbub.appspot.com/subscription-details', headers=headers, params=params
        )

print(response.text)