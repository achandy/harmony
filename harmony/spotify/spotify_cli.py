from rich.console import Console


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
        self.spotify_ascii = r"""
           _____             _   _  __       
          / ____|           | | (_)/ _|      
         | (___  _ __   ___ | |_ _| |_ _   _ 
          \___ \| '_ \ / _ \| __| |  _| | | |
          ____) | |_) | (_) | |_| | | | |_| |
         |_____/| .__/ \___/ \__|_|_|  \__, |
                | |                     __/ |
                |_|                    |___/ 
            """
        self.console = Console()
        self.spotify_client = spotify_client

    def display_menu(self):
        """
        Display the Spotify tools submenu and process user input.
        """
        menu_options = [
            ("Top Songs (Past Month)", lambda: self.show_top_tracks("short_term")),
            ("Top Songs (Past Year)", lambda: self.show_top_tracks("long_term")),
            ("Top Artists (Past Month)", lambda: self.show_top_artists("short_term")),
            ("Top Artists (Past Year)", lambda: self.show_top_artists("long_term")),
            ("Get User Playlists", lambda: self.show_user_playlists()),
            ("[magenta]Return to Main Menu[/magenta]", lambda: "return"),
            ("[red]Exit[/red]", lambda: "exit"),
        ]

        while True:
            self.console.print("\n\n[green1]" + self.spotify_ascii + "[/green1]")
            self.console.print("[green1]Spotify Menu:[/green1]")

            # Display menu items
            for index, (label, _) in enumerate(menu_options, start=1):
                self.console.print(f"[green1]{index}[/green1]. {label}")

            # Get user choice
            try:
                choice = int(self.console.input("Enter your choice: "))
                if 1 <= choice <= len(menu_options):
                    _, action = menu_options[choice - 1]
                    result = action()
                    if result == "return":
                        self.console.print(
                            "[bold magenta]Returning to the main menu...[/bold magenta]"
                        )
                        return
                    elif result == "exit":
                        self.console.print("[bold magenta]Goodbye![/bold magenta]")
                        exit(0)
                else:
                    self.console.print(
                        "[bold red]Invalid choice. Please select a valid option.[/bold red]"
                    )
            except ValueError:
                self.console.print("[bold red]Please enter a valid number.[/bold red]")

    def show_top_tracks(self, term: str):
        self._show_top_items("tracks", term)

    def show_top_artists(self, term: str):
        self._show_top_items("artists", term)

    def _show_top_items(self, top_type: str, term: str):
        """
        Helper method to retrieve and display user's top items (tracks or artists).

        Args:
            top_type (str): The type of top object to retrieve ('tracks' or 'artists').
            term (str): The time range for top items ('short_term', 'medium_term', 'long_term').
        """
        try:
            # Fetch the top items using the Spotify client
            top_items = self.spotify_client.get_top(top_type=top_type, term=term)

            # Display a message if no items are returned
            if not top_items:
                self.console.print(
                    f"[bold yellow]No {top_type} found for the specified time range.[/bold yellow]"
                )
                self._pause_for_user()
                return

            # Print the top items
            self.console.print(
                f"\n[green1]Your Top {top_type.capitalize()} ({term.replace('_', ' ').capitalize()}):[/green1]"
            )

            # Tracks and artists formatting
            for index, item in enumerate(top_items, start=1):
                if top_type == "tracks":
                    self.console.print(
                        f"[green1]{index}[/green1]. {item['name']} by {', '.join(artist['name'] for artist in item['artists'])}"
                    )
                elif top_type == "artists":
                    self.console.print(f"[green1]{index}[/green1]. {item['name']}")

        except Exception as e:
            self.console.print(
                f"[bold red]Failed to fetch top {top_type}: {str(e)}[/bold red]"
            )

        self._pause_for_user()

    def show_user_playlists(self):
        """
        Fetch and display the user's playlists and their tracks.
        Implements a submenu for navigating playlists and tracks.
        """
        try:
            # Step 1: Fetch all playlists
            playlists = self.spotify_client.get_user_playlists()
            if not playlists:
                self.console.print("[bold yellow]No playlists found.[/bold yellow]")
                self._pause_for_user()
                return

            # Step 2: Display Playlists Submenu
            while True:
                self.console.print(
                    "\n[green1]Select a playlist to view its tracks: [/green1]"
                )

                # List playlists with index
                for index, playlist in enumerate(playlists, start=1):
                    self.console.print(f"[green1]{index}[/green1]. {playlist['name']}")

                # Get user choice
                self.console.print(
                    f"[green1]{len(playlists) + 1}. Return to Spotify Menu[/green1]"
                )
                try:
                    choice = int(self.console.input("Enter the playlist number: "))
                    if 1 <= choice <= len(playlists):
                        selected_playlist = playlists[choice - 1]
                        self._display_playlist_tracks(selected_playlist)
                    elif choice == len(playlists) + 1:
                        return  # Go back to the previous menu
                    else:
                        self.console.print(
                            "[bold red]Invalid choice. Please try again.[/bold red]"
                        )
                except ValueError:
                    self.console.print(
                        "[bold red]Please enter a valid number.[/bold red]"
                    )
        except Exception as e:
            self.console.print(
                f"[bold red]Failed to fetch playlists: {str(e)}[/bold red]"
            )

        self._pause_for_user()

    def _display_playlist_tracks(self, playlist: dict):
        """
        Display the tracks from a specific playlist.

        Args:
            playlist (dict): The playlist details.
        """
        try:
            # Fetch playlist tracks
            self.console.print(
                f"\n[green1]Tracks in Playlist: {playlist['name']}[/green1]"
            )
            playlist_id = playlist["id"]
            tracks = self.spotify_client.get_playlist_tracks(playlist_id)

            # No tracks in the playlist
            if not tracks:
                self.console.print(
                    "[bold yellow]No tracks found in this playlist.[/bold yellow]"
                )
            else:
                # Print the tracks
                for index, item in enumerate(tracks, start=1):
                    self.console.print(
                        f"[green1]{index}[/green1]. {item['name']} by {item['artist']}"
                    )
        except Exception as e:
            self.console.print(f"[bold red]Failed to fetch tracks: {str(e)}[/bold red]")

        self._pause_for_user()

    def _pause_for_user(self):
        """
        Pauses execution to allow the user to review the content by pressing any key.
        """
        self.console.input("\n[green1]Press any key to return to the menu...[/green1]")
