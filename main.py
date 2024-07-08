import os
import sys
import cv2
import time
import numpy as np
import serial
import utills
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from model import load_model, run_inference_for_single_image, prepare_detections, initialize_tracker
from object_detection.utils import label_map_util
from pyqt5_ui.main_window import Ui_MainWindow
from pyqt5_ui.video_widget import Ui_VideoWidget
from pyqt5_ui.chat_widget import Ui_ChatWidget
from utills import resource_path
import config


class SerialThread(QtCore.QThread):
    def __init__(self, parent=None):
        super(SerialThread, self).__init__(parent)
        self._running = True
        self._paused = False
        self.mutex = QtCore.QMutex()
        self.pause_condition = QtCore.QWaitCondition()
        self.ser = None

    def run(self):
        if not self.ser:
            self.ser = serial.Serial(config.ComPort, config.BaudRate, timeout=1)
            time.sleep(2)  # Give some time for the connection to establish

        while self._running:
            self.mutex.lock()
            if self._paused:
                self.pause_condition.wait(self.mutex)
            self.mutex.unlock()

    def send_data(self, data):
        """Send data to the Arduino."""
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(data.encode())
                print(data)
            except serial.SerialException as e:
                print(f"Error sending data: {e}")

    def stop(self):
        self._running = False
        self.resume()  # Ensure thread is not paused when stopping
        if self.ser and self.ser.is_open:
            self.ser.close()

    def pause(self):
        self.mutex.lock()
        self._paused = True
        self.mutex.unlock()

    def resume(self):
        self.mutex.lock()
        self._paused = False
        self.mutex.unlock()
        self.pause_condition.wakeAll()


