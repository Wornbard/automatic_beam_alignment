from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
 
def gauss(x,a,x0,sigma,b):
    return b+a*np.exp(-(x-x0)**2/(2*sigma**2))
 
def find_center(imgarray):
    imgarray=imgarray[:,:,0]
    maxval=np.max(imgarray)
    noiseval=maxval/2
    for i in range(imgarray.shape[0]):
        for j in range(imgarray.shape[1]):
            if imgarray[i,j]<noiseval:
                imgarray[i,j]=0
            else:
                imgarray[i,j]-=noiseval
    colsum=imgarray.sum(axis=0)
    colprefix=np.cumsum(colsum)
    i=0
    x0=0
    while(2*colprefix[i]<colprefix[-1]):
        i+=1
    x0=i
    rowsum=imgarray.sum(axis=1)
    rowprefix=np.cumsum(rowsum)
    j=0
    y0=0
    while(2*rowprefix[j]<rowprefix[-1]):
        j+=1
    y0=j
    collen=np.linspace(0,colsum.size-1,colsum.size)
    rowlen=np.linspace(0,rowsum.size-1,rowsum.size)
    cpopt,cpcov=curve_fit(gauss,collen,colsum,p0=[1,x0,1,0])
    rpopt,rpcov=curve_fit(gauss,rowlen,rowsum,[1,y0,1,0])
    peak={'x':cpopt[1],'y':rpopt[1]}
    return peak
