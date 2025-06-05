import pytest
import responses
from harmony.streaming_client import StreamingClient


@pytest.fixture
def streaming_client():
    """
    Fixture to provide a StreamingClient instance with a mock base URL and API key.
    """
    return StreamingClient(
        client_name="Test Client",
        base_url="https://api.musicstreaming.com",
        api_key="test_api_key",
    )


@responses.activate
def test_fetch_song(streaming_client):
    """
    Test the fetch_song method of StreamingClient.
    """
    song_id = "12345"
    expected_response = {"id": song_id, "title": "Test Song"}

    # Mock the HTTP response
    responses.add(
        responses.GET,
        f"{streaming_client.base_url}/songs/{song_id}",
        json=expected_response,
        status=200,
    )

    # Call fetch_song and assert the response
    response = streaming_client.fetch_song(song_id)
    assert response == expected_response


@responses.activate
def test_fetch_album(streaming_client):
    """
    Test the fetch_album method of StreamingClient.
    """
    album_id = "67890"
    expected_response = {"id": album_id, "title": "Test Album"}

    # Mock the HTTP response
    responses.add(
        responses.GET,
        f"{streaming_client.base_url}/albums/{album_id}",
        json=expected_response,
        status=200,
    )

    # Call fetch_album and assert the response
    response = streaming_client.fetch_album(album_id)
    assert response == expected_response


@responses.activate
def test_fetch_artist(streaming_client):
    """
    Test the fetch_artist method of StreamingClient.
    """
    artist_id = "54321"
    expected_response = {"id": artist_id, "name": "Test Artist"}

    # Mock the HTTP response
    responses.add(
        responses.GET,
        f"{streaming_client.base_url}/artists/{artist_id}",
        json=expected_response,
        status=200,
    )

    # Call fetch_artist and assert the response
    response = streaming_client.fetch_artist(artist_id)
    assert response == expected_response


@responses.activate
def test_search_song(streaming_client):
    """
    Test the search method of StreamingClient for songs.
    """
    query = "Test Song"
    expected_response = {"results": [{"id": "12345", "title": "Test Song"}]}

    # Mock the HTTP response with query parameters
    responses.add(
        responses.GET,
        f"{streaming_client.base_url}/search",
        json=expected_response,
        status=200,
        match=[
            responses.matchers.query_string_matcher(f"query={query}&limit=10&type=song")
        ],
    )

    # Call search and assert the response
    response = streaming_client.search(query=query, types=["song"])
    assert response == expected_response


@responses.activate
def test_search_album(streaming_client):
    """
    Test the search method of StreamingClient for albums.
    """
    query = "Test Album"
    expected_response = {"results": [{"id": "67890", "title": "Test Album"}]}

    # Mock the HTTP response with query parameters
    responses.add(
        responses.GET,
        f"{streaming_client.base_url}/search",
        json=expected_response,
        status=200,
        match=[
            responses.matchers.query_string_matcher(
                f"query={query}&limit=10&type=album"
            )
        ],
    )

    # Call search and assert the response
    response = streaming_client.search(query=query, types=["album"])
    assert response == expected_response


@responses.activate
def test_search_artist(streaming_client):
    """
    Test the search method of StreamingClient for artists.
    """
    query = "Test Artist"
    expected_response = {"results": [{"id": "54321", "name": "Test Artist"}]}

    # Mock the HTTP response with query parameters
    responses.add(
        responses.GET,
        f"{streaming_client.base_url}/search",
        json=expected_response,
        status=200,
        match=[
            responses.matchers.query_string_matcher(
                f"query={query}&limit=10&type=artist"
            )
        ],
    )

    # Call search and assert the response
    response = streaming_client.search(query=query, types=["artist"])
    assert response == expected_response
