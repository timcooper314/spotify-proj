import requests
from pprint import pprint
from collections import defaultdict
import json
import numpy as np
import pandas as pd


class SpotifyClientAuthTokenExpiredException(Exception):
    pass


def get_auth_token():
    with open('auth_token.txt') as f:
        token = f.readlines()
        f.close()
    return token[0]


def check_api_response(response):
    if 'error' in response:
        raise SpotifyClientAuthTokenExpiredException(response['error']['message'])


def _filter_audio_features(spotify_data):
    desired_fields = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'speechiness']
    additional_fields = ['liveness', 'tempo', 'key', 'loudness', 'mode', 'time_signature', 'valence']
    return {field: spotify_data['audio_features'][0][field] for field in desired_fields}


def compute_cosine(v_1, v_2):
    """Computes the cosine of the angle between vectors v_1 and v_2"""
    return np.dot(v_1, v_2) / (np.linalg.norm(v_1)*np.linalg.norm(v_2))


def compute_similarity_matrix(audio_features_array):
    """Computes the (symmetrix, square) matrix of similarity values
     between tracks, given an array of audio features vectors."""
    num_tracks = len(audio_features_array)
    similarity_matrix = np.eye(num_tracks)
    # for i, vec in enumerate(audio_features_array):
    for i in range(num_tracks):
        v_i = audio_features_array[i]
        for j in range(i+1, num_tracks):
            v_j = audio_features_array[j]
            similarity_matrix[i][j] = compute_cosine(v_i, v_j)
    print(similarity_matrix)
    return similarity_matrix


