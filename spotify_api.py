import urllib3
import json
import requests
from pprint import pprint
from collections import defaultdict

class SpotifyClient:
    def __init__(self):
        self.AUTH_TOKEN = 'BQCaA-I3qKSrX8S2sB19YbWZymVwMWkKwaDRjWvy0Fnn_aXW1LayG2zGlzGah0wxw1dATZMqU7S-xu2jnyux6fVoQY9mHhbg-Ie9u0A3GuABj1nLXcjJt9-wamc9Jg_Z9EuKQ3coXTczMmseQgX84iuYW3Ie'
        self.base_url = 'https://api.spotify.com/'
        self.user = '1259570943'
        self._params = {}
        self.headers = {'Authorization': f"Bearer {self.AUTH_TOKEN}"}

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, value):
        self._params = value

    def _get_api_data(self, endpoint):
        response = requests.get(f"https://api.spotify.com/v1/me/{endpoint}",
                                headers=self.headers,
                                params=self._params)
        return response.json()

    def get_recently_played(self):
        endpoint = 'player/recently-played/'
        spotify_data = self._get_api_data(endpoint)
        recently_played = defaultdict(list)
        for item in spotify_data['items']:
            recently_played[item['track']['album']['artists'][0]['name']].append(item['track']['name'])
        pprint(recently_played)
        return recently_played

    def get_top_artists(self, time_range='medium_term'):
        endpoint = f"top/artists"
        self.params['time_range'] = time_range
        spotify_data = self._get_api_data(endpoint)
        fave_artists = [artist_object['name'] for artist_object in spotify_data['items']]
        pprint(fave_artists)
        return fave_artists

    def get_top_tracks(self, time_range='medium_term'):
        endpoint = f"top/tracks"
        self.params['time_range'] = time_range
        spotify_data = self._get_api_data(endpoint)
        top_tracks = defaultdict(list)
        for track_object in spotify_data['items']:
            top_tracks[track_object['artists'][0]['name']].append(track_object['name'])
        pprint(top_tracks)
        return top_tracks

    def get_current_playback(self):
        endpoint ="player/"
        spotify_data = self._get_api_data(endpoint)
        current_track = spotify_data['item']['name']
        current_artist = spotify_data['item']['artists'][0]['name']
        print(f"Currently playing:  {current_track} by {current_artist}")
        return spotify_data

    def get_available_genre_seeds(self):
        endpoint = 'recommendations/available-genre-seeds'
        spotify_data = self._get_api_data(endpoint)
        pprint(spotify_data)
        return

    def get_saved_tracks(self):
        endpoint = 'tracks'
        spotify_data = self._get_api_data(endpoint)
        # pprint(spotify_data)
        top_tracks = defaultdict(list)
        for track_object in spotify_data['items']:
            #pprint(track_object)
            artist = track_object['track']['album']['artists'][0]['name']
            track = track_object['track']['name']
            #top_tracks[track_object['artists'][0]['name']].append(track_object['track']['name'])
            top_tracks[artist].append(track)
        print(len(top_tracks))
        pprint(top_tracks)
        return top_tracks

    def get_audio_features(self):
        pass

if __name__ == '__main__':
    # idea: use cosine similarity on artist genres to find similar artsists
        # Make playlist based on two or more peoples common genre interests
        # Make playlist of a genre from music in library

    mySpotify = SpotifyClient()

    # mySpotify.get_current_playback()
    # mySpotify.get_recently_played()
    # mySpotify.get_top_artists('short_term')
    # mySpotify.get_top_tracks('short_term')
    #mySpotify.get_available_genre_seeds()
    mySpotify.get_saved_tracks()
