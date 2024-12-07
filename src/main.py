from spotify.spotify_client import SpotifyClient


def print_artist(access_token, artist_name):
    # Initialize the Spotify client with the provided access token
    spotify_client = SpotifyClient(access_token=access_token)

    # Search for the artist by name
    search_results = spotify_client.search(query=artist_name, type='artist')

    # Retrieve the first artist from the search results
    if search_results['artists']['items']:
        artist_details = search_results['artists']['items'][0]

        # Print the artist's details
        print(f"Artist Name: {artist_details['name']}")
        print(f"Genres: {', '.join(artist_details['genres'])}")
        print(f"Popularity: {artist_details['popularity']}")
        print(f"Followers: {artist_details['followers']['total']}")
    else:
        print(f"No artists found with the name: {artist_name}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Replace 'your_access_token' and 'artist_name_here' with actual values
    print_artist(access_token='your_access_token_here', artist_name='Drake')

