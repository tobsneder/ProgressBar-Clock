from UntisReader import UntisReader
from Conversions import unix_to_string
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import time
import datetime
import pytz
import webuntis
import config


class progress_bar:
    def __init__(self, start_time, end_time, start_label, end_label, title, index, range_l=0, range_h=100):
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
        else:
            return False


class MainWindow(QMainWindow):
    # noinspection PyArgumentList
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.untis_session = None
        self.current_lesson = None
        self.current_day = None
        self.current_week = None

        self.setWindowTitle("Untis Progress Clock")
        self.setWindowIcon(QIcon('src/icon.png'))
        self.setGeometry(200, 200, 400, 200)

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
        self.login_button.clicked.connect(self.login_button_pressed)

        self.logout_button = QPushButton("Logout")
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
        self.layout_login.addWidget(self.logout_button, 5, 0)
        self.layout_login.addWidget(self.login_message_label, 6, 0)

        # settings tab
        self.test_button = QPushButton("remove test")
        self.test_button.clicked.connect(self.remove_all_bars)
        self.layout_settings.addWidget(self.test_button)

        # uhr tab
        if self.test_login()[0]:
            self.show_bars()

        self.show()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_bars)
        self.timer.start()

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
        self.current_lesson = self.untis_session.get_current_lesson()
        self.current_day = self.untis_session.get_current_day()
        self.current_week = self.untis_session.get_current_week()

    def show_bars(self):
        # show bars with untis data
        self.get_current_data()
        self.add_bar(progress_bar(self.current_lesson[1], self.current_lesson[2], unix_to_string(self.current_lesson[1]), unix_to_string(self.current_lesson[2]), self.current_lesson[0], 0))  # add new progress bar
        self.add_bar(progress_bar(self.current_day[1], self.current_day[2], unix_to_string(self.current_day[1]), unix_to_string(self.current_day[2]), self.current_day[0], 1))
        self.add_bar(progress_bar(self.current_week[1], self.current_week[2], unix_to_string(self.current_week[1]), unix_to_string(self.current_week[2]), self.current_week[0], 2))

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


