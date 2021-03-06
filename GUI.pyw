from UntisReader import UntisReader
from Conversions import unix_to_string
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from configparser import ConfigParser
import qdarktheme
import time


class ProgressBar:
    def __init__(self):
        self.default_start_unix = 0
        self.default_end_unix = 10000000000
        self.start_unix = self.default_start_unix
        self.end_unix = self.default_end_unix
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        #self.bar.setStyleSheet("QProgressBar::chunk { background-color: green; } QProgressBar { color: white; }")
        self.title = QLabel()
        self.start_label = QLabel()
        self.end_label = QLabel()

    def set_data(self, start_unix, end_unix, title, start_label, end_label):
        self.start_unix = start_unix
        self.end_unix = end_unix
        self.title.setText(title)
        self.start_label.setText(start_label)
        self.end_label.setText(end_label)

    def set_default_data(self):
        self.set_data(self.default_start_unix, self.default_end_unix, "", "", "")

    def update_percentage(self):
        current_time = time.time()
        percentage = ((current_time - self.start_unix) / (self.end_unix - self.start_unix)) * 100
        if percentage <= 100:
            self.bar.setValue(int(percentage))
            self.bar.setFormat("%.01f%%" % percentage)

    def get_bar(self):
        return self.bar

    def get_title(self):
        return self.title

    def get_start_label(self):
        return self.start_label

    def get_end_label(self):
        return self.end_label

    def show(self, title=False, start_label=False, end_label=False, bar=False, bar_percentage=False):
        if title:
            self.title.show()
        else:
            self.title.hide()
        if start_label:
            self.start_label.show()
        else:
            self.start_label.hide()
        if end_label:
            self.end_label.show()
        else:
            self.end_label.hide()
        if bar:
            self.bar.show()
        else:
            self.bar.hide()
        if bar_percentage:
            self.bar.setTextVisible(True)
        else:
            self.bar.setTextVisible(False)


