import sys
import os
import json

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QStyleFactory
from PyQt5.QtWidgets import QAction, QMessageBox, QCheckBox, QProgressBar, QLabel, QComboBox
from PyQt5.QtWidgets import QFileDialog

from subregions import SUBREGION
from fmapper import reset_current_map

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(100, 100, 550, 300)
        self.setWindowTitle('Fortroute Mapper')
        self.setWindowIcon(QIcon('./favicon.ico'))
        self.load_settings()
        self.init_ui()

    def load_settings(self):
        with open('settings.json', 'r') as f:
            self.settings = json.load(f)

    def init_ui(self):
        QApplication.setStyle(QStyleFactory.create('Fusion'))

        self.res_label = QLabel('Select Fortnite Resolution:', self)
        self.res_label.resize(150, 10)
        self.res_label.move(10, 10)

        resolution_dropdown = QComboBox(self)
        for resolution in SUBREGION.keys():
            resolution_dropdown.addItem(resolution)
        resolution_dropdown.move(5,30)

        index = resolution_dropdown.findText(self.settings['resolution'], Qt.MatchFixedString)
        if index >= 0:
            resolution_dropdown.setCurrentIndex(index)

        resolution_dropdown.activated[str].connect(self.change_resolution)

        self.output_label = QLabel('Select image output folder:', self)
        self.output_label.adjustSize()
        self.output_label.move(10, 100)

        self.output_text = QLabel(self.settings['location_folder'], self)
        self.output_text.adjustSize()
        self.output_text.move(10, 125)

        self.folder_selector = QPushButton('...', self)
        self.folder_selector.move(20 + self.output_text.geometry().width(), 125)
        self.folder_selector.resize(20,15)
        self.folder_selector.clicked.connect(self.change_destination_folder)

        self.map_label = QLabel('Current Map:', self)
        self.map_label.adjustSize()
        self.map_label.move(275, 10)

        self.map_container = QLabel(self)
        self.update_pixmap()
        self.show()


    def change_setting(self, setting, value):
        with open('settings.json', 'r+') as f:
            settings = json.load(f)
            settings[setting] = value
            f.seek(0)
            json.dump(settings, f)
            f.truncate()
        self.load_settings()
        
    def change_resolution(self, resolution):
        self.change_setting('resolution', resolution)

    def update_pixmap(self):
        image_filepath = os.path.join(self.settings['location_folder'], 'current_map.png')
        self.pixmap = QPixmap(image_filepath).scaledToWidth(250)
        self.map_container.setPixmap(self.pixmap)
        self.map_container.resize(self.pixmap.width(),self.pixmap.height())
        self.map_container.move(275,30)

    def change_destination_folder(self):
        file_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if not os.path.isdir(file_path):
            return
        self.output_text.setText(file_path)
        self.output_text.adjustSize()
        self.folder_selector.move(20 + self.output_text.geometry().width(), 125)
        self.change_setting('location_folder', file_path)
        reset_current_map(folder_override=self.settings['location_folder'])
        self.update_pixmap()

def run():
    app = QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()