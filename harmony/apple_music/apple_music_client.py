import os
import jwt
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from urllib.parse import parse_qs
import webbrowser
from dotenv import load_dotenv
from harmony.streaming_client import StreamingClient

load_dotenv()


class AppleMusicClient(StreamingClient):
    """
    A client for interacting with the Apple Music API, authenticating
    via a local HTTP server and MusicKit.js toolkit.
    """

    JWT_ALGORITHM = "ES256"
    REDIRECT_URI = "http://localhost:8888/callback"

    def __init__(self, base_url: str = "https://api.music.apple.com/v1"):
        """
        Initialize the Apple Music client:
        - Generate the developer token.
        - Start a local HTTP server for user authentication.

        Args:
            base_url: The base URL for the Apple Music API. Default is AM's API URL.
        """

        super().__init__(client_name="Apple Music", base_url=base_url)

        self.developer_token = self._get_developer_token()
        self.user_token = self._authenticate(self.developer_token)

        # Configure session headers with both tokens
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.developer_token}",
                "Music-User-Token": self.user_token,
                "Content-Type": "application/json",
            }
        )

    def _authenticate(self, developer_token: str) -> str:
        """
        Start a local HTTP server for MusicKit.js-based user authentication.

        Args:
            developer_token: A valid developer token for authentication.

        Returns:
            str: The authenticated music user token.
        """

        # Open the authorization URL in the user's browser
        self.logger.log_and_print("Opening browser for Apple Music authorization")
        webbrowser.open("http://localhost:8888")

        class CallbackHandler(BaseHTTPRequestHandler):
            """Handles HTTP requests for the local authentication server."""

            music_user_token = None

            def log_message(self, format, *args):
                # Suppress HTTP server logging
                pass

            def do_GET(self):
                if self.path == "/":
                    self._serve_auth_page(developer_token)
                elif self.path.startswith("/callback"):
                    self._process_callback()

            def _serve_auth_page(self, token):
                """
                Serve the MusicKit.js authentication page.
                """
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                with open("harmony/apple_music/musickit_auth.html", "r") as file:
                    html_content = file.read().replace("{{DEVELOPER_TOKEN}}", token)
                    self.wfile.write(html_content.encode("utf-8"))

            def _process_callback(self):
                """
                Process the callback and extract the music user token.
                """
                query_components = parse_qs(self.path.split("?", 1)[-1])
                CallbackHandler.music_user_token = query_components.get(
                    "musicUserToken", [None]
                )[0]

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"Authorization successful! You can close this window."
                )

        self.logger.log_and_print("Waiting for Apple Music authorization callback")
        httpd = HTTPServer(("localhost", 8888), CallbackHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()

        # Wait for authorization confirmation
        while not CallbackHandler.music_user_token:
            time.sleep(1)
        authorization_code = CallbackHandler.music_user_token
        self.logger.info("Apple Music user token received")

        # Cleanup
        httpd.shutdown()
        thread.join()
        self.logger.debug("Authorization server shutdown")

        return authorization_code

    def _get_developer_token(self) -> str:
        """
        Generate an Apple Music developer token (JWT).
        Requires `APPLE_KEY_ID`, `APPLE_TEAM_ID`, and `APPLE_PRIVATE_KEY`
        environment variables set in `.env`.

        Returns:
            str: JWT developer token.
        """
        self.logger.info("Generating Apple Music developer token")
        key_id = os.getenv("APPLE_KEY_ID")
        team_id = os.getenv("APPLE_TEAM_ID")
        private_key = os.getenv("APPLE_PRIVATE_KEY")

        if not all([key_id, team_id, private_key]):
            error_msg = "APPLE_KEY_ID, APPLE_TEAM_ID, and APPLE_PRIVATE_KEY must be set in the .env file."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # JWT header and payload
        header = {"alg": self.JWT_ALGORITHM, "kid": key_id}
        payload = {
            "iss": team_id,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600 * 12,  # Token valid for 12 hours
        }

        token = jwt.encode(
            payload, private_key, algorithm=self.JWT_ALGORITHM, headers=header
        )
        self.logger.info("Successfully generated Apple Music developer token")
        return token

    def get_heavy_rotation(self, limit: int = 10) -> list[dict]:
        """
        Fetch the user's heavy rotation albums.

        Args:
            limit: The number of items to retrieve (default: 10).

        Returns:
            list[dict]: A list of albums with their names and artist names.
        """
        endpoint = f"{self.base_url}/me/history/heavy-rotation"
        params = {"limit": limit}

        # Make the API request
        response = self.session.get(endpoint, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to get heavy rotation data: {response.text}")

        # Parse and filter library-albums
        items = response.json().get("data", [])
        return [
            {
                "name": item["attributes"].get("name", "Unknown Album"),
                "artist": item["attributes"].get("artistName", "Unknown Artist"),
            }
            for item in items
            if item["type"] == "library-albums"
        ]

    def get_user_playlists(self, limit: int = 100) -> list[dict]:
        """
        Fetch the user's playlists.

        Args:
            limit: Maximum number of playlists to retrieve (default: 25).

        Returns:
            list[dict]: A list of playlists with their names and IDs.
        """
        endpoint = f"{self.base_url}/me/library/playlists"
        params = {"limit": limit}

        # Make the API request
        response = self.session.get(endpoint, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to get playlists: {response.text}")

        # Structure output playlists
        items = response.json().get("data", [])
        return [
            {
                "id": playlist["id"],
                "name": playlist["attributes"].get("name", "Unknown Playlist"),
            }
            for playlist in items
        ]

    def get_playlist_tracks(self, playlist_id: str, limit: int = 100) -> list[dict]:
        """
        Fetch the tracks from a specific playlist.

        Args:
            playlist_id: The Apple Music ID of the playlist.
            limit: Maximum number of tracks (default: 100).

        Returns:
            list[dict]: A list of tracks with their names and artist names.
        """
        endpoint = f"{self.base_url}/me/library/playlists/{playlist_id}/tracks"
        params = {"limit": limit}

        # Make the API request
        response = self.session.get(endpoint, params=params)
        if response.status_code == 404:
            error = response.json()
            if (
                error.get("errors")
                and error["errors"][0].get("detail")
                == "No related resources found for tracks"
            ):
                return []  # Handle empty playlist
        if response.status_code != 200:
            raise Exception(
                f"Failed to get tracks for playlist {playlist_id}: {response.text}"
            )

        # Structure output tracks
        items = response.json().get("data", [])
        return [
            {
                "name": track["attributes"].get("name", "Unknown Track"),
                "artist": track["attributes"].get("artistName", "Unknown Artist"),
            }
            for track in items
        ]

    def search(
        self,
        query: str,
        types: list[str] = None,
        limit: int = 10,
        storefront: str = "us",
        headers: dict = None,
    ) -> dict:
        """
        Search Apple Music catalog.

        Args:
            query: The search term
            types: Types of items to search for (e.g., ['songs', 'albums']).
                   Defaults to ['songs'].
            limit: Number of results to return.
            storefront: Storefront code.
            headers: Additional headers to include in the request.
                     If None, uses the session headers with authentication.

        Returns:
            dict: Search results organized by type.
        """
        url = f"{self.base_url}/catalog/{storefront}/search"

        params = {
            "term": query,
            "types": ",".join(types),
            "limit": limit,
        }

        try:
            request_headers = self.session.headers.copy()
            if headers:
                request_headers.update(headers)

            self.logger.debug(f"Searching Apple Music with params: {params}")
            response = self.session.get(url, params=params, headers=request_headers)
            response.raise_for_status()
            result = response.json()
            self.logger.debug(f"Search response status: {response.status_code}")
            return result
        except Exception as e:
            self.logger.error(f"Error searching Apple Music: {str(e)}")
            # Return empty results structure instead of raising an exception
            return {"results": {t: {"data": []} for t in types}}

    def add_tracks_to_playlist(self, playlist_id: str, track_ids: list[str]) -> bool:
        """
        Add tracks to a user library playlist.

        Args:
            playlist_id: The Apple Music playlist ID.
            track_ids: List of Apple Music track IDs to add.

        Returns:
            bool: True if successful, else raises an Exception.
        """
        endpoint = f"{self.base_url}/me/library/playlists/{playlist_id}/tracks"

        payload = {
            "data": [{"id": track_id, "type": "songs"} for track_id in track_ids]
        }

        response = self.session.post(endpoint, json=payload)
        if response.status_code == 204:
            return True
        raise Exception(f"Failed to add tracks: {response.status_code} {response.text}")

    def create_playlist(self, name: str, description: str = "") -> str:
        """
        Create a new Apple Music playlist in the user's library.

        Args:
            name: The name for the new playlist.
            description: A description for the playlist.

        Returns:
            str: Returns playlist id
        """
        endpoint = f"{self.base_url}/me/library/playlists"
        payload = {"attributes": {"name": name, "description": description}}
        response = self.session.post(endpoint, json=payload)
        if response.status_code not in (201, 202):
            raise Exception(
                f"Failed to create playlist: {response.status_code} {response.text}"
            )
        return response.json()["data"][0]["id"]
