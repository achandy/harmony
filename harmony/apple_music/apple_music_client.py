import os
import jwt
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from urllib.parse import parse_qs
import webbrowser
from dotenv import load_dotenv
from streaming_client import StreamingClient

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
            base_url (str): The base URL for the Apple Music API. Default is AM's API URL.
        """

        self.developer_token = self._get_developer_token()
        self.user_token = self._authenticate(self.developer_token)

        super().__init__(base_url)

        # Configure session headers with both tokens
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.developer_token}",
                "Music-User-Token": self.user_token,
            }
        )

    def _authenticate(self, developer_token: str) -> str:
        """
        Start a local HTTP server for MusicKit.js-based user authentication.

        Args:
            developer_token (str): A valid developer token for authentication.

        Returns:
            str: The authenticated music user token.
        """

        # Open the authorization URL in the user's browser
        print("Opening your browser for Apple Music authorization...")
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

        print("Waiting for AM authorization...")
        httpd = HTTPServer(("localhost", 8888), CallbackHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()

        # Wait for authorization confirmation
        while not CallbackHandler.music_user_token:
            time.sleep(1)
        authorization_code = CallbackHandler.music_user_token

        # Cleanup
        httpd.shutdown()
        thread.join()

        return authorization_code

    def _get_developer_token(self) -> str:
        """
        Generate an Apple Music developer token (JWT).
        Requires `APPLE_KEY_ID`, `APPLE_TEAM_ID`, and `APPLE_PRIVATE_KEY`
        environment variables set in `.env`.

        Returns:
            str: JWT developer token.
        """
        key_id = os.getenv("APPLE_KEY_ID")
        team_id = os.getenv("APPLE_TEAM_ID")
        private_key = os.getenv("APPLE_PRIVATE_KEY")

        if not all([key_id, team_id, private_key]):
            raise ValueError(
                "APPLE_KEY_ID, APPLE_TEAM_ID, and APPLE_PRIVATE_KEY must be set in the .env file."
            )

        # JWT header and payload
        header = {"alg": self.JWT_ALGORITHM, "kid": key_id}
        payload = {
            "iss": team_id,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600 * 12,  # Token valid for 12 hours
        }

        return jwt.encode(
            payload, private_key, algorithm=self.JWT_ALGORITHM, headers=header
        )
