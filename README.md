this project generates live stream of crypto related videos uploaded.
consists of 2 stages: 
- 1: initial database setup & load
- 2: data producing, consuming and virtulization

once we had big enough quality data, we potential can build extra features for NLP/ML in the future. 


guidance for colabrators:
## stage1 
- clone the repo
- create enviroment params file: src/.env. config it as src/.env.example:
    - create your own google api key for google_api_key (create key and enable youtube)
    - config when you have your postgres database ready, otherwise comment out: DS_DB_NAME. RDS_USERNAME. RDS_PASSWORD. RDS_HOSTNAME. RDS_PORT

- setup docker for dev&testing:  
    - make sure running docker application. for dev stage with local-dev-d    - spin up the container by CLI ``` docker-compose -f ./src/docker-compose-dev.yaml up -d```
    - make sure dev db use port 5432, testing db use port 5433.
    - if docker command not found. try to refresh in desktop application.
    - for checking the background container: ``` docker ps```
    - for stopping the container at the end:``` $ docker-compose -f ./src/docker-compose-dev.yaml down ```

- config in stage1.py:
    - reset_db_only: only turn is on when needing to reset database and run src/stage1.py
    - work_on_remote_db: #only turen is on after config the real postgres database and work on it. otherwise its defaulty set to work with local-dev-db container.
    - q: keyword to search for channels
    - channel_pages_to_search: amount of channels to fetch when searching. No=page*maxResult(its set as 5 defaulty now)

- run following, it setup database and populate channals and videos data into relavent tables. 
    - ```python src/stage1.py```

## stage2

- setup for dev
    - setup ngrok with credential,run it for por 5000. will get callback_url from it.
    - run server by :```python src/webhook_server.py``` 

google pubsubhubbub defaulty expiry 5 days. it can be renewed without expire.
take a few minutes to confirm the verified status.


- use google pubsubhubbub to get notification of watched channels new updates
    -ref: https://developers.google.com/youtube/v3/guides/push_notifications 
- implement it to kafka producer.
- get the data form consumer side. 
- after proper (validation, filter) processing. generate data virtulization

- there are a few ways to approach the video info fetching:
    - youtube api:
        - it has 10000 quota limit everyday. searching cost 100(max 50/page), extremely high. listing cost 1-2(max 50/page). such limit does not allow us for big volumn searching in high frenquent. its Inefficient.
            - ref: https://developers.google.com/youtube/v3/determine_quota_cost
    - push notification
        - it has no quota limit.
        - it pushes the notification for 3 actions: 
            - publish new videos
            - admend of title
            - admend of description
        - the problem is the we can not know which action is about from the notification.
        - as long as we have database from stage1. we can eaily know if its the action we are monitoring.
        - it's really a pain here as very lacking documentation. it can be achieved for single channel notification. it will require extra management utils for large amount for channels notifiction.
        
    - web scrap 
        - can not be borthered. lack of knowledge. but its open mind for other solution.


- sub-manager works for keep all channels notification alive.
- webhook-server. establish intention and receive the notification pass to producer client



---

figure out another with retrieve youtube api:
- list channel by chanel_id, show part of contentDetails. cached the upload_playlist_id
- list all the video by listing playlistitems by that upload_playlist_id
- store all the video to database with table name of the chanel_id/name
- compare the new retrieve and existing db, we will get the new-uploaded video.

schema:yt
https://dbdiagram.io/

 ![Alt text](md_images/image.png)


 autopep8 --in-place --aggressive --aggressive