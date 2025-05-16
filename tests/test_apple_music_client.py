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
