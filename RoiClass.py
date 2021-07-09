'''
Created on Mar 31, 2012

@author: renat
'''
from PyQt5 import QtCore, QtGui

class Roi:
    def __init__(self, shape=None, points=[[0,0],[0,0]]):
        self.shape = shape
        self.points = points
        self.getBox()
    
    def getBox(self):
        self.topLBox = [min([self.points[i][0] for i in range(len(self.points))]),\
                        min([self.points[i][1] for i in range(len(self.points))])]
        self.botRBox = [max([self.points[i][0] for i in range(len(self.points))]),\
                        max([self.points[i][1] for i in range(len(self.points))])]
        self.width = self.botRBox[0]-self.topLBox[0]
        self.height = self.botRBox[1]-self.topLBox[1]
    
    def getQPoints(self):
        return [QtCore.QPointF(self.points[i][0],self.points[i][1]) for i in range(len(self.points))]
    
    def delete(self):
        self.shape = None
        self.points = [[0,0],[0,0]]
        self.getBox()
        
    def addPoint(self,point):
        if self.shape == 'polygon' or self.shape == 'points':
            self.points.append(point)
            self.getBox()
    
    def scale(self,scale):
        self.points = [[x*scale,y*scale] for [x,y] in self.points]
        self.getBox()
    
    def checkPointIn(self,pos):
        if self.shape == 'rectangle':
            if (self.topLBox[0] <= pos[0] <= self.botRBox[0]) and\
               (self.topLBox[1] <= pos[1] <= self.botRBox[1]):
                return True
            else:
                return False
        elif self.shape == 'circle':
            center = (self.botRBox[0]+self.topLBox[0])/2
            a = self.botRBox[0]-self.topLBox[0]
            b = self.botRBox[1]-self.topLBox[1]
            pointLXSQR = 1 - (pos[1]-center[1])**2/b**2
            if (pointLXSQR >= 0):
                if (-sqrt(pointLXSQRT) <= pos[0]-center[0] <= sqrt(pointLXSQRT)):
                    return True
                else:
                    return False
            else:
                return False
            
        else:
            # polygon vertex check
            if pos in self.points: return True
            # boundary check
            for i in range(len(self.points)-1):
                if (self.points[i][0] == self.points[i][0] == x) and \
                   (min(self.points[i][1], self.points[i-1][1]) <= y <= \
                    max(self.points[i][1], self.points[i-1][1])):
                    return True
                elif (self.points[i][1] == self.points[i][1] == y) and \
                   (min(self.points[i][0], self.points[i-1][0]) <= x <= \
                    max(self.points[i][0], self.points[i-1][0])):
                    return True
            result = False
            point = self.points[0]
            for i in range(n+1):
                next = self.points[i % n]
                if (min(first[1],next[1]) <= pos[1] < max(first[1],next[1])):
                    x = (pos[1]-first[1])*(next[0]-first[0])/(next[1]-first[1]) + first[0]
                    if x > pos[0]:
                        result = not result
                first = next
            return result
        
        