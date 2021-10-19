from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
from calendar import monthrange


# all times are integer unix times


class time_bar:
    def __init__(self, start_time, stop_time, bar_label, start_label, stop_label):
        self.start_time = start_time
        self.stop_time = stop_time
        self.bar_label = bar_label
        self.start_label = start_label
        self.stop_label = stop_label

    def get_percentage(self):
        current_time = int(time.time())
        percentage = (current_time - self.start_time) / (self.stop_time - self.start_time)
        return percentage


start = 1634639400
stop = 1634642400






