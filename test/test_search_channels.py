import logging
import json
import pytest
from src.stage1.search_channels import search_channels, fetch_channels_page
from unittest.mock import Mock, patch
import os
from dotenv import load_dotenv
load_dotenv()

# logging.basicConfig(level=logging.info)

example_response_dict = {
    "items": [
        {
            "kind": "youtube#searchResult",
            "etag": "test1",
            "id": {
                "kind": "youtube#channel",
                "channelId": "testId1"
            },
            "snippet": {
                "publishedAt": "testTime",
                "channelId": "testId11",
                "title": "testTitle",
                "description": "testDescription",
                "thumbnails": {
                    "default": {
                        "url": "testUrl"
                    },
                    "medium": {
                        "url": "testUrl"
                    },
                    "high": {
                        "url": "testUrl"
                    }
                },
                "channelTitle": "testTitle",
                "liveBroadcastContent": "testContent",
                "publishTime": "testTime"
            }
        },
        {
            "kind": "youtube#searchResult",
            "etag": "test2",
            "id": {
                "kind": "youtube#channel",
                "channelId": "testId2"
            },
            "snippet": {
                "publishedAt": "testTime2",
                "channelId": "testId22",
                "title": "testTitle2",
                "description": "testDescription2",
                "thumbnails": {
                    "default": {
                        "url": "testUrl2"
                    },
                    "medium": {
                        "url": "testUrl2"
                    },
                    "high": {
                        "url": "testUrl2"
                    }
                },
                "channelTitle": "testTitle2",
                "liveBroadcastContent": "testContent2",
                "publishTime": "testTime2"
            }
        },]}


@pytest.fixture
def mock_response():
    with patch('src.stage1.search_channels.requests.get') as mock_get:
        response = Mock()
        mock_get.return_value = response
        response.text = json.dumps(example_response_dict)
        yield mock_get


@pytest.fixture
def mock_fetch_channels_page():
    with patch('src.stage1.search_channels.fetch_channels_page') as mock_get:
        example_response_dict['nextPageToken'] = 'testtoken'
        mock_get.return_value = example_response_dict
        yield mock_get


def test_fetch_channels_page_return_dict(mock_response):
    # with patcher:
    google_api_key = 'testkey'
    q = 'testkey'
    order = 'testorder',
    search_type = 'testtype'
    page_token = 'testtoken'
    result = fetch_channels_page(
        google_api_key,
        q,
        order,
        search_type,
        page_token)
    assert result == example_response_dict


def test_fetch_channels_page_handle_error_in_get_response(caplog):
    google_api_key = os.getenv('google_api_key')
    q = 'bitcoin'
    order = 'wrong_order',
    search_type = 'channel'
    with caplog.at_level(logging.ERROR):
        fetch_channels_page(google_api_key, q, order, search_type)
        assert "error in response: fetch_channels_page" in caplog.text


def test_search_channels_return_correct_format_with_single_page(
        mock_fetch_channels_page):
    # with patcher:
    pages_to_search = 2
    google_api_key = 'testkey'
    q = 'testkey'
    order = 'testorder',
    search_type = 'testtype'
    result = search_channels(
        pages_to_search,
        google_api_key,
        q,
        order,
        search_type)
    assert result == {
        "items": [
            {
                "id": "testId1",
                "title": "testTitle",
                "publishedAt": "testTime"
            },
            {
                "id": "testId2",
                "title": "testTitle2",
                "publishedAt": "testTime2"
            },
            {
                "id": "testId1",
                "title": "testTitle",
                "publishedAt": "testTime"
            },
            {
                "id": "testId2",
                "title": "testTitle2",
                "publishedAt": "testTime2"
            }]}
