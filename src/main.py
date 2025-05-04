from spotify.spotify_client import SpotifyClient


def print_artist(spotify_client, artist_name):
    """
    Searches for and prints details of an artist by name using the given Spotify client.

    Args:
        spotify_client (SpotifyClient): An instance of the Spotify client.
        artist_name (str): Name of the artist to search for.
    """
    search_results = spotify_client.search(query=artist_name, type="artist")

    if search_results["artists"]["items"]:
        artist_details = search_results["artists"]["items"][0]

        print(f"\nArtist Name: {artist_details['name']}")
        print(f"Genres: {', '.join(artist_details['genres'])}")
        print(f"Popularity: {artist_details['popularity']}")
        print(f"Followers: {artist_details['followers']['total']}")
    else:
        print(f"No artists found with the name: {artist_name}")


if __name__ == "__main__":
    print("\nWelcome to Harmony.")
    print("Search for an artist by entering their name or type exit to quit.\n")

    # Initialize the Spotify client
    spotify_client = SpotifyClient()

    # Run CLI
    while True:
        user_input = input("Enter artist name: ").strip()

        if user_input.lower() == "exit":
            break

        if not user_input:
            print("Artist name cannot be empty. Please try again.")
            continue

        print(f"\nSearching for artist: {user_input}...")
        try:
            print_artist(spotify_client=spotify_client, artist_name=user_input)
        except Exception as e:
            print(f"An error occurred while searching for the artist: {e}")
