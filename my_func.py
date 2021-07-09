import Image,numpy,math, pylab, scipy
import mpl_toolkits.mplot3d.axes3d as p3
from mayavi import mlab
import matplotlib.pyplot as plt
import gaussfitter
from scipy import ndimage

class Image_obj:
    def __init__ (self, image=None,array=None,surf=None):
        if image != None:
            self.im = image
            self.array = image2array(image)
            self.surf = numpy.transpose(self.array[::-1,:])
#            self.surf = self.array[::-1,:]
        elif array != None:
            self.array = array
            self.im = array2image(array)
            self.surf = numpy.transpose(self.array[::-1,:])
        elif surf != None:
            self.surf = surf
            self.array = numpy.transpose(self.surf[:,::-1])
            self.im = array2image(self.array)
    def sub_arr (self,circ):
        return Image_obj(array = self.array[max(circ.box_ind[0],0):min(circ.box_ind[0]+circ.size,self.array.shape[0]),\
                                            max(circ.box_ind[1],0):min(circ.box_ind[1]+circ.size,self.array.shape[1])])
    def sub_surf (self,circ):
        return Image_obj(surf = self.surf[max(circ.box_coor[0],0):min(circ.box_coor[0]+circ.size,self.surf.shape[0]),\
                                            max(circ.box_coor[1],0):min(circ.box_coor[1]+circ.size,self.surf.shape[1])])
    def show_im (self):
        self.im.show()
    def show_surf (self):
        x, y = numpy.meshgrid(numpy.arange(self.surf.shape[0]),numpy.arange(self.surf.shape[1]))
        return mlab.mesh(x,y,self.surf)

class Circ_obj:
    def __init__ (self, size, pos, im_size, col='white'):
        self.size = size
        self.im_size = numpy.array(im_size)
        self.coor = numpy.array(pos)
        self.ind = numpy.array(pos[::-1])
        self.ind[0] = self.im_size[1] - self.ind[0]
        self.box_coor = self.coor - self.size/2
        self.box_ind = self.ind - self.size/2
    def coor_set (self, pos):
        pos = numpy.round(pos)
        self.coor = numpy.array(pos)
        self.ind = numpy.array(pos[::-1])
        self.ind[0] = self.im_size[1] - self.ind[0]
        self.box_coor = self.coor - self.size/2
        self.box_ind = self.ind - self.size/2
    def ind_set (self, pos):
        pos = numpy.round(pos)
        self.ind = numpy.array(pos)
        self.coor = numpy.array(pos[::-1])
        self.coor[1] = self.im_size[1] - self.ind[1]
        self.box_coor = self.coor - self.size/2
        self.box_ind = self.ind - self.size/2
    def size_set (self, size):
        self.size = size
        self.box_coor = self.coor - self.size/2
        self.box_ind = self.ind - self.size/2
#-------------------------------------------------------------------------------------------------
def fit_gauss(im,im2,circ,adjust,n=1, param_guess = []):
    param_guess = numpy.array(param_guess)
    if param_guess.size > 0:
        param_guess[3:5] = [circ.size/2,circ.size/2]    

    im_ini = im.sub_surf(circ)
    g_params_ini= gaussfitter.gaussfit(im_ini.surf,params=[],limitedmin=numpy.repeat(True,7),
            limitedmax=numpy.repeat(True,7), minpars=[0,1,0,0,1,1,0],\
            maxpars=[im_ini.surf.max(),im_ini.surf.max(),im_ini.surf.shape[0],im_ini.surf.shape[1],\
                    2*im_ini.surf.shape[0],2*im_ini.surf.shape[1],180])
    def show_fit(params,im,circ):
        ## Plot fit and data
        im_tmp = im.sub_surf(circ)
        x, y = numpy.meshgrid(numpy.arange(im_tmp.surf.shape[0]),numpy.arange(im_tmp.surf.shape[1]))
        s = mlab.mesh(x,y,numpy.transpose(im_tmp.surf))
        G_fit = gaussfitter.twodgaussian(params,0,1,1)(*[x,y])
        s2 = mlab.mesh(x,y,G_fit)
        mlab.show()