class DetectionThread(QtCore.QThread):
    frame_updated = QtCore.pyqtSignal(QtGui.QImage)
    update_data_signal = QtCore.pyqtSignal(object, int, int)  # Signal for updating data fields

    def __init__(self, parent=None, camera_index=0):
        super(DetectionThread, self).__init__(parent)
        self._running = True
        self._paused = False
        self.camera_index = camera_index
        self.mutex = QtCore.QMutex()
        self.pause_condition = QtCore.QWaitCondition()
        self.cap = cv2.VideoCapture(self.camera_index)
        model_path = resource_path(config.DetectionModel)
        self.detection_model = load_model(model_path)
        self.category_index = label_map_util.create_category_index_from_labelmap(resource_path(config.LabelMap), use_display_name=True)
        self.valid_classes = config.ValidClasses
        self.tracker = initialize_tracker(embedder=config.DeepsortTracker)
        self.serial_thread = SerialThread()
        self.send_signal = False  # Flag to control sending data to Arduino

    def run(self):
        # Check COM port connected.
        if utills.check_port(config.ComPort):
            self.serial_thread.start()
        while self._running:
            self.mutex.lock()
            if self._paused:
                self.pause_condition.wait(self.mutex)
            self.mutex.unlock()

            ret, frame = self.cap.read()
            if not ret:
                break
            output_dict = run_inference_for_single_image(self.detection_model, frame)
            detections, centers, scores, class_names = prepare_detections(output_dict, self.valid_classes, self.category_index)
            tracks = self.tracker.update_tracks(detections, frame=frame)
            """
            for track in tracks:
                if not track.is_confirmed():
                    continue
                track_id = track.track_id
                ltrb = track.to_ltrb()
                cv2.rectangle(frame, (int(ltrb[0]), int(ltrb[1])), (int(ltrb[2]), int(ltrb[3])), (0, 255, 0), 2)
                cv2.putText(frame, f'ID: {track_id}', (int(ltrb[0]), int(ltrb[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 1)
            """
            # Switch between algorithms
            if config.TargetAlgorithm == "M":
                # Mean Target
                mean_center_x = None
                mean_center_y = None
                # Draw center points
                for center in centers:
                    cv2.drawMarker(frame, center, (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=10, thickness=1, line_type=cv2.LINE_AA)
                # Calculate and draw the mean center point if there are any bounding boxes
                if centers:
                    mean_center_x = int(np.mean([center[0] for center in centers]))
                    mean_center_y = int(np.mean([center[1] for center in centers]))
                    mean_center = (mean_center_x, mean_center_y)
                    cv2.drawMarker(frame, mean_center, (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=1, line_type=cv2.LINE_AA)
                    cv2.putText(frame, f'M', (mean_center_x + 10, mean_center_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # Add the target ID
                for track in tracks:
                    if not track.is_confirmed():
                        continue

                    track_id = track.track_id
                    ltrb = track.to_ltrb()
                    x_center = int((ltrb[0] + ltrb[2]) / 2)
                    y_center = int((ltrb[1] + ltrb[3]) / 2)
                    cv2.putText(frame, f'F-ID: {track_id}', ((x_center + 10), (y_center - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                if self.send_signal:
                    self.serial_thread.send_data(f"{utills.calculate_angle('horizontal', mean_center_x, config.ImageTotalWidthPixels, config.ImageRealWidth, config.RealRadius)},{utills.calculate_angle('vertical', mean_center_y, config.ImageTotalHeightPixels, config.ImageRealHeight, config.RealRadius)}\n")
                self.update_data_signal.emit(", ".join(class_names), mean_center_x, mean_center_y)

            if config.TargetAlgorithm == "F":
                # First Seen Target
                first_track_id = None
                first_track_lost = False

                # Visualization
                for track in tracks:
                    if not track.is_confirmed():
                        continue

                    track_id = track.track_id
                    ltrb = track.to_ltrb()

                    # Track the first detected object
                    if first_track_id is None:
                        first_track_id = track_id

                    if track_id == first_track_id:
                        x_center = int((ltrb[0] + ltrb[2]) / 2)
                        y_center = int((ltrb[1] + ltrb[3]) / 2)
                        cv2.drawMarker(frame, (x_center, y_center), (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=1, line_type=cv2.LINE_AA)
                        cv2.putText(frame, f'F-ID: {track_id}', ((x_center + 10), (y_center - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                        if self.send_signal:
                            self.serial_thread.send_data(f"{utills.calculate_angle('horizontal', x_center, config.ImageTotalWidthPixels, config.ImageRealWidth, config.RealRadius)},{utills.calculate_angle('vertical', y_center, config.ImageTotalHeightPixels, config.ImageRealHeight, config.RealRadius)}\n")
                        self.update_data_signal.emit(", ".join(class_names), x_center, y_center)
                        first_track_lost = False
                        break
                else:
                    # No confirmed tracks found
                    if first_track_id is not None:
                        first_track_lost = True

                if first_track_lost:
                    first_track_id = None

            if config.TargetAlgorithm == "MR":
                # Most Recognizable Target
                # Select the highest score object
                if scores:
                    max_score_index = np.argmax(scores)
                    max_center = centers[max_score_index]
                    cv2.drawMarker(frame, max_center, (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=1, line_type=cv2.LINE_AA)
                    cv2.putText(frame, f'MR', ((max_center[0] + 10), (max_center[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    if self.send_signal:
                        self.serial_thread.send_data(f"{utills.calculate_angle('horizontal', max_center[0], config.ImageTotalWidthPixels, config.ImageRealWidth, config.RealRadius)},{utills.calculate_angle('vertical', max_center[1], config.ImageTotalHeightPixels, config.ImageRealHeight, config.RealRadius)}\n")
                    self.update_data_signal.emit(", ".join(class_names), max_center[0], max_center[1])

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QtGui.QImage(frame.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.frame_updated.emit(q_image)
            time.sleep(0.01)

    def stop(self):
        self._running = False
        self.resume()  # Ensure thread is not paused when stopping
        self.cap.release()
        self.set_send_signal(False)  # Ensure the serial connection is closed

    def pause(self):
        self.mutex.lock()
        self._paused = True
        self.mutex.unlock()

    def resume(self):
        self.mutex.lock()
        self._paused = False
        self.mutex.unlock()
        self.pause_condition.wakeAll()

    def is_running(self):
        return self._running and not self._paused

    def update_camera(self, camera_index):
        self.camera_index = camera_index
        self.cap.release()
        self.cap = cv2.VideoCapture(self.camera_index)

    def set_send_signal(self, state):
        self.send_signal = state


class VideoWidget(QtWidgets.QWidget, Ui_VideoWidget):
    def __init__(self):
        super(VideoWidget, self).__init__()
        self.setupUi(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resource_path("data/images/icons/favicon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'mainWindow'):
            self.mainWindow.update_image_position()


class ChatWidget(QtWidgets.QWidget, Ui_ChatWidget):
    def __init__(self):
        super(ChatWidget, self).__init__()
        self.setupUi(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resource_path("data/images/icons/favicon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        message_icon = QtGui.QIcon()
        message_icon.addPixmap(QtGui.QPixmap(resource_path("data/images/icons/send.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.messageButton.setIcon(message_icon)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resource_path("data/images/icons/favicon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(QtGui.QIcon(resource_path("data/images/icons/favicon.png")))

        power_icon = QtGui.QIcon()
        power_icon.addPixmap(QtGui.QPixmap(resource_path("data/images/icons/power.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.powerToggleButton.setIcon(power_icon)

        signal_icon = QtGui.QIcon()
        signal_icon.addPixmap(QtGui.QPixmap(resource_path("data/images/icons/signal.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.signalToggleButton.setIcon(signal_icon)

        refresh_icon = QtGui.QIcon()
        refresh_icon.addPixmap(QtGui.QPixmap(resource_path("data/images/icons/refresh.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.refreshCameraListButton.setIcon(refresh_icon)

        # Initialize the VideoWidget
        self.videoWidget = VideoWidget()
        self.videoWidget.hide()
        self.videoWidget.mainWindow = self

        # Initialize the ChatWidget
        self.chatWidget = ChatWidget()
        self.chatWidget.hide()

        # Connect the signals to slots of video widget toggle
        self.videoWidget.showEvent = self.on_video_widget_open

        # Startup actions
        self.setup_camera_view()
        self.start_detection_thread()
        self.pause_detection_thread()

        # Create the menu slots
        self.actionVideo_Panel.triggered.connect(self.open_video_widget)
        self.actionChat.triggered.connect(self.open_chat_widget)
        self.actionHelp.triggered.connect(self.open_github_readme)
        self.actionExit.triggered.connect(self.exit_app)

        # Main window button slots
        self.powerToggleButton.clicked.connect(self.toggle_detection_thread)
        self.signalToggleButton.clicked.connect(self.toggle_signal_output)
        self.refreshCameraListButton.clicked.connect(self.refresh_camera_list)
        self.cameraComboBox.currentIndexChanged.connect(self.change_camera)

        # Check COM port connected. If its not connected disable signalToggleButton button.
        if not utills.check_port(config.ComPort):
            self.signalToggleButton.setEnabled(False)

        # Initial camera list setup
        self.refresh_camera_list()
        self.targetAllRadioButton.toggled.connect(
            lambda checked: self.update_target_type([1, 44]) if checked else None)  # All Objects
        self.targetPeopleRadioButton.toggled.connect(
            lambda checked: self.update_target_type([1]) if checked else None)  # People
        self.targetDronesRadioButton.toggled.connect(
            lambda checked: self.update_target_type([44]) if checked else None)  # Bottles
        self.targetAllRadioButton.setChecked(True)

        # Targeting algorithm / position type
        self.meanTargetAlgorithmRadioButton.toggled.connect(
            lambda checked: self.update_target_algorithm_type('M') if checked else None)  # Mean Target
        self.firstTargetAlgorithmRadioButton.toggled.connect(
            lambda checked: self.update_target_algorithm_type('F') if checked else None)  # First Target
        self.mostRecognizableTargetAlgorithmRadioButton.toggled.connect(
            lambda checked: self.update_target_algorithm_type('MR') if checked else None)  # Most Recognizable Target
        self.meanTargetAlgorithmRadioButton.setChecked(True)

    @staticmethod
    def update_target_type(value):
        config.ValidClasses = value

    @staticmethod
    def update_target_algorithm_type(value):
        config.TargetAlgorithm = value

    def update_data_fields(self, objects, x, y):
        self.objectLineEdit.setText(objects)
        self.xLineEdit.setText(utills.set_text(x))
        self.yLineEdit.setText(utills.set_text(y))

    def open_video_widget(self):
        if not self.videoWidget.isVisible():
            self.videoWidget.show()
            self.videoWidget.raise_()

    def on_video_widget_open(self, event):
        self.resume_detection_thread()
        super().showEvent(event)

    def open_chat_widget(self):
        if not self.chatWidget.isVisible():
            self.chatWidget.show()
            self.chatWidget.raise_()

    @staticmethod
    def open_github_readme():
        url = QUrl(config.HelpURL)
        QDesktopServices.openUrl(url)

    @staticmethod
    def exit_app():
        QtWidgets.QApplication.quit()

    def setup_camera_view(self):
        self.aspectRatio = config.InputStreamAspectRatio
        self.scene = QtWidgets.QGraphicsScene(self)
        self.videoWidget.cameraGraphicsView.setScene(self.scene)
        self.videoWidget.cameraGraphicsView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.videoWidget.cameraGraphicsView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.videoWidget.cameraGraphicsView.setStyleSheet("background: black; border: none")
        self.videoWidget.cameraGraphicsView.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.scene.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.transparent))

    def start_detection_thread(self):
        self.detection_thread = DetectionThread()
        self.detection_thread.frame_updated.connect(self.update_frame)
        self.detection_thread.update_data_signal.connect(self.update_data_fields)
        self.detection_thread.start()
        QtCore.QCoreApplication.instance().aboutToQuit.connect(self.detection_thread.stop)
        self.toggle_power_button(False)

    def stop_detection_thread(self):
        if self.detection_thread:
            self.cameraComboBox.setEnabled(False)
            self.refreshCameraListButton.setEnabled(False)
            self.targetAllRadioButton.setEnabled(False)
            self.targetPeopleRadioButton.setEnabled(False)
            self.targetDronesRadioButton.setEnabled(False)
            self.meanTargetAlgorithmRadioButton.setEnabled(False)
            self.firstTargetAlgorithmRadioButton.setEnabled(False)
            self.mostRecognizableTargetAlgorithmRadioButton.setEnabled(False)
            self.detection_thread.stop()
            self.detection_thread.wait()
            self.videoWidget.hide()
            self.toggle_power_button(True)
            self.detection_thread.set_send_signal(False)

    def pause_detection_thread(self):
        if self.detection_thread:
            self.detection_thread.pause()
            self.videoWidget.hide()
            self.toggle_power_button(True)
            self.detection_thread.set_send_signal(False)

    def resume_detection_thread(self):
        if self.detection_thread:
            self.detection_thread.resume()
            self.toggle_power_button(False)

    def toggle_detection_thread(self):
        if self.detection_thread and self.detection_thread.is_running():
            self.pause_detection_thread()
        else:
            self.resume_detection_thread()

    def toggle_signal_output(self):
        if self.detection_thread.send_signal:
            self.detection_thread.set_send_signal(False)
            self.signalToggleButton.setStyleSheet("background-color: none; color: black;")
        else:
            self.detection_thread.set_send_signal(True)
            self.signalToggleButton.setStyleSheet("background-color: #36d13c; color: white;")

    def toggle_power_button(self, activated):
        if activated:
            self.cameraComboBox.setEnabled(True)
            self.refreshCameraListButton.setEnabled(True)
            self.targetAllRadioButton.setEnabled(True)
            self.targetPeopleRadioButton.setEnabled(True)
            self.targetDronesRadioButton.setEnabled(True)
            self.meanTargetAlgorithmRadioButton.setEnabled(True)
            self.firstTargetAlgorithmRadioButton.setEnabled(True)
            self.mostRecognizableTargetAlgorithmRadioButton.setEnabled(True)
            self.powerToggleButton.setStyleSheet("background-color: none; color: black;")
        else:
            self.cameraComboBox.setEnabled(False)
            self.refreshCameraListButton.setEnabled(False)
            self.targetAllRadioButton.setEnabled(False)
            self.targetPeopleRadioButton.setEnabled(False)
            self.targetDronesRadioButton.setEnabled(False)
            self.meanTargetAlgorithmRadioButton.setEnabled(False)
            self.firstTargetAlgorithmRadioButton.setEnabled(False)
            self.mostRecognizableTargetAlgorithmRadioButton.setEnabled(False)
            self.powerToggleButton.setStyleSheet("background-color: #36d13c; color: white;")

    def update_frame(self, q_image):
        pixmap = QtGui.QPixmap.fromImage(q_image)
        self.aspectRatio = pixmap.width() / pixmap.height()
        self.scene.clear()
        self.image_item = self.scene.addPixmap(pixmap)
        self.videoWidget.cameraGraphicsView.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.update_image_position()

    def update_image_position(self):
        if hasattr(self, 'image_item') and self.image_item:
            view_size = self.videoWidget.cameraGraphicsView.size()
            if view_size.width() / view_size.height() > self.aspectRatio:
                new_height = view_size.height()
                new_width = int(new_height * self.aspectRatio)
            else:
                new_width = view_size.width()
                new_height = int(new_width / self.aspectRatio)
            scaled_pixmap = self.image_item.pixmap().scaled(
                new_width, new_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.image_item.setPixmap(scaled_pixmap)
            self.image_item.setOffset(-new_width / 2, -new_height / 2)
            self.image_item.setPos(view_size.width() / 2, view_size.height() / 2)
            self.videoWidget.cameraGraphicsView.setSceneRect(0, 0, view_size.width(), view_size.height())

    def refresh_camera_list(self):
        self.cameraComboBox.clear()
        cameras = self.get_connected_cameras()
        for camera in cameras:
            self.cameraComboBox.addItem(camera)
        if cameras:
            self.cameraComboBox.setCurrentIndex(0)

    def change_camera(self):
        selected_index = self.cameraComboBox.currentIndex()
        self.detection_thread.update_camera(selected_index)

    @staticmethod
    def get_connected_cameras():
        cameras = []
        index = 0
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            else:
                cameras.append(f"Camera {index}")
            cap.release()
            index += 1
        return cameras


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
