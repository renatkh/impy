import Image
from ImageConvertions import *
import Image

from ImageConvertions import *


class ImpyImage:
    def __init__(self,fileName,parent=None,imStack=None, arrayStack=None):
        # Define all elements necessary for the image manipulations
        self.parent = parent
        self.fileName = fileName
        self.imStack = []
        self.arrayStack = []
        self.frameRate = 25 #frames/second that the sequence is played
        self.zoomScale = 1.0 #scale to the original image size
        self.threshhold = None
        
        #default values for contrast and brightness
        self.maxPixelValue = 255
        self.thresholdMaximum = self.maxPixelValue
        self.thresholdMinimum = 0
        self.brightness = 50
        self.contrast = 50
        
        # Load sequence of images, create arrays and
        # surfaces (difference from arrays in coordinate system [x,y]) of intensities
        if imStack == None and arrayStack == None:
            self.imStack = []
            self.arrayStack = []
            imTmp = Image.open(fileName)
            try:
                while 1:
                    self.imStack.append(imTmp.point(lambda i: i))
                    imTmp.seek(imTmp.tell()+1)
            except EOFError:
                pass # end of sequence
            for imTmp in self.imStack:
                self.arrayStack.append(numpy.asarray(imTmp))
        elif imStack != None:
            self.imStack = imStack
            for imTmp in self.imStack:
                self.arrayStack.append(numpy.asarray(imTmp))
        elif arrayStack != None:
            self.arrayStack = arrayStack
            for arrayTmp in self.arrayStack:
                self.imStack.append(Image.fromarray(arrayTmp))
      
    # define various functions and operations with the image
    def makeSubArray (self,area):
        pass
#        return ImageObj(array = self.array[max(area.box_ind[0],0):min(area.box_ind[0]+area.size,self.array.shape[0]),\
#                                            max(area.box_ind[1],0):min(area.box_ind[1]+area.size,self.array.shape[1])])
#                                       max(area.box_coor[1],0):min(area.box_coor[1]+area.size,self.surf.shape[1])])
    def plotSurf3D (self):
        pass