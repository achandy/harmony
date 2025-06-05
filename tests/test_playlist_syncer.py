import pytest
from unittest.mock import patch, MagicMock
from harmony.tools.playlist_syncer import PlaylistSyncer, StreamingClient


@pytest.fixture
def mock_spotify_client():
    """
    Fixture to provide a mock Spotify client.
    """
    mock_client = MagicMock(spec=StreamingClient)
    mock_client.client_name = "Spotify"
    return mock_client


@pytest.fixture
def mock_apple_music_client():
    """
    Fixture to provide a mock Apple Music client.
    """
    mock_client = MagicMock(spec=StreamingClient)
    mock_client.client_name = "Apple Music"
    return mock_client


@pytest.fixture
def playlist_syncer(mock_spotify_client, mock_apple_music_client):
    """
    Fixture to provide a PlaylistSyncer instance with mocked clients.
    """
    with patch("harmony.tools.playlist_syncer.Logger"), patch(
        "harmony.tools.playlist_syncer.Console"
    ), patch("harmony.tools.playlist_syncer.display_menu"), patch(
        "harmony.tools.playlist_syncer.display_submenu"
    ), patch.object(
        PlaylistSyncer, "display_sync_selector_menu"
    ):
        syncer = PlaylistSyncer(mock_spotify_client, mock_apple_music_client)
        return syncer


def test_find_matching_playlist():
    """
    Test the find_matching_playlist static method.
    """
    playlist_name = "Drums and Guiter"
    playlists = [
        {"id": "1", "name": "Lifts"},
        {"id": "2", "name": "Drum and Guitar!"},
        {"id": "3", "name": "Playlists 2"},
    ]

    # Test exact match
    result = PlaylistSyncer.find_matching_playlist(playlist_name, playlists)
    assert result["id"] == "2"

    # Test close match
    result = PlaylistSyncer.find_matching_playlist("Drums Guitar", playlists)
    assert result["id"] == "2"

    # Test no match
    result = PlaylistSyncer.find_matching_playlist("Something Else", playlists)
    assert result is None


def test_normalize_text():
    """
    Test the _normalize_text method.
    """
    # Test track name normalization
    track_name = "Song Title (feat. Another Artist) [Remix]"
    normalized = PlaylistSyncer._normalize_text(track_name, is_artist=False)
    assert "feat" not in normalized
    assert "Remix" not in normalized
    assert normalized == "song title"

    # Test artist name normalization
    artist_name = "The Artist Name & Another Artist"
    normalized = PlaylistSyncer._normalize_text(artist_name, is_artist=True)
    assert normalized == "another artist, artist name"

    # Test artist with commas
    artist_name = "Artist1, Artist2, Artist3"
    normalized = PlaylistSyncer._normalize_text(artist_name, is_artist=True)
    assert normalized == "artist1, artist2, artist3"


def test_normalize_track_name(playlist_syncer):
    """
    Test the _normalize_track_name method.
    """
    track_name = "Song Title (feat. Another Artist) [Remix]"
    normalized = playlist_syncer._normalize_track_name(track_name)
    assert normalized == "song title"


def test_normalize_artist_name(playlist_syncer):
    """
    Test the _normalize_artist_name method.
    """
    artist_name = "The Artist Name & Another Artist"
    normalized = playlist_syncer._normalize_artist_name(artist_name)
    assert normalized == "another artist, artist name"


def test_is_track_duplicate(playlist_syncer):
    """
    Test the _is_track_duplicate method.
    """
    existing_track_keys = {
        ("song one", "artist one"),
        ("song two", "artist two"),
        ("song three", "artist three"),
    }

    # Test exact match
    assert playlist_syncer._is_track_duplicate(
        ("song one", "artist one"), existing_track_keys
    )

    # Test case insensitive match
    assert playlist_syncer._is_track_duplicate(
        ("Song One", "Artist One"), existing_track_keys
    )

    # Test close match
    assert playlist_syncer._is_track_duplicate(
        ("song one (remix)", "artist one"), existing_track_keys
    )

    # Test no match
    assert not playlist_syncer._is_track_duplicate(
        ("different song", "different artist"), existing_track_keys
    )


def test_search_track(playlist_syncer, mock_spotify_client, mock_apple_music_client):
    """
    Test the _search_track method.
    """
    # Setup for Spotify target
    playlist_syncer.source = mock_apple_music_client
    playlist_syncer.target = mock_spotify_client

    mock_spotify_client.search.return_value = {
        "tracks": {"items": [{"id": "spotify_track_id"}]}
    }

    # Test Spotify search
    track = ("Test Song", "Test Artist")
    track_id = playlist_syncer._search_track(track)
    assert track_id == "spotify_track_id"
    mock_spotify_client.search.assert_called_with(
        query="Test Song Test Artist", types=["track"], limit=1
    )

    # Setup for Apple Music target
    playlist_syncer.source = mock_spotify_client
    playlist_syncer.target = mock_apple_music_client

    mock_apple_music_client.search.return_value = {
        "results": {"songs": {"data": [{"id": "apple_music_track_id"}]}}
    }

    # Test Apple Music search
    track_id = playlist_syncer._search_track(track)
    assert track_id == "apple_music_track_id"
    mock_apple_music_client.search.assert_called_with(
        query="Test Song Test Artist", types=["songs"], limit=1
    )

    # Test failed search
    mock_apple_music_client.search.return_value = {"results": {"songs": {"data": []}}}
    track_id = playlist_syncer._search_track(track)
    assert track_id is None


