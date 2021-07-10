import sys
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout,\
    QPushButton, QRadioButton, QLineEdit, QDialog, QTableWidget, QTableView
from PyQt5.QtCore import QAbstractTableModel
from spotify_api import SpotifyClient


class SpotifyGUI(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Data...")
        self.setGeometry(100, 100, 500, 500)  # x,y pos, width,height
        self.window_layout = QVBoxLayout()
        self.create_horizontal_get_top_layout()
        self.create_horizontal_get_current_layout()
        self.create_results_table()

        self.window_layout.addWidget(self.horizontal_group_box)
        self.window_layout.addWidget(self.results_table_box)
        self.window_layout.addWidget(self.horizontal_group_box_2)
        self.setLayout(self.window_layout)
        self.show()

    def create_horizontal_get_top_layout(self):
        self.horizontal_group_box = QGroupBox("Top tracks")
        layout = QHBoxLayout()

        self.number_tracks_text = QLineEdit("Number of tracks", self)
        layout.addWidget(self.number_tracks_text)

        radio_buttons_layout = QVBoxLayout()
        self.short_term_button = QRadioButton("Short term", self)
        radio_buttons_layout.addWidget(self.short_term_button)
        self.medium_term_button = QRadioButton("Medium term", self)
        radio_buttons_layout.addWidget(self.medium_term_button)
        self.long_term_button = QRadioButton("Long term", self)
        radio_buttons_layout.addWidget(self.long_term_button)
        layout.addLayout(radio_buttons_layout)

        start_button = QPushButton("Get top tracks", self)
        start_button.clicked.connect(self.get_top_click)
        layout.addWidget(start_button)

        self.horizontal_group_box.setLayout(layout)

    def create_horizontal_get_current_layout(self):
        self.horizontal_group_box_2 = QGroupBox("Current")
        layout = QHBoxLayout()

        start_button = QPushButton("Get current playing track", self)
        start_button.clicked.connect(self.get_current_click)
        layout.addWidget(start_button)

        self.horizontal_group_box_2.setLayout(layout)

    def create_results_table(self):
        self.results_table_box = QTableWidget()

    def get_top_click(self):
        number_tracks = int(self.number_tracks_text.text())
        if self.short_term_button.isChecked():
            time_period = 'short_term'
        elif self.medium_term_button.isChecked():
            time_period = 'medium_term'
        else:
            time_period = 'long_term'
        print(f"Get {number_tracks} {time_period.replace('_', ' ')} top tracks")
        SpotifyClient().get_top(limit=number_tracks, time_range=time_period)

    def get_current_click(self):
        print("Getting currently playing track")
        SpotifyClient().get_current_playback()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SpotifyGUI()
    sys.exit(app.exec_())
