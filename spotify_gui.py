import sys
from pprint import pprint
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QGroupBox, \
    QPushButton, QRadioButton, QLineEdit, QDialog, QTableView  # QGridLayout, QTableWidget, QTextBrowser, QButtonGroup, QWidget
from PyQt5.QtCore import QAbstractTableModel, Qt, QSortFilterProxyModel
from spotify_api import SpotifyClient
from playlist import Playlist, create_playlist_of_top_tracks


def get_id_and_type_from_link(spotify_link_or_id):
    if spotify_link_or_id[0:4] == 'http':  # link
        spotify_id = (spotify_link_or_id.split('/'))[4].split('?')[0]
        spotify_type = (spotify_link_or_id.split('/'))[3]
    else:
        spotify_id = spotify_link_or_id
        spotify_type = ''
    return spotify_id, spotify_type


class MPlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = Figure(figsize=(2.5, 2.5), dpi=100)
        fig.set_facecolor('black')
        fig.set_alpha(1)
        self.axes = fig.add_axes([0.2, 0.2, 0.75, 0.75])
        self.axes.patch.set_facecolor('black')
        super(MPlotCanvas, self).__init__(fig)

    def update_af_bar_plot(self, af):
        self.axes.cla()
        self.axes.bar(af.keys(), af.values(), color='g')
        self.axes.tick_params(axis='both', which='major', labelsize=8, labelrotation=10, labelcolor='white')
        self.axes.patch.set_facecolor('black')
        self.draw()


