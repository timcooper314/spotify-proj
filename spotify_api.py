import requests
from pprint import pprint
from collections import defaultdict


class SpotifyClientAuthTokenExpiredException(Exception):
    pass


def _filter_audio_features(spotify_data):
    desired_fields = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'tempo']
    additional_fields = ['key', 'loudness', 'mode', 'time_signature', 'valence']
    return {field: spotify_data['audio_features'][0][field] for field in desired_fields}


def check_api_response(response):
    if 'error' in response:
        raise SpotifyClientAuthTokenExpiredException(response['error']['message'])


def get_auth_token():
    with open('auth_token.txt') as f:
        token = f.readlines()
        f.close()
    return token[0]


class SpotifyClient:
    def __init__(self):
        self.AUTH_TOKEN = get_auth_token()
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
        response = requests.get(f"https://api.spotify.com/v1/{endpoint}",
                                headers=self.headers,
                                params=self._params)
        return response.json()

    def get_recently_played(self):
        endpoint = 'player/recently-played/'
        spotify_data = self._get_api_data(endpoint)
        check_api_response(spotify_data)
        recently_played = defaultdict(list)
        for item in spotify_data['items']:
            recently_played[item['track']['album']['artists'][0]['name']].append(item['track']['name'])
        pprint(recently_played)
        return recently_played


    def get_top(self, type, time_range='medium_term', offset=0, limit=20):
        """Retrieves your most played.
            type: artists, tracks
            time_range: short_term, medium_term, long_term;
            0<=offset<50: a shift down the list;
            0<=limit<=50: number of results to retrieve"""
        endpoint = f"me/top/{type}"
        self.params['time_range'] = time_range
        self.params['limit'] = limit
        self.params['offset'] = offset
        spotify_data = self._get_api_data(endpoint)
        check_api_response(spotify_data)
        if type == 'artists':
            top_data = [artist_object['name'] for artist_object in spotify_data['items']]
            pprint(top_data)
        else: # 'tracks'
            # top_tracks = defaultdict(list)
            # top_tracks[track_object['artists'][0]['name']].append(track_object['name'])
            top_data = [f"{track_object['name']} - {track_object['artists'][0]['name']}"
                              for track_object in spotify_data['items']]
            # pprint(top_data)
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

    def get_saved_tracks(self):
        endpoint = 'me/tracks'
        spotify_data = self._get_api_data(endpoint)
        check_api_response(spotify_data)
        top_tracks = defaultdict(list)
        for track_object in spotify_data['items']:
            artist = track_object['track']['album']['artists'][0]['name']
            track = track_object['track']['name']
            top_tracks[artist].append(track)
        print(len(top_tracks))
        pprint(top_tracks)
        return top_tracks

    def get_audio_features(self, id):
        endpoint = "audio-features"
        self.params['ids'] = id
        spotify_data = self._get_api_data(endpoint)
        features = _filter_audio_features(spotify_data)
        return features

    def get_audio_features_of_currently_playing_track(self):
        """Requires OAuth token with scope user-read-currently-playing"""
        current_playing_data = self.get_current_playback()
        artist = current_playing_data['item']['artists'][0]['name']
        track = current_playing_data['item']['name']
        id = current_playing_data['item']['id']
        features = self.get_audio_features(id)
        pprint(features)
        return features

    def get_audio_features_of_top_tracks(self):
        """Requires OAuth token with scope user-read-top"""
        top_track_data = self.get_top('tracks', 'short_term', 0, 5)
        audio_features_vectors = []
        for track_object in top_track_data['items']:
            id = track_object['id']
            features = self.get_audio_features(id)
            audio_features_vectors.append(list(features.values()))
        pprint(audio_features_vectors)
        return audio_features_vectors


if __name__ == '__main__':
    mySpotify = SpotifyClient()

    # mySpotify.get_current_playback()
    # mySpotify.get_recently_played()
    # mySpotify.get_top('artists', 'medium_term')
    # mySpotify.get_top('tracks', 'short_term')
    # mySpotify.get_available_genre_seeds()
    # mySpotify.get_saved_tracks()
    # mySpotify.get_audio_features_of_currently_playing_track()
    mySpotify.get_audio_features_of_top_tracks()

    # idea: use cosine similarity on artist genres to find similar artsists
        # Make playlist based on two or more peoples common genre interests
        # Make playlist of a genre from music in library
    # use cosine similarity on audio features of tracks
        # Create symmetric matrix of similarity values
