from streaming_client import StreamingClient


class SpotifyClient(StreamingClient):
    """
    A client for interacting with the Spotify API.

    This client extends the StreamingClient to provide functionality specific to Spotify.
    """

    def __init__(self, access_token: str, base_url: str = 'https://api.spotify.com/v1'):
        """
        Initializes the SpotifyClient.

        Args:
            access_token: The Spotify access token for authentication.
            base_url: The base URL for the Spotify API. Defaults to Spotify's API URL.
        """
        super().__init__(base_url)
        self.session.headers.update({'Authorization': f'Bearer {access_token}'})

