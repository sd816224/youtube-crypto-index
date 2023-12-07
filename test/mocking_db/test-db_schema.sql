CREATE TABLE IF NOT EXISTS yt.statistics(
    id SERIAL PRIMARY KEY,
    view_count INT NOT NULL,
    subscriber_count INT NOT NULL,
    hidden_subscriber_count BOOLEAN NOT NULL,
    video_count INT NOT NULL
);
CREATE TABLE IF NOT EXISTS yt.status(
    id INT PRIMARY KEY ,
    privacy_status VARCHAR NOT NULL,
    is_linked BOOLEAN NOT NULL,
    long_uploads_status VARCHAR NOT NULL
);
CREATE TABLE IF NOT EXISTS yt.watch_channels(
    channel_id VARCHAR PRIMARY KEY,
    uploads_id VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    published_at TIMESTAMP NOT NULL,
    country VARCHAR NOT NULL,
    statistic_id INT,
    status_id INT,
    watch_status BOOLEAN DEFAULT true,
    videos_fetched BOOLEAN DEFAULT false,
    FOREIGN KEY (statistic_id) REFERENCES yt.statistics(id), 
    FOREIGN KEY (status_id) REFERENCES yt.status(id)
);
CREATE TABLE IF NOT EXISTS yt.videos(
    id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    video_published_at TIMESTAMP NOT NULL,
    video_id VARCHAR NOT NULL,
    channel_id VARCHAR NOT NULL,
    FOREIGN KEY (channel_id) REFERENCES yt.watch_channels(channel_id)      
)