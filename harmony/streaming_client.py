import requests


class StreamingClient:
    """
    A client for interacting with a music streaming endpoint.

    Attributes:
        base_url (str): The base URL for the music streaming API.
        api_key (str): Optional API key for authentication.
        session (requests.Session): A requests session for making HTTP calls.
    """

    def __init__(self, base_url: str, api_key: str = None):
        """
        Initializes the MusicStreamClient with the given base URL and API key.

        Args:
            base_url (str): The base URL for the music streaming API.
            api_key (str, optional): API key for authentication. Defaults to None.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def fetch_song(self, song_id: str):
        """
        Fetches the details of a song by its ID.

        Args:
            song_id (str): The ID of the song to fetch.

        Returns:
            dict: A dictionary containing the song details.
        """
        url = f"{self.base_url}/songs/{song_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def fetch_album(self, album_id: str):
        """
        Fetches the details of an album by its ID.

        Args:
            album_id (str): The ID of the album to fetch.

        Returns:
            dict: A dictionary containing the album details.
        """
        url = f"{self.base_url}/albums/{album_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def fetch_artist(self, artist_id: str):
        """
        Fetches the details of an artist by their ID.

        Args:
            artist_id (str): The ID of the artist to fetch.

        Returns:
            dict: A dictionary containing the artist details.
        """
        url = f"{self.base_url}/artists/{artist_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def search(self, query: str, type: str = "song"):
        """
        Searches for songs, albums, or artists matching the query.

        Args:
            query (str): The search query.
            type (str, optional): The type of items to search for. Can be 'song', 'album', or 'artist'. Defaults to 'song'.

        Returns:
            dict: A dictionary containing the search results.
        """
        url = f"{self.base_url}/search"
        params = {"query": query, "type": type}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()


# Example usage:
# client = MusicStreamClient(base_url='https://api.musicstreaming.com', api_key='your_api_key')
# song = client.fetch_song(song_id='12345')
# print(song)
