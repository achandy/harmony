import pytest
from unittest.mock import patch, MagicMock
import jwt
import time
from harmony.apple_music.apple_music_client import AppleMusicClient


@pytest.fixture
def mock_environment():
    """Fixture to mock environment variables."""
    mock_env = {
        "APPLE_KEY_ID": "test_key_id",
        "APPLE_TEAM_ID": "test_team_id",
        "APPLE_PRIVATE_KEY": "test_private_key",
    }

    with patch("harmony.apple_music.apple_music_client.os.getenv") as mock_getenv:
        # Use the dictionary's get() method for dynamic access to mock environment variables
        mock_getenv.side_effect = mock_env.get
        yield mock_getenv


@pytest.fixture
def mock_apple_music_client(mock_environment):
    """Fixture to mock the AppleMusicClient initialization."""
    """Fixture to mock the SpotifyClient.__authenticate method and provide a SpotifyClient instance."""
    with patch(
        "harmony.apple_music.apple_music_client.AppleMusicClient._authenticate",
        return_value="mock_user_token",
    ):
        with patch.object(AppleMusicClient, "__init__", lambda x: None):
            client = AppleMusicClient()
            client.session = MagicMock()
            client.base_url = "https://api.music.apple.com/v1"

            yield client


def test_get_developer_token(mock_apple_music_client):
    """
    Test that AppleMusicClient._get_developer_token() generates a valid JWT.
    """
    mock_private_key = "test_private_key"
    mock_key_id = "test_key_id"
    mock_team_id = "test_team_id"

    with patch.object(jwt, "encode", return_value="mock_jwt_token") as mock_jwt:
        generated_token = mock_apple_music_client._get_developer_token()

        mock_jwt.assert_called_once_with(
            {
                "iss": mock_team_id,
                "iat": int(time.time()),
                "exp": int(time.time()) + 3600 * 12,
            },
            mock_private_key,
            algorithm=AppleMusicClient.JWT_ALGORITHM,
            headers={"alg": AppleMusicClient.JWT_ALGORITHM, "kid": mock_key_id},
        )

        assert generated_token == "mock_jwt_token"


def test_missing_developer_token_env_vars():
    """
    Test that AppleMusicClient._get_developer_token() raises an error if env vars are missing.
    """
    with patch("harmony.apple_music.apple_music_client.os.getenv", return_value=None):
        with pytest.raises(
            ValueError,
            match="APPLE_KEY_ID, APPLE_TEAM_ID, and APPLE_PRIVATE_KEY must be set",
        ):
            client = AppleMusicClient()
            client._get_developer_token()


def test_client_initialization(mock_apple_music_client):
    """
    Test that AppleMusicClient initializes properly with tokens.
    """
    mock_apple_music_client.developer_token = "mock_developer_token"
    mock_apple_music_client.user_token = "mock_user_token"

    assert mock_apple_music_client.developer_token == "mock_developer_token"
    assert mock_apple_music_client.user_token == "mock_user_token"


def test_get_heavy_rotation(mock_apple_music_client):
    """
    Test that get_heavy_rotation fetches and parses heavy rotation albums correctly.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {
                "type": "library-albums",
                "attributes": {"name": "Album 1", "artistName": "Artist 1"},
            },
            {
                "type": "library-albums",
                "attributes": {"name": "Album 2", "artistName": "Artist 2"},
            },
            {
                "type": "other-type",  # This should be filtered out
                "attributes": {"name": "Unknown", "artistName": "Unknown"},
            },
        ]
    }
    mock_apple_music_client.session.get.return_value = mock_response

    # Call function being tested
    result = mock_apple_music_client.get_heavy_rotation()

    assert result == [
        {"name": "Album 1", "artist": "Artist 1"},
        {"name": "Album 2", "artist": "Artist 2"},
    ]
    mock_apple_music_client.session.get.assert_called_once_with(
        f"{mock_apple_music_client.base_url}/me/history/heavy-rotation",
        params={"limit": 10},
    )

    # Test with a different limit
    result_with_limit = mock_apple_music_client.get_heavy_rotation(limit=5)
    assert result_with_limit == [
        {"name": "Album 1", "artist": "Artist 1"},
        {"name": "Album 2", "artist": "Artist 2"},
    ]
    mock_apple_music_client.session.get.assert_called_with(
        f"{mock_apple_music_client.base_url}/me/history/heavy-rotation",
        params={"limit": 5},
    )


def test_get_user_playlists(mock_apple_music_client):
    """
    Test that get_user_playlists fetches and parses playlists correctly.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {
                "id": "playlist1",
                "attributes": {"name": "My Playlist 1"},
            },
            {
                "id": "playlist2",
                "attributes": {},  # missing name, should default
            },
        ]
    }
    mock_apple_music_client.session.get.return_value = mock_response

    result = mock_apple_music_client.get_user_playlists(limit=2)

    assert result == [
        {"id": "playlist1", "name": "My Playlist 1"},
        {"id": "playlist2", "name": "Unknown Playlist"},
    ]

    mock_apple_music_client.session.get.assert_called_with(
        f"{mock_apple_music_client.base_url}/me/library/playlists",
        params={"limit": 2},
    )


def test_get_playlist_tracks(mock_apple_music_client):
    """
    Test that get_playlist_tracks fetches and parses playlist tracks correctly.
    """
    playlist_id = "abcd1234"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {
                "attributes": {
                    "name": "Song A",
                    "artistName": "Artist A",
                }
            },
            {
                "attributes": {},  # Missing name and artistName
            },
        ]
    }
    mock_apple_music_client.session.get.return_value = mock_response

    result = mock_apple_music_client.get_playlist_tracks(
        playlist_id=playlist_id, limit=2
    )

    assert result == [
        {"name": "Song A", "artist": "Artist A"},
        {"name": "Unknown Track", "artist": "Unknown Artist"},
    ]

    mock_apple_music_client.session.get.assert_called_with(
        f"{mock_apple_music_client.base_url}/me/library/playlists/{playlist_id}/tracks",
        params={"limit": 2},
    )