#---------------------------------------------------------------------- 
    def fit_params(size,x,y):
        #cut piece of image size size start at x and y in image coordinats
        base = g_params_ini[0][0]
        usemoment = numpy.array([],dtype='bool')
        circ_tmp = Circ_obj(size,[x,y],im.im.size)
        im_fit = im.sub_surf(circ_tmp)
        result = gaussfitter.gaussfit(im_fit.surf-base,params=param_guess[2:8],usemoment=usemoment,vheight=0,\
                 returnfitimage=True,limitedmin=numpy.repeat(True,7),limitedmax=numpy.repeat(True,7),\
                 minpars=[0,1,0,0,1,1,0],maxpars=[im_fit.surf.max(),im_fit.surf.max(),im_fit.surf.shape[0],\
                                    im_fit.surf.shape[1],2*im_fit.surf.shape[0],2*im_fit.surf.shape[1],180])
            # fit Gauss    
        return result
#----------------------------------------------------------------------    
    def fit_adjusting():
        def error_size(pars):
            size = pars[0].astype(int)
            x = pars[1].astype(int)
            y = pars[2].astype(int)
            if con1(pars)>0 and con2(pars)>0 and con3(pars)>0 and con4(pars)>0 and con5(pars)>0 and con6(pars)>0:
                fit_err = fit_params(size,x,y)[0][1]
                err = numpy.sqrt(sum(fit_err[2:4]**2))
            else:
                err = 100.
            return err
        
        def con1(pars):
            return pars[0]-4
        def con2(pars):
            return circ.size-pars[0]
        def con3(pars):
            return pars[1]-circ.box_coor[0]-pars[0]
        def con4(pars):
            return circ.box_coor[0]+circ.size-pars[1]-pars[0]
        def con5(pars):
            return pars[2]-circ.box_coor[1]-pars[0]
        def con6(pars):
            return circ.box_coor[1]+circ.size-pars[2]-pars[0]
        best_coor = scipy.optimize.fmin_cobyla(error_size,x0=ini_guess,cons=[con1,con2,con3,con4,con5,con6],\
                                            args=(),rhobeg=[-circ.size/3,1,1],rhoend=0.1,iprint=0,maxfun=100).astype(int)
        
        [g_params, G_fit] = fit_params(*best_coor)
        g_params[0][2] = g_params[0][2] + (best_coor[1] - best_coor[0]/2 - circ.box_coor[0])
        g_params[0][3] = g_params[0][3] + (best_coor[2] - best_coor[0]/2 - circ.box_coor[1])
        g_params[0][0] = g_params_ini[0][0]
        g_params[1][0] = g_params_ini[1][0]
        g_params[1][1] = g_params[1][0]+g_params[1][1]
        g_params=adj_base_int(g_params,im,circ)
        show_fit(g_params[0],im,circ)
        ch2_params=fit_ch2(g_params,best_coor)
        g_params[0][2] = g_params[0][2] + circ.box_coor[0]
        g_params[0][3] = g_params[0][3] + circ.box_coor[1]
        ch2_params[0][2] = ch2_params[0][2] + circ.box_coor[0]
        ch2_params[0][3] = ch2_params[0][3] + circ.box_coor[1]
        return ch2_params
#---------------------------------------------------------------------- 
    def fit_ch2(params,best_coor):
        usemoment = numpy.repeat(False,7)
        circ_tmp = Circ_obj(best_coor[0],best_coor[1:],im2.im.size)
        im_fit = im2.sub_surf(circ_tmp)
        guess = params[0][0:7]
        guess[2] = guess[2] - (best_coor[1] - best_coor[0]/2 - circ.box_coor[0])
        guess[3] = guess[3] - (best_coor[2] - best_coor[0]/2 - circ.box_coor[1])
        fixed = [False,False,True,True,True,True,True]
        result = gaussfitter.gaussfit(im_fit.surf,params=guess,usemoment=usemoment,vheight=1,fixed=fixed,\
                 limitedmin=numpy.repeat(True,7),limitedmax=numpy.repeat(True,7),\
                 minpars=[0,0,0,0,1,1,0],maxpars=[im_fit.surf.max(),im_fit.surf.max(),im_fit.surf.shape[0],\
                                    im_fit.surf.shape[1],2*im_fit.surf.shape[0],2*im_fit.surf.shape[1],180])
        result[0][2] = result[0][2] + (best_coor[1] - best_coor[0]/2 - circ.box_coor[0])
        result[0][3] = result[0][3] + (best_coor[2] - best_coor[0]/2 - circ.box_coor[1])
        result = adj_base_int(result,im2,circ)
        show_fit(result[0],im2,circ)
        return result
