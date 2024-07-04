import os
import sys
import cv2
import time
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


class DetectionThread(QtCore.QThread):
    frame_updated = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, parent=None):
        super(DetectionThread, self).__init__(parent)
        self._running = True
        self._paused = False
        self.mutex = QtCore.QMutex()
        self.pause_condition = QtCore.QWaitCondition()
        self.cap = cv2.VideoCapture(0)
        model_path = resource_path(config.DetectionModel)
        self.detection_model = load_model(model_path)
        self.category_index = label_map_util.create_category_index_from_labelmap(resource_path(config.LabelMap), use_display_name=True)
        self.valid_classes = config.ValidClasses
        self.tracker = initialize_tracker(embedder=config.DeepsortTracker)

    def run(self):
        while self._running:
            self.mutex.lock()
            if self._paused:
                self.pause_condition.wait(self.mutex)
            self.mutex.unlock()

            ret, frame = self.cap.read()
            if not ret:
                break
            output_dict = run_inference_for_single_image(self.detection_model, frame)
            detections, centers = prepare_detections(output_dict, self.valid_classes)
            tracks = self.tracker.update_tracks(detections, frame=frame)
            for track in tracks:
                if not track.is_confirmed():
                    continue
                track_id = track.track_id
                ltrb = track.to_ltrb()
                cv2.rectangle(frame, (int(ltrb[0]), int(ltrb[1])), (int(ltrb[2]), int(ltrb[3])), (0, 255, 0), 2)
                cv2.putText(frame, f'ID: {track_id}', (int(ltrb[0]), int(ltrb[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QtGui.QImage(frame.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.frame_updated.emit(q_image)
            time.sleep(0.01)

    def stop(self):
        self._running = False
        self.resume()  # Ensure thread is not paused when stopping

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


class VideoWidget(QtWidgets.QWidget, Ui_VideoWidget):
    def __init__(self):
        super(VideoWidget, self).__init__()
        self.setupUi(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'mainWindow'):
            self.mainWindow.update_image_position()


class ChatWidget(QtWidgets.QWidget, Ui_ChatWidget):
    def __init__(self):
        super(ChatWidget, self).__init__()
        self.setupUi(self)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

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

        # Main window button slots
        self.powerToggleButton.clicked.connect(self.toggle_detection_thread)

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
        self.detection_thread.start()
        QtCore.QCoreApplication.instance().aboutToQuit.connect(self.detection_thread.stop)
        self.toggle_power_button_design(False)

    def stop_detection_thread(self):
        if self.detection_thread:
            self.detection_thread.stop()
            self.detection_thread.wait()
            self.videoWidget.hide()
            self.toggle_power_button_design(True)

    def pause_detection_thread(self):
        if self.detection_thread:
            self.detection_thread.pause()
            self.videoWidget.hide()
            self.toggle_power_button_design(True)

    def resume_detection_thread(self):
        if self.detection_thread:
            self.detection_thread.resume()
            self.toggle_power_button_design(False)

    def toggle_detection_thread(self):
        if self.detection_thread and self.detection_thread.is_running():
            self.pause_detection_thread()
        else:
            self.resume_detection_thread()

    def toggle_power_button_design(self, activated):
        if activated:
            self.powerToggleButton.setStyleSheet("background-color: none; color: black;")
        else:
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


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
