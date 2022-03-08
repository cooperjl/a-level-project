from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (QSlider, QFrame, QHBoxLayout, 
        QPushButton, QSizePolicy, QAbstractSlider, QLabel)


class ZoomBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.layout = QHBoxLayout()

        self.layout.setContentsMargins(0, 0, 9, 0)

        self.zoomslider = ZoomSlider()
        self.minusbutton = QPushButton('-', self)
        self.plusbutton = QPushButton('+', self)
        self.percent = QLabel('100.0%')

        self.minusbutton.setFixedSize(QSize(20, 20))
        self.plusbutton.setFixedSize(QSize(20, 20))

        self.layout.addWidget(self.percent)
        self.layout.addWidget(self.minusbutton)
        self.layout.addWidget(self.zoomslider)
        self.layout.addWidget(self.plusbutton)

        self.minusbutton.clicked.connect(self.zoom_out_event)
        self.plusbutton.clicked.connect(self.zoom_in_event)
        self.zoomslider.valueChanged.connect(self.update_text)
        self.setLayout(self.layout)

        self.zoom_percent = 100
        self.zoom_level = 0

    def zoom_in_event(self):
        self.zoomslider.triggerAction(QAbstractSlider.SliderSingleStepAdd)
    
    def zoom_out_event(self):
        self.zoomslider.triggerAction(QAbstractSlider.SliderSingleStepSub)

    def update_text(self, level):
        level -= 7 # level from bar is always positive but functions use 0 as the middle
        diff = level - self.zoom_level
        self.zoom_level += diff
        self.zoom_percent *= 2**diff
        self.percent.setText(f"{self.zoom_percent}%")


class ZoomSlider(QSlider):
    def __init__(self):
        super().__init__(Qt.Horizontal)
       # self.setTickPosition(QSlider.TicksBelow)
        self.setTickInterval(1)
        self.setRange(0, 14)
        self.setSliderPosition(7)  
