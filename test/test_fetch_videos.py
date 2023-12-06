import logging
import json
import pytest
from src.fetch_videos import fetch_videos_page, fetch_videos
from unittest.mock import Mock, patch
import os
from dotenv import load_dotenv
load_dotenv()

# logging.basicConfig(level=logging.info)

example_response_dict = {
    "etag": "hNPFKYFNqNJA45aRyFkdRrHkPjM",
    "items": [
        {
            "contentDetails": {
                "videoId": "testvideoId1",
                "videoPublishedAt": "testTime1"
            },
            "etag": "DFjcNVq151uZmeJeTXrlrdp06iA",
            "id": "testId1",
            "kind": "youtube#playlistItem",
            "snippet": {
                "channelId": "testchannelId1",
                "channelTitle": "testchannelTitle1",
                "description": "testdescription1",
                "playlistId": "testplaylistId1",
                "position": 0,
                "publishedAt": "testTime1",
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": "testvideoId1"
                },
                "thumbnails": {
                    "default": {
                        "height": 90,
                        "url": "testurl1",
                        "width": 120
                    },
                    "high": {
                        "height": 360,
                        "url": "testurl1",
                        "width": 480
                    },
                    "medium": {
                        "height": 180,
                        "url": "tseturl1",
                        "width": 320
                    },
                    "standard": {
                        "height": 480,
                        "url": "testurl1",
                        "width": 640
                    }
                },
                "title": "testTitle1",
                "videoOwnerChannelId": "testchannelId1",
                "videoOwnerChannelTitle": "testchannelTitle1"
            }
        },
        {
            "contentDetails": {
                "videoId": "testvideoId2",
                "videoPublishedAt": "testTime2"
            },
            "etag": "tTLfOH3pGdENtrCTRZVI6RFblqg",
            "id": "testId2",
            "kind": "youtube#playlistItem",
            "snippet": {
                "channelId": "testchannelId2",
                "channelTitle": "testchannelTitle2",
                "description": "testdescription2",
                "playlistId": "testplaylistId2",
                "position": 1,
                "publishedAt": "testTime2",
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": "testvideoId2"
                },
                "thumbnails": {
                    "default": {
                        "height": 90,
                        "url": "testurl2",
                        "width": 120
                    },
                    "high": {
                        "height": 360,
                        "url": "testurl2",
                        "width": 480
                    },
                    "maxres": {
                        "height": 720,
                        "url": "testurl2",
                        "width": 1280
                    },
                    "medium": {
                        "height": 180,
                        "url": "testurl2",
                        "width": 320
                    },
                    "standard": {
                        "height": 480,
                        "url": "testurl2",
                        "width": 640
                    }
                },
                "title": "testTitle2",
                "videoOwnerChannelId": "testchannelId2",
                "videoOwnerChannelTitle": "testchannelTitle2"
            }
        },
        {
            "contentDetails": {
                "videoId": "testvideoId3",
                "videoPublishedAt": "testTime3"
            },
            "etag": "JfaYjRM8hnqqYrMHUjptXveT8ho",
            "id": "testId3",
            "kind": "youtube#playlistItem",
            "snippet": {
                "channelId": "testchannelId3",
                "channelTitle": "testchannelTitle3",
                "description": "testdescription3",
                "playlistId": "testplaylistId3",
                "position": 2,
                "publishedAt": "testTime3",
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": "testvideoId3"
                },
                "thumbnails": {
                    "default": {
                        "height": 90,
                        "url": "testurl3",
                        "width": 120
                    },
                    "high": {
                        "height": 360,
                        "url": "testurl3",
                        "width": 480
                    },
                    "maxres": {
                        "height": 720,
                        "url": "testurl3",
                        "width": 1280
                    },
                    "medium": {
                        "height": 180,
                        "url": "testurl3",
                        "width": 320
                    },
                    "standard": {
                        "height": 480,
                        "url": "testurl3",
                        "width": 640
                    }
                },
                "title": "testTitle3",
                "videoOwnerChannelId": "testchannelId3",
                "videoOwnerChannelTitle": "testchannelTitle3"
            }
        }
    ],
    "kind": "youtube#playlistItemListResponse",
    "pageInfo": {
        "resultsPerPage": 3,
        "totalResults": 500
    }
}


@pytest.fixture
def mock_response():
    with patch('src.fetch_videos.requests.get') as mock_get:
        response = Mock()
        mock_get.return_value = response
        response.text = json.dumps(example_response_dict)
        yield mock_get


def test_fetch_videos_page_return_dict(mock_response):
    # with patcher:
    google_api_key = 'testkey'
    playlistId = 'testId',
    maxResults = 'test5'
    result = fetch_videos_page(
        google_api_key,
        playlistId,
        maxResults
    )
    assert result == example_response_dict


def test_fetch_videos_page_handle_error_in_get_response(caplog):
    google_api_key = os.getenv('google_api_key')
    playlistId = 'testId'
    maxResults = '6'
    with caplog.at_level(logging.ERROR):
        fetch_videos_page(google_api_key, playlistId, maxResults)
        assert "error in response: fetch_videos_page" in caplog.text


def test_search_channels_return_correct_format_with_single_page(
        mock_response):
    google_api_key = 'testkey'
    playlistId = 'testId'
    maxResults = '6'
    result = fetch_videos(google_api_key, playlistId, maxResults)
    assert result == {
        "items": [
            {
                "id": "testId1",
                "title": "testTitle1",
                "videoPublishedAt": "testTime1",
                'videoId': 'testvideoId1',
                'channel_id': 'testchannelId1'
            },
            {
                "id": "testId2",
                "title": "testTitle2",
                "videoPublishedAt": "testTime2",
                'videoId': 'testvideoId2',
                'channel_id': 'testchannelId2'
            },
            {
                "id": "testId3",
                "title": "testTitle3",
                "videoPublishedAt": "testTime3",
                'videoId': 'testvideoId3',
                'channel_id': 'testchannelId3'
            }
        ]}
