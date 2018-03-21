import sys
import os
import json
import keyboard

from PyQt5.QtCore import QCoreApplication, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QStyleFactory
from PyQt5.QtWidgets import QAction, QMessageBox, QCheckBox, QProgressBar, QLabel, QComboBox
from PyQt5.QtWidgets import QFileDialog

from subregions import SubregionManager
from settings import SettingsManager
from fmapper import reset_current_map, record_point, update_map, save_map

class Window(QMainWindow):
    resized = pyqtSignal()
    def __init__(self):
        super(Window, self).__init__()
        self.map_loc = (200,70)
        self.setGeometry(100, 100, 620, 485)
        self.setWindowTitle('Fortroute Mapper')
        self.setWindowIcon(QIcon('./img/favicon.ico'))
        self.timer_should_be_on = False
        self.timer_on = False
        self.points = []
        self.time_checker = QTimer()
        self.time_checker.timeout.connect(self.check_for_timer)
        self.time_checker.start(1000)
        keyboard.add_hotkey('ctrl+shift+r', self.signal_timer_toggle)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_action)
        self.settings = SettingsManager.initialize_settings()
        self.resized.connect(self.update_pixmap)
        self.init_ui()
        self.reset_map()

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
        for resolution in SubregionManager.get_available_resolutions():
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

        self.output_text = QLabel(self.truncate_path_name(self.settings['location_folder']), self)
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

        self.auto_save = QCheckBox('Save on Stop?', self)
        self.auto_save.move(40, 360)
        self.auto_save.adjustSize()
        if self.settings['auto_save']:
            self.auto_save.toggle()
        self.auto_save.stateChanged.connect(self.change_autosave)

        self.show()

    def resizeEvent(self, event):
        self.resized.emit()
        return super(Window, self).resizeEvent(event)

    def reset_map(self):
        reset_current_map()
        self.update_pixmap()

    def change_setting(self, setting, value):
        if setting == 'auto_save':
            value = self.auto_save.checkState() == 2
        self.settings = SettingsManager.change_setting(setting, value)
        
    def change_resolution(self, resolution):
        self.change_setting('resolution', resolution)

    def determine_map_resize(self):
        loc_x, loc_y = self.map_loc
        a = self.geometry().width() - 15 - loc_x
        b = self.geometry().height() - 15 - loc_y
        return min(a, b)

    def update_pixmap(self):
        image_filepath = os.path.join(self.settings['location_folder'], 'current_map.png')
        self.pixmap = QPixmap(image_filepath).scaledToWidth(self.determine_map_resize())
        self.map_container.setPixmap(self.pixmap)
        self.map_container.resize(self.pixmap.width(),self.pixmap.height())
        self.map_container.move(*self.map_loc)

    def truncate_path_name(self, pathname):
        if len(pathname) > 26:
            paths = pathname.split('/')
            new_path = paths[0] + '/.../' + paths[-1]
            return new_path
        else:
            return pathname

    def change_autosave(self):
        self.change_setting('auto_save', self.auto_save.checkState() == 2)

    def change_destination_folder(self):
        file_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if not os.path.isdir(file_path):
            return
        self.output_text.setText(self.truncate_path_name(file_path))
        self.output_text.adjustSize()
        self.folder_selector.move(30 + self.output_text.geometry().width(), 205)
        self.change_setting('location_folder', file_path)
        reset_current_map(folder_override=self.settings['location_folder'])
        self.update_pixmap()

    def signal_timer_toggle(self):
        self.timer_should_be_on = not self.timer_should_be_on

    def check_for_timer(self):
        if (self.timer_should_be_on != self.timer_on):
            self.toggle_timer(shortcut=True)

    def timer_action(self):
        coord = record_point(print_coord=True, setting=self.settings, show_one=True)
        if coord:
            self.points.append(coord)
            update_map(self.points)
            self.update_pixmap()

    def toggle_timer(self, shortcut=False):
        if self.timer_on:
            self.timer.stop()
            self.timer_on = False
            if not shortcut:
                self.timer_should_be_on = False
            self.timer_button.setText('START')
            if self.auto_save.checkState() == 2:
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
            if not shortcut:
                self.timer_should_be_on = True
            self.timer_button.setText('STOP')

def run():
    app = QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()