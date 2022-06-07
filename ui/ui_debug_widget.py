# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'debug_widget.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DebugWidget(object):
    def setupUi(self, DebugWidget):
        DebugWidget.setObjectName("DebugWidget")
        DebugWidget.resize(379, 346)
        DebugWidget.setStyleSheet("")
        self.gridLayout = QtWidgets.QGridLayout(DebugWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(DebugWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tabWidget.setStyleSheet("")
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.East)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabBarAutoHide(True)
        self.tabWidget.setObjectName("tabWidget")
        self.watchesTab = QtWidgets.QWidget()
        self.watchesTab.setObjectName("watchesTab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.watchesTab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.addWatchButton = QtWidgets.QPushButton(self.watchesTab)
        self.addWatchButton.setEnabled(False)
        self.addWatchButton.setObjectName("addWatchButton")
        self.gridLayout_2.addWidget(self.addWatchButton, 0, 1, 1, 1)
        self.itemWatchTabs = QtWidgets.QTabWidget(self.watchesTab)
        self.itemWatchTabs.setStyleSheet("")
        self.itemWatchTabs.setTabPosition(QtWidgets.QTabWidget.South)
        self.itemWatchTabs.setDocumentMode(True)
        self.itemWatchTabs.setTabsClosable(True)
        self.itemWatchTabs.setMovable(True)
        self.itemWatchTabs.setTabBarAutoHide(False)
        self.itemWatchTabs.setObjectName("itemWatchTabs")
        self.gridLayout_2.addWidget(self.itemWatchTabs, 1, 0, 1, 2)
        self.tabWidget.addTab(self.watchesTab, "")
        self.eventsTab = QtWidgets.QWidget()
        self.eventsTab.setObjectName("eventsTab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.eventsTab)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.eventsList = QtWidgets.QListWidget(self.eventsTab)
        self.eventsList.setStyleSheet("")
        self.eventsList.setObjectName("eventsList")
        self.gridLayout_3.addWidget(self.eventsList, 0, 0, 1, 1)
        self.tabWidget.addTab(self.eventsTab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(DebugWidget)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DebugWidget)

    def retranslateUi(self, DebugWidget):
        _translate = QtCore.QCoreApplication.translate
        DebugWidget.setWindowTitle(_translate("DebugWidget", "Form"))
        self.addWatchButton.setText(_translate("DebugWidget", "Add Watch"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.watchesTab), _translate("DebugWidget", "Watches"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.eventsTab), _translate("DebugWidget", "Events"))

