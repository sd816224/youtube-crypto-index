# import time

# def iteratr_channels():

#     # select channel from db. until no more video_fetched is false
#     # result= select query limit = 1.
#     # while result not None:


#     for i in range(10):
#         print('get the channel **********', i)
        
#         yield from search_video(i)

#         # video_list=search_video()  #pass 1 channel_id everytime into search_video. let it work.
#         # write_video(video_list)


# def search_video(i): # 
#     print('search_video from api',i)
#     return ['video1', 'video2', 'video3']

# def write_video(video_list):
#     print('write_video to db',video_list)

# # channels_gen=iteratr_channels()
# # while True:
# #     search_video(next(channels_gen))    
# #     time.sleep(2)

# iteratr_channels()

import time
print(time.time())