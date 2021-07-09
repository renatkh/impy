from PyQt5 import QtWidgets
import RoiClass
from ImageConvertions import *
from UI.ImageWindowUI import *


class ImageWindow(QtWidgets.QDialog):
    def __init__(self,fileName,parent=None,imStack=None, arrayStack=None):
        self.image = ImageClass.ImpyImage(fileName,self,imStack, arrayStack)
        self.windowName = fileName
        self.Roi = RoiClass.Roi()
        self.timer = QtCore.QTimer()
        self.playFlag = False
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.playFrameUpdate)
        #create UI with its buttons, fields and connections
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_ImageWindow()
        self.ui.setupUi(self) #put all elements on the window
        #set window size same as image
        self.resize(max(self.image.imStack[0].size[0]+50,250), self.image.imStack[0].size[1]+70)
        #set window title to be fileName
        self.setWindowTitle(QtGui.QApplication.translate("ImageWindow", fileName, None, QtGui.QApplication.UnicodeUTF8))
        #set maximum values of zSpinBox and slider as a number of images
        self.ui.zSpinBox.setMaximum(len(self.image.imStack)-1)
        self.ui.imageScrollBar.setMaximum(len(self.image.imStack)-1)
        #update image when slider moved
        QtCore.QObject.connect(self.ui.imageScrollBar, QtCore.SIGNAL("valueChanged(int)"), self.updateImage)
        #display image
        self.scene = QtGui.QGraphicsScene()
        self.scene.setObjectName('scene')
        self.scene.setSceneRect(QtCore.QRectF(0, 0, self.image.imStack[0].size[0], self.image.imStack[0].size[1]))

        self.scene.addPixmap(PIL2QPixmap(self.image.imStack[0].resize(numpy.asarray(numpy.asarray(self.image.imStack[0].size)*self.image.zoomScale, dtype = numpy.int))))
        
        self.ui.imageSpace.setScene(self.scene)
        #Play button
        QtCore.QObject.connect(self.ui.playPause, QtCore.SIGNAL("clicked()"), self.playPause)
        
        self.shortcutL = QtGui.QShortcut(QtGui.QKeySequence("Left"),self, self.moveL)
        self.shortcutR = QtGui.QShortcut(QtGui.QKeySequence("Right"),self, self.moveR)
        
    # define various functions and operations with the window
    def updateImage(self,imNum=None):
        imNum = self.ui.zSpinBox.value()
        def adjustBrCont(i):
            if i >= self.image.thresholdMaximum:
                return self.image.maxPixelValue
            elif i <= self.image.thresholdMinimum:
                return 0
            else:
                return self.image.maxPixelValue*(i-self.image.thresholdMinimum)/(self.image.thresholdMaximum-self.image.thresholdMinimum)
        imTmp = self.image.imStack[imNum].point(adjustBrCont)
        self.scene.clear()#clean scene
# redraw image            
        self.scene.addPixmap(PIL2QPixmap(imTmp.resize(numpy.asarray(numpy.asarray(imTmp.size)*self.image.zoomScale, dtype = numpy.int))))
        self.scene.setSceneRect(QtCore.QRectF(0, 0, self.image.imStack[0].size[0]*self.image.zoomScale,
                                               self.image.imStack[0].size[1]*self.image.zoomScale))
