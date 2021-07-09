import numpy
from mayavi import mlab
from PIL import Image
from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
from BrConWindowUI import *
import ImageClass

class BrConWindow(QtGui.QDialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_BrCon()
        self.ui.setupUi(self) #put all elements on the window
        self.image = self.parent().lastImFocus.image
        self.maxPixelValue = self.image.maxPixelValue
        #workaround for avoiding recursion with valueChanged() signal. sliderMoed() doesn't work well.
        self.sliderMovedFlag=True
        if self.image != None:
            self.ui.sliderMaximum.setValue(self.image.thresholdMaximum*100/self.maxPixelValue)
            self.ui.sliderMinimum.setValue(self.image.thresholdMinimum*100/self.maxPixelValue)
            self.ui.sliderBrightness.setValue(self.image.brightness)
            self.ui.sliderContrast.setValue(self.image.contrast)
        #display histogram
        self.histoGraph = Histogram(self.ui.histoWidget, width=5, height=4, dpi=100)
        self.ui.histoLayout.insertWidget(0,self.histoGraph)
        QtCore.QObject.connect(self.ui.sliderMaximum, QtCore.SIGNAL("valueChanged(int)"), self.setMaximum)
        QtCore.QObject.connect(self.ui.sliderMinimum, QtCore.SIGNAL("valueChanged(int)"), self.setMinimum)
        QtCore.QObject.connect(self.ui.sliderBrightness, QtCore.SIGNAL("valueChanged(int)"), self.setBrightness)
        QtCore.QObject.connect(self.ui.sliderContrast, QtCore.SIGNAL("valueChanged(int)"), self.setContrast)
        QtCore.QObject.connect(self.ui.apply, QtCore.SIGNAL("clicked()"), self.applyBrCon)
        QtCore.QObject.connect(self.ui.reset, QtCore.SIGNAL("clicked()"), self.resetBrCon)
        QtCore.QObject.connect(self.ui.autoBrCon, QtCore.SIGNAL("clicked()"), self.autoBrCon)
    def setMaximum(self):
        if self.sliderMovedFlag and self.image != None:
            self.sliderMovedFlag = False
            self.image.thresholdMaximum = self.ui.sliderMaximum.value()*self.maxPixelValue/100
            maximum = self.ui.sliderMaximum.value()
            minimum = self.image.thresholdMinimum*100/self.maxPixelValue
            if maximum <= minimum + 1:
                self.ui.sliderMinimum.setValue(maximum -2)
                self.image.thresholdMinimum = (maximum -2)*self.maxPixelValue/100
            average = (maximum + minimum)/2
            hDiff = max(1,(maximum - minimum)/2)
            self.ui.sliderBrightness.setValue(100 - average)
            self.image.brightness = 100 - average
            slope = numpy.pi/200
            offset = numpy.pi/1000
            contrast = int((numpy.arctan(50./hDiff) - offset)/slope)
            self.ui.sliderContrast.setValue(contrast)
            self.image.contrast = contrast
            self.histoGraph.updateHisto()
            self.image.parent.updateImage()
            self.sliderMovedFlag = True
    def setMinimum(self):
        if self.sliderMovedFlag and self.image != None:
            self.sliderMovedFlag = False
            self.image.thresholdMinimum = self.ui.sliderMinimum.value()*self.maxPixelValue/100
            maximum = self.image.thresholdMaximum*100/self.maxPixelValue
            minimum = self.ui.sliderMinimum.value()
            if minimum >= maximum - 1:
                self.ui.sliderMaximum.setValue(minimum + 2)
                self.image.thresholdMaximum = (minimum + 2)*self.maxPixelValue/100
            average = (maximum + minimum)/2
            hDiff = max(1,(maximum - minimum)/2)
            self.ui.sliderBrightness.setValue(100 - average)
            self.image.brightness = 100 - average
            slope = numpy.pi/200
            offset = numpy.pi/1000
            contrast = int((numpy.arctan(50./hDiff) - offset)/slope)
            self.ui.sliderContrast.setValue(contrast)
            self.image.contrast = contrast
            self.histoGraph.updateHisto()
            self.image.parent.updateImage()
            self.sliderMovedFlag = True
    def setBrightness(self):
        if self.sliderMovedFlag and self.image != None:
            self.sliderMovedFlag = False
            maximum = self.image.thresholdMaximum*100/self.maxPixelValue
            minimum = self.image.thresholdMinimum*100/self.maxPixelValue
            average = 100 - self.ui.sliderBrightness.value()
            self.image.brightness = self.ui.sliderBrightness.value()
            hDiff = max(1,(maximum - minimum)/2)
            self.image.thresholdMaximum = (average + hDiff)*self.maxPixelValue/100
            self.ui.sliderMaximum.setValue(average + hDiff)
            self.image.thresholdMinimum = (average - hDiff)*self.maxPixelValue/100
            self.ui.sliderMinimum.setValue(average - hDiff)
            self.histoGraph.updateHisto()
            self.image.parent.updateImage()
            self.sliderMovedFlag = True
    def setContrast(self):
        if self.sliderMovedFlag and self.image != None:
            self.sliderMovedFlag = False
            average = 100 - self.ui.sliderBrightness.value()
            contrast = self.ui.sliderContrast.value()
            self.image.contrast = contrast
            slope = numpy.pi/205
            offset = numpy.pi/100
            hDiff = int(50/numpy.tan(slope*contrast+offset))
            self.image.thresholdMaximum = (average + hDiff)*self.maxPixelValue/100
            self.image.thresholdMinimum = (average - hDiff)*self.maxPixelValue/100
            self.ui.sliderMaximum.setValue(average + hDiff)
            self.ui.sliderMinimum.setValue(average - hDiff)
            self.histoGraph.updateHisto()
            self.image.parent.updateImage()
            self.sliderMovedFlag = True
    def applyBrCon(self):
        def adjustBrCont(i):
            if i >= self.image.thresholdMaximum:
                return self.image.maxPixelValue
            elif i <= self.image.thresholdMinimum:
                return 0
            else:
                return self.image.maxPixelValue*(i-self.image.thresholdMinimum)/(self.image.thresholdMaximum-self.image.thresholdMinimum)
        imStackTmp = [self.image.imStack[i].point(adjustBrCont) for i in range(len(self.image.imStack))]
        frameRateTmp = self.image.frameRate
        zoomScaleTmp = self.image.zoomScale
        self.parent().lastImFocus.image = ImageClass.ImpyImage(self.image.fileName,self.image.parent,imStack=imStackTmp)
        self.image = self.parent().lastImFocus.image
        self.image.frameRate = frameRateTmp
        self.image.zoomScale = zoomScaleTmp
        self.image.parent.updateImage()
    def resetBrCon(self):
        self.ui.sliderMaximum.setValue(100)
        self.ui.sliderMinimum.setValue(0)
    def autoBrCon(self):
        self.ui.sliderMaximum.setValue(numpy.max(numpy.max(numpy.max(self.image.arrayStack)))*100/self.maxPixelValue)
        self.ui.sliderMinimum.setValue(0)
    def closeEvent(self,event):
        self.parent().brCon = None
class MplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=10, height=10, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)



