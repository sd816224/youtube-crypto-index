from datetime import datetime
import json
xml_dict={'feed': {'xmlns': 'http://www.w3.org/2005/Atom'}}



import codecs
from pprint import pprint
import json

# def html_reader(html):
#     print(html)




# with open("feed_example/sample_check_health_response_1702319577.46871.html", "r") as html_file: 
#     html = html_file.read() 


f=codecs.open("feed_example/sample_check_health_response_1702319577.46871.html", 'r')
html=f.read()

# with open("feed_example/sample_check_health_response_1702319577.46871.html", "r", encoding='utf-8') as f:
#     html= f.read()

# print(html)

def save_json(input, file_name):
    with open(file_name, 'w') as file:
        json.dump(input, file, indent=4)
    logger.info('json file done: %s', file_name)


# with open("feed_example/sample_check_health_response_1702319577.46871.html", "r", encoding='utf-8') as html_file: 
#     html = html_file.read() 

save_json(json_, "feed_example/html_to_json_health_check_result.json")

