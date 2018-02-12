import sys
import os
import json

from PyQt5.QtCore import QCoreApplication, Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QFont, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QStyleFactory
from PyQt5.QtWidgets import QAction, QMessageBox, QCheckBox, QProgressBar, QLabel, QComboBox
from PyQt5.QtWidgets import QFileDialog

from subregions import SUBREGION
from fmapper import reset_current_map, record_point, update_map, save_map

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(100, 100, 620, 485)
        self.setWindowTitle('Fortroute Mapper')
        self.setWindowIcon(QIcon('./img/favicon.ico'))
        self.timer_on = False
        self.points = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_action)
        self.load_settings()
        self.init_ui()

    def load_settings(self):
        with open('settings.json', 'r') as f:
            self.settings = json.load(f)

    def init_ui(self):
        boldFont = QFont()
        boldFont.setBold(True)
        QApplication.setStyle(QStyleFactory.create('Fusion'))

        self.title = QLabel(self)
        self.title_image = QPixmap('./img/fortmapper.png')
        self.title.setPixmap(self.title_image)
        self.title.resize(self.title_image.width(),self.title_image.height())
        self.title.move(20,0)

        self.namelabel = QLabel('Made with love by abyssalheaven', self)
        self.namelabel.adjustSize()
        self.namelabel.move(23, 55)


        self.res_label = QLabel('Select Fortnite Resolution:', self)
        self.res_label.setFont(boldFont)
        self.res_label.resize(150, 10)
        self.res_label.move(20, 100)

        resolution_dropdown = QComboBox(self)
        for resolution in SUBREGION.keys():
            resolution_dropdown.addItem(resolution)
        resolution_dropdown.move(20,120)

        index = resolution_dropdown.findText(self.settings['resolution'], Qt.MatchFixedString)
        if index >= 0:
            resolution_dropdown.setCurrentIndex(index)

        resolution_dropdown.activated[str].connect(self.change_resolution)

        self.output_label = QLabel('Select image output folder:', self)
        self.output_label.setFont(boldFont)
        self.output_label.adjustSize()
        self.output_label.move(20, 190)

        self.output_text = QLabel(self.settings['location_folder'], self)
        self.output_text.adjustSize()
        self.output_text.move(20, 205)

        self.folder_selector = QPushButton('...', self)
        self.folder_selector.move(30 + self.output_text.geometry().width(), 205)
        self.folder_selector.resize(20,15)
        self.folder_selector.clicked.connect(self.change_destination_folder)

        self.map_container = QLabel(self)
        self.update_pixmap()

        self.timer_button = QPushButton('START', self)
        self.timer_button.move(40, 280)
        self.timer_button.clicked.connect(self.toggle_timer)

        self.reset_button = QPushButton('RESET MAP', self)
        self.reset_button.move(40, 320)
        self.reset_button.clicked.connect(self.reset_map)

        self.show()

    def reset_map(self):
        reset_current_map()
        self.update_pixmap()

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
        self.pixmap = QPixmap(image_filepath).scaledToWidth(400)
        self.map_container.setPixmap(self.pixmap)
        self.map_container.resize(self.pixmap.width(),self.pixmap.height())
        self.map_container.move(200,70)

    def change_destination_folder(self):
        file_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if not os.path.isdir(file_path):
            return
        self.output_text.setText(file_path)
        self.output_text.adjustSize()
        self.folder_selector.move(30 + self.output_text.geometry().width(), 205)
        self.change_setting('location_folder', file_path)
        reset_current_map(folder_override=self.settings['location_folder'])
        self.update_pixmap()

    def timer_action(self):
        coord = record_point(print_coord=True)
        if coord:
            self.points.append(coord)
            update_map(self.points)
            self.update_pixmap()

    def toggle_timer(self):
        if self.timer_on:
            self.timer_on = False
            self.timer.stop()
            self.timer_button.setText('START')
            choice = QMessageBox.question(self, 'Save', 'Do you want to save this route map?', QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                name, _  = QFileDialog.getSaveFileName(self, 'Save Route Map As...', filter='*.png')
                if name:
                    save_map(name)

        else:
            print('Timer started - will record first point in 5 seconds.')
            reset_current_map()
            self.update_pixmap()
            self.points = []
            self.timer.start(5000)
            self.timer_on = True
            self.timer_button.setText('STOP')

def run():
    app = QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()