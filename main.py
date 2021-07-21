import sys
import cv2
from collections import deque
from multiprocessing.pool import ThreadPool
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from ui_window import *

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.color = (255, 255, 255)
        self.stroke = 3

        self.timer = QTimer()
        self.timer.timeout.connect(self.viewCam1)
        self.timer.timeout.connect(self.viewCam2)
        self.timer.timeout.connect(self.viewCam3)
        self.ui.btnStart.clicked.connect(self.startFunc)

    def process_frame1(self,frame):
        return frame

    def process_frame2(self,frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_rects = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in face_rects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Unknown", (x, y - 6), self.font, 2, self.color, self.stroke, cv2.LINE_AA)
        return frame

    def process_frame3(self,frame):
        diff = frame #cv2.absdiff(frame, self.frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = gray #cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            if cv2.contourArea(contour) < 700:
                continue
            else:
                gray = cv2.medianBlur(gray, 7)
                # frame = cv2.GaussianBlur(frame, 7)
                cv2.rectangle(gray, (x, y), (x + w, y + h), (0, 255, 0), 4)
        return gray

    def startFunc(self):
        if not self.timer.isActive():
            self.cap = cv2.VideoCapture(0)
            self.timer.start(0)

            self.thread_num = cv2.getNumberOfCPUs()
            self.thread_num_queue = int(self.thread_num / 4)
            print(self.thread_num,self.thread_num_queue, int(6/4))
            self.pool1 = ThreadPool(processes=self.thread_num_queue)
            self.pending_task1 = deque()
            self.pool2 = ThreadPool(processes=self.thread_num_queue)
            self.pending_task2 = deque()
            self.pool3 = ThreadPool(processes=self.thread_num_queue*2)
            self.pending_task3 = deque()

            self.ui.btnStart.setText("Stop")
        else:
            self.timer.stop()
            self.cap.release()
            self.ui.btnStart.setText("Start")

    def viewCam1(self):

        while len(self.pending_task1) > 0 and self.pending_task1[0].ready():
            image = self.pending_task1.popleft().get()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, channel = image.shape
            step = channel * width
            qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
            qImg = qImg.scaled(480, 270, QtCore.Qt.KeepAspectRatio)
            self.ui.image_label1.setPixmap(QPixmap.fromImage(qImg))
            # Populate queue 2.
            if len(self.pending_task2) < self.thread_num_queue:
                task2 = self.pool2.apply_async(self.process_frame2, (image.copy(),))
                self.pending_task2.append(task2)
            # Populate queue 3.
            if len(self.pending_task3) < self.thread_num_queue:
                task3 = self.pool3.apply_async(self.process_frame3, (image.copy(),))
                self.pending_task3.append(task3)
        # Populate queue 1.
        if len(self.pending_task1) < self.thread_num_queue:
            frame_got, frame = self.cap.read()
            if frame_got:
                task1 = self.pool1.apply_async(self.process_frame1, (frame.copy(),))
                self.pending_task1.append(task1)

    def viewCam2(self):
        while len(self.pending_task2) > 0 and self.pending_task2[0].ready():
            image = self.pending_task2.popleft().get()
            height, width, channel = image.shape
            step = channel * width
            qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
            qImg = qImg.scaled(480, 270, QtCore.Qt.KeepAspectRatio)
            self.ui.image_label2.setPixmap(QPixmap.fromImage(qImg))

    def viewCam3(self):
        while len(self.pending_task3) > 0 and self.pending_task3[0].ready():
            image = self.pending_task3.popleft().get()
            # height, width, channel = image.shape
            # step = channel * width
            # qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
            height, width = image.shape
            step = 1 * width
            qImg = QImage(image.data, width, height, step, QImage.Format_Grayscale8)
            qImg = qImg.scaled(480, 270, QtCore.Qt.KeepAspectRatio)
            self.ui.image_label3.setPixmap(QPixmap.fromImage(qImg))

if __name__ == '__main__':

    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())