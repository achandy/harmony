import requests
from harmony.tools.logger import Logger
from rich.console import Console


class StreamingClient:
    """
    A client for interacting with a music streaming endpoint.

    Attributes:
        base_url (str): The base URL for the music streaming API.
        api_key (str): Optional API key for authentication.
        session (requests.Session): A requests session for making HTTP calls.
    """

    def __init__(self, client_name: str, base_url: str, api_key: str = None):
        """
        Initializes the MusicStreamClient with the given base URL and API key.

        Args:
            base_url: The base URL for the music streaming API.
            api_key: API key for authentication. Defaults to None.
        """
        self.console = Console()

        self.client_name = client_name
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.logger = Logger(f"harmony.{client_name.lower().replace(' ', '_')}")
        self.logger.info(f"Initializing {client_name} client with base URL: {base_url}")
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
            self.logger.debug("API key set in session headers")

    def fetch_song(self, song_id: str):
        """
        Fetches the details of a song by its ID.

        Args:
            song_id: The ID of the song to fetch.

        Returns:
            dict: A dictionary containing the song details.
        """
        self.logger.info(f"Fetching song with ID: {song_id}")
        url = f"{self.base_url}/songs/{song_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            self.logger.debug(f"Successfully fetched song: {song_id}")
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching song {song_id}: {str(e)}")
            raise

    def fetch_album(self, album_id: str):
        """
        Fetches the details of an album by its ID.

        Args:
            album_id: The ID of the album to fetch.

        Returns:
            dict: A dictionary containing the album details.
        """
        self.logger.info(f"Fetching album with ID: {album_id}")
        url = f"{self.base_url}/albums/{album_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            self.logger.debug(f"Successfully fetched album: {album_id}")
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching album {album_id}: {str(e)}")
            raise

    def fetch_artist(self, artist_id: str):
        """
        Fetches the details of an artist by their ID.

        Args:
            artist_id: The ID of the artist to fetch.

        Returns:
            dict: A dictionary containing the artist details.
        """
        self.logger.info(f"Fetching artist with ID: {artist_id}")
        url = f"{self.base_url}/artists/{artist_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            self.logger.debug(f"Successfully fetched artist: {artist_id}")
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching artist {artist_id}: {str(e)}")
            raise

    def search(
        self, query: str, types: list[str] = None, limit: int = 10, headers: dict = None
    ) -> dict:
        """
        Searches for items in the music service catalog.

        Args:
            query: The search query.
            types: Types of items to search for (e.g., ['songs', 'albums', 'artists']).
                   Defaults to None (all types).
            limit: Number of results to return per type. Defaults to 10.
            headers: HTTP headers to send with each request. Defaults to None.
            **kwargs: Additional service-specific parameters.

        Returns:
            dict: A dictionary containing the search results organized by type.
        """
        self.logger.info(f"Searching for '{query}' with types: {types}")
        url = f"{self.base_url}/search"
        params = {
            "query": query,
            "limit": limit,
            **({"type": ",".join(types)} if types else {}),
        }
        try:
            response = self.session.get(url, params=params, headers=headers or {})
            response.raise_for_status()
            self.logger.debug(f"Search successful for '{query}'")
            return response.json()
        except Exception as e:
            self.logger.error(f"Error searching for '{query}': {str(e)}")
            raise

    def add_tracks_to_playlist(self, playlist_id: str, track_ids: list[str]) -> dict:
        """
        Add tracks to a playlist on the streaming service.

        Args:
            playlist_id: The identifier for the playlist to add tracks to.
            track_ids: A list of track IDs to be added to the playlist.

        Returns:
            dict: Details of the operation or the updated playlist.
        """
        self.logger.info(f"Adding {len(track_ids)} tracks to playlist {playlist_id}")
        self.logger.debug(f"Track IDs to add: {track_ids}")
        raise NotImplementedError("This method must be implemented by a subclass")

    def create_playlist(self, name: str, description: str = "") -> str:
        """
        Create a new playlist on the streaming service.

        Args:
            name: The name for the new playlist.
            description: The playlist description.

        Returns:
            str: Return playlist id
        """
        self.logger.info(f"Creating new playlist: '{name}'")
        self.logger.debug(f"Playlist details - Description: '{description}'")
        raise NotImplementedError("This method must be implemented by a subclass")
