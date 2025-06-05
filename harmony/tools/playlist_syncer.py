from typing import Protocol, List, Optional, Tuple
import re
import logging
from rich.console import Console
from rich.progress import Progress
from difflib import SequenceMatcher
from harmony.tools.logger import Logger
from harmony.tools.cli_tools import display_menu, display_submenu


class StreamingClient(Protocol):
    """Protocol defining required methods for streaming services."""

    def __init__(self):
        self.client_name = None

    def search(self, query: str, types: List[str], limit: int) -> dict:
        ...

    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> bool:
        ...

    def get_playlist_tracks(self, playlist_id: str, limit: int = 1000) -> List[dict]:
        ...

    def get_user_playlists(self, limit: int = 1000) -> List[dict]:
        ...

    def create_playlist(self, name: str) -> dict:
        ...


class PlaylistSyncer:
    """Class to handle syncing playlists between two streaming services."""

    def __init__(
        self, spotify_client: StreamingClient, apple_music_client: StreamingClient
    ):
        """
        Initialize the PlaylistSyncer with available streaming clients.

        Args:
            spotify_client: The Spotify client instance.
            apple_music_client: The Apple Music client instance.
        """
        self.spotify_client = spotify_client
        self.apple_music_client = apple_music_client
        self.source = None
        self.target = None
        self.console = Console()
        self.logger = Logger("harmony.playlist_syncer")

        # Display the menu after initialization
        self.display_sync_selector_menu()

    def sync_playlist(
        self, source_playlist: dict, target_playlists: List[dict]
    ) -> Tuple[int, int]:
        """
        Sync a playlist from the source service to the target service.

        Args:
            source_playlist: The source playlist to sync.
            target_playlists: List of playlists in the target service.

        Returns:
            A tuple containing:
                - total_tracks: Total number of tracks in the source playlist
                - synced_tracks: Number of successfully synced tracks
        """
        self.logger.log_and_print(
            f"Starting playlist sync for playlist: {source_playlist['name']}"
        )

        # Step 1: Get source tracks
        source_tracks = self.source.get_playlist_tracks(source_playlist["id"])
        self.logger.log_and_print(
            f"Found {len(source_tracks)} tracks in source playlist"
        )

        # Step 2: Get or create target playlist
        target_playlist_id, existing_target_tracks = self._get_target_playlist(
            source_playlist["name"], target_playlists
        )
        self.logger.info(
            f"Target playlist ID: {target_playlist_id} with {len(existing_target_tracks)} existing tracks"
        )

        # Step 3: Process tracks to find which ones need to be added
        successful_syncs, failed_syncs = self._process_tracks(
            source_tracks, existing_target_tracks
        )

        # Step 4: Add tracks to target playlist
        if successful_syncs:
            try:
                self.logger.log_and_print(
                    f"Adding {len(successful_syncs)} tracks to target playlist"
                )
                self.target.add_tracks_to_playlist(target_playlist_id, successful_syncs)
                self.logger.log_and_print(
                    f"\n[green]Successfully synced {len(successful_syncs)} new tracks[/green]"
                )
            except Exception as e:
                error_msg = f"Error adding tracks to playlist: {str(e)}"
                self.logger.log_and_print(
                    f"[red]{error_msg}[/red]", level=logging.ERROR
                )
        else:
            self.logger.log_and_print("\n[green]All tracks are already synced[/green]")

        # Step 5: Report any failures
        if failed_syncs:
            failed_msg = f"Failed to sync {len(failed_syncs)} tracks"
            self.logger.log_and_print(
                f"\n[yellow]{failed_msg}:[/yellow]", level=logging.WARNING
            )
            for track in failed_syncs:
                self.logger.warning(f"Failed to sync: {track}")
                self.console.print(f"[red]- {track}[/red]")

        return len(source_tracks), len(successful_syncs)

    @staticmethod
    def find_matching_playlist(
        playlist_name: str, playlists: List[dict]
    ) -> Optional[dict]:
        """
        Find the playlist with the most similar name using fuzzy matching.

        Args:
            playlist_name: The name of the playlist to match.
            playlists: List of existing playlists with 'name' keys.

        Returns:
            The best matching playlist, or None if no close match found (similarity < 0.8).
        """

        def similarity(name1: str, name2: str) -> float:
            return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

        if not playlists:
            return None

        best_match = max(playlists, key=lambda p: similarity(p["name"], playlist_name))
        similarity_score = similarity(best_match["name"], playlist_name)

        return best_match if similarity_score > 0.8 else None

    def _search_track(self, track: Tuple[str, str]) -> Optional[str]:
        """
        Search for a track in the target streaming service using multiple strategies.

        Args:
            track: Track information as a tuple of (track_name, track_artist).

        Returns:
            Track ID if found, None otherwise.
        """
        track_name = track[0]
        track_artist = track[1]

        if self.target.client_name == "Apple Music":
            types = ["songs"]
            result_path = ["results", "songs", "data"]
        elif self.target.client_name == "Spotify":
            types = ["track"]
            result_path = ["tracks", "items"]
        else:
            return None

        # Strategy 1: Full query with track name and artist
        search_query = f"{track_name} {track_artist}"
        search_results = self.target.search(query=search_query, types=types, limit=1)

        # Navigate through the nested dictionary based on service type
        items = search_results
        for key in result_path:
            items = items.get(key, {}) if isinstance(items, dict) else []

        track_id = items[0]["id"] if items else None

        # If first search fails, try additional strategies for Apple Music as Apple Music search can be stricter
        if not track_id and self.target.client_name == "Apple Music":
            # Strategy 2: Try with just the track name
            search_query = track_name
            search_results = self.target.search(
                query=search_query, types=types, limit=5
            )

            items = search_results
            for key in result_path:
                items = items.get(key, {}) if isinstance(items, dict) else []

            # Try to find a match by artist name in the results
            for item in items:
                artist_name = item.get("attributes", {}).get("artistName", "").lower()
                if (
                    track_artist.lower() in artist_name
                    or artist_name in track_artist.lower()
                ):
                    track_id = item["id"]
                    break

            # Strategy 3: Try with a simplified query (remove parentheses and features)
            if not track_id:
                simplified_name = re.sub(r"\([^)]*\)", "", track_name).strip()
                search_query = f"{simplified_name} {track_artist}"
                search_results = self.target.search(
                    query=search_query, types=types, limit=1
                )

                items = search_results
                for key in result_path:
                    items = items.get(key, {}) if isinstance(items, dict) else []

                track_id = items[0]["id"] if items else None

        return track_id

    def _get_target_playlist(
        self, source_playlist_name: str, target_playlists: List[dict]
    ) -> Tuple[str, List[dict]]:
        """
        Find or create a target playlist and get its existing tracks.

        Args:
            source_playlist_name: The name of the source playlist.
            target_playlists: List of playlists in the target service.

        Returns:
            A tuple containing:
                - target_playlist_id: ID of the target playlist (existing or newly created)
                - existing_tracks: List of tracks already in the target playlist
        """

        # Find matching playlist in target service
        matching_playlist = self.find_matching_playlist(
            source_playlist_name, target_playlists
        )

        if matching_playlist:
            self.logger.log_and_print(
                f"[magenta]Found matching playlist: {matching_playlist['name']}[/magenta]"
            )
            target_playlist_id = matching_playlist["id"]
            existing_tracks = self.target.get_playlist_tracks(target_playlist_id)
        else:
            self.logger.log_and_print(
                "[yellow]No matching playlist found. Creating new playlist...[/yellow]"
            )
            target_playlist_id = self.target.create_playlist(source_playlist_name)
            existing_tracks = []

        return target_playlist_id, existing_tracks

    @staticmethod
    def _normalize_text(text: str, is_artist: bool = False) -> str:
        """
        Normalize text by removing common variations and special characters.

        Args:
            text: The text to normalize.
            is_artist: Whether the text is an artist name (True) or track name (False).

        Returns:
            The normalized text.
        """
        # Convert to lowercase and strip whitespace
        normalized = text.lower().strip()

        if not is_artist:
            # Remove content in parentheses and brackets
            normalized = re.sub(r"\([^)]*\)", "", normalized)
            normalized = re.sub(r"\[[^\]]*\]", "", normalized)
        else:
            # Remove "the" prefix if present
            if normalized.startswith("the "):
                normalized = normalized[4:]

        # Remove common featuring indicators with various formats
        normalized = re.sub(
            r"(feat\.|ft\.|featuring|with|feat|ft)\s+[\w\s,&]+", "", normalized
        )

        # Remove special characters
        if is_artist:
            # Keep commas and ampersands for artists
            normalized = re.sub(r"[^\w\s,&]", "", normalized)
        else:
            # Remove all special characters for tracks
            normalized = re.sub(r"[^\w\s]", "", normalized)

        # Remove extra spaces
        normalized = re.sub(r"\s+", " ", normalized)

        # Handle multiple artists by splitting and sorting
        if is_artist:
            for separator in [",", " & ", " and ", " with "]:
                if separator in normalized:
                    artists = [a.strip() for a in normalized.split(separator)]
                    normalized = ", ".join(sorted(artists))
                    break

        return normalized.strip()

    def _normalize_track_name(self, name: str) -> str:
        """
        Normalize a track name by removing common variations and special characters.

        Args:
            name: The track name to normalize.

        Returns:
            The normalized track name.
        """
        return self._normalize_text(name, is_artist=False)

    def _normalize_artist_name(self, artist: str) -> str:
        """
        Normalize an artist name by removing common variations and special characters.
        Also handles multiple artists by sorting them alphabetically.

        Args:
            artist: The artist name to normalize.

        Returns:
            The normalized artist name.
        """
        return self._normalize_text(artist, is_artist=True)

    def _is_track_duplicate(
        self, track_key: Tuple[str, str], existing_track_keys: set[Tuple[str, str]]
    ) -> bool:
        """
        Check if a track (as normalized (name, artist) tuple) is already in existing tracks using various matching strategies.

        Args:
            track_key: (name, artist) tuple (should be lowercased and stripped already).
            existing_track_keys: Set of (name, artist) tuples from existing tracks.

        Returns:
            True if the track is a duplicate, False otherwise.
        """
        track_name, track_artist = track_key
        normalized_track_name = self._normalize_track_name(track_name)
        normalized_track_artist = self._normalize_artist_name(track_artist)

        for existing_name, existing_artist in existing_track_keys:
            normalized_existing_name = self._normalize_track_name(existing_name)
            normalized_existing_artist = self._normalize_artist_name(existing_artist)

            # Exact matching
            if track_name == existing_name and track_artist == existing_artist:
                return True

            if (
                normalized_track_name == normalized_existing_name
                and normalized_track_artist == normalized_existing_artist
            ):
                return True

            # Fuzzy matching
            name_similarity = SequenceMatcher(None, track_name, existing_name).ratio()
            artist_similarity = SequenceMatcher(
                None, track_artist, existing_artist
            ).ratio()
            normalized_name_similarity = SequenceMatcher(
                None, normalized_track_name, normalized_existing_name
            ).ratio()
            normalized_artist_similarity = SequenceMatcher(
                None, normalized_track_artist, normalized_existing_artist
            ).ratio()

            if name_similarity > 0.75 and artist_similarity > 0.5:
                return True
            if normalized_name_similarity > 0.75 and normalized_artist_similarity > 0.5:
                return True

            # Combined similarity
            combined_similarity = (name_similarity * 0.6) + (artist_similarity * 0.4)
            normalized_combined_similarity = (normalized_name_similarity * 0.6) + (
                normalized_artist_similarity * 0.4
            )
            if combined_similarity > 0.7 or normalized_combined_similarity > 0.7:
                return True

        return False

    def _process_tracks(
        self, source_tracks: List[dict], existing_tracks: List[dict]
    ) -> Tuple[List[str], List[str]]:
        """
        Process tracks to find which ones need to be added to the target playlist.

        Args:
            source_tracks: List of tracks from the source playlist.
            existing_tracks: List of tracks already in the target playlist.

        Returns:
            A tuple containing:
                - successful_syncs: List of track IDs to add to the target playlist
                - failed_syncs: List of track descriptions that failed to sync
        """
        successful_syncs = []
        failed_syncs = []

        # Sets of (name, artist) for fast lookup
        existing_track_keys = {
            (track["name"].lower().strip(), track["artist"].lower().strip())
            for track in existing_tracks
        }

        with Progress() as progress:
            task = progress.add_task(
                "[magenta]Syncing tracks...", total=len(source_tracks)
            )

            for track in source_tracks:
                progress.update(task, advance=1)
                track_key = (
                    track["name"].lower().strip(),
                    track["artist"].lower().strip(),
                )

                # Skip tracks already present
                if track_key in existing_track_keys or self._is_track_duplicate(
                    track_key, existing_track_keys
                ):
                    continue

                try:
                    track_id = self._search_track(track_key)
                    if track_id:
                        successful_syncs.append(track_id)
                        existing_track_keys.add(
                            track_key
                        )  # Prevents repeated adds if source_tracks has duplicates
                        self.logger.debug(f"Successful sync: {track_key}")
                    else:
                        failed_syncs.append(track_key)
                        self.logger.debug(f"Failed sync: {track_key}")
                except Exception as e:
                    failed_syncs.append(f"{track['name']} - Error: {str(e)}")

        return successful_syncs, failed_syncs

    def _get_playlists_from_services(self) -> Tuple[List[dict], List[dict], str, str]:
        """
        Fetch playlists from both source and target services.

        Returns:
            A tuple containing:
                - source_playlists: List of playlists from the source service
                - target_playlists: List of playlists from the target service
                - source_name: Name of the source service
                - target_name: Name of the target service
        """
        source_name = self.source.client_name
        target_name = self.target.client_name

        # Fetch playlists from source service
        self.logger.info(f"Fetching playlists from {source_name}")
        source_playlists = self.source.get_user_playlists()
        self.logger.info(f"Found {len(source_playlists)} playlists in {source_name}")

        # Fetch playlists from target service
        self.logger.info(f"Fetching playlists from {target_name}")
        target_playlists = self.target.get_user_playlists()
        self.logger.info(f"Found {len(target_playlists)} playlists in {target_name}")

        return source_playlists, target_playlists, source_name, target_name

    def display_sync_menu(
        self, source_client: StreamingClient, target_client: StreamingClient
    ) -> None:
        """
        Display the sync menu for the selected source and target clients.
        The direction of sync is determined by which client is passed as source and which as target.

        Args:
            source_client: The source streaming service client.
            target_client: The target streaming service client.
        """
        # Set source/target for this sync operation
        self.source = source_client
        self.target = target_client

        while True:
            # Fetch all playlists everytime you reach submenu to avoid stale data
            (
                source_playlists,
                target_playlists,
                source_name,
                target_name,
            ) = self._get_playlists_from_services()

            # Create menu options: playlists + return option
            menu_options = tuple(playlist["name"] for playlist in source_playlists) + (
                "[magenta]Return to Sync Menu[/magenta]",
            )

            # Display menu and get selection
            selection = display_submenu(
                title=f"{source_name} Playlists:",
                menu_options=menu_options,
                color="magenta",
            )

            if selection is None:
                continue
            elif selection == len(menu_options) - 1:  # Return option
                self.logger.info("User returned to main menu")
                return
            else:
                selected_playlist = source_playlists[selection]
                self.logger.info(f"User selected playlist: {selected_playlist['name']}")
                self.console.print(
                    f"\n[magenta]Syncing '{selected_playlist['name']}' from {source_name} to {target_name}...[/magenta]"
                )
                self.sync_playlist(selected_playlist, target_playlists)

    def display_sync_selector_menu(self) -> None:
        """
        Display playlist sync main menu to select source and target clients
        """
        self.logger.info("Displaying playlist sync menu")

        # Define menu options with their actions
        menu_options = [
            (
                "Sync Spotify → Apple Music",
                lambda: self.display_sync_menu(
                    self.spotify_client, self.apple_music_client
                ),
            ),
            (
                "Sync Apple Music → Spotify",
                lambda: self.display_sync_menu(
                    self.apple_music_client, self.spotify_client
                ),
            ),
        ]

        harmony_ascii = r"""
         _    , __  _ __  _ _ _   __  _ __  _    ,
        ' )  / /  )' )  )' ) ) ) / ')' )  )' )  / 
         /--/ /--/  /--'  / / / /  /  /  /  /  /  
        /  (_/  (_ /  \_ / ' (_(__/  /  (_ (__/_  
                                            //    
                                           (/     
        """

        display_menu(
            title="Sync Playlists menu",
            menu_options=menu_options,
            color="magenta",
            ascii_art=harmony_ascii,
        )
