from UntisReader import UntisReader
from Conversions import unix_to_string
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from configparser import ConfigParser
import time
import datetime
import pytz
import webuntis
import qdarktheme


class ProgressBar:
    def __init__(self, start_time=0, end_time=0, start_label="", end_label="", title="", index=0, range_l=0, range_h=100):
        self.start_time = start_time
        self.end_time = end_time
        self.start_label = QLabel(start_label)
        self.end_label = QLabel(end_label)
        self.title = QLabel(title)
        self.bar = QProgressBar()
        self.bar.setRange(range_l, range_h)
        self.index = index

    def update_percentage(self):
        current_time = int(time.time())
        percentage = ((current_time - self.start_time) / (self.end_time - self.start_time)) * 100
        if percentage <= 100:
            self.bar.setValue(int(percentage))
            self.bar.setFormat("%.01f%%" % percentage)
            return True
        return False


class MainWindow(QMainWindow):
    # noinspection PyArgumentList
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.config = ConfigParser()
        self.config.read("config.ini")

        self.untis_session = None
        self.current_data = []

        self.setWindowTitle("Untis Progress Clock")
        self.setWindowIcon(QIcon('src/icon.png'))
        self.setGeometry(200, 200, 400, 200)
        # todo set change window border color https://envyen.com/posts/2021-10-24-QT-Windows-Dark-theme/

        self.bars = []

        self.tabs = QTabWidget()
        self.w_uhr = QWidget()
        self.w_login = QWidget()
        self.w_settings = QWidget()
        self.layout_uhr = QGridLayout()
        self.layout_login = QGridLayout()
        self.layout_settings = QGridLayout()

        self.w_uhr.setLayout(self.layout_uhr)
        self.w_login.setLayout(self.layout_login)
        self.w_settings.setLayout(self.layout_settings)

        self.tabs.addTab(self.w_uhr, "Uhr")
        self.tabs.addTab(self.w_login, "Login")
        self.tabs.addTab(self.w_settings, "Settings")

        self.setCentralWidget(self.tabs)

        # login tab
        # todo make option for teacher mode
        self.username_inp = QLineEdit()
        self.password_inp = QLineEdit()
        self.password_inp.setEchoMode(QLineEdit.Password)
        self.klasse_inp = QLineEdit()

        self.username_inp_label = QLabel("username")
        self.password_inp_label = QLabel("password")
        self.klasse_inp_label = QLabel("class")

        try:    # try reading login data from file / create one if not there
            with open("user_credentials.txt", "r") as file:
                self.username_inp.setText(file.readline().strip())
                self.password_inp.setText(file.readline().strip())
                self.klasse_inp.setText(file.readline().strip())
        except FileNotFoundError:
            open("user_credentials.txt", "w").close()

        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("background-color: #34A835; color: white;")
        self.login_button.clicked.connect(self.login_button_pressed)

        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("background-color: #E91224; color: white;")
        self.logout_button.clicked.connect(self.logout)

        self.login_message_label = QLabel()
        self.login_message_label.setAlignment(Qt.AlignTop)
        self.login_message_label.setAlignment(Qt.AlignLeft)

        self.layout_login.addWidget(self.username_inp_label, 0, 1)
        self.layout_login.addWidget(self.username_inp, 0, 0)
        self.layout_login.addWidget(self.password_inp_label, 1, 1)
        self.layout_login.addWidget(self.password_inp, 1, 0)
        self.layout_login.addWidget(self.klasse_inp_label, 2, 1)
        self.layout_login.addWidget(self.klasse_inp, 2, 0)
        self.layout_login.addWidget(self.login_button, 3, 0)
        self.layout_login.addWidget(self.logout_button, 4, 0)
        self.layout_login.addWidget(self.login_message_label, 5, 0)

        # settings tab
        self.theme_checkbox = QCheckBox("Dark-Mode")
        self.theme_checkbox.stateChanged.connect(self.theme_checkbox_toggled)
        self.theme_checkbox.setChecked(self.config.getboolean("Settings", "dark-mode"))

        self.show_start_end_label_checkbox = QCheckBox("Show Start/End time")
        self.show_start_end_label_checkbox.stateChanged.connect(self.show_start_end_label_checkbox_toggled)
        self.show_start_end_label_checkbox.setChecked(self.config.getboolean("Settings", "show-start-end-label"))

        self.show_bar_percentage_checkbox = QCheckBox("Show Percentage")
        self.show_bar_percentage_checkbox.stateChanged.connect(self.show_bar_percentage_checkbox_toggled)
        self.show_bar_percentage_checkbox.setChecked(self.config.getboolean("Settings", "show-bar-percentage"))

        self.teacher_mode_checkbox = QCheckBox("Teacher Mode")      # todo teacher mode
        self.teacher_mode_checkbox.stateChanged.connect(self.teacher_mode_checkbox_toggled)
        self.teacher_mode_checkbox.setChecked(self.config.getboolean("Settings", "teacher-mode"))

        self.layout_settings.addWidget(self.theme_checkbox, 0, 0)
        self.layout_settings.addWidget(self.show_start_end_label_checkbox, 1, 0)
        self.layout_settings.addWidget(self.show_bar_percentage_checkbox, 2, 0)

        # uhr tab
        if self.test_login()[0]:
            self.show_bars()
            # execute previously loaded settings
            self.theme_checkbox_toggled()
            self.show_start_end_label_checkbox_toggled()
            self.show_bar_percentage_checkbox_toggled()
            self.teacher_mode_checkbox_toggled()

        self.show()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_bars)
        self.timer.start()

    def load_settings(self):
        # todo laod settings
        pass

    def save_settings(self):
        # todo save settings
        pass

    def theme_checkbox_toggled(self):
        if self.theme_checkbox.isChecked():
            self.setStyleSheet(qdarktheme.load_stylesheet("dark"))
        else:
            self.setStyleSheet(qdarktheme.load_stylesheet("light"))

    def show_start_end_label_checkbox_toggled(self):
        if self.show_start_end_label_checkbox.isChecked():
            for bar in self.bars:
                bar.start_label.show()
                bar.end_label.show()
        else:
            for bar in self.bars:
                bar.start_label.hide()
                bar.end_label.hide()

    def show_bar_percentage_checkbox_toggled(self):
        if self.show_bar_percentage_checkbox.isChecked():
            for bar in self.bars:
                bar.bar.setTextVisible(True)
        else:
            for bar in self.bars:
                bar.bar.setTextVisible(False)

    def teacher_mode_checkbox_toggled(self):
        # todo teacher mode
        pass

    def update_bars(self):
        for bar in self.bars:
            if not bar.update_percentage():
                self.remove_all_bars()
                self.show_bars()

    def add_bar(self, bar):
        self.bars.append(bar)

        self.layout_uhr.addWidget(bar.title, bar.index, 0)
        self.layout_uhr.addWidget(bar.start_label, bar.index, 1)
        self.layout_uhr.addWidget(bar.bar, bar.index, 2)
        self.layout_uhr.addWidget(bar.end_label, bar.index, 3)

        self.update_bars()

    def get_current_data(self):
        self.current_data = [self.untis_session.get_current_lesson(),
                             self.untis_session.get_current_day(),
                             self.untis_session.get_current_week()]

    def show_bars(self):
        # show bars with untis data
        self.get_current_data()
        for data in self.current_data:
            if data is not None:
                self.add_bar(ProgressBar(data[1], data[2], unix_to_string(data[1]), unix_to_string(data[2]), data[0], 0))  # add new progress bar

    def remove_bar(self, bar):
        self.layout_uhr.removeWidget(bar.title)
        self.layout_uhr.removeWidget(bar.start_label)
        self.layout_uhr.removeWidget(bar.bar)
        self.layout_uhr.removeWidget(bar.end_label)

    def remove_all_bars(self):
        for bar in self.bars:
            self.remove_bar(bar)
        self.bars.clear()

    def test_login(self):
        try:
            self.untis_session = UntisReader(class_name=self.klasse_inp.text(), username=self.username_inp.text(), password=self.password_inp.text())
            return True, "login successful"
        except Exception as e:
            return False, "login failed: " + str(e)

    def login_button_pressed(self):
        if self.untis_session is None:
            success, message = self.test_login()
            if success:
                self.login_message_label.setText(message)

                # save login data in file
                with open("user_credentials.txt", "w") as file:
                    file.write(str(self.username_inp.text() + "\n"))
                    file.write(str(self.password_inp.text() + "\n"))
                    file.write(str(self.klasse_inp.text()))

                self.show_bars()
            else:
                self.login_message_label.setText(message)

    def logout(self):
        open("user_credentials.txt", "w").close()
        self.untis_session.logout()
        self.untis_session = None
        self.username_inp.setText("")
        self.password_inp.setText("")
        self.klasse_inp.setText("")
        self.remove_all_bars()
        self.login_message_label.setText("logout successful")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec_()