#----------------------------------------------------------------------    
    def adj_base_int(g_params,im,circ):
        im_ini = im.sub_surf(circ)
        def base_int(tmp):
            params = numpy.zeros(7)
            params = numpy.array(g_params[0][0:7])
            params[0] = tmp[0]
            params[1] = tmp[1]
            x, y = numpy.meshgrid(numpy.arange(im_ini.surf.shape[0]),numpy.arange(im_ini.surf.shape[1]))
            return sum(sum((numpy.transpose(im_ini.surf)-gaussfitter.twodgaussian(params,0,1,1)(*[x,y]))**2))
        def con1(pars):
            return pars[0]
        def con2(pars):
            return pars[1]
        g_params[0][0:2] = scipy.optimize.fmin_cobyla(base_int,x0=g_params[0][0:2],cons=[con1,con2],\
                        args=(),rhobeg=[10,0,0],rhoend=0.1,iprint=0,maxfun=100).astype(int)
        chi_sq=[]
        x = []
        params_tmp = numpy.zeros(2)
        for k in range(-5,5):
            if g_params[0][0] == 0:
                params_tmp[0] =  k*0.02
                params_tmp[1] = g_params[0][1] - k*0.02
            else:
                params_tmp[0] = g_params[0][0]*(1. + k*0.02)
                params_tmp[1] = g_params[0][1] - g_params[0][0]* k*0.02
            chi_sq = numpy.append(chi_sq,base_int(params_tmp[0:2]))
            x = numpy.append(x,params_tmp[0])
        def errfunc(p, y, x):
            res = (y - p[0]*(x-p[2])**2-p[1])**2
            return res
        pinit = [-1.,chi_sq[5],g_params[0][0]]
        fit_value = scipy.optimize.leastsq(errfunc, pinit, args=(chi_sq,x))[0]
        if fit_value[0]>0:
            error = numpy.sqrt(1./fit_value[0])
            g_params[0][1] = g_params[0][1]+g_params[0][0]-fit_value[2]
            g_params[0][0] = fit_value[2]
            g_params[1][0] = error
            g_params[1][1] = g_params[1][1]+error
        return g_params
