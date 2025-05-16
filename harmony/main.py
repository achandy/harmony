from rich.console import Console
from spotify.spotify_client import SpotifyClient
from spotify.spotify_cli import SpotifyCLI
from apple_music.apple_music_client import AppleMusicClient
from apple_music.apple_music_cli import AppleMusicCLI

console = Console()

harmony_ascii = r"""
 _    , __  _ __  _ _ _   __  _ __  _    ,
' )  / /  )' )  )' ) ) ) / ')' )  )' )  / 
 /--/ /--/  /--'  / / / /  /  /  /  /  /  
/  (_/  (_ /  \_ / ' (_(__/  /  (_ (__/_  
                                    //    
                                   (/     
"""


class MainMenu:
    """Handles the main menu for the Harmony CLI."""

    def __init__(self):
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
            menu_options.insert(1, ("Spotify Tools", self.display_spotify_menu))
        if self.apple_music_client:
            menu_options.append(("Apple Music Tools", self.display_apple_music_menu))

        # Exit option
        menu_options.append(("Exit", self.exit_program))

        return menu_options

    def authenticate_spotify(self):
        """Authenticate Spotify."""
        console.print("\nAuthenticating Spotify")
        self.spotify_client = SpotifyClient()
        console.print("Spotify authentication successful!")

    def authenticate_apple_music(self):
        """Authenticate Apple Music."""
        console.print("\nAuthenticating Apple Music")
        self.apple_music_client = AppleMusicClient()
        console.print("Apple Music authentication successful!")

    def display_spotify_menu(self):
        """Display Spotify tools menu."""
        SpotifyCLI(self.spotify_client).display_menu()

    def display_apple_music_menu(self):
        """Display Apple Music tools menu."""
        AppleMusicCLI(self.apple_music_client).display_menu()

    def display(self):
        """Display the dynamically updating menu."""
        while True:
            console.print("\n\n" + harmony_ascii)
            console.print("[bold magenta]Main Menu:[/bold magenta]")

            menu_options = self._get_menu_options()

            # Display menu items
            for index, (label, _) in enumerate(menu_options, start=1):
                console.print(f"[bold magenta]{index}[/bold magenta]. {label}")

            # Get user choice
            try:
                choice = int(console.input("Enter your choice: "))
                if 1 <= choice <= len(menu_options):
                    _, action = menu_options[choice - 1]
                    action()  # Execute the corresponding action
                else:
                    console.print("[bold red]Invalid choice. Try again.[/bold red]")
            except ValueError:
                console.print("[bold red]Please enter a valid number.[/bold red]")

    @staticmethod
    def exit_program():
        """
        Exit the program entirely.
        """
        console.print("[bold magenta]Goodbye![/bold magenta]")
        exit(0)


def main():
    MainMenu().display()


if __name__ == "__main__":
    main()
