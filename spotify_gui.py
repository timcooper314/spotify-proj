import sys
from pprint import pprint
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout,\
    QPushButton, QRadioButton, QLineEdit, QDialog, QTableWidget, QTableView, QTextBrowser, QButtonGroup, QWidget
from PyQt5.QtCore import QAbstractTableModel
from spotify_api import SpotifyClient
from playlist import Playlist, create_playlist_of_top_tracks


class MPlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = Figure(figsize=(2.5, 2.5), dpi=100)
        self.axes = fig.add_axes([0.2, 0.2, 0.75, 0.75])
        super(MPlotCanvas, self).__init__(fig)

    def update_af_bar_plot(self, af):
        self.axes.cla()
        self.axes.bar(af.keys(), af.values(), color='g')
        self.axes.tick_params(axis='both', which='major', labelsize=8, labelrotation=10)
        self.draw()

class SpotifyGUI(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Data...")
        self.setGeometry(100, 100, 800, 500)  # x,y pos, width,height
        self.window_layout = QVBoxLayout()
        self.create_horizontal_get_top_layout()
        # self.create_results_table()
        self.create_horizontal_get_af_layout()

        self.window_layout.addWidget(self.horizontal_group_box)
        # self.window_layout.addWidget(self.results_table_box)
        self.window_layout.addWidget(self.horizontal_group_box_2)
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

        get_current_track_button = QPushButton("Get current playing track", self)
        get_current_track_button.clicked.connect(self.get_current_click)
        v_layout.addWidget(get_current_track_button)

        layout.addLayout(v_layout)

        get_current_af_button = QPushButton("Get audio features of track", self)
        get_current_af_button.clicked.connect(self.get_af_click)
        layout.addWidget(get_current_af_button)

        self.af_plot = MPlotCanvas(self)
        # self.af_plot.axes.bar(['a','b','c','d','e'], [0, 0, 0, 0, 0])
        # self.af_plot.axes.tick_params(axis='both', which='major', labelsize=8)
        layout.addWidget(self.af_plot)

        self.horizontal_group_box_2.setLayout(layout)

    # def create_results_table(self):
    #     self.results_table_box = QTextBrowser()  # QTableWidget()

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
        else:
            top_type = 'tracks'
        print(f"{number_tracks} {time_period.replace('_', ' ')} top {top_type}:")
        top_data = SpotifyClient().get_top(top_type=top_type, limit=number_tracks, time_range=time_period)
        # self.results_table_box.append(str(top_data))

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

    # TODO: Playlist analysis section...
    # Input playlist id/link...
    # Create playlist df, with audio features..
    # Display as pd df, sortable by column...


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SpotifyGUI()
    sys.exit(app.exec_())
