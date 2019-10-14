import sys
import os
import cv2
import json
from glob import glob
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QLabel, QDesktopWidget, QMessageBox, QCheckBox
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QColor, QPen, QFont
from PyQt5.QtCore import QRect, QPoint

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        mainWidget = MainWidget(self)

        self.setCentralWidget(mainWidget)
        statusbar = self.statusBar()
        self.setStatusBar(statusbar)
        self.fileName = QLabel('Ready')
        self.cursorPos = QLabel('      ')
        self.imageSize = QLabel('      ')
        self.autoLabel = QLabel('Manual Label')
        self.progress = QLabel('                 ')  # reserve widget space

        widget = QWidget(self)
        widget.setLayout(QHBoxLayout())
        widget.layout().addWidget(self.fileName)
        widget.layout().addStretch(1)
        widget.layout().addWidget(self.imageSize)
        widget.layout().addWidget(self.cursorPos)
        widget.layout().addStretch(1)
        widget.layout().addWidget(self.autoLabel)
        widget.layout().addStretch(2)
        widget.layout().addWidget(self.progress)
        statusbar.addWidget(widget, 1)

        self.setGeometry(50, 50, 1200, 800)
        self.setWindowTitle('im2trainData')
        self.show()
        
    def fitSize(self):
        self.setFixedSize(self.layout().sizeHint())

class ImageWidget(QWidget):
    def __init__(self, parent, key_cfg):
        super(ImageWidget, self).__init__(parent)
        self.parent = parent
        self.results = []
        self.setMouseTracking(True)
        self.key_config = key_cfg
        self.screen_height = QDesktopWidget().screenGeometry().height()
        self.last_idx = 0

        self.initUI()
        
    def initUI(self):
        self.pixmap = QPixmap('start.png')
        self.label_img = QLabel()
        self.label_img.setObjectName("image")
        self.pixmapOriginal = QPixmap.copy(self.pixmap)
        
        self.drawing = False
        self.lastPoint = QPoint()
        hbox = QHBoxLayout(self.label_img)
        self.setLayout(hbox)
        # self.setFixedSize(1200,800)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.prev_pixmap = self.pixmap
            self.drawing = True
            self.lastPoint = event.pos()
        elif event.button() == Qt.RightButton:
            x, y = event.pos().x(), event.pos().y()
            for i, box in enumerate(self.results):
                lx, ly, rx, ry = box[:4]
                if lx <= x <= rx and ly <= y <= ry:
                    self.results.pop(i)
                    self.pixmap = self.drawResultBox()
                    self.update()
                    break
            
    def mouseMoveEvent(self, event):
        self.parent.cursorPos.setText('({}, {})'.format(event.pos().x(), event.pos().y()))
        if event.buttons() and Qt.LeftButton and self.drawing:
            self.pixmap = QPixmap.copy(self.prev_pixmap)
            painter = QPainter(self.pixmap)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            p1_x, p1_y, p2_x, p2_y = self.lastPoint.x(), self.lastPoint.y(), event.pos().x(), event.pos().y()
            painter.drawRect(min(p1_x, p2_x), min(p1_y, p2_y), abs(p1_x-p2_x), abs(p1_y-p2_y))
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            p1_x, p1_y, p2_x, p2_y = self.lastPoint.x(), self.lastPoint.y(), event.pos().x(), event.pos().y()
            lx, ly, w, h = min(p1_x, p2_x), min(p1_y, p2_y), abs(p1_x-p2_x), abs(p1_y-p2_y)
            if (p1_x, p1_y) != (p2_x, p2_y):
                if self.results and len(self.results[-1]) == 4 and self.parent.autoLabel.text() == 'Manual Label':
                    self.showPopupOk('warning messege', 'please mark the box you drew.')
                    self.pixmap = self.drawResultBox()
                    self.update()
                elif self.parent.autoLabel.text() == 'Auto Label':
                    self.results.append([lx, ly, lx+w, ly+h, self.last_idx])
                    for i, result in enumerate(self.results):  # fill empty labels
                        if len(result) == 4:
                            self.results[i].append(self.last_idx)
                    self.pixmap = self.drawResultBox()
                    self.update()
                else:
                    self.results.append([lx, ly, lx+w, ly+h])
                self.drawing = False

    def showPopupOk(self, title: str, content: str):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(content)
        msg.setStandardButtons(QMessageBox.Ok)
        result = msg.exec_()
        if result == QMessageBox.Ok:
            msg.close()

    def drawResultBox(self):
        res = QPixmap.copy(self.pixmapOriginal)
        painter = QPainter(res)
        font = QFont('mono', 15, 1)
        painter.setFont(font)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        for box in self.results:
            lx, ly, rx, ry = box[:4]
            painter.drawRect(lx, ly, rx-lx, ry-ly)
            if len(box) == 5:
                painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
                painter.drawText(lx, ly+15, self.key_config[box[-1]])
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        return res

    def setPixmap(self, image_fn):
        self.pixmap = QPixmap(image_fn)
        self.W, self.H = self.pixmap.width(), self.pixmap.height()

        if self.H > self.screen_height * 0.8:
            resize_ratio = (self.screen_height * 0.8) / self.H
            self.W = round(self.W * resize_ratio)
            self.H = round(self.H * resize_ratio)
            self.pixmap = QPixmap.scaled(self.pixmap, self.W, self.H,
                                transformMode=Qt.SmoothTransformation)
        
        self.parent.imageSize.setText('{}x{}'.format(self.W, self.H))
        self.setFixedSize(self.W, self.H)
        self.pixmapOriginal = QPixmap.copy(self.pixmap)

    def cancelLast(self):
        if self.results:
            self.results.pop()  # pop last
            self.pixmap = self.drawResultBox()
            self.update()
    
    def getRatio(self):
        return self.W, self.H

    def getResult(self):
        return self.results

    def resetResult(self):
        self.results = []

    def markBox(self, idx):
        self.last_idx = idx
        if self.results:
            if len(self.results[-1]) == 4:
                self.results[-1].append(idx)
            elif len(self.results[-1]) == 5:
                self.results[-1][-1] = idx
            else:
                raise ValueError('invalid results')
            self.pixmap = self.drawResultBox()
            self.update()

