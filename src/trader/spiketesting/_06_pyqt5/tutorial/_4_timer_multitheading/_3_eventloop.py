import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.event_loop = QEventLoop()

        btn1 = QPushButton("button1", self)
        btn1.move(10, 10)
        btn1.clicked.connect(self.btn1_clicked)

        btn2 = QPushButton("button2", self)
        btn2.move(10, 40)
        btn2.clicked.connect(self.btn2_clicked)

        btn3 = QPushButton("button3", self)
        btn3.move(10, 70)
        btn3.clicked.connect(self.btn3_clicked)

    def btn1_clicked(self):
        print("before loop exec")
        self.event_loop.exec_()
        print("after loop exec")

    def btn2_clicked(self):
        print("before loop exit")
        self.event_loop.exit()
        print("after loop exit")
        time.sleep(5)
        print("after time sleep")

    def btn3_clicked(self):
        print("button3 clicked event")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()