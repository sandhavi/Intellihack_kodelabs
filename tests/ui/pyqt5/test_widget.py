from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QWidget, QVBoxLayout, QLabel, QPushButton
import sys


class SubWindow(QWidget):
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

        # Initialize the reference to widgets
        self.sw = SubWindow()

        # Main window content
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

    def open_sub_window(self):
        if self.sw.isVisible():
            # Bring the existing sub-window to the front
            self.sw.show()
        else:
            self.sw.show()

    def on_sub_window_closed(self):
        # Reset the reference when the sub-window is closed
        self.sw.hide()


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
