import os
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
from harmony.streaming_client import StreamingClient

load_dotenv()


class SpotifyClient(StreamingClient):
    """
    A client for interacting with the Spotify API.

    This client handles authentication automatically using Spotify's
    authorization code flow and allows making authenticated requests
    to the Spotify API.
    """

    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    REDIRECT_URI = "http://localhost:8888/callback"  # Using a local server for callback

    def __init__(self, base_url: str = "https://api.spotify.com/v1"):
        """
        Initialize the Spotify client and handle authentication.

        Args:
            base_url: The base URL for the Spotify API. Default is Spotify's API URL.
        """

        super().__init__(client_name="Spotify", base_url=base_url, api_key=None)

        self.access_token = self._authenticate()
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        self.api_key = self.access_token

    def _authenticate(self) -> str:
        """
        Handle Spotify's authorization code flow to obtain the access token.

        Returns:
            str: The authenticated music user token.
        """
        # Step 1: Get Client Credentials
        client_id, client_secret = self._get_client_credentials()

        # Step 2: Open Authorization URL to Get Code
        authorization_code = self._request_authorization_code(client_id)

        # Step 3: Exchange Code for Access Token
        access_token = self._exchange_code_for_token(
            authorization_code, client_id, client_secret
        )

        return access_token

    @staticmethod
    def _get_client_credentials() -> tuple[str, str]:
        """
        Retrieve client credentials from the environment.

        Returns:
            tuple[str, str]: The Spotify client ID and secret.
        """
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in the .env file"
            )

        return client_id, client_secret

    def _request_authorization_code(self, client_id: str) -> str:
        """
        Request the authorization code by opening the Spotify login page and
        listening for the callback.

        Args:
            client_id: The application's Spotify client ID.

        Returns:
            str: The authorization code provided by Spotify.
        """
        auth_params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": self.REDIRECT_URI,
            "scope": "user-read-private user-top-read user-read-email playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative",
        }
        auth_url = f"{self.AUTH_URL}?{urlencode(auth_params)}"

        # Open the authorization URL in the user's browser
        self.logger.log_and_print("Opening browser for Spotify authorization")
        webbrowser.open(auth_url)

        # Start the HTTP server to capture the authorization code
        class CallbackHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def do_GET(self):
                query_components = parse_qs(urlparse(self.path).query)
                if "code" in query_components:
                    self.server.authorization_code = query_components["code"][0]
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(
                        b"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Authorization Complete</title>
                            <script>
                                window.onload = function() {
                                    setTimeout(function() {
                                        window.close(); // Close the authorization window after a delay
                                    }, 3000); // 3000ms = 3 seconds delay
                                };
                            </script>
                        </head>
                        <body>
                            <h1>Authorization successful!</h1>
                            <p>This window will close automatically in a few seconds.</p>
                        </body>
                        </html>
                        """
                    )
                else:
                    self.server.authorization_code = None
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Authorization failed!")

        self.logger.log_and_print("Waiting for Spotify authorization...")
        httpd = HTTPServer(("localhost", 8888), CallbackHandler)
        httpd.handle_request()  # Wait for a single authorization request (blocking)

        # Retrieve the authorization code from the HTTP handler
        authorization_code = getattr(httpd, "authorization_code", None)
        if not authorization_code:
            error_msg = "Authorization code could not be obtained. Please try again."
            self.logger.error(error_msg)
            raise Exception(error_msg)

        self.logger.info("Spotify authorization code received")

        return authorization_code

    def _exchange_code_for_token(
        self, authorization_code: str, client_id: str, client_secret: str
    ) -> str:
        """
        Exchange the authorization code for an access token from Spotify.

        Args:
            authorization_code: The authorization code from Spotify.
            client_id: Spotify's client ID for your app.
            client_secret: Spotify's client secret for your app.

        Returns:
            str: The access token for authenticated API requests.
        """
        token_data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.REDIRECT_URI,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        self.logger.info("Exchanging authorization code for access token")
        try:
            response = self.session.post(self.TOKEN_URL, data=token_data)
            if response.status_code != 200:
                error_msg = f"Failed to obtain an access token: {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

            # Parse the response for the access token
            token_response = response.json()
            access_token = token_response.get("access_token")
            if not access_token:
                error_msg = "Access token is missing in the response."
                self.logger.error(error_msg)
                raise Exception(error_msg)

            self.logger.info("Successfully obtained Spotify access token")
        except Exception as e:
            self.logger.error(f"Error during token exchange: {str(e)}")
            raise

        return access_token

    def get_top(
        self, top_type: str, limit: int = 10, term: str = "medium_term"
    ) -> list[dict]:
        """
        Get the user's top objects (artists or tracks) from Spotify for a specific time range.

        Args:
            top_type: The type of top object to retrieve ('artists' or 'tracks').
            limit: Number of objects to retrieve (default is 10).
            term: The time range for top items ('short_term', 'medium_term', or 'long_term').

        Returns:
            list[dict]: A list of the top objects with their details.
        """
        if top_type not in {"artists", "tracks"}:
            raise ValueError(
                "Invalid value for top_type. Expected 'artists' or 'tracks'."
            )

        if term not in {"short_term", "medium_term", "long_term"}:
            raise ValueError(
                "Invalid value for term. Expected 'short_term', 'medium_term', or 'long_term'."
            )

        endpoint = f"{self.base_url}/me/top/{top_type}"
        params = {
            "limit": limit,
            "time_range": term,
        }

        response = self.session.get(endpoint, headers=self.headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to get top {top_type}: {response.text}")

        return response.json().get("items", [])

    def get_user_playlists(self, limit: int = 50) -> list[dict]:
        """
        Fetch the user's playlists.

        Args:
            limit: The number of playlists to retrieve (default is 50).

        Returns:
            list[dict]: A list of playlists with their details.
        """
        endpoint = f"{self.base_url}/me/playlists"
        params = {"limit": limit}

        response = self.session.get(endpoint, headers=self.headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to get playlists: {response.text}")

        items = response.json().get("items", [])
        return [
            {
                "id": playlist["id"],
                "name": playlist.get("name", "Unknown Playlist"),
            }
            for playlist in items
        ]

    def get_playlist_tracks(self, playlist_id: str, limit: int = 100) -> list[dict]:
        """
        Fetch the tracks from a specific playlist.

        Args:
            playlist_id: The Spotify ID of the playlist.
            limit: The number of tracks to retrieve (default is 100).

        Returns:
            list[dict]: A list of tracks with their details.
        """
        endpoint = f"{self.base_url}/playlists/{playlist_id}/tracks"
        params = {"limit": limit}

        response = self.session.get(endpoint, headers=self.headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to get tracks: {response.text}")

        items = response.json().get("items", [])
        return [
            {
                "name": track["track"].get("name", "Unknown Track"),
                "artist": ", ".join(
                    artist["name"] for artist in track["track"].get("artists", [])
                )
                if track.get("track")
                else "Unknown Artist",
            }
            for track in items
        ]

    def search(
        self,
        query: str,
        types: list[str] = None,
        limit: int = 10,
        headers: dict = None,
    ) -> dict:
        """
        Search Spotify catalog.

        Args:
            query: The search query.
            types: Types of items to search for (e.g., ['track', 'album']).
                   Defaults to all types if None.
            limit: Number of results to return. Defaults to 10.
            headers: HTTP headers to send.

        Returns:
            dict: Search results organized by type.
        """
        url = f"{self.base_url}/search"

        params = {
            "q": query,
            "limit": limit,
        }

        if types:
            params["type"] = ",".join(types)

        response = self.session.get(url, params=params, headers=headers or self.headers)
        response.raise_for_status()
        return response.json()

    def add_tracks_to_playlist(self, playlist_id: str, track_ids: list[str]) -> bool:
        """
        Add tracks to a playlist.

        Args:
            playlist_id: The Spotify playlist ID.
            track_ids: List of Spotify track IDs to add.

        Returns:
            bool: True if successful, else raises an Exception.
        """
        endpoint = f"{self.base_url}/playlists/{playlist_id}/tracks"

        # Spotify expects URIs in the format "spotify:track:id"
        uris = [f"spotify:track:{track_id}" for track_id in track_ids]

        response = self.session.post(
            endpoint, headers=self.headers, json={"uris": uris}
        )

        if response.status_code == 201:
            return True
        raise Exception(f"Failed to add tracks: {response.status_code} {response.text}")

    def create_playlist(
        self, name: str, description: str = "", public: bool = True
    ) -> str:
        """
        Create a new playlist

        Args:
            name: The name of the new playlist.
            description: The playlist description.
            public: Whether the playlist is public.

        Returns:
            str: Spotify's response for the created playlist.
        """
        endpoint = f"{self.base_url}/me/playlists"
        payload = {"name": name, "description": description, "public": public}
        response = self.session.post(endpoint, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()["id"]