class SpotifyClient:
    def __init__(self):
        self.AUTH_TOKEN = get_auth_token()
        self.base_url = 'https://api.spotify.com/'
        self.user = '1259570943'
        self._params = {}
        self._headers = {'Authorization': f"Bearer {self.AUTH_TOKEN}"}
        self._data = {}
        self.track_audio_features_df = pd.DataFrame(columns=['track', 'artist', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'speechiness'])

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, value):
        self._params = value

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, body):
        self._data = body

    def _get_api_data(self, endpoint):
        response = requests.get(f"https://api.spotify.com/v1/{endpoint}",
                                headers=self._headers,
                                params=self._params)
        return response.json()

    def _post_api_data(self, endpoint):
        response = requests.post(f"https://api.spotify.com/v1/{endpoint}",
                                 headers=self._headers,
                                 data=self._data)
        return response.json()

    def get_recently_played(self):
        endpoint = 'me/player/recently-played/'
        spotify_data = self._get_api_data(endpoint)
        check_api_response(spotify_data)
        recently_played = defaultdict(list)
        for item in spotify_data['items']:
            recently_played[item['track']['artists'][0]['name']].append(item['track']['name'])
        pprint(recently_played)
        return recently_played

    def get_top(self, top_type, time_range='medium_term', offset=0, limit=20):
        """Retrieves your most played.
            top_type: artists, tracks
            time_range: short_term, medium_term, long_term;
            0<=offset<50: a shift down the list;
            0<=limit<=50: number of results to retrieve"""
        # TODO: Make this method work for limit>50 (i.e. by using offset>0)
        endpoint = f"me/top/{top_type}"
        self.params['time_range'] = time_range
        self.params['limit'] = limit
        self.params['offset'] = offset
        spotify_data = self._get_api_data(endpoint)
        check_api_response(spotify_data)
        if top_type == 'artists':
            top_data = [artist_object['name'] for artist_object in spotify_data['items']]
            pprint(top_data)
        else:  # 'tracks'
            # top_tracks = defaultdict(list)
            # top_tracks[track_object['artists'][0]['name']].append(track_object['name'])
            top_data = [f"{track_object['name']} - {track_object['artists'][0]['name']}"
                        for track_object in spotify_data['items']]
        pprint(top_data)
        return spotify_data

    def get_current_playback(self):
        endpoint = "me/player/"
        spotify_data = self._get_api_data(endpoint)
        check_api_response(spotify_data)
        current_track = spotify_data['item']['name']
        current_artist = spotify_data['item']['artists'][0]['name']
        print(f"Currently playing:  {current_track} by {current_artist}")
        # pprint(spotify_data)
        return spotify_data

    def get_available_genre_seeds(self):
        endpoint = 'me/recommendations/available-genre-seeds'
        spotify_data = self._get_api_data(endpoint)
        check_api_response(spotify_data)
        pprint(spotify_data)
        return

    def get_saved_tracks(self, limit=20, offset=0):
        endpoint = 'me/tracks'
        self.params['limit'] = limit
        self.params['offset'] = offset
        spotify_data = self._get_api_data(endpoint)
        check_api_response(spotify_data)
        pprint(spotify_data)
        top_tracks = defaultdict(list)
        for track_object in spotify_data['items']:
            artist = track_object['track']['artists'][0]['name']
            track = track_object['track']['name']
            top_tracks[artist].append(track)
        print(len(top_tracks))
        pprint(top_tracks)
        return top_tracks

    def get_audio_features(self, track_ids):
        endpoint = "audio-features"
        self.params['ids'] = track_ids
        spotify_data = self._get_api_data(endpoint)
        check_api_response(spotify_data)
        features = _filter_audio_features(spotify_data)
        return features

    def get_audio_features_of_currently_playing_track(self):
        """Requires OAuth token with scope user-read-currently-playing"""
        current_playing_data = self.get_current_playback()
        # artist = current_playing_data['item']['artists'][0]['name']
        # track = current_playing_data['item']['name']
        track_id = current_playing_data['item']['id']
        features = self.get_audio_features(track_id)
        pprint(features)
        return features

    def get_audio_features_of_top_tracks(self):
        """Requires OAuth token with scope user-read-top"""
        top_track_data = self.get_top('tracks', 'medium_term', 0, 5)
        audio_features_vectors = []
        for track_object in top_track_data['items']:
            track_id = track_object['id']
            features = self.get_audio_features(track_id)
            audio_features_vectors.append(list(features.values()))
        pprint(audio_features_vectors)
        return np.array([vec for vec in audio_features_vectors])

    def create_playlist(self, name, description):
        """Creates a playlist. Requires scope playlist-modify-public."""
        endpoint = f"users/{self.user}/playlists"
        self._headers['Content-Type'] = 'application/json'
        request = {"name": name,
                   "description": description,
                   "public": True}
        self._data = json.dumps(request)
        response = self._post_api_data(endpoint)
        check_api_response(response)
        pprint(response)
        return response

    def add_tracks_to_playlist(self, playlist_id, track_ids):  # '3b6enPHFMgh3Wrlavc0kY2'
        """Adds tracks defined by track_ids (list) to playlist defined by playlist_id."""
        endpoint = f"playlists/{playlist_id}/tracks"
        self._headers['Content-Type'] = 'application/json'
        self._data = json.dumps([f'spotify:track:{track_id}' for track_id in track_ids])
        response = self._post_api_data(endpoint)
        check_api_response(response)
        pprint(response)
        return response

    def create_playlist_of_top_tracks(self, time_range='short_term', limit=20):
        response = self.create_playlist(f"{limit}_{time_range}",
                                        f"{limit} ripper tracks from the {time_range} based on number of plays.")
        playlist_id = response['id']
        top_tracks_data = self.get_top('tracks', time_range, 0, limit)
        track_ids = [track_data['id'] for track_data in top_tracks_data['items']]
        response = self.add_tracks_to_playlist(playlist_id, track_ids)
        pprint(response)
        return response


    def create_track_df(self):
        top_data = self.get_top('tracks', limit=5)
        self.track_audio_features_df['track'] = [track_object['name'] for track_object in top_data['items']]
        self.track_audio_features_df['artist'] = [track_object['artists'][0]['name'] for track_object in top_data['items']]
        print(self.track_audio_features_df.head())


if __name__ == '__main__':
    mySpotify = SpotifyClient()

    # mySpotify.get_current_playback()
    # mySpotify.get_recently_played()
    # mySpotify.get_top('artists', 'medium_term')
    # mySpotify.get_top('tracks', 'medium_term')
    # mySpotify.get_available_genre_seeds()
    # mySpotify.get_saved_tracks(limit=2)
    # mySpotify.get_audio_features_of_currently_playing_track()

    # mySpotify.create_playlist("autogen2 playlist", "a new playlist")
    # mySpotify.add_tracks_to_playlist()
    # mySpotify.create_playlist_of_top_tracks('short_term')

    # audio_array = mySpotify.get_audio_features_of_top_tracks()
    # compute_similarity_matrix(audio_array)

    mySpotify.create_track_df()
    # idea: use cosine similarity on artist genres to find similar artsists
        # Make playlist based on two or more peoples common genre interests
        # Make playlist of a genre from music in library
    # use cosine similarity on audio features of tracks
        # Create symmetric matrix of similarity values

    # analyse tracks in a playlist, or album ("vibe" of album?) eg. e-1
    # Make playlist of tracks with tempo=120
    # TODO: Start making tests
    # TODO: Make create playlist function
    # TODO: Try recommendations endpoint
    # TODO: create track subclass
    # Use liveness metrix to make playlist of live music

    # Reorder playlist e- in ascending energy order?