def test_get_target_playlist(
    playlist_syncer, mock_spotify_client, mock_apple_music_client
):
    """
    Test the _get_target_playlist method.
    """
    playlist_syncer.source = mock_spotify_client
    playlist_syncer.target = mock_apple_music_client

    # Test finding existing playlist
    target_playlists = [
        {"id": "1", "name": "Some Playlist"},
        {"id": "2", "name": "My Playlist"},
    ]

    with patch.object(PlaylistSyncer, "find_matching_playlist") as mock_find:
        mock_find.return_value = target_playlists[1]
        mock_apple_music_client.get_playlist_tracks.return_value = ["track1", "track2"]

        playlist_id, existing_tracks = playlist_syncer._get_target_playlist(
            "My Playlist", target_playlists
        )

        assert playlist_id == "2"
        assert existing_tracks == ["track1", "track2"]
        mock_find.assert_called_with("My Playlist", target_playlists)

    # Test creating new playlist
    with patch.object(PlaylistSyncer, "find_matching_playlist") as mock_find:
        mock_find.return_value = None
        mock_apple_music_client.create_playlist.return_value = "new_playlist_id"

        playlist_id, existing_tracks = playlist_syncer._get_target_playlist(
            "New Playlist", target_playlists
        )

        assert playlist_id == "new_playlist_id"
        assert existing_tracks == []
        mock_apple_music_client.create_playlist.assert_called_with("New Playlist")


def test_process_tracks(playlist_syncer, mock_spotify_client, mock_apple_music_client):
    """
    Test the _process_tracks method.
    """
    playlist_syncer.source = mock_spotify_client
    playlist_syncer.target = mock_apple_music_client

    source_tracks = [
        {"name": "Track 1", "artist": "Artist 1"},
        {"name": "Track 2", "artist": "Artist 2"},
        {"name": "Track 3", "artist": "Artist 3"},
    ]

    existing_tracks = [
        {"name": "Track 1", "artist": "Artist 1"}  # Track 1 already exists
    ]

    # Mock _search_track to return IDs for tracks 2 and 3, but fail for track 4
    with patch.object(playlist_syncer, "_search_track") as mock_search, patch.object(
        playlist_syncer, "_is_track_duplicate"
    ) as mock_duplicate:
        # Track 1 is a duplicate
        mock_duplicate.side_effect = (
            lambda track, existing: track[0].lower() == "track 1"
        )

        # Track 2 is found, Track 3 is not found
        mock_search.side_effect = (
            lambda track: "track_2_id" if track[0] == "track 2" else None
        )

        # Add logger mock to prevent AttributeError
        playlist_syncer.logger = MagicMock()
        playlist_syncer.logger.debug = MagicMock()

        successful, failed = playlist_syncer._process_tracks(
            source_tracks, existing_tracks
        )

        assert successful == ["track_2_id"]
        assert len(failed) == 1
        assert failed[0] == ("track 3", "artist 3")


def test_sync_playlist(playlist_syncer, mock_spotify_client, mock_apple_music_client):
    """
    Test the sync_playlist method.
    """
    playlist_syncer.source = mock_spotify_client
    playlist_syncer.target = mock_apple_music_client

    source_playlist = {"id": "source_id", "name": "Source Playlist"}
    target_playlists = [{"id": "target_id", "name": "Target Playlist"}]

    # Mock the methods called by sync_playlist
    mock_spotify_client.get_playlist_tracks.return_value = [
        "track1",
        "track2",
        "track3",
    ]

    with patch.object(
        playlist_syncer, "_get_target_playlist"
    ) as mock_get_target, patch.object(
        playlist_syncer, "_process_tracks"
    ) as mock_process:
        mock_get_target.return_value = ("target_id", ["existing_track"])
        mock_process.return_value = (
            ["new_track_id1", "new_track_id2"],
            ["failed_track"],
        )

        total, synced = playlist_syncer.sync_playlist(source_playlist, target_playlists)

        assert total == 3  # Total tracks in source playlist
        assert synced == 2  # Successfully synced tracks

        mock_spotify_client.get_playlist_tracks.assert_called_with("source_id")
        mock_get_target.assert_called_with("Source Playlist", target_playlists)
        mock_process.assert_called_with(
            ["track1", "track2", "track3"], ["existing_track"]
        )
        mock_apple_music_client.add_tracks_to_playlist.assert_called_with(
            "target_id", ["new_track_id1", "new_track_id2"]
        )


def test_get_playlists_from_services(
    playlist_syncer, mock_spotify_client, mock_apple_music_client
):
    """
    Test the _get_playlists_from_services method.
    """
    playlist_syncer.source = mock_spotify_client
    playlist_syncer.target = mock_apple_music_client

    mock_spotify_client.get_user_playlists.return_value = [
        "spotify_playlist1",
        "spotify_playlist2",
    ]
    mock_apple_music_client.get_user_playlists.return_value = [
        "apple_playlist1",
        "apple_playlist2",
    ]

    (
        source_playlists,
        target_playlists,
        source_name,
        target_name,
    ) = playlist_syncer._get_playlists_from_services()

    assert source_playlists == ["spotify_playlist1", "spotify_playlist2"]
    assert target_playlists == ["apple_playlist1", "apple_playlist2"]
    assert source_name == "Spotify"
    assert target_name == "Apple Music"

    mock_spotify_client.get_user_playlists.assert_called_once()
    mock_apple_music_client.get_user_playlists.assert_called_once()
