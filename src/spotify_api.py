import requests
import json
from typing import List, Dict
import numpy as np
from pprint import pprint
from collections import defaultdict


class SpotifyClientAuthTokenExpiredException(Exception):
    pass


def _get_auth_token():
    with open("auth_token.txt") as f:
        token = f.readlines()
        f.close()
    return token[0]


def _check_api_response(response):
    if "error" in response:
        raise SpotifyClientAuthTokenExpiredException(response["error"]["message"])


def _filter_audio_features(spotify_data):
    desired_fields = [
        "acousticness",
        "danceability",
        "energy",
        "instrumentalness",
    ]  # , 'speechiness']
    # additional_fields = ['liveness', 'tempo', 'key', 'loudness', 'mode', 'time_signature', 'valence']
    return {field: spotify_data["audio_features"][0][field] for field in desired_fields}


def compute_cosine(v_1, v_2):
    """Computes the cosine of the angle between vectors v_1 and v_2"""
    return np.dot(v_1, v_2) / (np.linalg.norm(v_1) * np.linalg.norm(v_2))


def compute_similarity_matrix(audio_features_array):
    """Computes the (symmetric, square) matrix of similarity values
    between tracks, given an array of audio features vectors."""
    num_tracks = len(audio_features_array)
    similarity_matrix = np.eye(num_tracks)
    for i in range(num_tracks):
        v_i = audio_features_array[i]
        for j in range(i + 1, num_tracks):
            v_j = audio_features_array[j]
            similarity_matrix[i][j] = compute_cosine(v_i, v_j)
    print(similarity_matrix)
    return similarity_matrix


def _get_artists(track_obj):
    return ", ".join([artist["name"] for artist in track_obj["artists"]])


class SpotifyClient:
    def __init__(self):
        self.AUTH_TOKEN = _get_auth_token()
        self.base_url = "https://api.spotify.com/"
        self.user = "1259570943"
        self._params = {}
        self._headers = {"Authorization": f"Bearer {self.AUTH_TOKEN}"}
        self._data = {}

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
        response = requests.get(
            f"https://api.spotify.com/v1/{endpoint}",
            headers=self._headers,
            params=self._params,
        )
        _check_api_response(response.json())
        return response.json()

    def _post_api_data(self, endpoint):
        response = requests.post(
            f"https://api.spotify.com/v1/{endpoint}",
            headers=self._headers,
            data=self._data,
        )
        _check_api_response(response.json())
        return response.json()

    def get_recently_played(self):
        endpoint = "me/player/recently-played/"
        spotify_data = self._get_api_data(endpoint)
        recently_played = defaultdict(list)
        for item in spotify_data["items"]:
            recently_played[item["track"]["artists"][0]["name"]].append(
                item["track"]["name"]
            )
        pprint(recently_played)
        return recently_played

    def get_top(
        self, top_type="tracks", time_range="medium_term", limit=10
    ) -> List[str]:
        """Retrieves your most played
        top_type: artists, tracks
        time_range: short_term, medium_term, long_term;
        0<=limit<100: number of results to retrieve"""
        if limit <= 50:
            top_list = self._get_top_limited_list(top_type, time_range, 0, limit)
        else:
            top_list = self._get_top_limited_list(top_type, time_range, 0, 50)
            more_list = self._get_top_limited_list(
                top_type, time_range, 49, limit - 49
            )[1:]
            top_list.extend(more_list)
        return top_list

    def _get_top_limited_list(self, top_type, time_range, offset, limit):
        """Retrieves your most played.
        top_type: artists, tracks
        time_range: short_term, medium_term, long_term;
        0<=offset<50: a shift down the list;
        0<=limit<=50: number of results to retrieve"""
        endpoint = f"me/top/{top_type}"
        self.params["time_range"] = time_range
        self.params["limit"] = limit
        self.params["offset"] = offset
        spotify_data = self._get_api_data(endpoint)
        if top_type == "artists":
            top_data = [
                artist_object["name"] for artist_object in spotify_data["items"]
            ]
        else:  # 'tracks'
            top_data = [
                f"{track_object['name']} - {_get_artists(track_object)}"
                for track_object in spotify_data["items"]
            ]
        pprint(top_data)
        return spotify_data["items"]

    def get_current_playback(self):
        """This only works when a song is playing..."""
        endpoint = "me/player/currently-playing"
        spotify_data = self._get_api_data(endpoint)
        current_track = spotify_data["item"]["name"]
        current_artist = _get_artists(
            spotify_data["item"]
        )  # spotify_data['item']['artists'][0]['name']
        print(f"Currently playing:  {current_track} by {current_artist}")
        return spotify_data

    def get_available_genre_seeds(self):
        endpoint = "me/recommendations/available-genre-seeds"
        spotify_data = self._get_api_data(endpoint)
        return spotify_data

    def get_saved_tracks(self, limit=20, offset=0):
        endpoint = "me/tracks"
        self.params["limit"] = limit
        self.params["offset"] = offset
        spotify_data = self._get_api_data(endpoint)
        pprint(spotify_data)
        top_tracks = defaultdict(list)
        for track_object in spotify_data["items"]:
            artist = track_object["track"]["artists"][0]["name"]
            track = track_object["track"]["name"]
            top_tracks[artist].append(track)
        print(len(top_tracks))
        pprint(top_tracks)
        return top_tracks

    def get_audio_features(self, track_ids):
        # TODO: Get this to work for a list of ids
        endpoint = "audio-features"
        self.params["ids"] = track_ids
        spotify_data = self._get_api_data(endpoint)
        return _filter_audio_features(spotify_data)

    def get_audio_features_of_currently_playing_track(self):
        """Requires OAuth token with scope user-read-currently-playing"""
        current_playing_data = self.get_current_playback()
        track_id = current_playing_data["item"]["id"]
        features = self.get_audio_features(track_id)
        pprint(features)
        return features

    def create_playlist(self, name, description):
        """Creates a playlist. Requires scope playlist-modify-public."""
        endpoint = f"users/{self.user}/playlists"
        self._headers["Content-Type"] = "application/json"
        request = {"name": name, "description": description, "public": True}
        self._data = json.dumps(request)
        response = self._post_api_data(endpoint)
        print(f"Created playlist {response['name']}")
        return response

    def get_track_from_id(self, id_):
        endpoint = "tracks"
        self.params["ids"] = id_
        spotify_data = self._get_api_data(endpoint)
        print(
            f"{_get_artists(spotify_data['tracks'][0]['album'])} - {spotify_data['tracks'][0]['name']}"
        )
        return spotify_data["tracks"]

    def get_album_from_id(self, id_):
        endpoint = "albums"
        self.params["ids"] = id_
        spotify_data = self._get_api_data(endpoint)
        album_tracks = [
            track_obj["name"]
            for track_obj in spotify_data["albums"][0]["tracks"]["items"]
        ]
        pprint(album_tracks)
        # print(f"{_get_artists(spotify_data['tracks'][0]['album'])} - {spotify_data['tracks'][0]['name']}")
        return spotify_data["albums"][0]["tracks"]
