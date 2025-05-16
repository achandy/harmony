from rich.console import Console

console = Console()

apple_music_ascii = r"""
 ▗▄▖ ▗▄▄▖ ▗▄▄▖ ▗▖   ▗▄▄▄▖    ▗▖  ▗▖▗▖ ▗▖ ▗▄▄▖▗▄▄▄▖ ▗▄▄▖    
▐▌ ▐▌▐▌ ▐▌▐▌ ▐▌▐▌   ▐▌       ▐▛▚▞▜▌▐▌ ▐▌▐▌     █  ▐▌       
▐▛▀▜▌▐▛▀▘ ▐▛▀▘ ▐▌   ▐▛▀▀▘    ▐▌  ▐▌▐▌ ▐▌ ▝▀▚▖  █  ▐▌       
▐▌ ▐▌▐▌   ▐▌   ▐▙▄▄▖▐▙▄▄▖    ▐▌  ▐▌▝▚▄▞▘▗▄▄▞▘▗▄█▄▖▝▚▄▄▖                                                     
    """


class AppleMusicCLI:
    """
    Handles the Apple Music submenu in the CLI.
    Communicates directly with the AppleMusicClient for operations.
    """

    def __init__(self, apple_music_client):
        """
        Initialize the Apple Music CLI.

        Args:
            apple_music_client: An authenticated instance of AppleMusicClient.
        """
        self.apple_music_client = apple_music_client

    def display_menu(self):
        """
        Display the Apple Music tools submenu and process user input.
        """
        menu_options = [
            ("Return to Main Menu", self.return_to_main_menu),
            ("Exit", self.exit_program),
        ]

        while True:
            console.print("\n\n[red]" + apple_music_ascii + "[/red]")
            console.print("[red]Apple Music Menu:[/red]")

            # Display menu items
            for index, (label, _) in enumerate(menu_options, start=1):
                console.print(f"[red]{index}[/red]. {label}")

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
