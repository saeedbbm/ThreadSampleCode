from PyQt5 import QtCore, QtWidgets
import numpy as np
import os
class Ui_Form(object):
    def setupUi(self, Form):
        Form.resize(525, 386)

        self.layout = QtWidgets.QGridLayout(Form)

        self.image_label2 = QtWidgets.QLabel(Form)
        self.image_label2.setStyleSheet("background-color: black; border: 1px solid black;")
        self.image_label2.setFixedSize(480,270)
        self.layout.addWidget(self.image_label2,0,0)

        self.image_label1 = QtWidgets.QLabel()
        self.image_label1.setStyleSheet("background-color: black; border: 1px solid black;")
        self.image_label1.setFixedSize(480, 270)
        self.layout.addWidget(self.image_label1, 0, 1)

        self.image_label3 = QtWidgets.QLabel()
        self.image_label3.setStyleSheet("background-color: black; border: 1px solid black;")
        self.image_label3.setFixedSize(480, 270)
        self.layout.addWidget(self.image_label3, 0, 2)

        self.btnStart = QtWidgets.QPushButton(Form)
        self.btnStart.setText("Start")
        self.layout.addWidget(self.btnStart,1,1)

        Form.setLayout(self.layout)