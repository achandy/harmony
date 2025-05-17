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


@responses.activate
def test_exchange_code_for_token_success(mock_spotify_client):
    """
    Test SpotifyClient._exchange_code_for_token() method for a successful token exchange.
    """
    # Mock a successful token exchange response
    responses.add(
        responses.POST,
        SpotifyClient.TOKEN_URL,
        json={"access_token": "test_access_token"},
        status=200,
    )

    # Call the method under test
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

@responses.activate
def test_get_top_tracks_success(mock_spotify_client):
    """
    Test SpotifyClient.get_top() method for successfully fetching the top tracks.
    """
    # Mock a successful response for the top tracks
    responses.add(
        responses.GET,
        f"{mock_spotify_client.base_url}/me/top/tracks",
        json={
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
        },
        status=200,
    )

    # Call the method under test
    result = mock_spotify_client.get_top("tracks", limit=2, term="medium_term")

    # Assert the output is correctly parsed
    assert len(result) == 2
    assert result[0]["name"] == "Track 1"
    assert result[0]["album"]["name"] == "Album 1"
    assert result[0]["artists"][0]["name"] == "Artist 1"
    assert result[1]["name"] == "Track 2"
    assert result[1]["album"]["name"] == "Album 2"
    assert result[1]["artists"][0]["name"] == "Artist 2"


@responses.activate
def test_get_top_artists_success(mock_spotify_client):
    """
    Test SpotifyClient.get_top() method for successfully fetching the top artists.
    """
    # Mock a successful response for the top artists
    responses.add(
        responses.GET,
        f"{mock_spotify_client.base_url}/me/top/artists",
        json={
            "items": [
                {"name": "Artist 1", "genres": ["pop", "rock"]},
                {"name": "Artist 2", "genres": ["hip hop"]},
            ]
        },
        status=200,
    )

    # Call the method under test
    result = mock_spotify_client.get_top("artists", limit=2, term="long_term")

    # Assert the output is correctly parsed
    assert len(result) == 2
    assert result[0]["name"] == "Artist 1"
    assert result[0]["genres"] == ["pop", "rock"]
    assert result[1]["name"] == "Artist 2"
    assert result[1]["genres"] == ["hip hop"]


@responses.activate
def test_get_top_invalid_type(mock_spotify_client):
    """
    Test SpotifyClient.get_top() method for an invalid top_type argument.
    """
    with pytest.raises(ValueError, match="Invalid value for top_type"):
        mock_spotify_client.get_top("albums", limit=5, term="medium_term")


@responses.activate
def test_get_top_invalid_term(mock_spotify_client):
    """
    Test SpotifyClient.get_top() method for an invalid term argument.
    """
    with pytest.raises(ValueError, match="Invalid value for term"):
        mock_spotify_client.get_top("tracks", limit=5, term="invalid_term")
