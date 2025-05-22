from rich.console import Console


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
        self.apple_music_ascii = r"""
         ▗▄▖ ▗▄▄▖ ▗▄▄▖ ▗▖   ▗▄▄▄▖    ▗▖  ▗▖▗▖ ▗▖ ▗▄▄▖▗▄▄▄▖ ▗▄▄▖    
        ▐▌ ▐▌▐▌ ▐▌▐▌ ▐▌▐▌   ▐▌       ▐▛▚▞▜▌▐▌ ▐▌▐▌     █  ▐▌       
        ▐▛▀▜▌▐▛▀▘ ▐▛▀▘ ▐▌   ▐▛▀▀▘    ▐▌  ▐▌▐▌ ▐▌ ▝▀▚▖  █  ▐▌       
        ▐▌ ▐▌▐▌   ▐▌   ▐▙▄▄▖▐▙▄▄▖    ▐▌  ▐▌▝▚▄▞▘▗▄▄▞▘▗▄█▄▖▝▚▄▄▖                                                     
            """
        self.console = Console()
        self.apple_music_client = apple_music_client

    def display_menu(self):
        """
        Display the Apple Music tools submenu and process user input.
        """
        menu_options = [
            ("Top Albums", lambda: self.show_top_albums()),
            ("Get User Playlists", lambda: self.show_user_playlists()),
            ("[magenta]Return to Main Menu[/magenta]", lambda: "return"),
            ("[red]Exit[/red]", lambda: "exit"),
        ]

        while True:
            self.console.print("\n\n[red]" + self.apple_music_ascii + "[/red]")
            self.console.print("[red]Apple Music Menu:[/red]")

            for index, (label, _) in enumerate(menu_options, start=1):
                self.console.print(f"[red]{index}[/red]. {label}")

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

    def show_top_albums(self):
        """
        Fetch and display the user's heavy rotation albums.
        """
        try:
            # Heavy Rotation is what Apple Music refers to as top recent albums
            heavy_rotation_data = self.apple_music_client.get_heavy_rotation(limit=10)

            if not heavy_rotation_data:
                self.console.print(
                    "[bold yellow]No heavy rotation albums found.[/bold yellow]"
                )
                self._pause_for_user()
                return

            # Display album names and artist names
            self.console.print("\n[red]Your Heavy Rotation Albums:[/red]")
            for index, album in enumerate(heavy_rotation_data, start=1):
                album_name = album.get("name", "Unknown Album")
                artist_name = album.get("artist", "Unknown Artist")
                self.console.print(f"[red]{index}[/red]. {album_name} by {artist_name}")

        except Exception as e:
            self.console.print(
                f"[bold red]Failed to fetch heavy rotation data: {str(e)}[/bold red]"
            )

        self._pause_for_user()

    def show_user_playlists(self):
        """
        Fetch and display the user's playlists and their tracks.
        Implements a submenu for navigating playlists and tracks.
        """
        try:
            # Step 1: Fetch all playlists
            playlists = self.apple_music_client.get_user_playlists()
            if not playlists:
                self.console.print("[bold yellow]No playlists found.[/bold yellow]")
                self._pause_for_user()
                return

            # Step 2: Display Playlists Submenu
            while True:
                self.console.print(
                    "\n[red]Your Playlists (select a playlist to list tracks):[/red]"
                )

                # List playlists with index
                for index, playlist in enumerate(playlists, start=1):
                    self.console.print(f"[red]{index}[/red]. {playlist['name']}")

                # Get user choice
                self.console.print(
                    f"[red]{len(playlists) + 1}. Return to Apple Music Menu[/red]"
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
            self.console.print(f"\n[red]Tracks in Playlist: {playlist['name']}[/red]")
            playlist_id = playlist["id"]
            tracks = self.apple_music_client.get_playlist_tracks(playlist_id)

            # No tracks in the playlist
            if not tracks:
                self.console.print(
                    "[bold yellow]No tracks found in this playlist.[/bold yellow]"
                )
            else:
                # Print the tracks
                for index, track in enumerate(tracks, start=1):
                    self.console.print(
                        f"[red]{index}[/red]. {track['name']} by {track['artist']}"
                    )
        except Exception as e:
            self.console.print(f"[bold red]Failed to fetch tracks: {str(e)}[/bold red]")

        self._pause_for_user()

    def _pause_for_user(self):
        """
        Pauses execution to allow the user to review the content by pressing any key.
        """
        self.console.input("\n[red]Press any key to return to the menu...[/red]")
