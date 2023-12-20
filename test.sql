

SELECT * from generate_series(
	NOW(),
   NOW()-interval '5 DAY', INTERVAL '-1 day'
  ) table1
 
 
select 
date_trunc('day',video_published_at+interval '1 day') as day_up,
title, 
video_published_at,
video_id  
from yt.videos order by video_published_at desc limit 20


SELECT *
FROM generate_series(NOW(), NOW() - INTERVAL '5 DAY', INTERVAL '-1 day') AS table1
JOIN (
    SELECT
        date_trunc('day', video_published_at + INTERVAL '1 day') AS day_up,
        title,
        video_published_at,
        video_id
    FROM yt.videos
) AS yt_videos ON table1 = yt_videos.day_up
ORDER BY yt_videos.video_published_at DESC
LIMIT 20
