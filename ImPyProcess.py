'''
Created on Dec 14, 2011

@author: renat
'''
import Image, ImageFilter, numpy, ImPyClasses

def applyGaussBlur(imageSeq,radius=2):
    gaussBlur=[]
    for image in imageSeq:
        gaussBlur.append(image.filter(ImageFilter.BLUR))
    return gaussBlur