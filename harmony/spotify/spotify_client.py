import os
import requests
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
from streaming_client import StreamingClient

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
            base_url (str): The base URL for the Spotify API. Default is Spotify's API URL.
        """
        self.access_token = self._authenticate()

        super().__init__(base_url=base_url, api_key=self.access_token)

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

    def _get_client_credentials(self) -> tuple[str, str]:
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
            client_id (str): The application's Spotify client ID.

        Returns:
            str: The authorization code provided by Spotify.
        """
        auth_params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": self.REDIRECT_URI,
            "scope": "user-read-private",
        }
        auth_url = f"{self.AUTH_URL}?{urlencode(auth_params)}"

        # Open the authorization URL in the user's browser
        print("Opening your browser for Spotify authorization...")
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

        print("Waiting for Spotify authorization...")
        httpd = HTTPServer(("localhost", 8888), CallbackHandler)
        httpd.handle_request()  # Wait for a single authorization request (blocking)

        # Retrieve the authorization code from the HTTP handler
        authorization_code = getattr(httpd, "authorization_code", None)
        if not authorization_code:
            raise Exception(
                "Authorization code could not be obtained. Please try again."
            )

        return authorization_code

    def _exchange_code_for_token(
        self, authorization_code: str, client_id: str, client_secret: str
    ) -> str:
        """
        Exchange the authorization code for an access token from Spotify.

        Args:
            authorization_code (str): The authorization code from Spotify.
            client_id (str): Spotify's client ID for your app.
            client_secret (str): Spotify's client secret for your app.

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

        response = requests.post(self.TOKEN_URL, data=token_data)
        if response.status_code != 200:
            raise Exception(f"Failed to obtain an access token: {response.text}")

        # Parse the response for the access token
        token_response = response.json()
        access_token = token_response.get("access_token")
        if not access_token:
            raise Exception("Access token is missing in the response.")

        return access_token
