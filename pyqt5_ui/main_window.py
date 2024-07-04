# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyqt5_ui/main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(380, 242)
        MainWindow.setMinimumSize(QtCore.QSize(380, 0))
        MainWindow.setMaximumSize(QtCore.QSize(440, 242))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("pyqt5_ui\\../data/images/icons/favicon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setToolTip("")
        MainWindow.setDockNestingEnabled(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setMaximumSize(QtCore.QSize(16777215, 64))
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.powerToggleButton = QtWidgets.QPushButton(self.groupBox_3)
        self.powerToggleButton.setMinimumSize(QtCore.QSize(31, 31))
        self.powerToggleButton.setMaximumSize(QtCore.QSize(31, 31))
        self.powerToggleButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("pyqt5_ui\\../data/images/icons/power.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.powerToggleButton.setIcon(icon1)
        self.powerToggleButton.setObjectName("powerToggleButton")
        self.horizontalLayout.addWidget(self.powerToggleButton)
        self.signalToggleButton = QtWidgets.QPushButton(self.groupBox_3)
        self.signalToggleButton.setMinimumSize(QtCore.QSize(31, 31))
        self.signalToggleButton.setMaximumSize(QtCore.QSize(31, 31))
        self.signalToggleButton.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("pyqt5_ui\\../data/images/icons/signal.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.signalToggleButton.setIcon(icon2)
        self.signalToggleButton.setObjectName("signalToggleButton")
        self.horizontalLayout.addWidget(self.signalToggleButton)
        self.cameraComboBox = QtWidgets.QComboBox(self.groupBox_3)
        self.cameraComboBox.setMinimumSize(QtCore.QSize(0, 31))
        self.cameraComboBox.setMaximumSize(QtCore.QSize(16777215, 31))
        self.cameraComboBox.setCurrentText("")
        self.cameraComboBox.setIconSize(QtCore.QSize(16, 16))
        self.cameraComboBox.setObjectName("cameraComboBox")
        self.cameraComboBox.addItem("")
        self.cameraComboBox.addItem("")
        self.cameraComboBox.addItem("")
        self.horizontalLayout.addWidget(self.cameraComboBox)
        self.refreshCameraListButton = QtWidgets.QPushButton(self.groupBox_3)
        self.refreshCameraListButton.setMinimumSize(QtCore.QSize(31, 31))
        self.refreshCameraListButton.setMaximumSize(QtCore.QSize(31, 31))
        self.refreshCameraListButton.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("pyqt5_ui\\../data/images/icons/refresh.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.refreshCameraListButton.setIcon(icon3)
        self.refreshCameraListButton.setObjectName("refreshCameraListButton")
        self.horizontalLayout.addWidget(self.refreshCameraListButton)
        self.verticalLayout_3.addWidget(self.groupBox_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.allObjectRadioButton = QtWidgets.QRadioButton(self.groupBox)
        self.allObjectRadioButton.setChecked(False)
        self.allObjectRadioButton.setObjectName("allObjectRadioButton")
        self.verticalLayout.addWidget(self.allObjectRadioButton)
        self.peopleObjectRadioButton = QtWidgets.QRadioButton(self.groupBox)
        self.peopleObjectRadioButton.setObjectName("peopleObjectRadioButton")
        self.verticalLayout.addWidget(self.peopleObjectRadioButton)
        self.dronesObjectRadioButton = QtWidgets.QRadioButton(self.groupBox)
        self.dronesObjectRadioButton.setObjectName("dronesObjectRadioButton")
        self.verticalLayout.addWidget(self.dronesObjectRadioButton)
        self.horizontalLayout_5.addWidget(self.groupBox)
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.meanTargetRadioButton = QtWidgets.QRadioButton(self.groupBox_4)
        self.meanTargetRadioButton.setChecked(False)
        self.meanTargetRadioButton.setObjectName("meanTargetRadioButton")
        self.verticalLayout_4.addWidget(self.meanTargetRadioButton)
        self.firstTargetRadioButton = QtWidgets.QRadioButton(self.groupBox_4)
        self.firstTargetRadioButton.setObjectName("firstTargetRadioButton")
        self.verticalLayout_4.addWidget(self.firstTargetRadioButton)
        self.mostRecognizableTargetRadioButton = QtWidgets.QRadioButton(self.groupBox_4)
        self.mostRecognizableTargetRadioButton.setObjectName("mostRecognizableTargetRadioButton")
        self.verticalLayout_4.addWidget(self.mostRecognizableTargetRadioButton)
        self.horizontalLayout_5.addWidget(self.groupBox_4)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setMinimumSize(QtCore.QSize(31, 0))
        self.label.setMaximumSize(QtCore.QSize(31, 16777215))
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.objectLineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.objectLineEdit.setReadOnly(True)
        self.objectLineEdit.setObjectName("objectLineEdit")
        self.horizontalLayout_2.addWidget(self.objectLineEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setMinimumSize(QtCore.QSize(31, 0))
        self.label_2.setMaximumSize(QtCore.QSize(31, 16777215))
        self.label_2.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.xLineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.xLineEdit.setObjectName("xLineEdit")
        self.horizontalLayout_3.addWidget(self.xLineEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setMinimumSize(QtCore.QSize(31, 0))
        self.label_3.setMaximumSize(QtCore.QSize(31, 16777215))
        self.label_3.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.yLineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.yLineEdit.setObjectName("yLineEdit")
        self.horizontalLayout_4.addWidget(self.yLineEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5.addWidget(self.groupBox_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 380, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuEDit = QtWidgets.QMenu(self.menubar)
        self.menuEDit.setObjectName("menuEDit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionCHat = QtWidgets.QAction(MainWindow)
        self.actionCHat.setObjectName("actionCHat")
        self.actionVideo = QtWidgets.QAction(MainWindow)
        self.actionVideo.setObjectName("actionVideo")
        self.actionVideo_Panel = QtWidgets.QAction(MainWindow)
        self.actionVideo_Panel.setObjectName("actionVideo_Panel")
        self.actionChat = QtWidgets.QAction(MainWindow)
        self.actionChat.setObjectName("actionChat")
        self.actionHelp = QtWidgets.QAction(MainWindow)
        self.actionHelp.setObjectName("actionHelp")
        self.actionClear_Recordings = QtWidgets.QAction(MainWindow)
        self.actionClear_Recordings.setObjectName("actionClear_Recordings")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuView.addAction(self.actionVideo_Panel)
        self.menuView.addAction(self.actionChat)
        self.menuHelp.addAction(self.actionHelp)
        self.menuEDit.addAction(self.actionClear_Recordings)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEDit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ASAM System"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Controls"))
        self.powerToggleButton.setToolTip(_translate("MainWindow", "Toggle Power"))
        self.signalToggleButton.setToolTip(_translate("MainWindow", "Toggle Serial Signal"))
        self.cameraComboBox.setToolTip(_translate("MainWindow", "Select Camera"))
        self.cameraComboBox.setPlaceholderText(_translate("MainWindow", "Select Camera"))
        self.cameraComboBox.setItemText(0, _translate("MainWindow", "Select Camera"))
        self.cameraComboBox.setItemText(1, _translate("MainWindow", "Camera 1"))
        self.cameraComboBox.setItemText(2, _translate("MainWindow", "Camera 2"))
        self.refreshCameraListButton.setToolTip(_translate("MainWindow", "Toggle Serial Signal"))
        self.groupBox.setTitle(_translate("MainWindow", "Track Objects"))
        self.allObjectRadioButton.setText(_translate("MainWindow", "All"))
        self.peopleObjectRadioButton.setText(_translate("MainWindow", "People"))
        self.dronesObjectRadioButton.setText(_translate("MainWindow", "Drones"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Target Type"))
        self.meanTargetRadioButton.setText(_translate("MainWindow", "Mean"))
        self.firstTargetRadioButton.setText(_translate("MainWindow", "First"))
        self.mostRecognizableTargetRadioButton.setText(_translate("MainWindow", "Most Recognizable"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Target"))
        self.label.setText(_translate("MainWindow", "Object"))
        self.label_2.setText(_translate("MainWindow", "X"))
        self.label_3.setText(_translate("MainWindow", "Y"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.menuEDit.setTitle(_translate("MainWindow", "Edit"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionCHat.setText(_translate("MainWindow", "Summarize"))
        self.actionVideo.setText(_translate("MainWindow", "Video"))
        self.actionVideo_Panel.setText(_translate("MainWindow", "Video"))
        self.actionChat.setText(_translate("MainWindow", "Chat"))
        self.actionHelp.setText(_translate("MainWindow", "Manual"))
        self.actionClear_Recordings.setText(_translate("MainWindow", "Clear Recordings"))