#---------------------------------------------------------------------- 
    def find_obj():
        def check_obj(x,y):
            params = param_guess[1:8]
            params[2] = x
            params[3] = y
            size = 2*numpy.round(params[4])
            circ_tmp = Circ_obj(size,[x,y],im_ini.im.size)
            im_tmp = im_ini.sub_surf(circ_tmp)
            x, y = numpy.meshgrid(numpy.arange(im_ini.surf.shape[0]),numpy.arange(im_ini.surf.shape[1]))
            fit_err = numpy.transpose(im_tmp.surf) - gaussfitter.twodgaussian(params,0,1,1)\
                                     (*[x[max(circ_tmp.box_coor[1],0):min(circ_tmp.box_coor[1]+circ_tmp.size+1,max(circ_tmp.box_coor[1],0)+im_tmp.surf.shape[1]),\
                                          max(circ_tmp.box_coor[0],0):min(circ_tmp.box_coor[0]+circ_tmp.size+1,max(circ_tmp.box_coor[0],0)+im_tmp.surf.shape[0])],\
                                        y[max(circ_tmp.box_coor[1],0):min(circ_tmp.box_coor[1]+circ_tmp.size+1,max(circ_tmp.box_coor[1],0)+im_tmp.surf.shape[1]),\
                                          max(circ_tmp.box_coor[0],0):min(circ_tmp.box_coor[0]+circ_tmp.size+1,max(circ_tmp.box_coor[0],0)+im_tmp.surf.shape[0])]])
            err = sum(sum(fit_err**2))/fit_err.size
            return err
    
        def con2(pars):
            return pars[1]
        def con3(pars):
            return circ_size-pars[1]
        def con4(pars):
            return pars[2]
        def con5(pars):
            return circ_size-pars[2]
        err_m = numpy.zeros([im_ini.surf.shape[0]-4*numpy.int(param_guess[5]),im_ini.surf.shape[1]-4*numpy.int(param_guess[5])])
        for i in range(im_ini.surf.shape[0]-4*numpy.int(param_guess[5])):
            for j in range(im_ini.surf.shape[1]-4*numpy.int(param_guess[5])):
                err_m[i,j] = check_obj(i+2*numpy.round(param_guess[5]),j+2*numpy.round(param_guess[5]))
        best_coor = numpy.zeros(3)
        best_coor[0] = min(param_guess[5],param_guess[6])
        best_coor[1] = numpy.where(err_m == err_m.ravel()[err_m.argmin()])[0] + circ.box_coor[0] + 2*numpy.round(param_guess[5])
        best_coor[2] = numpy.where(err_m == err_m.ravel()[err_m.argmin()])[1] + circ.box_coor[1] + 2*numpy.round(param_guess[5])
        [g_params, G_fit] = fit_params(*best_coor)
        g_params[0][2] = g_params[0][2] + (best_coor[1] - best_coor[0]/2 - circ.box_coor[0])
        g_params[0][3] = g_params[0][3] + (best_coor[2] - best_coor[0]/2 - circ.box_coor[1])
        g_params[0][0] = g_params_ini[0][0]
        show_fit(g_params[0])
        g_params[0][2] = g_params[0][2] + circ.box_coor[0]
        g_params[0][3] = g_params[0][3] + circ.box_coor[1]
        return g_params
#---------------------------------------------------------------------- 
    ini_guess = numpy.append(circ.size,circ.coor)
    if adjust ==1:
        g_params = fit_adjusting()
    else:
        g_params = g_params_ini
        show_fit(g_params[0],im,circ)
        g_params[0][2] = g_params[0][2] + circ.box_coor[0]
        g_params[0][3] = g_params[0][3] + circ.box_coor[1]
    return g_params
#-------------------------------------------------------------------------------------------------
def show_prof(im,circ_pos,circ_size,angle):
    im_a = image2array(im)[circ_pos[1]-circ_size/2:circ_pos[1]+circ_size/2,circ_pos[0]-circ_size/2:circ_pos[0]+circ_size/2]
    im_prof1 = image2array(array2image(im_a).rotate(angle))[:,circ_size/2]
    im_prof2 = image2array(array2image(im_a).rotate(angle))[circ_size/2,:]
    y1 = im_prof1.ravel()
    y2 = im_prof2.ravel()
    x = numpy.arange(y1.size)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x,y1)
    ax.plot(x,y2)
    plt.show()

def open_image(filename="/home/renat/Documents/work/imaging/ems_GFP_Z=4.tif",im_num=0):
    im = Image.open(filename)
    im.seek(im_num)
    im.show()
    return im

def image2array(im):
    """Convert image to Numeric array"""
    if im.mode not in ("L", "I;16B", "F"):
        raise ValueError, "can only convert math.single-layer images"
    if im.mode == "L":
         a = numpy.array([im.getdata()], numpy.uint8)
    if im.mode == "I;16B":
         a = numpy.array( [im.getdata()], numpy.int16)
    if im.mode == "F":
         a = numpy.array( [im.getdata()], numpy.Float32)
    a.shape = im.size[1], im.size[0]
    return a
    
def array2image(a):
    """Convert Numeric array to image"""
    if a.dtype == numpy.uint8:
         mode = "L"
    elif a.dtype == numpy.Float32:
         mode = "F"
    elif a.dtype == numpy.Int16:
         mode = "I;16"
    else:
         raise ValueError, "unsupported image mode"
    return Image.fromstring(mode, (a.shape[1], a.shape[0]), a.tostring())

def arr2coor (a):
    """Converts multidimensional matrix to an array of elements indexes and value"""
    out=[]
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
          out.append([i,j,a[i,j]])
    return numpy.array(out) 

