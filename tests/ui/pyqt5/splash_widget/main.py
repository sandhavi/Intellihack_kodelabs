import sys
from PyQt5 import QtWidgets, QtGui
from splash_screen import SplashScreen  # Import the generated SplashScreen class
from main_window import MainWindow  # Import the MainWindow class from your main_window.py

def main():
    app = QtWidgets.QApplication(sys.argv)

    # Create and show the splash screen
    splash_screen = SplashScreen()
    splash_screen.show()

    # Initialize MainWindow
    main_window = MainWindow()

    # Define a slot to close the splash screen
    def close_splash():
        splash_screen.close()

    # Connect the main window's signal to close the splash screen
    main_window.initialized.connect(close_splash)

    # Show the main window
    main_window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
