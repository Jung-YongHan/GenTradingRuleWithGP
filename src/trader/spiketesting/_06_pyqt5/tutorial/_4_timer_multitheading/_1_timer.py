import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import datetime

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # timer
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout)

    def timeout(self):
        now = datetime.datetime.now()
        self.statusBar().showMessage(str(now))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()