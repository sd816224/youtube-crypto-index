                    CREATE TABLE IF NOT EXISTS yt.watch_channels(
                        channel_id VARCHAR PRIMARY KEY,
                        uploads_id VARCHAR NOT NULL UNIQUE,
                        title VARCHAR NOT NULL,
                        published_at TIMESTAMP NOT NULL,
                        country VARCHAR NOT NULL,
                        watch_status BOOLEAN DEFAULT true,
                        videos_fetched BOOLEAN DEFAULT false
                    );
                    CREATE TABLE IF NOT EXISTS yt.statistics(
                        channel_id VARCHAR NOT NULL,
                        view_count INT NOT NULL,
                        subscriber_count INT NOT NULL,
                        hidden_subscriber_count BOOLEAN NOT NULL,
                        video_count INT NOT NULL,
                        FOREIGN KEY (channel_id) REFERENCES yt.watch_channels(channel_id)
                    );
                    CREATE TABLE IF NOT EXISTS yt.status(
                        channel_id VARCHAR NOT NULL ,
                        privacy_status VARCHAR NOT NULL,
                        is_linked BOOLEAN NOT NULL,
                        long_uploads_status VARCHAR NOT NULL,
                        FOREIGN KEY (channel_id) REFERENCES yt.watch_channels(channel_id)
                    );
                    CREATE TABLE IF NOT EXISTS yt.videos(
                        id VARCHAR PRIMARY KEY,
                        title VARCHAR NOT NULL,
                        video_published_at TIMESTAMP NOT NULL,
                        video_id VARCHAR NOT NULL,
                        list_id VARCHAR NOT NULL,
                        FOREIGN KEY (list_id) REFERENCES yt.watch_channels(uploads_id)  
                      );