class Histogram(MplCanvas):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)
#        self.image = self.parent().parent().image
#        self.maxPixelValue = self.image.maxPixelValue
        self.updateHisto()

    def updateHisto(self):
        self.parent().parent().image = self.parent().parent().parent().lastImFocus.image
        self.parent().parent().image.maxPixelValue = self.parent().parent().parent().lastImFocus.image.maxPixelValue
        self.image = self.parent().parent().parent().lastImFocus.image
        self.maxPixelValue = self.image.maxPixelValue
        if self.image != None:
            average = 100 - self.image.brightness
            contrast = self.image.contrast
        else:
            average = 50
            contrast = 50
        slope = -1
        offset = 100
        hDiff = int(slope*contrast + offset)
        if self.image != None:
            maximum = self.image.thresholdMaximum
            minimum = self.image.thresholdMinimum
        else:
            maximum = (average + hDiff)*self.maxPixelValue/100
            minimum = (average - hDiff)*self.maxPixelValue/100
        self.axes.hold(False)
        if self.image != None:
            imNum = self.image.parent.ui.zSpinBox.value()
            data = self.image.arrayStack[imNum].ravel()
            histList, bins = numpy.histogram(data, 100)
            self.axes.hist(data, 100, normed=False, facecolor='gray')
            self.axes.hold(True) 
            maxBin = numpy.max(histList)
        else:
            maxBin = 1.0
        x = numpy.array(numpy.arange(self.maxPixelValue), numpy.float)
        brConLine = maxBin*(x - minimum)/(maximum-minimum)
        self.axes.plot(x, brConLine, 'k-')
        # update the view limits
        self.axes.set_xlim(0, self.maxPixelValue)
        self.axes.set_ylim(0, maxBin)
        self.axes.set_xticks([0,self.maxPixelValue])
        self.axes.set_yticks([])
        self.draw()