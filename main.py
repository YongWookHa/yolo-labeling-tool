import sys
import os
from PIL import Image, ExifTags
from glob import glob
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QLabel, QDesktopWidget, QProgressBar, QMessageBox
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
        self.progress = QLabel('                 ')  # reserve widget space
        self.resizeProgressBar = QProgressBar() 

        widget = QWidget(self)
        widget.setLayout(QHBoxLayout())
        widget.layout().addWidget(self.fileName)
        widget.layout().addStretch(1)
        widget.layout().addWidget(self.imageSize)
        widget.layout().addWidget(self.cursorPos)
        widget.layout().addStretch(5)
        widget.layout().addWidget(self.progress)
        widget.layout().addWidget(self.resizeProgressBar)
        statusbar.addWidget(widget, 1)

        self.setGeometry(50, 50, 1200, 800)
        self.setWindowTitle('im2trainData')
        self.show()
        
    def fitSize(self):
        self.setFixedSize(self.layout().sizeHint())

class ImageWidget(QWidget):
    def __init__(self, parent):
        super(ImageWidget, self).__init__(parent)
        self.parent = parent
        self.results = []
        self.setMouseTracking(True)
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
                if self.results and len(self.results[-1]) == 4:
                    self.showPopupOk('warning messege', 'please mark the box you drew.')
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
                painter.drawText(lx, ly+15, box[-1])
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        return res

    def setPixmap(self, image_fn):
        self.pixmap = QPixmap(image_fn)
        self.W, self.H = self.pixmap.width(), self.pixmap.height()
        self.parent.imageSize.setText('{}x{}'.format(self.W, self.H))
        self.setFixedSize(self.W ,self.H)
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

    def markBox(self, marker):
        if self.results:
            if len(self.results[-1]) == 4:
                self.results[-1].append(marker)
            elif len(self.results[-1]) == 5:
                self.results[-1][-1] = marker
            else:
                raise ValueError('invalid results')
            self.pixmap = self.drawResultBox()
            self.update()

class MainWidget(QWidget):
    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)
        self.parent = parent
        self.currentImg = "start.png"
        self.key_config = []
        with open('config.txt', 'r', encoding='utf8') as f:
            lines = f.readlines()
            for line in lines:
                if 'project_name' in line:
                    self.project_name = line.split(':')[1].strip()
                if 'max_height' in line:
                    self.max_height = int(line.split(':')[1].strip())
                if line[:3] == 'key' and line.split(':')[1].strip() != '':
                    self.key_config.append(line.split(':')[1].strip())
        self.initUI()

    def initUI(self):
        # UI elements
        pathButton = QPushButton('Path', self)
        okButton = QPushButton('Next', self)
        cancelButton = QPushButton('Cancel', self)
        pathLabel = QLabel('Path not selected', self)
        self.label_img = ImageWidget(self.parent)

        # Events
        okButton.clicked.connect(self.setNextImage)
        okButton.setEnabled(False)
        cancelButton.clicked.connect(self.label_img.cancelLast)
        pathButton.setCheckable(True)
        pathButton.clicked.connect(lambda:self.registerPath(pathButton, pathLabel, okButton))
        
        hbox = QHBoxLayout()
        
        hbox.addWidget(pathButton)
        hbox.addWidget(pathLabel)
        hbox.addStretch(5)
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)

        vbox = QVBoxLayout()
        vbox.addWidget(self.label_img)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def setNextImage(self, img=None):
        if not img:
            res = self.label_img.getResult()
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
            for elements in res:
                lx, ly, rx, ry = elements[:4]
                yolo_format = [(lx+rx)/2/W, (ly+ry)/2/H, (rx-lx)/W, (ry-ly)/H]
                idx = self.key_config.index(elements[-1])
                yolo_format.insert(0, idx)
                with open(self.currentImg[:-4]+'.txt', 'a', encoding='utf8') as resultFile:
                    resultFile.write(' '.join([str(x) for x in yolo_format])+'\n')

    def registerPath(self, pathButton, label, okButton):
        pathButton.toggle()
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        
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

        for idx, img in enumerate(self.imgList):
            self.parent.progress.setText('Resizing.'+'.'*(idx%3))
            im = Image.open(img)
            w, h = im.size
            self.parent.resizeProgressBar.setValue(int(idx/len(self.imgList)*100)+1)
            if h > self.max_height:
                ratio = self.max_height/h
                im = im.resize((int(w*ratio), self.max_height) ,resample=Image.BICUBIC)
                try:
                    for orientation in ExifTags.TAGS.keys(): 
                        if ExifTags.TAGS[orientation]=='Orientation':
                            break 
                    exif=dict(im.getexif().items())
                    if exif[orientation] in [3,6,8]: 
                        im = im.transpose(Image.ROTATE_180)
                except:
                    pass
                im.save(img)
        self.parent.resizeProgressBar.close()
        self.parent.progress.setText('Resize Completed')

        basename = os.path.basename(directory)
        label.setText(basename+'/')
        okButton.setEnabled(True)
    
    def keyPressEvent(self, e):
        config_len = len(self.key_config)
        for i, key_n in enumerate(range(49,58), 1):
            if e.key() == key_n and config_len >= i:
                self.label_img.markBox(self.key_config[i-1]) 
                break
        if e.key() == Qt.Key_Escape:
            self.label_img.cancelLast()
        elif e.key() == Qt.Key_Space:
            self.setNextImage()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())