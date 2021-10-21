from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import ics_reader_new as ics


# all times are integer unix times
class time_bar:
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

    def get_percentage(self):
        current_time = int(time.time())
        percentage = (current_time - self.start_time) / (self.end_time - self.start_time)
        return percentage


class MainWindow(QMainWindow):
    # noinspection PyArgumentList
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Progress Untis Clock")

        self.tabs = QTabWidget()
        self.w_uhr = QWidget()
        self.w_settings = QWidget()
        self.uhr_layout = QGridLayout()
        self.settings_layout = QGridLayout()

        self.bars_data = []
        self.bars = []
        self.titles = []
        self.left_labels = []
        self.right_labels = []
        self.get_bars()

        self.w_uhr.setLayout(self.uhr_layout)
        self.w_settings.setLayout(self.settings_layout)

        self.tabs.addTab(self.w_uhr, "Uhr")
        self.tabs.addTab(self.w_settings, "Settings")

        self.setCentralWidget(self.tabs)

        self.get_bars()
        self.update_bars()
        self.update_percentage()

        self.show()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_percentage)
        self.timer.start()

    def get_bars(self):
        self.bars_data.clear()
        self.bars.clear()
        self.titles.clear()
        self.left_labels.clear()
        self.right_labels.clear()
        # bar_data = [[title, startdt, enddt], [...], ...]
        # labels = [[title, left_label, right_label], [...], ...]
        self.bars_data.append(ics.ics_reader("EderTob.ics").get_current_lesson())
        self.bars_data.append(ics.ics_reader("EderTob.ics").get_current_day())
        self.bars_data.append(ics.ics_reader("EderTob.ics").get_current_week())

        for bar in self.bars_data:
            self.bars.append(QProgressBar())
            self.titles.append(QLabel(str(bar[0])))
            self.left_labels.append(QLabel(str(bar[1].strftime("%d/%m/%Y, %H:%M"))))
            self.right_labels.append(QLabel(str(bar[2].strftime("%d/%m/%Y, %H:%M"))))

    def update_bars(self):
        for title in self.titles:
            self.uhr_layout.addWidget(title, self.titles.index(title), 0)
        for left_label in self.left_labels:
            self.uhr_layout.addWidget(left_label, self.left_labels.index(left_label), 1)
        for bar in self.bars:
            self.uhr_layout.addWidget(bar, self.bars.index(bar), 2)
            bar.setRange(0, 100)
        for right_label in self.right_labels:
            self.uhr_layout.addWidget(right_label, self.right_labels.index(right_label), 3)

    def update_percentage(self):
        self.update_bars()
        for bar in self.bars:
            startdt = time.mktime((self.bars_data[self.bars.index(bar)][1]).timetuple())
            enddt = time.mktime((self.bars_data[self.bars.index(bar)][2]).timetuple())
            value = (time_bar(startdt, enddt).get_percentage()) * 100
            bar.setValue(int(value))
            bar.setFormat("%.01f %%" % value)
            if int(value) >= 100:
                self.get_bars()


app = QApplication([])
window = MainWindow()
app.exec_()


