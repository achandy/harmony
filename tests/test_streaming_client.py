import unittest
from unittest import mock
import responses
from src.streaming_client import StreamingClient


class TestStreamingClient(unittest.TestCase):

    def setUp(self):
        self.base_url = 'https://api.musicstreaming.com'
        self.client = StreamingClient(base_url=self.base_url, api_key='test_api_key')

    @responses.activate
    def test_fetch_song(self):
        song_id = '12345'
        expected_response = {'id': song_id, 'title': 'Test Song'}
        responses.add(
            responses.GET,
            f"{self.base_url}/songs/{song_id}",
            json=expected_response,
            status=200
        )

        response = self.client.fetch_song(song_id)
        self.assertEqual(response, expected_response)

    @responses.activate
    def test_fetch_album(self):
        album_id = '67890'
        expected_response = {'id': album_id, 'title': 'Test Album'}
        responses.add(
            responses.GET,
            f"{self.base_url}/albums/{album_id}",
            json=expected_response,
            status=200
        )

        response = self.client.fetch_album(album_id)
        self.assertEqual(response, expected_response)

    @responses.activate
    def test_fetch_artist(self):
        artist_id = '54321'
        expected_response = {'id': artist_id, 'name': 'Test Artist'}
        responses.add(
            responses.GET,
            f"{self.base_url}/artists/{artist_id}",
            json=expected_response,
            status=200
        )

        response = self.client.fetch_artist(artist_id)
        self.assertEqual(response, expected_response)

    @responses.activate
    def test_search_song(self):
        query = 'Test Song'
        expected_response = {'results': [{'id': '12345', 'title': 'Test Song'}]}
        responses.add(
            responses.GET,
            f"{self.base_url}/search",
            json=expected_response,
            status=200,
            match=[responses.matchers.query_string_matcher(f"query={query}&type=song")]
        )

        response = self.client.search(query=query, type='song')
        self.assertEqual(response, expected_response)

    @responses.activate
    def test_search_album(self):
        query = 'Test Album'
        expected_response = {'results': [{'id': '67890', 'title': 'Test Album'}]}
        responses.add(
            responses.GET,
            f"{self.base_url}/search",
            json=expected_response,
            status=200,
            match=[responses.matchers.query_string_matcher(f"query={query}&type=album")]
        )

        response = self.client.search(query=query, type='album')
        self.assertEqual(response, expected_response)

    @responses.activate
    def test_search_artist(self):
        query = 'Test Artist'
        expected_response = {'results': [{'id': '54321', 'name': 'Test Artist'}]}
        responses.add(
            responses.GET,
            f"{self.base_url}/search",
            json=expected_response,
            status=200,
            match=[responses.matchers.query_string_matcher(f"query={query}&type=artist")]
        )

        response = self.client.search(query=query, type='artist')
        self.assertEqual(response, expected_response)
