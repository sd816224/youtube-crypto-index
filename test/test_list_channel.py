from src.stage1.list_channel import list_all_channels, list_channel_detail
import logging
import json
import pytest
from unittest.mock import Mock, patch
from dotenv import load_dotenv
load_dotenv()

example_response_dict = {'items':
                         [{'contentDetails':
                           {'relatedPlaylists':
                            {'likes': '',
                             'uploads': 'testUploads'}},
                             'country': 'CA',
                             'id': 'testId',
                          'publishedAt': 'testTime',
                           'statistics':
                             {'hiddenSubscriberCount': False,
                              'subscriberCount': '1111',
                              'videoCount': '2222',
                              'viewCount': '3333'},
                           'snippet': 'testSnippet',
                           'status':
                           {'isLinked': True,
                            'longUploadsStatus': 'longUploadsUnspecified',
                            'madeForKids': False,
                            'privacyStatus': 'public'},
                           'title': 'testTitle'}]}


@pytest.fixture
def mock_response():
    with patch('src.stage1.list_channel.requests.get') as mocked_get:
        response = Mock()
        mocked_get.return_value = response
        mocked_get.return_value.text = json.dumps(example_response_dict)
        yield mocked_get


def test_list_channel_with_error_response(caplog):
    with caplog.at_level(logging.ERROR):
        list_channel_detail('google_api_key', 'part', 'id', page_token=None)
        assert "error in response: list_channel_detail" in caplog.text


def test_list_channel_return_correct_format(mock_response):
    assert example_response_dict == list_channel_detail(
        'test_api', 'test_part', 'test_id', page_token=None)


example_single_response_dict = {
    "kind": "youtube#channelListResponse",
    "etag": "C3H4ki3PVMo4dP3zVklI22bb99g",
    "pageInfo": {
        "totalResults": 1,
        "resultsPerPage": 5
    },
    "items": [
        {
            "kind": "youtube#channel",
            "etag": "xg3skB5uQnMGtHTB5q0i_be0ulQ",
            "id": "testId",
            "snippet": {
                "title": "testTitle",
                "description": "testDescription",
                "customUrl": "@testUrl",
                "publishedAt": "testTime",
                "thumbnails": {
                    "default": {
                        "url": "https://yt3.ggpht.-no-rj",
                        "width": 88,
                        "height": 88
                    },
                    "medium": {
                        "url": "https://yt3.ggpht.com/ytc/-no-rj",
                        "width": 240,
                        "height": 240
                    },
                    "high": {
                        "url": "https://yt3.-no-rj",
                        "width": 800,
                        "height": 800
                    }
                },
                "localized": {
                    "title": "testTitle",
                    "description": "testDescription"
                },
                "country": "RS"
            },
            "contentDetails": {
                "relatedPlaylists": {
                    "likes": "",
                    "uploads": "testUploads",
                }
            },
            "statistics": {
                "viewCount": "1111",
                "subscriberCount": "2222",
                "hiddenSubscriberCount": False,
                "videoCount": "3333"
            },
            "status": {
                "privacyStatus": "public",
                "isLinked": True,
                "longUploadsStatus": "longUploadsUnspecified",
                "madeForKids": False
            }
        }
    ]
}


@patch('src.stage1.list_channel.list_channel_detail',
       return_value=example_single_response_dict)
def test_list_all_channels_return_correct_format(mock_list_channel_detail):
    listof_channels = {'items': [{'id': 'testId',
                                  'publishedAt': 'testTime',
                                 'title': 'testTitle'}]}
    expected_result = [{'uploads_id': 'testUploads',
                        'country': 'RS',
                        'id': 'testId',
                        'publishedAt': 'testTime',
                        'statistics':
                        {'hiddenSubscriberCount': False,
                         'subscriberCount': '2222',
                         'videoCount': '3333',
                         'viewCount': '1111'},
                        'status':
                        {'isLinked': True,
                         'longUploadsStatus': 'longUploadsUnspecified',
                         'madeForKids': False,
                         'privacyStatus': 'public'},
                        'title': 'testTitle'}]
    result = list_all_channels(listof_channels, 'test_api')
    assert result == expected_result
