import requests
from pprint import pprint
from collections import defaultdict

class SpotifyClient:
    def __init__(self):
        self.AUTH_TOKEN = 'BQCYS9ZZlHYVpsSwy4gpQHudiMV6xfyFE_e9drIOLYMfudTjt7Zx8SSGiVZvHhAntuL5GKxoHUqKDeurjmNSiYBm15EqAISuM1Vz_-Aq5nGaO-57VstY9nwtn2F4Ge4v6c9m2SDgcIU0KDL695ndlWNHZfgi8YG-z7VzQ5wwB6P3N2OdIn29'
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
        recently_played = defaultdict(list)
        for item in spotify_data['items']:
            recently_played[item['track']['album']['artists'][0]['name']].append(item['track']['name'])
        pprint(recently_played)
        return recently_played

    def get_top_artists(self, time_range='medium_term', offset=0, limit=20):
        """Retrieves your most played artists.
            time_range: short_term, medium_term, long_term;
            0<=offset<50: a shift down the list;
            0<=limit<=50: number of results to retrieve"""
        endpoint = f"me/top/artists"
        self.params['time_range'] = time_range
        self.params['limit'] = limit
        self.params['offset'] = offset
        spotify_data = self._get_api_data(endpoint)
        fave_artists = [artist_object['name'] for artist_object in spotify_data['items']]
        pprint(fave_artists)
        return fave_artists

    def get_top_tracks(self, time_range='medium_term', offset=0, limit=20):
        """Retrieves your most played tracks.
                time_range: short_term, medium_term, long_term;
                0<=offset<50: a shift down the list;
                0<=limit<=50: number of results to retrieve"""
        endpoint = f"me/top/tracks"
        self.params['time_range'] = time_range
        self.params['limit'] = limit
        self.params['offset'] = offset
        spotify_data = self._get_api_data(endpoint)
        # top_tracks = defaultdict(list)
        # top_tracks[track_object['artists'][0]['name']].append(track_object['name'])
        top_track_list = [f"{track_object['name']} - {track_object['artists'][0]['name']}"
                          for track_object in spotify_data['items']]
        pprint(top_track_list)
        return top_track_list

    def get_current_playback(self):
        endpoint ="me/player/"
        spotify_data = self._get_api_data(endpoint)
        current_track = spotify_data['item']['name']
        current_artist = spotify_data['item']['artists'][0]['name']
        print(f"Currently playing:  {current_track} by {current_artist}")
        pprint(spotify_data)
        return spotify_data

    def get_available_genre_seeds(self):
        endpoint = 'me/recommendations/available-genre-seeds'
        spotify_data = self._get_api_data(endpoint)
        pprint(spotify_data)
        return

    def get_saved_tracks(self):
        endpoint = 'me/tracks'
        spotify_data = self._get_api_data(endpoint)
        top_tracks = defaultdict(list)
        for track_object in spotify_data['items']:
            artist = track_object['track']['album']['artists'][0]['name']
            track = track_object['track']['name']
            top_tracks[artist].append(track)
        print(len(top_tracks))
        pprint(top_tracks)
        return top_tracks

    def get_audio_features_of_currently_playing_track(self):
        """Requires OAuth token with scope user-read-currently-playing"""
        current_data = self.get_current_playback()
        self.params['ids'] = current_data['item']['id']  # '54TbgZjTIl5ACMgBblalDk', '7EPTw7FcIoe6r6TI5VGoVx'
        endpoint = "audio-features"
        spotify_data = self._get_api_data(endpoint)
        pprint(spotify_data)
        return spotify_data


if __name__ == '__main__':
    mySpotify = SpotifyClient()

    # mySpotify.get_current_playback()
    # mySpotify.get_recently_played()
    # mySpotify.get_top_artists('medium_term')
    #mySpotify.get_top_tracks('short_term')
    # mySpotify.get_available_genre_seeds()
    # mySpotify.get_saved_tracks()
    mySpotify.get_audio_features_of_currently_playing_track()

    # idea: use cosine similarity on artist genres to find similar artsists
        # Make playlist based on two or more peoples common genre interests
        # Make playlist of a genre from music in library