class MainWindow(QMainWindow):
    # noinspection PyArgumentList
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.config = ConfigParser()
        self.config_path = "config.ini"
        self.config.read(self.config_path)

        self.untis_session = None
        self.current_data = [None, None, None]
        self.bars = [ProgressBar(), ProgressBar(), ProgressBar()]

        self.setWindowTitle("Untis Progress Clock")
        self.setWindowIcon(QIcon("src/icon.png"))
        self.setGeometry(400, 400, 300, 172)
        self.setMinimumWidth(300)
        # todo set change window border color https://envyen.com/posts/2021-10-24-QT-Windows-Dark-theme/

        self.tabs = QTabWidget()
        self.w_uhr = QWidget()
        self.w_login = QWidget()
        self.w_settings = QWidget()
        self.w_info = QWidget()

        self.layout_clock = QGridLayout()
        self.layout_login = QGridLayout()
        self.layout_settings = QGridLayout()
        self.layout_info = QGridLayout()

        self.w_uhr.setLayout(self.layout_clock)
        self.w_login.setLayout(self.layout_login)
        self.w_settings.setLayout(self.layout_settings)
        self.w_info.setLayout(self.layout_info)

        self.tabs.addTab(self.w_uhr, "   Clock   ")
        self.tabs.addTab(self.w_login, "   Login   ")
        self.tabs.addTab(self.w_settings, " Settings ")
        self.tabs.addTab(self.w_info, "   Info   ")

        self.setCentralWidget(self.tabs)

        # Info tab
        # max text with "Consolas" font: 45 x 9
        with open("src/info.txt", "r") as file:
            self.info = file.read()
        self.info_label = QLabel(self.info)
        self.info_label.setFont(QFont("Consolas"))
        self.layout_info.addWidget(self.info_label, 0, 0, alignment=Qt.AlignLeft | Qt.AlignTop)

        # login tab
        self.username_inp = QLineEdit()
        self.password_inp = QLineEdit()
        self.password_inp.setEchoMode(QLineEdit.Password)
        self.full_name_inp = QLineEdit()

        self.username_inp_label = QLabel("Username")
        self.password_inp_label = QLabel("Password")
        self.full_name_inp_label = QLabel("Full Name")

        try:    # try reading login data from file / create one if not there
            with open("user_credentials.txt", "r") as file:
                self.username_inp.setText(file.readline().strip())
                self.password_inp.setText(file.readline().strip())
                self.full_name_inp.setText(file.readline().strip())
        except FileNotFoundError:
            open("user_credentials.txt", "w").close()

        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("background-color: #34A835; color: white;")
        self.login_button.clicked.connect(self.login_button_clicked)
        self.login_button.setFixedWidth(60)
        self.login_button.setCursor(QCursor(Qt.PointingHandCursor))

        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("background-color: #E91224; color: white;")
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setFixedWidth(60)
        self.logout_button.setCursor(QCursor(Qt.PointingHandCursor))

        self.update_button = QPushButton("Update")
        self.update_button.setStyleSheet("background-color: #8AB4F7; color: white;")
        self.update_button.clicked.connect(self.reparse_button_clicked)
        self.update_button.setFixedWidth(60)
        self.update_button.setCursor(QCursor(Qt.PointingHandCursor))

        self.login_message_label = QLabel()

        self.layout_login.addWidget(self.username_inp, 0, 0)
        self.layout_login.addWidget(self.username_inp_label, 0, 1)
        self.layout_login.addWidget(self.password_inp, 1, 0)
        self.layout_login.addWidget(self.password_inp_label, 1, 1)
        self.layout_login.addWidget(self.full_name_inp, 2, 0)
        self.layout_login.addWidget(self.full_name_inp_label, 2, 1)
        self.layout_login.addWidget(self.login_button, 3, 0, alignment=Qt.AlignLeft)
        self.layout_login.addWidget(self.update_button, 3, 0, alignment=Qt.AlignCenter)
        self.layout_login.addWidget(self.logout_button, 3, 0, alignment=Qt.AlignRight)
        self.layout_login.addWidget(self.login_message_label, 4, 0, 4, 2, alignment=Qt.AlignLeft | Qt.AlignTop)

        # uhr tab
        self.create_bars()

        # settings tab
        self.theme_checkbox = QCheckBox("Dark-Mode")
        self.theme_checkbox.stateChanged.connect(self.theme_checkbox_toggled)
        self.theme_checkbox.setChecked(self.config.getboolean("Settings", "dark-mode"))
        self.theme_checkbox_toggled()

        self.show_start_end_label_checkbox = QCheckBox("Show Start/End time")
        self.show_start_end_label_checkbox.stateChanged.connect(self.show_start_end_label_checkbox_toggled)
        self.show_start_end_label_checkbox.setChecked(self.config.getboolean("Settings", "show-start-end-label"))
        self.show_start_end_label_checkbox_toggled()

        self.show_bar_percentage_checkbox = QCheckBox("Show Percentage")
        self.show_bar_percentage_checkbox.stateChanged.connect(self.show_bar_percentage_checkbox_toggled)
        self.show_bar_percentage_checkbox.setChecked(self.config.getboolean("Settings", "show-bar-percentage"))
        self.show_bar_percentage_checkbox_toggled()

        self.teacher_mode_checkbox = QCheckBox("Teacher Mode")
        self.teacher_mode_checkbox.stateChanged.connect(self.teacher_mode_checkbox_toggled)
        self.teacher_mode_checkbox.setChecked(self.config.getboolean("Settings", "teacher-mode"))
        self.teacher_mode_checkbox_toggled()

        self.window_on_top_checkbox = QCheckBox("Keep Window on Top")
        self.window_on_top_checkbox.stateChanged.connect(self.window_on_top_checkbox_toggled)
        self.window_on_top_checkbox.setChecked(self.config.getboolean("Settings", "window-on-top"))
        self.window_on_top_checkbox_toggled()

        self.layout_settings.addWidget(self.theme_checkbox, 0, 0)
        self.layout_settings.addWidget(self.show_start_end_label_checkbox, 1, 0)
        self.layout_settings.addWidget(self.show_bar_percentage_checkbox, 2, 0)
        self.layout_settings.addWidget(self.teacher_mode_checkbox, 3, 0)
        self.layout_settings.addWidget(self.window_on_top_checkbox, 4, 0, alignment=Qt.AlignTop)

        # end of layout creation

        self.login_button_clicked()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_bars)
        self.timer.start()

        self.show()

    # Settings
    def theme_checkbox_toggled(self):
        if self.theme_checkbox.isChecked():
            self.setStyleSheet(qdarktheme.load_stylesheet("dark"))
        else:
            self.setStyleSheet(qdarktheme.load_stylesheet("light"))
        # save
        self.config.set("Settings", "dark-mode", str(self.theme_checkbox.isChecked()))
        with open(self.config_path, 'w') as configfile:  # save
            self.config.write(configfile)

    def show_start_end_label_checkbox_toggled(self):
        self.update_bars()
        # save
        self.config.set("Settings", "show-start-end-label", str(self.show_start_end_label_checkbox.isChecked()))
        with open(self.config_path, 'w') as configfile:  # save
            self.config.write(configfile)

    def show_bar_percentage_checkbox_toggled(self):
        self.update_bars()
        # save
        self.config.set("Settings", "show-bar-percentage", str(self.show_bar_percentage_checkbox.isChecked()))
        with open(self.config_path, 'w') as configfile:  # save
            self.config.write(configfile)

    def teacher_mode_checkbox_toggled(self):
        # save
        self.config.set("Settings", "teacher-mode", str(self.teacher_mode_checkbox.isChecked()))
        with open(self.config_path, 'w') as configfile:  # save
            self.config.write(configfile)

    def window_on_top_checkbox_toggled(self):
        if self.window_on_top_checkbox.isChecked():
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
        # save
        self.config.set("Settings", "window-on-top", str(self.window_on_top_checkbox.isChecked()))
        with open(self.config_path, 'w') as configfile:  # save
            self.config.write(configfile)

    # Bars
    def update_bars(self):
        if self.untis_session is not None:
            self.update_current_data()
        for i in range(len(self.bars)):
            data = self.current_data[i]
            bar = self.bars[i]
            if data is not None and self.untis_session is not None:
                bar.set_data(data[1], data[2], data[0], unix_to_string(data[1]), unix_to_string(data[2]))
                bar.update_percentage()

                show_start_end_label = self.show_start_end_label_checkbox.isChecked()
                show_bar_percentage = self.show_bar_percentage_checkbox.isChecked()
                bar.show(title=True,
                         start_label=show_start_end_label,
                         end_label=show_start_end_label,
                         bar=True,
                         bar_percentage=show_bar_percentage)
            else:
                bar.set_default_data()
                bar.show(title=False, start_label=False, end_label=False, bar=False)

    def create_bars(self):
        for i in range(len(self.bars)):
            self.layout_clock.addWidget(self.bars[i].get_title(), i, 0)
            self.layout_clock.addWidget(self.bars[i].get_start_label(), i, 1)
            self.layout_clock.addWidget(self.bars[i].get_bar(), i, 2)
            self.layout_clock.addWidget(self.bars[i].get_end_label(), i, 3)

    def update_current_data(self):
        self.current_data = [self.untis_session.get_current_lesson(),
                             self.untis_session.get_current_day(),
                             self.untis_session.get_current_week()]

    # Login/Logout
    def reparse_button_clicked(self):
        if self.untis_session is not None:
            try:
                self.parse_with_current_input()
                self.login_message_label.setText("Updated name to: " + self.full_name_inp.text())
            except Exception as exc:
                self.untis_session = None
                self.login_message_label.setText("Update failed: " + str(exc))
        else:
            self.login_message_label.setText("No Untis session running (try logging in)")

    def parse_with_current_input(self):
        if self.teacher_mode_checkbox.isChecked():
            is_teacher = True
            is_student = False
        else:
            is_teacher = False
            is_student = True

        if self.full_name_inp.text().count(" ") == 1:
            forename = self.full_name_inp.text().split(" ")[0]
            surname = self.full_name_inp.text().split(" ")[1]
        else:
            forename = None
            surname = None

        try:
            self.untis_session.parse(is_teacher=is_teacher, is_student=is_student, forename=forename, surname=surname)
        except Exception as exc:
            self.untis_session = None
            raise Exception(exc)
        if not self.untis_session.get_lessons():
            self.untis_session = None
            raise Exception("no timetable for:" + self.full_name_inp.text())

    def test_login(self):
        try:
            self.untis_session = UntisReader(username=self.username_inp.text(), password=self.password_inp.text())
            self.parse_with_current_input()
            return True, "Login successful!   Set name to: " + self.full_name_inp.text()
        except Exception as exc:
            return False, "Login failed: " + str(exc)

    def login_button_clicked(self):
        if self.untis_session is None:
            success, message = self.test_login()
            if success:
                self.login_message_label.setText(message)

                # save login data in file
                with open("user_credentials.txt", "w") as file:
                    file.write(str(self.username_inp.text() + "\n"))
                    file.write(str(self.password_inp.text() + "\n"))
                    file.write(str(self.full_name_inp.text()))

            else:
                self.login_message_label.setText(message)

    def logout(self):
        open("user_credentials.txt", "w").close()
        if self.untis_session is not None:
            self.untis_session.logout()
        self.untis_session = None
        self.username_inp.setText("")
        self.password_inp.setText("")
        self.full_name_inp.setText("")
        for bar in self.bars:
            bar.set_default_data()
            bar.hide()
        self.login_message_label.setText("logout successful")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec_()

