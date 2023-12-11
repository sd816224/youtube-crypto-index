
# from pprint import pprint
# import logging
# import sys
# import os
# import json
# from dotenv import load_dotenv

# def read_json_file(file_path):
#     with open(file_path, 'r') as file:
#         data = json.load(file)
#     return data


# data=read_json_file('data_example/debug_stage1_list_channels_return_2.json') # noqa E501

# # pprint(data)      

# LL=[i['id'] for i in data]
# pprint(LL)
# print(len(LL))
# print(len(set(LL)))

# while len(LL)>0:
#       x=LL.pop()
#       if x in LL:
#             print(x)

for i in range(10):
      if i==5:
        continue  
      print(i)