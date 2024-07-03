from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import cv2
import time
from model import load_model, run_inference_for_single_image, prepare_detections, initialize_tracker
from object_detection.utils import label_map_util
from pyqt5_ui.main_window import Ui_MainWindow
from pyqt5_ui.video_widget import Ui_VideoWidget
from pyqt5_ui.chat_widget import Ui_ChatWidget


class DetectionThread(QtCore.QThread):
    frame_updated = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, parent=None):
        super(DetectionThread, self).__init__(parent)
        self.keep_running = True
        self.cap = cv2.VideoCapture(0)
        self.detection_model = load_model("data/models/ssd_mobilenet_v2_320x320_coco17_tpu-8/saved_model")
        self.category_index = label_map_util.create_category_index_from_labelmap("data/label_maps/mscoco_label_map.pbtxt", use_display_name=True)
        self.valid_classes = [1]
        self.tracker = initialize_tracker(embedder='mobilenet')

    def run(self):
        while self.keep_running:
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
                cv2.putText(frame, f'ID: {track_id}', (int(ltrb[0]), int(ltrb[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QtGui.QImage(frame.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.frame_updated.emit(q_image)
            time.sleep(0.01)

    def stop(self):
        self.keep_running = False
        self.cap.release()


class VideoWidget(QtWidgets.QWidget, Ui_VideoWidget):
    def __init__(self):
        super(VideoWidget, self).__init__()
        self.setupUi(self)


class ChatWidget(QtWidgets.QWidget, Ui_ChatWidget):
    def __init__(self):
        super(ChatWidget, self).__init__()
        self.setupUi(self)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # Initialize the widgets
        self.videoWidget = VideoWidget()
        self.chatWidget = ChatWidget()

        # Startup actions
        self.setup_camera_view()
        self.start_detection_thread()
        self.connect_buttons()

        # Create the menu slots
        self.actionVideo_Panel.triggered.connect(self.open_video_widget)
        self.actionChat.triggered.connect(self.open_chat_widget)

    def open_video_widget(self):
        if self.videoWidget.isVisible():
            self.videoWidget.show()
        else:
            self.videoWidget.show()

    def open_chat_widget(self):
        if self.chatWidget.isVisible():
            self.chatWidget.show()
        else:
            self.chatWidget.show()

    def setup_camera_view(self):
        self.aspectRatio = 4 / 3
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

    def connect_buttons(self):
        # self.stopButton.clicked.connect(self.stop_detection)
        # self.pauseButton.clicked.connect(self.pause_video)
        pass

    def stop_detection(self):
        self.detection_thread.stop()

    def update_frame(self, q_image):
        pixmap = QtGui.QPixmap.fromImage(q_image)
        self.aspectRatio = pixmap.width() / pixmap.height()
        self.scene.clear()
        self.image_item = self.scene.addPixmap(pixmap)
        self.videoWidget.cameraGraphicsView.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.update_image_position()

    def resizeEvent(self, event):
        super().resizeEvent(event)
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
