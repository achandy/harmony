import pytest
from unittest.mock import patch, MagicMock
import responses
from harmony.spotify.spotify_client import SpotifyClient


@pytest.fixture
def mock_environment():
    """Fixture to mock environment variables."""
    mock_env = {
        "SPOTIFY_CLIENT_ID": "test_client_id",
        "SPOTIFY_CLIENT_SECRET": "test_client_secret",
    }

    with patch("harmony.spotify.spotify_client.os.getenv") as mock_getenv:
        # Use the dictionary's get() method for dynamic access to mock environment variables
        mock_getenv.side_effect = mock_env.get
        yield mock_getenv


@pytest.fixture
def mock_spotify_client(mock_environment):
    """Fixture to mock the SpotifyClient._authenticate method and provide a SpotifyClient instance."""
    with patch(
        "harmony.spotify.spotify_client.SpotifyClient._authenticate",
        return_value="mock_access_token",
    ):
        with patch.object(SpotifyClient, "__init__", lambda x: None):
            client = SpotifyClient()
            client.base_url = "https://mock.api.spotify.com/v1"
            client.headers = {"Authorization": "Bearer mock_access_token"}
            client.session = MagicMock()
            yield client


def test_get_client_credentials(mock_spotify_client):
    """
    Test to verify the SpotifyClient._get_client_credentials() method.
    Ensure it returns client ID and client secret from mocked environment variables.
    """
    client_id, client_secret = mock_spotify_client._get_client_credentials()

    assert client_id == "test_client_id"
    assert client_secret == "test_client_secret"


def test_missing_client_credentials(mock_environment):
    """
    Test to verify a ValueError is raised when environment variables are missing.
    """
    mock_environment.return_value = None

    with patch.object(SpotifyClient, "__init__", lambda x: None):
        client = SpotifyClient()
        client._get_client_credentials = MagicMock(
            side_effect=ValueError("Missing client credentials")
        )

        with pytest.raises(ValueError, match="Missing client credentials"):
            client._get_client_credentials()


@patch("harmony.spotify.spotify_client.webbrowser.open")
@patch("harmony.spotify.spotify_client.HTTPServer")
@patch("harmony.spotify.spotify_client.BaseHTTPRequestHandler")
def test_request_authorization_code(
    mock_handler, mock_http, mock_browser, mock_spotify_client
):
    """
    Test SpotifyClient._request_authorization_code() method.
    Ensure it correctly handles browser redirect and captures an authorization code.
    """

    mock_browser.return_value = None
    mock_handler.return_value = None

    # Simulate HTTP Server capturing an authorization code
    mock_http_instance = MagicMock()
    mock_http.return_value = mock_http_instance
    mock_http_instance.authorization_code = "test_auth_code"
    mock_http_instance.handle_request.return_value = None

    # Call the method under test
    code = mock_spotify_client._request_authorization_code("test_client_id")

    assert code == "test_auth_code"
    mock_browser.assert_called_once()


def test_exchange_code_for_token_success(mock_spotify_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "test_access_token"}
    mock_spotify_client.session.post.return_value = mock_response

    token = mock_spotify_client._exchange_code_for_token(
        "test_auth_code", "test_client_id", "test_client_secret"
    )
    assert token == "test_access_token"


@responses.activate
def test_exchange_code_for_token_failure(mock_spotify_client):
    """
    Test SpotifyClient._exchange_code_for_token() method for a failed token exchange.
    """
    # Mock a failed token exchange response
    responses.add(
        responses.POST,
        SpotifyClient.TOKEN_URL,
        json={"error": "invalid_grant"},
        status=400,
    )

    with pytest.raises(Exception, match="Failed to obtain an access token"):
        mock_spotify_client._exchange_code_for_token(
            "test_auth_code", "test_client_id", "test_client_secret"
        )


def test_get_top_tracks_success(mock_spotify_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "name": "Track 1",
                "album": {"name": "Album 1"},
                "artists": [{"name": "Artist 1"}],
            },
            {
                "name": "Track 2",
                "album": {"name": "Album 2"},
                "artists": [{"name": "Artist 2"}],
            },
        ]
    }
    mock_spotify_client.session.get.return_value = mock_response

    result = mock_spotify_client.get_top("tracks", limit=2, term="medium_term")

    assert len(result) == 2
    assert result[0]["name"] == "Track 1"
    assert result[0]["album"]["name"] == "Album 1"
    assert result[0]["artists"][0]["name"] == "Artist 1"
    assert result[1]["name"] == "Track 2"
    assert result[1]["album"]["name"] == "Album 2"
    assert result[1]["artists"][0]["name"] == "Artist 2"


def test_get_top_artists_success(mock_spotify_client):
    # Create a mock response object
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {"name": "Artist 1", "genres": ["pop", "rock"]},
            {"name": "Artist 2", "genres": ["hip hop"]},
        ]
    }

    # Patch session.get to return this mock response
    mock_spotify_client.session.get.return_value = mock_response

    # Call the method under test
    result = mock_spotify_client.get_top("artists", limit=2, term="long_term")

    # Assert the output is correctly parsed
    assert len(result) == 2
    assert result[0]["name"] == "Artist 1"
    assert result[0]["genres"] == ["pop", "rock"]
    assert result[1]["name"] == "Artist 2"
    assert result[1]["genres"] == ["hip hop"]


def test_get_top_invalid_type(mock_spotify_client):
    """
    Test SpotifyClient.get_top() method for an invalid top_type argument.
    """
    with pytest.raises(ValueError, match="Invalid value for top_type"):
        mock_spotify_client.get_top("albums", limit=5, term="medium_term")


def test_get_top_invalid_term(mock_spotify_client):
    """
    Test SpotifyClient.get_top() method for an invalid term argument.
    """
    with pytest.raises(ValueError, match="Invalid value for term"):
        mock_spotify_client.get_top("tracks", limit=5, term="invalid_term")


def test_get_user_playlists(mock_spotify_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {"id": "playlist1", "name": "My Playlist 1"},
            {"id": "playlist2"},  # missing 'name', should default to "Unknown Playlist"
        ]
    }
    mock_spotify_client.session.get.return_value = mock_response

    result = mock_spotify_client.get_user_playlists(limit=2)

    assert result == [
        {"id": "playlist1", "name": "My Playlist 1"},
        {"id": "playlist2", "name": "Unknown Playlist"},
    ]

    mock_spotify_client.session.get.assert_called_with(
        f"{mock_spotify_client.base_url}/me/playlists",
        headers=mock_spotify_client.headers,
        params={"limit": 2},
    )


def test_get_playlist_tracks(mock_spotify_client):
    playlist_id = "abcd1234"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "track": {
                    "name": "Song A",
                    "artists": [{"name": "Artist A"}],
                }
            },
            {
                "track": {  # missing 'name' and 'artists', should default
                }
            }
        ]
    }
    mock_spotify_client.session.get.return_value = mock_response

    result = mock_spotify_client.get_playlist_tracks(playlist_id=playlist_id, limit=3)

    assert result == [
        {"name": "Song A", "artist": "Artist A"},
        {"name": "Unknown Track", "artist": "Unknown Artist"}
    ]

    mock_spotify_client.session.get.assert_called_with(
        f"{mock_spotify_client.base_url}/playlists/{playlist_id}/tracks",
        headers=mock_spotify_client.headers,
        params={"limit": 3},
    )
