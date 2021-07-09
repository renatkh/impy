'''
Created on Jan 10, 2012

@author: renat
'''
import numpy,cv
from PIL import Image
from PyQt5 import QtCore, QtGui


def PIL2QImage(pilimage):
    w,h = pilimage.size
    if pilimage.mode != "RGBA":
        pilimage = pilimage.convert("RGBA")
    if w % 4 != 0:
        w = w + 4 - (w % 4)
        pilimage = pilimage.resize([w, h])
    w,h = pilimage.size
    data = pilimage.tostring("raw", "RGBA")
    qimage = QtGui.QImage(data, w, h, QtGui.QImage.Format_ARGB32)
    return qimage

def PIL2QPixmap(pilimage):
    qimage = PIL2QImage(pilimage)
    pix = QtGui.QPixmap.fromImage(qimage)
    return pix

def QImage2PIL(qimage):
    buffer = QtCore.QBuffer()
    buffer.open(QtCore.QIODevice.ReadWrite)
    qimage.save(buffer, "TIF")
    strio = cStringIO.StringIO()
    strio.write(buffer.data())
    buffer.close()
    strio.seek(0)
    pil_im = Image.open(strio)
    return pil_im

def QImage2numpy(qimage, dtype = 'array'):
    """Convert QImage to numpy.ndarray.  The dtype defaults to uint8
    for QImage.Format_Indexed8 or `bgra_dtype` (i.e. a record array)
    for 32bit color images.  You can pass a different dtype to use, or
    'array' to get a 3D uint8 array for color images."""
    result_shape = (qimage.height(), qimage.width())
    temp_shape = (qimage.height(),
                  qimage.bytesPerLine() * 8 / qimage.depth())
    if qimage.format() in (QtGui.QImage.Format_ARGB32_Premultiplied,
                           QtGui.QImage.Format_ARGB32,
                           QtGui.QImage.Format_RGB32):
        if dtype == 'rec':
            dtype = QtGui.bgra_dtype
        elif dtype == 'array':
            dtype = numpy.uint8
            result_shape += (4, )
            temp_shape += (4, )
    elif qimage.format() == QtGui.QImage.Format_Indexed8:
        dtype = numpy.uint8
    else:
        raise ValueError("qimage2numpy only supports 32bit and 8bit images")
    # FIXME: raise error if alignment does not match
    buf = qimage.bits().asstring(qimage.numBytes())
    result = numpy.frombuffer(buf, dtype).reshape(temp_shape)
    if result_shape != temp_shape:
        result = result[:,:result_shape[1]]
    if qimage.format() == QtGui.QImage.Format_RGB32 and dtype == numpy.uint8:
        result = result[...,:3]
    return result

def numpy2QImage(array):
    if numpy.ndim(array) == 2:
        return gray2qimage(array)
    elif numpy.ndim(array) == 3:
        return rgb2qimage(array)
    raise ValueError("can only convert 2D or 3D arrays")

def gray2qimage(gray):
    """Convert the 2D numpy array `gray` into a 8-bit QImage with a gray
    colormap.  The first dimension represents the vertical image axis.

    ATTENTION: This QImage carries an attribute `ndimage` with a
    reference to the underlying numpy array that holds the data. On
    Windows, the conversion into a QPixmap does not copy the data, so
    that you have to take care that the QImage does not get garbage
    collected (otherwise PyQt will throw away the wrapper, effectively
    freeing the underlying memory - boom!)."""
    if len(gray.shape) != 2:
        raise ValueError("gray2QImage can only convert 2D arrays")

    gray = numpy.require(gray, numpy.uint8, 'C')

    h, w = gray.shape

    result = QtGui.QImage(gray.data, w, h, QtGui.QImage.Format_Indexed8)
    result.ndarray = gray
    for i in range(256):
        result.setColor(i, QtGui.QColor(i, i, i).rgb())
    return result

def rgb2qimage(rgb):
    """Convert the 3D numpy array `rgb` into a 32-bit QImage.  `rgb` must
    have three dimensions with the vertical, horizontal and RGB image axes.

    ATTENTION: This QImage carries an attribute `ndimage` with a
    reference to the underlying numpy array that holds the data. On
    Windows, the conversion into a QPixmap does not copy the data, so
    that you have to take care that the QImage does not get garbage
    collected (otherwise PyQt will throw away the wrapper, effectively
    freeing the underlying memory - boom!)."""
    if len(rgb.shape) != 3:
        raise ValueError("rgb2QImage can only convert 3D arrays")
    if rgb.shape[2] not in (3, 4):
        raise ValueError("rgb2QImage can expects the last dimension to contain exactly three (R,G,B) or four (R,G,B,A) channels")

    h, w, channels = rgb.shape

    # Qt expects 32bit BGRA data for color images:
    bgra = numpy.empty((h, w, 4), numpy.uint8, 'C')
    bgra[...,0] = rgb[...,2]
    bgra[...,1] = rgb[...,1]
    bgra[...,2] = rgb[...,0]
    if rgb.shape[2] == 3:
        bgra[...,3].fill(255)
        fmt = QtGui.QImage.Format_RGB32
    else:
        bgra[...,3] = rgb[...,3]
        fmt = QtGui.QImage.Format_ARGB32

    result = QtGui.QImage(bgra.data, w, h, fmt)
    result.ndarray = bgra
    return result

def PIL2CV(pil_img):
    if pil_img.mode == "L":
        pil_img = Image.merge("RGB", (pil_img,pil_img,pil_img))
    cv_img = cv.CreateImageHeader(pil_img.size, cv.IPL_DEPTH_8U, 3)  # RGB image
    cv.SetData(cv_img, pil_img.tostring())#, pil_img.size[0]*3)
    return cv_img

def CV2PIL(cvImage):
    return Image.fromstring("L", cv.GetSize(cvImage), cvImage.tostring())

def cv2array(im):
    depth2dtype = {
        cv.IPL_DEPTH_8U: 'uint8',
        cv.IPL_DEPTH_8S: 'int8',
        cv.IPL_DEPTH_16U: 'uint16',
        cv.IPL_DEPTH_16S: 'int16',
        cv.IPL_DEPTH_32S: 'int32',
        cv.IPL_DEPTH_32F: 'float32',
        cv.IPL_DEPTH_64F: 'float64',
    }

    arrdtype=im.depth
    a = numpy.fromstring(
         im.tostring(),
         dtype=depth2dtype[im.depth],
         count=im.width*im.height*im.nChannels)
    a.shape = (im.height,im.width,im.nChannels)
    return a

def array2cv(a):
    dtype2depth = {
        'uint8':   cv.IPL_DEPTH_8U,
        'int8':    cv.IPL_DEPTH_8S,
        'uint16':  cv.IPL_DEPTH_16U,
        'int16':   cv.IPL_DEPTH_16S,
        'int32':   cv.IPL_DEPTH_32S,
        'float32': cv.IPL_DEPTH_32F,
        'float64': cv.IPL_DEPTH_64F,
    }
    try:
        nChannels = a.shape[2]
    except:
        nChannels = 1
    cv_im = cv.CreateImageHeader((a.shape[1],a.shape[0]),
                                 dtype2depth[str(a.dtype)],
                                 nChannels)
    cv.SetData(cv_im, a.tostring(),
               a.dtype.itemsize*nChannels*a.shape[1])
    return cv_im
