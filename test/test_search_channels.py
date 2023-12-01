import logging

from src.search_channels import search_channels,fetch_channels_page
from unittest.mock import Mock, patch
logging.basicConfig(level=logging.info)

# patcher = patch('src.search_channels.fetch_channels_page',return_value={'items':['item1','item2'],'nextPageToken':'abc'})
@patch('src.search_channels.fetch_channels_page',return_value={'items':['item1','item2'],'nextPageToken':'abc'})
def test_search_channels_return_list(fetch_channels_page_mock):
    # with patcher:
    pages_to_search=2
    google_api_key='testkey'
    q='testkey'
    order='testorder',
    search_type='testtype'
    result=search_channels(pages_to_search,google_api_key,q,order,search_type)

    assert result==['item1','item2','item1','item2']


@patch('src.search_channels.fetch_channels_page',return_value={'items':['item1','item2']})
def test_search_channels_return_list_without_enough_page(fetch_channels_page_mock):
    # with patcher:
    pages_to_search=2
    google_api_key='testkey'
    q='testkey'
    order='testorder',
    search_type='testtype'
    result=search_channels(pages_to_search,google_api_key,q,order,search_type)

    assert result==['item1','item2']