# Update histogram       
        if self.parent():
            if self.parent().brCon != None:
                self.parent().brCon.histoGraph.updateHisto()
            self.drawRoi()# redraw Roi
    
    def moveL(self):
        v = self.ui.zSpinBox.value()
        if v>0: self.ui.zSpinBox.setValue(v-1)
        else: self.ui.zSpinBox.setValue(self.ui.zSpinBox.maximum())
        
    def moveR(self):
        v = self.ui.zSpinBox.value()
        if v<self.ui.zSpinBox.maximum(): self.ui.zSpinBox.setValue(v+1)
        else: self.ui.zSpinBox.setValue(0)
    
    def drawRoi(self):
        color = QtGui.QColor(200,200,0)
        scale = self.image.zoomScale
        if self.Roi.shape == 'rectangle':
            self.scene.addRect(self.Roi.topLBox[0]*scale,self.Roi.topLBox[1]*scale,
                               self.Roi.width*scale, self.Roi.height*scale,color)
        elif self.Roi.shape == 'circle':
            self.scene.addEllipse(self.Roi.topLBox[0]*scale,self.Roi.topLBox[1]*scale,
                                  self.Roi.width*scale, self.Roi.height*scale,color)
        elif self.Roi.shape == 'line':
            self.scene.addLine(self.Roi.points[0][0]*scale,self.Roi.points[0][1]*scale,
                               self.Roi.points[1][0]*scale,self.Roi.points[1][1]*scale,color)
        elif self.Roi.shape == 'points':
            for point in self.Roi.points:
                self.scene.addRect(point[0]*scale-1, point[1]*scale-1,
                                     1, 1,color)
        elif self.Roi.shape == 'polygon':
            points = []
            for obj in self.Roi.getQPoints():
                obj.setX(obj.x()*scale)
                obj.setY(obj.y()*scale)
                points.append(obj)
            self.scene.addPolygon(QtGui.QPolygonF(points),color)
        
    def playFrameUpdate(self):
            if self.ui.imageScrollBar.value() < len(self.image.imStack)-1:
                imNum = self.ui.imageScrollBar.value() + 1
            else:
                imNum = 0
            self.ui.imageScrollBar.setValue(imNum)
            self.timer.start(1000/self.image.frameRate)
    def mousePressEvent(self, event):
        button = event.button()
        item = self.childAt(event.x(), event.y())
        mousePos = self.ui.imageSpace.mapToScene(event.pos())
        if button == 2 and item == self.ui.playPause:
            class FrameRateDialog(QtGui.QDialog):
                def __init__(self,parent=None):
                    QtGui.QDialog.__init__(self,parent)
                    self.gridLayout = QtGui.QGridLayout(self)
                    self.label = QtGui.QLabel(self)
                    self.label.setText('Frame Rate')
                    self.zSpinBox = QtGui.QSpinBox(self)
                    self.zSpinBox.setValue(self.parent().image.frameRate)
                    QtCore.QObject.connect(self.zSpinBox, QtCore.SIGNAL("valueChanged(int)"), self.setFrameRate)
                    self.gridLayout.addWidget(self.label)
                    self.gridLayout.addWidget(self.zSpinBox)
                def setFrameRate(self,rate):
                    self.parent().image.frameRate = rate
            self.userDialog = FrameRateDialog(self)
            self.userDialog.show()
                    
    def zoomImage(self,button):
        if button == 1: # if left button pressed zoom in
            self.image.zoomScale = self.image.zoomScale*1.5
        else: # if right button pressed zoom out
            self.image.zoomScale = self.image.zoomScale/1.5
        self.resize(max(int(self.image.imStack[0].size[0]*self.image.zoomScale)+50,250),
                            int(self.image.imStack[0].size[1]*self.image.zoomScale)+70) #resize image window
        self.updateImage()
    def playPause(self):
        if self.playFlag:
            self.timer.stop()
            self.playFlag = False
        else:
            self.timer.start(1000/self.image.frameRate)
            self.playFlag = True
    def closeEvent(self,event):
        self.timer.stop()
        if self.parent(): self.parent().closeFile(self.windowName)
    def focusInEvent(self, event):
        if self.parent():
            self.parent().lastImFocus = self
            if self.parent().brCon != None:
                self.parent().brCon.histoGraph.updateHisto()
    def focusOutEvent(self, event):
        pass
    
    def setTitle(self, title):
        self.setWindowTitle(QtGui.QApplication.translate("ImageWindow", title, None, QtGui.QApplication.UnicodeUTF8))