from PyQt5.QtCore import *
from PyQt5.QtGui import *
import RoiClass

class MyQGView(QGraphicsView):
    moved = pyqtSignal(QMouseEvent)

    def __init__(self, parent = None):
        super(MyQGView, self).__init__(parent)
        self.firstPoint = None
        self.lastPoint = None

    def mousePressEvent(self, event):
        button = event.button()
        if self.parent()!=None and self.parent().parent()!=None:
            if self.parent().parent().mouseState == 'zoom':
                self.parent().zoomImage(button)
            elif (self.parent().parent().mouseState == 'rectangle') or\
                 (self.parent().parent().mouseState == 'circle') or\
                 (self.parent().parent().mouseState == 'line') or\
                 (self.parent().parent().mouseState == 'point') or\
                 (self.parent().parent().mouseState == 'polygon'):
                for obj in self.parent().scene.items():
                        if (((type(obj)==QGraphicsRectItem) or\
                             (type(obj)==QGraphicsEllipseItem) or\
                             (type(obj)==QGraphicsLineItem)) and\
                            (self.parent().Roi.shape != 'polygon')) or\
                           ((self.parent().Roi.shape == 'polygon') and\
                            (type(obj)==QGraphicsPolygonItem)):
                            self.parent().scene.removeItem(obj)
                            self.parent().Roi.delete()
    # Get normalized to the image size position of the click                         
                self.firstPoint = self.mapToScene(event.pos())
                if int(self.firstPoint.x())<0:
                    self.firstPoint = QPoint(0,int(self.firstPoint.y()))
                if int(self.firstPoint.y())<0:
                    self.firstPoint = QPoint(int(self.firstPoint.x()),0)
                if int(self.firstPoint.x())>self.parent().image.imStack[0].size[0]*self.parent().image.zoomScale:
                    self.firstPoint =  QPoint(self.parent().image.imStack[0].size[0]*self.parent().image.zoomScale,int(self.firstPoint.y()))
                if int(self.firstPoint.y())>self.parent().image.imStack[0].size[1]*self.parent().image.zoomScale:
                    self.firstPoint = QPoint(int(self.firstPoint.x()),self.parent().image.imStack[0].size[1]*self.parent().image.zoomScale)
    # Add point to the scene if its points                
                if self.parent().parent().mouseState == 'point':
                    self.parent().Roi.shape = 'points'
                    self.parent().Roi.points = [[int(self.firstPoint.x()), int(self.firstPoint.y())]]
                    color = QColor(200,200,0)
                    self.parent().scene.addRect(int(self.firstPoint.x())-1, int(self.firstPoint.y())-1,
                                         1, 1,color)
    # Add vortex to the Roi if it is polygon
                if self.parent().parent().mouseState == 'polygon':
                    color = QColor(200,200,0)
                    if self.parent().Roi.shape == None:
                        self.parent().Roi.shape = 'polygon'
                        self.parent().Roi.points = [[int(self.firstPoint.x()),int(self.firstPoint.y())]]
                        self.setMouseTracking(True)
                    else:
                        if ((self.parent().Roi.points[0][0]-5 < int(self.firstPoint.x()) < self.parent().Roi.points[0][0]+5) and\
                           (self.parent().Roi.points[0][1]-5 < int(self.firstPoint.y()) < self.parent().Roi.points[0][1]+5)) or\
                           button == 2:
                            self.parent().Roi.addPoint(self.parent().Roi.points[0])
                        else:
                            self.parent().Roi.addPoint([int(self.firstPoint.x()),int(self.firstPoint.y())])
                        if QPolygonF(self.parent().Roi.getQPoints()).isClosed():
                            for obj in self.parent().scene.items():
                                if (type(obj)==QGraphicsRectItem) or\
                                   (type(obj)==QGraphicsEllipseItem) or\
                                   (type(obj)==QGraphicsLineItem) or\
                                   (type(obj)==QGraphicsPolygonItem):
                                    self.parent().scene.removeItem(obj)
                            self.parent().scene.addPolygon(QPolygonF(self.parent().Roi.getQPoints()),color)
                            self.setMouseTracking(False)
                self.lastPoint = None            
        
    def mouseMoveEvent(self, event):
        super(MyQGView, self).mouseMoveEvent(event)
