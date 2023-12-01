import json
from pprint import pprint

# Specify the file path
file_path = "./data_example/listof_channels.json"

# Open the file and load the JSON data into a dictionary
with open(file_path, "r") as file:
    payload = json.load(file)

# Now you can use the 'data' dictionary
# print(payload)

{'items':[{
    'id': x['id']['channelId'],
    'title':x['snippet']['title'],
    'publishedAt':x['snippet']['publishedAt'],
} for x in payload['items']]}

pprint(items)