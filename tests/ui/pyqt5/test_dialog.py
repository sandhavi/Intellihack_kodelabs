from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QWidget, QVBoxLayout, QLabel, QMenuBar, QDialog, \
    QPushButton


class SubWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sub Window')
        layout = QVBoxLayout()
        label = QLabel('This is the sub-window.')
        layout.addWidget(label)
        close_button = QPushButton('Close')
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 800, 600)

        # Create the menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')

        # Create the menu item
        open_subwindow_action = QAction('Open Sub Window', self)
        open_subwindow_action.triggered.connect(self.open_sub_window)
        file_menu.addAction(open_subwindow_action)

        # Main window content
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

    def open_sub_window(self):
        # Create and show the sub-window
        self.sub_window = SubWindow()
        self.sub_window.exec_()  # Use exec_() to show as modal dialog or show() for non-modal


def main():
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