#Renormalize position to the image size
        self.lastPoint = self.mapToScene(event.pos())
        if int(self.lastPoint.x())<0:
            self.lastPoint = QPoint(0,int(self.lastPoint.y()))
        if int(self.lastPoint.y())<0:
            self.lastPoint = QPoint(int(self.lastPoint.x()),0)
        if int(self.lastPoint.x())>self.parent().image.imStack[0].size[0]*self.parent().image.zoomScale:
            self.lastPoint =  QPoint(self.parent().image.imStack[0].size[0]*self.parent().image.zoomScale,int(self.lastPoint.y()))
        if int(self.lastPoint.y())>self.parent().image.imStack[0].size[1]*self.parent().image.zoomScale:
            self.lastPoint = QPoint(int(self.lastPoint.x()),self.parent().image.imStack[0].size[1]*self.parent().image.zoomScale)
            
        if self.parent()!=None:
            if (self.parent().parent().mouseState == 'rectangle') or\
                 (self.parent().parent().mouseState == 'circle') or\
                 (self.parent().parent().mouseState == 'line') or\
                 (self.parent().parent().mouseState == 'point') or\
                 (self.parent().parent().mouseState == 'polygon'):
                width = abs(int(self.lastPoint.x())-int(self.firstPoint.x()))
                height = abs(int(self.lastPoint.y())-int(self.firstPoint.y()))
                color = QColor(200,200,0)
                polyLines = []
        # Delete all drawn objects on the scene except points
                for obj in self.parent().scene.items():
                        if ((type(obj)==QGraphicsRectItem) or\
                           (type(obj)==QGraphicsEllipseItem) or\
                           (type(obj)==QGraphicsLineItem)) and\
                           (self.parent().parent().mouseState != 'point'):
                            self.parent().scene.removeItem(obj)
        # Draw rectangle                    
                if self.parent().parent().mouseState == 'rectangle':
                    self.parent().Roi = RoiClass.Roi('rectangle',[[int(self.firstPoint.x()),int(self.firstPoint.y())],
                                                                  [int(self.lastPoint.x()),int(self.lastPoint.y())]])
                    self.parent().scene.addRect(min(int(self.firstPoint.x()),int(self.lastPoint.x())),
                                         min(int(self.firstPoint.y()),int(self.lastPoint.y())),
                                         width, height,color)
        # Draw circle
                elif self.parent().parent().mouseState == 'circle':
                    self.parent().Roi = RoiClass.Roi('circle',[[int(self.firstPoint.x()),int(self.firstPoint.y())],
                                                                  [int(self.lastPoint.x()),int(self.lastPoint.y())]])
                    self.parent().scene.addEllipse(min(int(self.firstPoint.x()),int(self.lastPoint.x())),
                                         min(int(self.firstPoint.y()),int(self.lastPoint.y())),
                                         width, height,color)
        # Draw line
                elif self.parent().parent().mouseState == 'line':
                    self.parent().Roi = RoiClass.Roi('line',[[int(self.firstPoint.x()),int(self.firstPoint.y())],
                                                                  [int(self.lastPoint.x()),int(self.lastPoint.y())]])
                    self.parent().scene.addLine(int(self.firstPoint.x()), int(self.firstPoint.y()),
                                         int(self.lastPoint.x()), int(self.lastPoint.y()),color)
        # Draw polygon
                elif self.parent().parent().mouseState == 'polygon':
                    first = self.parent().Roi.points[0]
                    for point in self.parent().Roi.points[1:]:
                        self.parent().scene.addLine(first[0], first[1],
                                             point[0],point[1],color)
                        first = point
                    self.parent().scene.addLine(int(self.firstPoint.x()), int(self.firstPoint.y()),
                                         int(self.lastPoint.x()), int(self.lastPoint.y()),color)