class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class SpotifyGUI(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Data...")
        self.setGeometry(100, 100, 1000, 800)  # x,y pos, width,height
        self.window_layout = QVBoxLayout()
        self.create_horizontal_get_top_layout()
        self.create_horizontal_get_af_layout()
        self.create_df_layout()

        self.window_layout.addWidget(self.horizontal_group_box)
        self.window_layout.addWidget(self.horizontal_group_box_2)
        self.window_layout.addWidget(self.df_group_box)

        self.setLayout(self.window_layout)
        self.show()

    def create_horizontal_get_top_layout(self):
        self.horizontal_group_box = QGroupBox("Top tracks/artists")
        h_layout = QHBoxLayout()

        self.number_tracks_text = QLineEdit("Number of tracks/artists", self)
        h_layout.addWidget(self.number_tracks_text)

        time_period_buttons_layout = QVBoxLayout()
        # TODO: Use button groups
        self.short_term_button = QRadioButton("Short term", self)
        self.medium_term_button = QRadioButton("Medium term", self)
        self.long_term_button = QRadioButton("Long term", self)
        time_period_buttons_layout.addWidget(self.short_term_button)
        time_period_buttons_layout.addWidget(self.medium_term_button)
        time_period_buttons_layout.addWidget(self.long_term_button)
        self.short_term_button.setChecked(True)
        self.short_term_button.setAutoExclusive(False)
        self.medium_term_button.setAutoExclusive(False)
        self.long_term_button.setAutoExclusive(False)

        h_layout.addLayout(time_period_buttons_layout)

        top_type_buttons_layout = QVBoxLayout()
        self.tracks_button = QRadioButton("Tracks", self)
        self.tracks_button.setChecked(True)
        top_type_buttons_layout.addWidget(self.tracks_button)
        self.artists_button = QRadioButton("Artists", self)
        top_type_buttons_layout.addWidget(self.artists_button)
        h_layout.addLayout(top_type_buttons_layout)

        push_buttons_layout = QVBoxLayout()
        get_top_data_button = QPushButton("Get data", self)
        get_top_data_button.clicked.connect(self.get_top_click)
        push_buttons_layout.addWidget(get_top_data_button)

        create_playlist_button = QPushButton("Create playlist", self)
        create_playlist_button.clicked.connect(self.create_playlist_click)
        push_buttons_layout.addWidget(create_playlist_button)
        h_layout.addLayout(push_buttons_layout)

        self.horizontal_group_box.setLayout(h_layout)

    def create_horizontal_get_af_layout(self):
        self.horizontal_group_box_2 = QGroupBox("Audio features")
        layout = QHBoxLayout()
        v_layout = QVBoxLayout()
        h_layout_1 = QHBoxLayout()
        self.link_or_id_text = QLineEdit("Track/Album/Playlist link/ID", self)
        h_layout_1.addWidget(self.link_or_id_text)

        get_current_track_button = QPushButton("Get current playing track", self)
        get_current_track_button.clicked.connect(self.get_current_click)
        h_layout_1.addWidget(get_current_track_button)

        v_layout.addLayout(h_layout_1)

        h_buttons_layout = QHBoxLayout()

        get_current_af_button = QPushButton("Get track", self)
        get_current_af_button.clicked.connect(self.get_track_click)
        h_buttons_layout.addWidget(get_current_af_button)

        get_playlist_af_button = QPushButton("Get playlist", self)
        get_playlist_af_button.clicked.connect(self.get_playlist_click)
        h_buttons_layout.addWidget(get_playlist_af_button)

        get_album_af_button = QPushButton("Get album", self)
        get_album_af_button.clicked.connect(self.get_album_click)
        h_buttons_layout.addWidget(get_album_af_button)

        v_layout.addLayout(h_buttons_layout)
        layout.addLayout(v_layout)
        self.af_plot = MPlotCanvas(self)
        # self.af_plot.axes.bar(['a','b','c','d','e'], [0, 0, 0, 0, 0])
        # self.af_plot.axes.tick_params(axis='both', which='major', labelsize=8)
        layout.addWidget(self.af_plot)
        layout.deleteLater()
        self.horizontal_group_box_2.setLayout(layout)

    def create_df_layout(self):
        self.df_group_box = QGroupBox("df grid")
        self.df = pd.DataFrame(columns=['track', 'artist', 'acousticness', 'danceability',
                                        'energy', 'instrumentalness', 'speechiness'])
        self.df_model = PandasModel(self.df)
        self.update_df_widget()

    def update_df_widget(self):
        self.df_model._data = self.df

        view = QTableView()
        view.setModel(self.df_model)
        view.setSortingEnabled(True)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(self.df_model)
        view.setModel(proxy_model)
        layout = QHBoxLayout()
        layout.addWidget(view)
        self.df_group_box.setLayout(layout)
        layout.deleteLater()

    def get_time_period(self):
        if self.short_term_button.isChecked():
            time_period = 'short_term'
        elif self.medium_term_button.isChecked():
            time_period = 'medium_term'
        else:
            time_period = 'long_term'
        return time_period

    def get_top_click(self):
        number_tracks = int(self.number_tracks_text.text())
        time_period = self.get_time_period()
        if self.artists_button.isChecked():
            top_type = 'artists'
            print(f"{number_tracks} {time_period.replace('_', ' ')} top {top_type}:")
            top_data = SpotifyClient().get_top(top_type=top_type, limit=number_tracks, time_range=time_period)
        else:
            top_type = 'tracks'
            top_playlist = Playlist('')
            top_data = top_playlist.spotify_client.get_top(top_type=top_type, limit=number_tracks,
                                                           time_range=time_period)
            print(f"{number_tracks} {time_period.replace('_', ' ')} top {top_type}:")
            top_df = top_playlist.create_playlist_df(top_data)
            af = top_playlist.get_mean_audio_features()
            self.df = top_df
            self.update_gui_data(af)

    def create_playlist_click(self):
        if self.artists_button.isChecked():
            print("Must select tracks button to create playlist!")
            return
        number_tracks = int(self.number_tracks_text.text())
        time_period = self.get_time_period()
        create_playlist_of_top_tracks(time_range=time_period, limit=number_tracks)

    def get_current_click(self):
        current_data = SpotifyClient().get_current_playback()
        current_id = current_data['item']['id']
        self.link_or_id_text.setText(current_id)

    def get_track_click(self):
        track_link_or_id = self.link_or_id_text.text()
        track_id, _ = get_id_and_type_from_link(track_link_or_id)
        track_playlist = Playlist('')
        track_data = SpotifyClient().get_track_from_id(track_id)
        track_playlist.create_playlist_df({'items': track_data})
        af = track_playlist.get_mean_audio_features()
        self.df = track_playlist.playlist_df
        self.update_gui_data(af)

    def get_playlist_click(self):
        playlist_link_or_id = self.link_or_id_text.text()
        playlist_id, _ = get_id_and_type_from_link(playlist_link_or_id)
        pl = Playlist(playlist_id)
        pl_data = pl.get_playlists_items()
        pl.create_playlist_df(pl_data)
        af = pl.get_mean_audio_features()
        self.df = pl.playlist_df
        self.update_gui_data(af)

    def get_album_click(self):
        album_link_or_id = self.link_or_id_text.text()
        album_id, _ = get_id_and_type_from_link(album_link_or_id)
        album_playlist = Playlist('')
        album_data = SpotifyClient().get_album_from_id(album_id)
        album_playlist.create_playlist_df(album_data)
        af = album_playlist.get_mean_audio_features()
        self.df = album_playlist.playlist_df
        self.update_gui_data(af)

    def update_gui_data(self, audio_features):
        self.af_plot.update_af_bar_plot(audio_features)
        self.update_df_widget()

# TODO: Handle errors nicely


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SpotifyGUI()
    sys.exit(app.exec_())
