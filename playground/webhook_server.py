import xmltodict
from xml.parsers.expat import ExpatError
from flask import Flask, request
from werkzeug.local import LocalProxy   
import json

app = Flask(__name__)

@app.route('/feed', methods=['GET','POST'])

def webhook():
    challenge = request.args.get('hub.challenge')
    print('hello here')
    if challenge:
        print('hello challenge', challenge)
        return challenge
    try:
        xml_dict = xmltodict.parse(request.data)
        print(xml_dict)
        
        # Save the dictionary to a JSON file
        # with open('./data_example/notification_feed.json', 'w') as json_file:
        #     json.dump(xml_dict, json_file,indent=4)
            
    except (ExpatError, LookupError):
        return "", 403
    
    return "", 204

if __name__ == '__main__':
    app.run()

