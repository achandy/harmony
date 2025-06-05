from rich.console import Console
from harmony.tools.logger import Logger
from harmony.spotify.spotify_client import SpotifyClient
from harmony.spotify.spotify_cli import SpotifyCLI
from harmony.apple_music.apple_music_client import AppleMusicClient
from harmony.apple_music.apple_music_cli import AppleMusicCLI
from harmony.tools.playlist_syncer import PlaylistSyncer
from harmony.tools.cli_tools import display_menu


class MainMenu:
    """Handles the main menu for the Harmony CLI."""

    def __init__(self):
        self.console = Console()
        self.logger = Logger("harmony.main")
        self.spotify_client = None
        self.apple_music_client = None

    def _get_menu_options(self):
        """
        Dynamically generate menu options based on authentication states.

        Returns:
            list: A list of tuples, where each tuple contains a menu label and its corresponding action.
        """

        # Default options
        menu_options = [
            ("Authenticate Spotify", self.authenticate_spotify),
            ("Authenticate Apple Music", self.authenticate_apple_music),
        ]

        # Add tools options only if authenticated
        if self.spotify_client:
            menu_options.append(("Spotify Tools", self.display_spotify_menu))
        if self.apple_music_client:
            menu_options.append(("Apple Music Tools", self.display_apple_music_menu))
        if self.spotify_client and self.apple_music_client:
            menu_options.append(("Sync Playlists", self.display_sync_menu))

        return menu_options

    def authenticate_spotify(self):
        """Authenticate Spotify."""
        self.logger.log_and_print("\nAuthenticating Spotify")
        self.spotify_client = SpotifyClient()
        self.logger.log_and_print("Spotify authentication successful")

    def authenticate_apple_music(self):
        """Authenticate Apple Music."""
        self.logger.log_and_print("Starting Apple Music authentication")
        self.apple_music_client = AppleMusicClient()
        self.logger.log_and_print("Apple Music authentication successful")

    def display_spotify_menu(self):
        """Display Spotify tools menu."""
        SpotifyCLI(self.spotify_client).display_menu()

    def display_apple_music_menu(self):
        """Display Apple Music tools menu."""
        AppleMusicCLI(self.apple_music_client).display_menu()

    def display_sync_menu(self):
        """Display the playlist sync menu"""
        PlaylistSyncer(self.spotify_client, self.apple_music_client)

    def display(self):
        """Display the main menu."""
        self.logger.info("Starting Harmony main menu")
        harmony_ascii = r"""
         _    , __  _ __  _ _ _   __  _ __  _    ,
        ' )  / /  )' )  )' ) ) ) / ')' )  )' )  / 
         /--/ /--/  /--'  / / / /  /  /  /  /  /  
        /  (_/  (_ /  \_ / ' (_(__/  /  (_ (__/_  
                                            //    
                                           (/     
        """

        display_menu(
            title="Main Menu",
            color="magenta",
            dynamic_options=self._get_menu_options,
            ascii_art=harmony_ascii,
        )

    def exit_program(self):
        """
        Exit the program entirely.
        """
        self.logger.info("User exited the application")
        self.console.print("[bold magenta]Goodbye![/bold magenta]")
        exit(0)


def main():
    logger = Logger("harmony")
    logger.info("Starting Harmony application")
    try:
        MainMenu().display()
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        raise


if __name__ == "__main__":
    main()