# threshold. input is an array of intensities.
def thresh(a,th):
    outa=numpy.array(zero_matrix(len(a[:,1]),len(a[0,:])),dtype=a.dtype)
    for i in (0..len(a[:,1])-1):
        for k in (0..len(a[0,:])-1):
            if a[i,k] > th : outa[i,k] = a[i,k]
    return outa
    
#edge tracking function for grayscale images. Input is an image file.
def prewitt(a): 
    img=array2image(a)
    math.pixels=list(img.getdata())
    width, height =img.size
    xmask, ymask = get_prewitt_masks() 
 
    # create a new greyscale image for the output 
    outimg = Image.new('L', (width, height)) 
    outmath.pixels = list(outimg.getdata()) 
    outangles = list(outimg.getdata())
 
    for y in xrange(height-1): 
        for x in xrange(width-1): 
            sumX, sumY, magnitude = 0, 0, 0 
 
            if y == 0 or y == height-1: magnitude = 0 
            elif x == 0 or x == width-1: magnitude = 0 
            else: 
                for i in xrange(-1, 2): 
                    for j in xrange(-1, 2): 
                        # convolve the image math.pixels with the Prewitt mask, approximating x 
                        sumX += (math.pixels[x+i+(y+j)*width]) * xmask[i+1, j+1] 
 
            for i in xrange(-1, 2): 
                for j in xrange(-1, 2): 
                    # convolve the image math.pixels with the Prewitt mask, approximating y 
                    sumY += (math.pixels[x+i+(y+j)*width]) * ymask[i+1, j+1] 
 
            # approximate the magnitude of the gradient 
            magnitude = abs(sumX) + abs(sumY)
            if sumX > 0: theta=arctan(sumY/sumX)
            if sumX ==0: theta=math.pi/2
            
            if magnitude > 255 : magnitude = 255 
            if magnitude < 0 : magnitude = 0 
            outmath.pixels[x+y*width] = magnitude 
            outangles[x+y*width] = theta
 
    outimg.putdata(outmath.pixels) 
    return outimg,outmath.pixels,outangles

# Uses hashes of tuples to simulate 2-d arrays for the masks. 
def get_prewitt_masks(): 
    xmask = {} 
    ymask = {} 
 
    xmask[(0,0)] = -1 
    xmask[(0,1)] = 0 
    xmask[(0,2)] = 1 
    xmask[(1,0)] = -1 
    xmask[(1,1)] = 0 
    xmask[(1,2)] = 1 
    xmask[(2,0)] = -1 
    xmask[(2,1)] = 0 
    xmask[(2,2)] = 1 

    ymask[(0,0)] = 1 
    ymask[(0,1)] = 1 
    ymask[(0,2)] = 1 
    ymask[(1,0)] = 0 
    ymask[(1,1)] = 0 
    ymask[(1,2)] = 0 
    ymask[(2,0)] = -1 
    ymask[(2,1)] = -1 
    ymask[(2,2)] = -1 
    return (xmask, ymask)
    
def gaussian2(height, center_x, center_y, width_x, width_y,center_x2):
    """Returns a sum of 2 gaussian functions with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    
    return lambda x,y: height*exp(-(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)+\
        height*exp(-(((center_x2-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

def fit2gaussian(data,params):
#    params are parameters of a single gaussian fit. 
    data_tmp=data[0:params[1]+1,:]
    params = numpy.array(moments(data_tmp))
    errorfunction = lambda p: numpy.ravel(gaussian(*p[0:5])(*numpy.indices(data_tmp.shape)) - (data_tmp-p[5]))
    p, success = optimize.leastsq(errorfunction, params)
    x, y = numpy.meshgrid(range(data_tmp.shape[1]),range(data_tmp.shape[0]))
    G_fit=gaussian(*p[0:5])(x,y)+p[5]
    s = mlab.mesh(x,y,data_tmp)
    s2 = mlab.mesh(y,x,G_fit)
    mlab.show()
    data=data-gaussian(*p[0:5])(*numpy.indices(data.shape))
    p2=fitgaussian(data)
    return numpy.append(p[0:5],p2)