# This is a sample Python script.

from spotify.spotify_client import SpotifyClient


def print_artist(access_token, artist_id):
    # Initialize the Spotify client with the provided access token
    spotify_client = SpotifyClient(access_token=access_token)

    # Fetch artist details using the client
    artist_details = spotify_client.fetch_artist(artist_id=artist_id)

    # Print the artist's details
    print(f"Artist Name: {artist_details['name']}")
    print(f"Genres: {', '.join(artist_details['genres'])}")
    print(f"Popularity: {artist_details['popularity']}")
    print(f"Followers: {artist_details['followers']['total']}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Replace 'your_access_token' and 'artist_id' with actual values
    print_artist(access_token='', artist_id='4Z8W4fKeB5YxbusRsdQVPb')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
