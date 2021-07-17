import sys
from pprint import pprint
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout,\
    QPushButton, QRadioButton, QLineEdit, QDialog, QTableView  # , QTableWidget, QTextBrowser, QButtonGroup, QWidget
from PyQt5.QtCore import QAbstractTableModel, Qt, QSortFilterProxyModel
from spotify_api import SpotifyClient
from playlist import Playlist, create_playlist_of_top_tracks


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
        self.track_link_text = QLineEdit("Track link/ID", self)
        v_layout.addWidget(self.track_link_text)

        self.playlist_link_text = QLineEdit("Playlist link/ID", self)
        v_layout.addWidget(self.playlist_link_text)

        self.album_link_text = QLineEdit("Album link/ID", self)
        v_layout.addWidget(self.album_link_text)
        layout.addLayout(v_layout)

        v_layout2 = QVBoxLayout()

        get_current_track_button = QPushButton("Get current playing track", self)
        get_current_track_button.clicked.connect(self.get_current_click)
        v_layout2.addWidget(get_current_track_button)

        get_current_af_button = QPushButton("Get track", self)
        get_current_af_button.clicked.connect(self.get_af_click)
        v_layout2.addWidget(get_current_af_button)

        get_playlist_af_button = QPushButton("Get playlist", self)
        get_playlist_af_button.clicked.connect(self.get_playlist_click)
        v_layout2.addWidget(get_playlist_af_button)

        get_album_af_button = QPushButton("Get album", self)
        get_album_af_button.clicked.connect(self.get_album_click)
        v_layout2.addWidget(get_album_af_button)

        layout.addLayout(v_layout2)

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

        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(self.df_model)
        view.setModel(proxyModel)
        # view.show()
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
        print(f"{number_tracks} {time_period.replace('_', ' ')} top {top_type}:")
        if self.artists_button.isChecked():
            top_type = 'artists'
            top_data = SpotifyClient().get_top(top_type=top_type, limit=number_tracks,
                                                           time_range=time_period)
        else:
            top_type = 'tracks'
            top_playlist = Playlist('')
            top_data = top_playlist.spotify_client.get_top(top_type=top_type, limit=number_tracks,
                                                           time_range=time_period)
            top_df = top_playlist.create_playlist_df(top_data)
            af = top_playlist.get_mean_audio_features()
            self.af_plot.update_af_bar_plot(af)
            self.df = top_df
            self.update_df_widget()

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
        self.track_link_text.setText(current_id)

    def get_af_click(self):
        track_link_or_id = self.track_link_text.text()
        if track_link_or_id[0:4] == 'http':  # link
            track_id = (track_link_or_id.split('/'))[4].split('?')[0]
            SpotifyClient().get_track_from_id(track_id)
        else:
            track_id = track_link_or_id
        af = SpotifyClient().get_audio_features(track_id)
        self.af_plot.update_af_bar_plot(af)
        pprint(af)

    def get_playlist_click(self):
        playlist_link_or_id = self.playlist_link_text.text()
        if playlist_link_or_id[0:4] == 'http':  # link
            playlist_id = (playlist_link_or_id.split('/'))[4].split('?')[0]
        else:
            playlist_id = playlist_link_or_id
        pl = Playlist(playlist_id)
        pl_data = pl.get_playlists_items()
        pl.create_playlist_df(pl_data)
        print(pl.playlist_df)
        af = pl.get_mean_audio_features()
        self.af_plot.update_af_bar_plot(af)

        self.df = pl.playlist_df
        self.update_df_widget()

    def get_album_click(self):
        album_link_or_id = self.album_link_text.text()
        if album_link_or_id[0:4] == 'http':  # link
            album_id = (album_link_or_id.split('/'))[4].split('?')[0]
        else:
            album_id = album_link_or_id

        album_playlist = Playlist('')
        album_data = SpotifyClient().get_album_from_id(album_id)
        #top_data = album_playlist.spotify_client.get_top(top_type=top_type, limit=number_tracks, time_range=time_period)
        album_df = album_playlist.create_playlist_df(album_data)
        af = album_playlist.get_mean_audio_features()
        self.af_plot.update_af_bar_plot(af)
        self.df = album_df
        self.update_df_widget()


    # TODO: Playlist analysis section...
    # Input playlist id/link...
    # Create playlist df, with audio features..
    # Display as pd df, sortable by column...


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SpotifyGUI()
    sys.exit(app.exec_())
