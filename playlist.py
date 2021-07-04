import json
import numpy as np
import pandas as pd
from pprint import pprint
# from track import Track
from spotify_api import SpotifyClient


def get_track(playlist_item):
    if 'track' in playlist_item:
        return playlist_item['track']['name']
    else:
        return playlist_item['name']


def get_artist(playlist_item):
    if 'track' in playlist_item:
        return playlist_item['track']['artists'][0]['name']
    else:
        return playlist_item['artists'][0]['name']


def get_id(playlist_item):
    if 'track' in playlist_item:
        return playlist_item['track']['id']
    else:
        return playlist_item['id']


class Playlist:  # (SpotifyClient):
    def __init__(self, playlist_id):
        self.spotify_client = SpotifyClient()
        self.playlist_id = playlist_id
        self.playlist_df = pd.DataFrame(columns=['track', 'artist'])

    def create_playlist_df(self, spotify_data):
        self.playlist_df = pd.DataFrame(columns=['track', 'artist'])
        af = self.get_audio_features_of_tracks(spotify_data)
        self.playlist_df['track'] = [get_track(item) for item in spotify_data['items']]
        self.playlist_df['artist'] = [get_artist(item) for item in spotify_data['items']]
        self.playlist_df['acousticness'] = af[:, 0]  # Get these fields from desired_fields...?
        self.playlist_df['danceability'] = af[:, 1]
        self.playlist_df['energy'] = af[:, 2]
        self.playlist_df['instrumentalness'] = af[:, 3]
        self.playlist_df['speechiness'] = af[:, 4]
        return self.playlist_df

    def get_playlists_items(self):
        endpoint = f"playlists/{self.playlist_id}/tracks"
        spotify_data = self.spotify_client.get_api_data(endpoint)
        return spotify_data

    def add_tracks_to_playlist(self, track_ids):
        """Adds tracks defined by track_ids (list) to playlist defined by playlist_id."""
        endpoint = f"playlists/{self.playlist_id}/tracks"
        self.spotify_client._headers['Content-Type'] = 'application/json'
        self.spotify_client._data = json.dumps([f'spotify:track:{track_id}' for track_id in track_ids])
        response = self.spotify_client.post_api_data(endpoint)
        return response

    def get_audio_features_of_tracks(self, playlist_data):
        """Requires OAuth token with scope user-read-top"""
        audio_features_vectors = []
        for track_object in playlist_data['items']:
            track_id = get_id(track_object)
            track_features = self.spotify_client.get_audio_features(track_id)
            audio_features_vectors.append(list(track_features.values()))
        return np.array([vec for vec in audio_features_vectors])

# TODO: Make a gui - tkinter?, pyqt5?


if __name__ == '__main__':
    # my_pid = '1uPPJSAPbKGxszadexGQJL'
    # simply = Playlist(my_pid)
    # simply_data = simply.get_playlists_items()
    # simply.create_playlist_df(simply_data)
    # # simply.add_tracks_to_playlist(['1c6usMjMA3cMG1tNM67g2C'])
    # pprint(simply.playlist_df.head())

    # mySpotify.get_current_playback()
    # mySpotify.get_recently_played()

    # top_playlist = Playlist('')
    # top_data = top_playlist.spotify_client.get_top('tracks', 'short_term', limit=10)
    # top_df = top_playlist.create_playlist_df(top_data)
    # print(top_df.head())


    # mySpotify.get_audio_features_of_currently_playing_track()

    # mySpotify.create_playlist("autogen2 playlist", "a new playlist")
    # mySpotify.create_playlist_of_top_tracks('short_term')

    # audio_array = mySpotify.get_audio_features_of_top_tracks()
    # compute_similarity_matrix(audio_array)
    # mySpotify.create_top_tracks_df()

    # idea: use cosine similarity on artist genres to find similar artists
        # Make playlist based on two or more peoples common genre interests
        # Make playlist of a genre from music in library
    # use cosine similarity on audio features of tracks
        # Create symmetric matrix of similarity values

    # analyse tracks in a playlist, or album ("vibe" of album?) eg. e-1
    # Make playlist of tracks with tempo=120
    # TODO: Start making tests
    # TODO: Try recommendations endpoint
    # TODO: create track subclass
    # Use liveness metrix to make playlist of live music

    # Reorder playlist e- in ascending energy order?

    # For n tracks, the number of similarity computations will be
    # 1+2+...+(n-1)  = n*(n-1)/2  = O(n^2)...
