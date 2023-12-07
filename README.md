this project generates live stream of crypto related videos uploaded.
consists of 2 stages: 
- 1: initial database setup & load
- 2: data producing, consuming and virtulization

once we had big enough quality data, we potential can build extra features for NLP/ML in the future. 

guidance for colabrators:
## stage1 
- clone the repo
- create file: into src/.env. config as below:
```
google_api_key = *** (create your own google api key)
DS_DB_NAME = *** (config when you have your postgres database ready, otherwise comment out)
RDS_USERNAME = *** (same)
RDS_PASSWORD = *** (same)
RDS_HOSTNAME = *** (same)
RDS_PORT = *** (same)
```
- make sure running docker application. for dev stage with local-dev-db
- spin up the container by CLI:  
``` docker-compose -f ./src/docker-compose-dev.yaml up -d```
    - if docker command not found. try to refresh in desktop application.
    - for checking the background container: ``` docker ps```
    - for stopping the container at the end:``` $ docker-compose -f ./src/docker-compose-dev.yaml down ```
- config in stage1.py:
    - reset_db: only turn is on when needing to reset database and run src/stage1.py
    - work_on_remote_db: #only turen is on after config the real postgres database and work on it. otherwise its defaulty set to work with local-dev-db container.
    - q: keyword to search for channels
    - channel_pages_to_search: amount of channels to fetch when searching. No=page*maxResult(its set as 5 defaulty now)
- run following, it setup database and populate channals and videos data into relavent tables. 
    - ```python src/stage1.py```

## stage2
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

---
figure out another with retrieve youtube api:
- list channel by chanel_id, show part of contentDetails. cached the upload_playlist_id
- list all the video by listing playlistitems by that upload_playlist_id
- store all the video to database with table name of the chanel_id/name
- compare the new retrieve and existing db, we will get the new-uploaded video.

schema:yt
https://dbdiagram.io/

 ![Alt text](md_image/image.png)


 autopep8 --in-place --aggressive --aggressive