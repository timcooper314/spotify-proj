import sys
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, \
    QPushButton, QRadioButton, QLineEdit, QDialog, QMainWindow, QTableWidget
from spotify_api import SpotifyClient


class SpotifyGUI(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Data...")
        self.setGeometry(100, 100, 300, 300)  # x,y pos, width,height
        self.window_layout = QVBoxLayout()
        self.create_horizontal_layout()
        self.create_results_table()

        self.window_layout.addWidget(self.horizontal_group_box)
        self.setLayout(self.window_layout)
        self.show()

    def create_horizontal_layout(self):
        self.horizontal_group_box = QGroupBox("Top tracks")
        layout = QHBoxLayout()

        self.number_tracks_text = QLineEdit("Number of tracks", self)
        layout.addWidget(self.number_tracks_text)

        start_button = QPushButton("Get top tracks", self)
        start_button.clicked.connect(self.start_click)
        layout.addWidget(start_button)

        self.horizontal_group_box.setLayout(layout)

    def create_results_table(self):
        self.results_table_box = QTableWidget()
        self.results_table_box.show()

    def start_click(self):
        number_tracks = self.number_tracks_text.text()
        print(f"Get {number_tracks} top tracks")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SpotifyGUI()
    sys.exit(app.exec_())
