from rich.console import Console

console = Console()

spotify_ascii = r"""
   _____             _   _  __       
  / ____|           | | (_)/ _|      
 | (___  _ __   ___ | |_ _| |_ _   _ 
  \___ \| '_ \ / _ \| __| |  _| | | |
  ____) | |_) | (_) | |_| | | | |_| |
 |_____/| .__/ \___/ \__|_|_|  \__, |
        | |                     __/ |
        |_|                    |___/ 
    """


class SpotifyCLI:
    """
    Handles the Spotify submenu in the CLI.
    Communicates directly with the SpotifyClient for operations like searching.
    """

    def __init__(self, spotify_client):
        """
        Initialize the Spotify CLI.

        Args:
            spotify_client: An authenticated instance of SpotifyClient.
        """
        self.spotify_client = spotify_client

    def display_menu(self):
        """
        Display the Spotify tools submenu and process user input.
        """
        menu_options = [
            ("Return to Main Menu", self.return_to_main_menu),
            ("Exit", self.exit_program),
        ]

        while True:
            console.print("\n\n[green1]" + spotify_ascii + "[/green1]")
            console.print("[green1]Spotify Menu:[/green1]")

            # Display menu items
            for index, (label, _) in enumerate(menu_options, start=1):
                console.print(f"[green1]{index}[/green1]. {label}")

            # Get user choice
            try:
                choice = int(console.input("Enter your choice: "))
                if 1 <= choice <= len(menu_options):
                    _, action = menu_options[choice - 1]
                    if action == self.return_to_main_menu:
                        action()
                        break
                    action()
                else:
                    console.print(
                        "[bold red]Invalid choice. Please select a valid option.[/bold red]"
                    )
            except ValueError:
                console.print("[bold red]Please enter a valid number.[/bold red]")

    @staticmethod
    def return_to_main_menu():
        """
        Return to the main menu (breaking out of the loop).
        """
        console.print("[bold magenta]Returning to the main menu...[/bold magenta]")
        return

    @staticmethod
    def exit_program():
        """
        Exit the program entirely.
        """
        console.print("[bold magenta]Goodbye![/bold magenta]")
        exit(0)
