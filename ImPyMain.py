'''
Created on Dec 11, 2011

@author: renat
'''
import re
import sys
from PyQt4 import QtCore, QtGui

from MainWindow import *

import BrightContrastClass
import ImPyPlugins
import ImPyProcess
import ImageWindow
from UI import DuplicateDialog


class StartImpy(QtGui.QMainWindow):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.move(QtCore.QPoint(0,0))
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
# File menu
        self.connect(self.ui.actionOpen, QtCore.SIGNAL("triggered()"),self.openFile)
        
# Edit menu
        self.connect(self.ui.actionCrop, QtCore.SIGNAL("triggered()"),self.crop)
        self.connect(self.ui.actionDuplicate, QtCore.SIGNAL("triggered()"),self.duplicate)
        self.connect(self.ui.actionInvert, QtCore.SIGNAL("triggered()"),self.invert)
        self.connect(self.ui.actionBritnessContrast, QtCore.SIGNAL("triggered()"),self.setBrCon)

# Process menu
        self.connect(self.ui.actionGaussBlur, QtCore.SIGNAL("triggered()"),self.GaussBlur)
        
# Plugin menu
        self.connect(self.ui.actionBALM, QtCore.SIGNAL("triggered()"),self.BALM)

#Buttons
        self.connect(self.ui.drawRec, QtCore.SIGNAL('clicked()'), self.drawRec)
        self.connect(self.ui.drawCirc, QtCore.SIGNAL('clicked()'), self.drawCirc)
        self.connect(self.ui.drawPoly, QtCore.SIGNAL('clicked()'), self.drawPoly)
        self.connect(self.ui.drawLine, QtCore.SIGNAL('clicked()'), self.drawLine)
        self.connect(self.ui.markPoint, QtCore.SIGNAL('clicked()'), self.markPoint)
        self.connect(self.ui.zoom, QtCore.SIGNAL('clicked()'), self.zoom)

        
        self.imageWindows=[]
        self.brCon = None
        self.lastImFocus = None
        self.mouseState = 'mouse'

    def openFile(self, fileName=None, imStack=None, arrayStack=None):
        fileFilter = "TIF (*.tif)"
        if fileName == None and imStack==None and arrayStack==None:
            fileName = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file',\
                                 "/home/renat/Documents/work/imaging/", fileFilter))
        elif fileName == None and (imStack != None or arrayStack != None):
            fileName = 'Stack'
        if fileName != '':
            self.imageWindows.append([ImageWindow.ImageWindow(fileName,self,imStack,arrayStack),fileName])
            self.imageWindows[-1][0].move(QtCore.QPoint(200 + 30*(len(self.imageWindows)%10),
                                self.size().height() + 30*(len(self.imageWindows)%10)))
            self.imageWindows[-1][0].show()
    def closeFile(self,fileName):
        for item in self.imageWindows:
            if item[1] == fileName:
                self.imageWindows.remove(item)
                self.lastImFocus = None
    
    def crop(self):
        imInFocus = self.lastImFocus
        fileName = imInFocus.windowName
        stackTmp = [imInFocus.image.imStack[i].crop(imInFocus.Roi.topLBox + imInFocus.Roi.botRBox)\
                    for i in range(len(imInFocus.image.imStack))]
        self.lastImFocus.close()
        self.openFile(fileName,stackTmp)
    def duplicate(self):
        class duplicateStackDialog(QtGui.QDialog):
            def __init__(self,parent=None):
                QtGui.QDialog.__init__(self,parent)
                self.ui = DuplicateDialog.Ui_Dialog()
                self.ui.setupUi(self) #put all elements on the window
                self.ui.stackRange.setText('1-10')
                QtCore.QObject.connect(self.ui.buttons, QtCore.SIGNAL("accepted()"), self.accept)
            def accept(self):
                if self.ui.stack.isChecked==True:
                    start = self.parent().lastImFocus.ui.zSpinBox.value()
                    end = start
                else:
                    start, end = re.findall(r'\b\d+\b', str(self.ui.stackRange.text()))
                    start = int(start)
                    end = int(end)
                print(start,end)
                self.close()
        self.userDialog = duplicateStackDialog(self)
        self.userDialog.show()
    def invert(self):
        pass
    def convolve(self,karnel,imageWindow):
        pass
    def BALM(self):
        balmArrayStack = ImPyPlugins.BALM(self.lastImFocus.image.arrayStack)
        self.openFile('BALM', arrayStack=balmArrayStack)
    def GaussBlur(self):
        gaussBlurIm = ImPyProcess.applyGaussBlur(self.lastImFocus.image.imStack)
        self.openFile('Gauss Blur',imStack = gaussBlurIm)
    def setBrCon(self):
        self.brCon = BrightContrastClass.BrConWindow(parent=self)
        self.brCon.show()
    def zoom(self):
        self.lastImFocus.ui.imageSpace.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.mouseState = 'zoom'
    def drawRec(self):
        self.lastImFocus.ui.imageSpace.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.mouseState = 'rectangle'
    def drawCirc(self):
        self.lastImFocus.ui.imageSpace.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.mouseState = 'circle'
    def drawPoly(self):
        self.lastImFocus.ui.imageSpace.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.mouseState = 'polygon'
    def drawLine(self):
        self.lastImFocus.ui.imageSpace.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.mouseState = 'line'
    def markPoint(self):
        self.lastImFocus.ui.imageSpace.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.mouseState = 'point'
                                
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    impy = StartImpy()
    impy.show()
    sys.exit(app.exec_())