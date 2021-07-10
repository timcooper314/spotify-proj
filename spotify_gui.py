import sys
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout,\
    QPushButton, QRadioButton, QLineEdit, QDialog, QTableWidget, QTableView, QTextBrowser, QButtonGroup, QWidget
from PyQt5.QtCore import QAbstractTableModel
from spotify_api import SpotifyClient


class SpotifyGUI(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Data...")
        self.setGeometry(100, 100, 500, 500)  # x,y pos, width,height
        self.window_layout = QVBoxLayout()
        self.create_horizontal_get_top_layout()
        self.create_results_table()
        self.create_horizontal_get_current_layout()

        self.window_layout.addWidget(self.horizontal_group_box)
        self.window_layout.addWidget(self.results_table_box)
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
        self.short_term_button.setChecked(True)
        self.medium_term_button = QRadioButton("Medium term", self)
        self.long_term_button = QRadioButton("Long term", self)
        time_period_buttons_layout.addWidget(self.short_term_button)
        time_period_buttons_layout.addWidget(self.medium_term_button)
        time_period_buttons_layout.addWidget(self.long_term_button)
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

        start_button = QPushButton("Get data", self)
        start_button.clicked.connect(self.get_top_click)
        h_layout.addWidget(start_button)

        self.horizontal_group_box.setLayout(h_layout)

    def create_horizontal_get_current_layout(self):
        self.horizontal_group_box_2 = QGroupBox("Current")
        layout = QHBoxLayout()

        start_button = QPushButton("Get current playing track", self)
        start_button.clicked.connect(self.get_current_click)
        layout.addWidget(start_button)

        self.horizontal_group_box_2.setLayout(layout)

    def create_results_table(self):
        self.results_table_box = QTextBrowser()  # QTableWidget()

    def get_top_click(self):
        number_tracks = int(self.number_tracks_text.text())
        if self.short_term_button.isChecked():
            time_period = 'short_term'
        elif self.medium_term_button.isChecked():
            time_period = 'medium_term'
        else:
            time_period = 'long_term'
        if self.artists_button.isChecked():
            top_type = 'artists'
        else:
            top_type = 'tracks'
        print(f"Get {number_tracks} {time_period.replace('_', ' ')} top {top_type}")
        top_data = SpotifyClient().get_top(top_type=top_type, limit=number_tracks, time_range=time_period)
        self.results_table_box.append(str(top_data))

    def get_current_click(self):
        print("Getting currently playing track")
        SpotifyClient().get_current_playback()

    # TODO: Add create playlist functionality - for top songs, etc


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SpotifyGUI()
    sys.exit(app.exec_())
