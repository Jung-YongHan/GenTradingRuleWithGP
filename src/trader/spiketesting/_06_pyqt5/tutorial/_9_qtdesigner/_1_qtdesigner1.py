# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import QRect, QMetaObject, QCoreApplication, Qt
from PyQt5.QtWidgets import QAction, QWidget, QTabWidget, QMenuBar, QMenu, QStatusBar, QApplication, QMainWindow, \
    QHBoxLayout, QVBoxLayout, QTableView, QSlider, QSpacerItem, QSizePolicy, QPushButton


################################################################################
## Form generated from reading UI file 'micro_candle_analyzerqBqxio.ui'
##
## Created by: Qt User Interface Compiler version 5.14.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################



class Ui_MainWindow(QMainWindow):
    def setupUi(self) :

        self.resize(720, 587)

        self.action_Exit = QAction(self)
        self.action_Exit.setObjectName(u"action_Exit")
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName(u"centralwidget")
        self.market_tabs = QTabWidget(self.centralwidget)
        self.market_tabs.setObjectName(u"market_tabs")
        self.market_tabs.setGeometry(QRect(0, -1, 801, 581))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")

        ####################################################
        ##
        self.tab_body_layout = QWidget(self.tab)
        self.tab_body_layout.setGeometry(QRect(40, 50, 621, 471))

        self.top_layout = QVBoxLayout(self.tab_body_layout)
        self.tab_body_layout.setLayout(self.top_layout)
        top_ = QHBoxLayout()

        self.big_ctrl_slider = QSlider()
        self.big_ctrl_slider.setOrientation(Qt.Horizontal)
        top_.addWidget(self.big_ctrl_slider)

        btn2 = QPushButton()
        btn2.setText('Button&2')
        top_.addWidget(btn2)


        self.body_layout = QHBoxLayout()

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tableView = QTableView(self.tab_body_layout)
        self.tableView.setObjectName(u"tableView")

        self.verticalLayout_2.addWidget(self.tableView)

        self.horizontalSlider = QSlider(self.tab_body_layout)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setOrientation(Qt.Horizontal)

        self.verticalLayout_2.addWidget(self.horizontalSlider)

        self.top_layout.addLayout(self.verticalLayout_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.top_layout.addItem(self.verticalSpacer)

        self.horizontalSlider_2 = QSlider(self.tab_body_layout)
        self.horizontalSlider_2.setObjectName(u"horizontalSlider_2")
        self.horizontalSlider_2.setOrientation(Qt.Horizontal)

        self.top_layout.addWidget(self.horizontalSlider_2)

        self.tableView_2 = QTableView(self.tab_body_layout)
        self.tableView_2.setObjectName(u"tableView_2")

        self.top_layout.addWidget(self.tableView_2)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")

        self.top_layout.addLayout(self.verticalLayout_6)

        self.market_tabs.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.market_tabs.addTab(self.tab_2, "")
        self.setCentralWidget(self.centralwidget)

        self.menubar = QMenuBar(self)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 720, 22))
        self.menuMicro_Candle_Analyzer = QMenu(self.menubar)
        self.menuMicro_Candle_Analyzer.setObjectName(u"menuMicro_Candle_Analyzer")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName(u"statusbar")
        self.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuMicro_Candle_Analyzer.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuMicro_Candle_Analyzer.addSeparator()
        self.menuMicro_Candle_Analyzer.addAction(self.action_Exit)

        self.retranslateUi()

        self.market_tabs.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(self)

    # setupUi

    def retranslateUi(self) :
        self.setWindowTitle(QCoreApplication.translate("MainWindow", u"Micro Candle Analyzer", None))
        self.action_Exit.setText(QCoreApplication.translate("MainWindow", u"&Exit", None))
        self.market_tabs.setTabText(self.market_tabs.indexOf(self.tab),
                                    QCoreApplication.translate("MainWindow", u"KRW-BTC", None))
        self.market_tabs.setTabText(self.market_tabs.indexOf(self.tab_2),
                                    QCoreApplication.translate("MainWindow", u"Tab 2", None))
        self.menuMicro_Candle_Analyzer.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = Ui_MainWindow()
    mywindow.setupUi()
    mywindow.show()
    app.exec_()