class MainWidget(QWidget):
    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)
        self.parent = parent
        self.currentImg = "start.png"
        config_dict = self.getConfigFromJson('config.json')
        self.key_config = [config_dict['key_'+str(i)] for i in range(1, 10) if config_dict['key_'+str(i)]]
        self.crop_mode = False
        self.save_directory = None

        self.initUI()

    def initUI(self):
        # UI elements
        InputPathButton = QPushButton('Input Path', self)
        SavePathButton = QPushButton('Save Path', self)
        SavePathButton.setEnabled(False)
        okButton = QPushButton('Next', self)
        cancelButton = QPushButton('Cancel', self)
        cropModeCheckBox = QCheckBox("Crop Mode", self)
        InputPathLabel = QLabel('Input Path not selected', self)
        SavePathLabel = QLabel('Save Path not selected', self)
        self.label_img = ImageWidget(self.parent, self.key_config)

        # Events
        okButton.clicked.connect(self.setNextImage)
        okButton.setEnabled(False)
        cancelButton.clicked.connect(self.label_img.cancelLast)
        cropModeCheckBox.stateChanged.connect(lambda state: self.cropMode(state, SavePathButton))
        InputPathButton.clicked.connect(lambda:self.registerInputPath(InputPathButton, InputPathLabel, okButton))
        SavePathButton.clicked.connect(lambda:self.registerSavePath(SavePathButton, SavePathLabel))
        
        hbox = QHBoxLayout()

        vbox = QVBoxLayout()
        vbox.addWidget(InputPathButton)
        vbox.addWidget(SavePathButton)
    
        hbox.addLayout(vbox)

        
        vbox = QVBoxLayout()
        vbox.addWidget(InputPathLabel)
        vbox.addWidget(SavePathLabel)

        hbox.addLayout(vbox)
        hbox.addStretch(3)
        hbox.addWidget(cropModeCheckBox)
        hbox.addStretch(1)
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)

        vbox = QVBoxLayout()
        vbox.addWidget(self.label_img)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def setNextImage(self, img=None):
        if not img:
            res = self.label_img.getResult()
            if res and len(res[-1]) != 5:
                self.label_img.showPopupOk('warning messege', 'please mark the box you drew.')
                return 'Not Marked'
            self.writeResults(res)
            self.label_img.resetResult()
            try:
                self.currentImg = self.imgList.pop(0)
            except Exception:
                self.currentImg = 'end.png'
        else:
            self.label_img.resetResult()

        basename = os.path.basename(self.currentImg)
        self.parent.fileName.setText(basename)
        self.parent.progress.setText(str(self.total_imgs-len(self.imgList))+'/'+str(self.total_imgs))

        self.label_img.setPixmap(self.currentImg)
        self.label_img.update()
        self.parent.fitSize()

    def writeResults(self, res:list):
        if self.parent.fileName.text() != 'Ready':
            W, H = self.label_img.getRatio()
            if not res:
                open(self.currentImg[:-4]+'.txt', 'a', encoding='utf8').close()
            for i, elements in enumerate(res):  # box : (lx, ly, rx, ry, idx)
                lx, ly, rx, ry, idx = elements
                # yolo : (idx center_x_ratio, center_y_ratio, width_ratio, height_ratio)
                yolo_format = [(lx+rx)/2/W, (ly+ry)/2/H, (rx-lx)/W, (ry-ly)/H]
                yolo_format.insert(0, idx)  
                with open(self.currentImg[:-4]+'.txt', 'a', encoding='utf8') as resultFile:
                    resultFile.write(' '.join([str(x) for x in yolo_format])+'\n')
                if self.crop_mode:
                    img = cv2.imread(self.currentImg)
                    oh, ow = img.shape[:2]
                    w, h = round(yolo_format[3]*ow), round(yolo_format[4]*oh)
                    x, y = round(yolo_format[1]*ow - w/2), round(yolo_format[2]*oh - h/2)
                    crop_img = img[y:y+h, x:x+w]
                    basename = os.path.basename(self.currentImg)
                    filename = basename[:-4]+'-{}-{}.jpg'.format(self.key_config[0], i)
                    cv2.imwrite(os.path.join(self.save_directory, filename), crop_img)

    def registerSavePath(self, SavePathButton, label):
        SavePathButton.toggle()
        self.save_directory = str(QFileDialog.getExistingDirectory(self, "Select Save Directory"))
        basename = os.path.basename(self.save_directory)
        if basename:
            label.setText(basename+'/')
        else:
            print("Output Path not selected")
            self.output_directory = None

    def registerInputPath(self, InputPathButton, label, okButton):
        InputPathButton.toggle()
        directory = str(QFileDialog.getExistingDirectory(self, "Select Input Directory"))
        
        types = ('*.jpg', '*.png')
        self.imgList = []
        for t in types:
            self.imgList.extend(glob(directory+'/'+t))
        self.total_imgs = len(self.imgList)

        to_skip = []
        for imgPath in self.imgList:
            if os.path.exists(imgPath[:-4] + '.txt'):
                to_skip.append(imgPath)
        for skip in to_skip:
            self.imgList.remove(skip)

        basename = os.path.basename(directory)
        label.setText(basename+'/')
        okButton.setEnabled(True)

        if self.save_directory is None:
            self.save_directory = directory

    def getConfigFromJson(self, json_file):
        # parse the configurations from the config json file provided
        with open(json_file, 'r') as config_file:
            try:
                config_dict = json.load(config_file)
                # EasyDict allows to access dict values as attributes (works recursively).
                return config_dict
            except ValueError:
                print("INVALID JSON file format.. Please provide a good json file")
                exit(-1)

    def cropMode(self, state, SavePathButton):
        if state == Qt.Checked:
            self.crop_mode = True
            SavePathButton.setEnabled(True)
        else:
            self.crop_mode = False
            SavePathButton.setEnabled(False)
    
    def keyPressEvent(self, e):
        config_len = len(self.key_config)
        for i, key_n in enumerate(range(49,58), 1):
            if e.key() == key_n and config_len >= i:
                self.label_img.markBox(i-1) 
                break
        if e.key() == Qt.Key_Escape:
            self.label_img.cancelLast()
        elif e.key() == Qt.Key_E:
            self.setNextImage()
        elif e.key() == Qt.Key_Q:
            self.label_img.resetResult()
            self.label_img.pixmap = self.label_img.drawResultBox()
            self.label_img.update()
        elif e.key() == Qt.Key_A:
            if self.parent.autoLabel.text() == 'Auto Label':
                self.parent.autoLabel.setText('Manual Label')
            else:
                self.parent.autoLabel.setText('Auto Label')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())