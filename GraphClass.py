'''
@author: renat

Creates a Qt window with matplotlib figure inside
'''

import sys, os, numpy
from PyQt5 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from numpy import array, float32

progname = os.path.basename(sys.argv[0])
progversion = "0.1"
numpy.set_printoptions(threshold=numpy.nan)


class MplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent, width=5, height=4, dpi=100,):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
class MplGraph(MplCanvas):
    def __init__(self, parent=None, **kwargs):
        for name, value in kwargs.iteritems():
            exec("%s = %s" % (name, value))
        MplCanvas.__init__(self, parent)
    
    def addSubPlot(self, **kwargs):
        '''Puts new plot or adds to existing plots in a single column'''
        #Resize existing plots
        try:
            n = len(self.fig.axes)
        except:
            n = 0
        for i in range(n):
            self.fig.axes[i].change_geometry(n+1, 1, i+1)
        
        for name, value in kwargs.iteritems():
            exec("%s = %s" % (name, value))
        legendVal = False
        legendPassed = False
        for name, value in kwaxes.iteritems():
            if name == 'legend':
                legendVal = value
                legendPassed = True
        
        self.fig.subplots_adjust(hspace = 0.5)
        self.fig.add_subplot(n+1, 1, n+1)
        if legendPassed:
            kwaxes.pop('legend', legendVal)
            if legendVal: self.fig.axes[n].legend()
        self.fig.axes[n].set(**kwaxes)
        self.makePlot(self.fig.axes[n], **kwplt)
        self.draw()
        
    def addPlot(self, **kwargs):
        for name, value in kwargs.iteritems():
            exec("%s = %s" % (name, value))
        legendVal = False
        legendPassed = False
        for name, value in kwaxes.iteritems():
            if name == 'legend':
                legendVal = value
                legendPassed = True
        
        if legendPassed:
            kwaxes.pop('legend', legendVal)
            if legendVal: self.fig.axes[n].legend()       
        self.fig.axes[-1].set(**kwaxes)
        self.makePlot(self.fig.axes[-1], **kwplt)
        self.draw()

    def makePlot(self, axes, x, y, xerr=[None], yerr=[None], **kwargs):
        if xerr[0] != None or yerr[0] !=None:
            if xerr[0] != None:
                xerrTmp = xerr
            else:
                xerrTmp = numpy.zeros(len(yerr))
            if yerr[0] != None:
                yerrTmp = yerr
            else:
                yerrTmp = numpy.zeros(len(xerr))
            axes.errorbar( x, y, xerr=xerrTmp, yerr=yerrTmp, **kwargs)
        else:
            axes.plot( x, y, **kwargs)

class GraphWindow(QtGui.QDialog):
    ''' to use initialize QtGui externally with
    app = QtGui.QApplication(sys.argv)
    
    Examples of arguments:
    kwaxes = {'xlabel' : 'x coordinate', 'ylabel' : 'y coordinate',\
              'title' : 'my title', 'legend' : False}
    kwplt = {'x': x, 'y': y, 'yerr' : yerr}
    kwargs = {'kwplt' : kwplt, 'kwaxes' : kwaxes}'''
    
    def __init__(self, parent=None, multiplot = False, *args, **kwargs):
        QtGui.QDialog.__init__(self,parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.resize(600, 600)
        self.setWindowTitle("Graph")
        self.main_widget = QtGui.QWidget(self)
        self.graphLayout = QtGui.QVBoxLayout(self)
        self.graph = MplGraph(self)
        self.graphLayout.addWidget(self.graph)
        self.multiplot = multiplot
        self.multiKwargs = [[]]
        if True:
            self.sliderLayout = QtGui.QHBoxLayout()
            self.sliderLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
            self.zSpinBox = QtGui.QSpinBox(self)
            self.zSpinBox.setFocusPolicy(QtCore.Qt.ClickFocus)
            self.zSpinBox.setMaximum(0)
            self.sliderLayout.addWidget(self.zSpinBox)
            self.scrollBar = QtGui.QScrollBar(self)
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.scrollBar.sizePolicy().hasHeightForWidth())
            self.scrollBar.setSizePolicy(sizePolicy)
            self.scrollBar.setOrientation(QtCore.Qt.Horizontal)
            self.scrollBar.setMaximum(0)
            self.sliderLayout.addWidget(self.scrollBar)
            self.graphLayout.addLayout(self.sliderLayout)
            QtCore.QObject.connect(self.scrollBar, QtCore.SIGNAL("valueChanged(int)"), self.showPlot)
            QtCore.QObject.connect(self.scrollBar, QtCore.SIGNAL("valueChanged(int)"), self.zSpinBox.setValue)
            QtCore.QObject.connect(self.zSpinBox, QtCore.SIGNAL("valueChanged(int)"), self.scrollBar.setValue)
        self.saveButton = QtGui.QToolButton(self)
        self.saveButton.setText(QtGui.QApplication.translate("Graph", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.sliderLayout.addWidget(self.saveButton)
        QtCore.QObject.connect(self.saveButton, QtCore.SIGNAL("clicked()"), self.save)
        self.shortcutL = QtGui.QShortcut(QtGui.QKeySequence("Left"),self, self.moveL)
        self.shortcutR = QtGui.QShortcut(QtGui.QKeySequence("Right"),self, self.moveR)
    
    def moveL(self):
        v = self.zSpinBox.value()
        if v>0: self.zSpinBox.setValue(v-1)
        else: self.zSpinBox.setValue(self.zSpinBox.maximum())
        
    def moveR(self):
        v = self.zSpinBox.value()
        if v<self.zSpinBox.maximum(): self.zSpinBox.setValue(v+1)
        else: self.zSpinBox.setValue(0)
    
    def showPlot(self, value=0):
        ''' shows window'''
        self.graph.fig.clf()
        for command in self.multiKwargs[value]:
            exec(command)
    def plotXY(self, x, y, color=None, title=None):
        if color: kwplt = {'x': x, 'y': y, 'color': color}
        else: kwplt = {'x': x, 'y': y}
        if title: kwaxes = {'title':title}
        else: kwaxes = {}
        kwargs = {'kwplt' : kwplt, 'kwaxes': kwaxes}
        self.addPlot(**kwargs)
    def plotXY2Prev(self, x, y, color=None):
        if color: kwplt = {'x': x, 'y': y, 'color': color}
        else: kwplt = {'x': x, 'y': y}
        kwaxes = {}
        kwargs = {'kwplt' : kwplt, 'kwaxes': kwaxes}
        self.add2PrevPlot(**kwargs)
    def addPlot(self, **kwargs):
        ''' adds subfigure next to previous figure'''
        self.multiKwargs[-1].append('self.graph.addSubPlot(**%s)' % (kwargs))
    def add2PrevPlot(self, **kwargs):
        ''' plots on the same canvas as previous figure'''
        if len(self.multiKwargs[-1]) == 0:
            self.multiKwargs[-1].append('self.graph.addSubPlot(**%s)' % (kwargs))
        else:
            self.multiKwargs[-1].append('self.graph.addPlot(**%s)' % (kwargs))
    def addNext(self):
        ''' Creates next slide'''
        self.multiKwargs.append([])
        self.scrollBar.setMaximum(len(self.multiKwargs)-1)
        self.zSpinBox.setMaximum(len(self.multiKwargs)-1)
        
    def save(self):
        ''' saves figure'''
        fileName = str(QtGui.QFileDialog.getSaveFileName(self))
        self.graph.fig.savefig(fileName)
        
        