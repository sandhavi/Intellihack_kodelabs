from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import cv2
import time
from model import load_model, run_inference_for_single_image, prepare_detections, initialize_tracker
from object_detection.utils import label_map_util
from ui import Ui_MainWindow


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
                cv2.putText(frame, f'ID: {track_id}', (int(ltrb[0]), int(ltrb[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QtGui.QImage(frame.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.frame_updated.emit(q_image)
            time.sleep(0.01)

    def stop(self):
        self.keep_running = False
        self.cap.release()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setup_camera_view()
        self.start_detection_thread()
        self.connect_buttons()

    def setup_camera_view(self):
        self.aspectRatio = 4 / 3
        self.scene = QtWidgets.QGraphicsScene(self)
        self.cameraView.setScene(self.scene)
        self.cameraView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.cameraView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.cameraView.setStyleSheet("background: black; border: none")
        self.cameraView.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.scene.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.transparent))

    def start_detection_thread(self):
        self.detection_thread = DetectionThread()
        self.detection_thread.frame_updated.connect(self.update_frame)
        self.detection_thread.start()
        QtCore.QCoreApplication.instance().aboutToQuit.connect(self.detection_thread.stop)

    def connect_buttons(self):
        self.stopButton.clicked.connect(self.stop_detection)
        self.recordButton.clicked.connect(self.record_video)
        self.pauseButton.clicked.connect(self.pause_video)

    def stop_detection(self):
        self.detection_thread.stop()

    def record_video(self):
        # Implement video recording functionality
        pass

    def pause_video(self):
        # Implement video pause functionality
        pass

    def update_frame(self, q_image):
        pixmap = QtGui.QPixmap.fromImage(q_image)
        self.aspectRatio = pixmap.width() / pixmap.height()
        self.scene.clear()
        self.image_item = self.scene.addPixmap(pixmap)
        self.cameraView.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.update_image_position()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image_position()

    def update_image_position(self):
        if hasattr(self, 'image_item') and self.image_item:
            view_size = self.cameraView.size()
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
            self.cameraView.setSceneRect(0, 0, view_size.width(), view_size.height())

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
