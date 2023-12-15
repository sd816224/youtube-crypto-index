this project generates live stream of crypto related videos uploaded.
consists of following parts: 
- 1: init_db: fetch the existing data from API and store to database accordingly.
- 2: webhook_server: receiving and responding feed of the new video notification
- 3: sub_manager : managment of channels subscription. 
- 4: display: implement to website for virtulization
- 5: deployment: build CICD pipe for above 1-4 parts to AWS cloud.

once we had big enough quality data, we potential can build extra features for NLP/ML in the future. 

guidance for colabrators:
# 1. init_db 
- clone the repo
- create enviroment params file: src/.env. config it as src/.env.example:
    - create your own google api key for google_api_key (enable youtube bigdata v3 and create key)
    - config when you have your postgres database ready, otherwise comment out: DS_DB_NAME. RDS_USERNAME. RDS_PASSWORD. RDS_HOSTNAME. RDS_PORT

- setup docker for dev&testing:  
    - make sure running docker application. for dev stage with local-dev-d    - spin up the container by CLI ``` docker-compose -f ./src/docker-compose-dev.yaml up -d```
    - make sure dev db use port 5432, testing db use port 5433.
    - if docker command not found. try to refresh in desktop application.
    - for checking the background container: ``` docker ps```
    - for stopping the container at the end:``` $ docker-compose -f ./src/docker-compose-dev.yaml down ```

- config in init_db.py:
    - reset_db_only: only turn is on when needing to reset database and run src/init_db.py
    - work_on_remote_db: #only turen is on after config the real postgres database and work on it. otherwise its defaulty set to work with local-dev-db container.
    - channel_pages_to_search: amount of channels to fetch when searching. No=page*maxResult(its set as 5 defaulty now)
    - q: keyword to search for channels
    - maxResults_channels: max result for each search page of channels (1-50)
    - maxResults_videos: max result for each search page of videos (1-50)

- run following, it setup database and populate channals and videos data into relavent tables. Caution: it will take your api quota and time depends on your configuration.
    - ```python src/init_db.py```

# 2. webhook_server
- dev config
    - setup ngrok with credential,run it for port 5000. 
    - config in webhook_server.py:
        - work_on_remote_db: #only turen is on after config the real postgres database and work on it. otherwise its defaulty set to work with local-dev-db container.
    - run server by :```python src/webhook_server.py``` 

# 3. sub_manager
- dev config:
    - callback_url: get it from ngrok terminal+/feed
    - work_on_remote_db: #only turen is on after config the real postgres database and work on it. otherwise its defaulty set to work with local-dev-db container.
- it designed to run hourly to check the expiring channels.  
    - for dev&testing to run locally hourly: uncomment line 243-248 
    - it run once for prod. got to use event trigger on AWS when deploy
- run by :```python src/sub_manager.py``` 
# 4. display



# reason of such design
- there are a few ways to approach the video info fetching:
    - youtube api:
        - it has 10000 quota limit everyday. searching cost 100(max 50/page), extremely high. listing cost 1-2(max 50/page). such limit does not allow us for big volumn searching in high frenquent. its Inefficient.
            - ref: https://developers.google.com/youtube/v3/determine_quota_cost
    - push notification from google pubsubhubbub (https://developers.google.com/youtube/v3/guides/push_notifications)
        - it has no quota limit.
        - it pushes the notification for 3 actions: 
            - publish new videos
            - admend of title
            - admend of description
        - the problem is the we can not know which action is about from the notification.
        - as long as we have database from init_db. we can eaily know if its the action we are monitoring.
        - it's really a pain here as very lacking documentation. 
        - subscription defaulty expiry in 5 days. it can be renewed anytime to extend the expiry date.
        
    - web scrape 
        - can not be borthered. lack of knowledge. but its open mind for other solution.


---

# database design:

schema:yt


 ![Alt text](md_images/image.png)

