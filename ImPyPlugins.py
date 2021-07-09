'''
Created on Dec 14, 2011

@author: renat
'''
import numpy, ImPyClasses

def BALM(imageArraySeq):
    balm = []
    for i in range(len(imageArraySeq)-1):
        slide1 = numpy.array(imageArraySeq[i], numpy.int16)
        slide2 = numpy.array(imageArraySeq[i+1], numpy.int16)
        balm.append(numpy.array(abs(slide1-slide2), numpy.uint8))
    return balm