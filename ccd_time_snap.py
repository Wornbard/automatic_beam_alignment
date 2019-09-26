# -*- coding: utf-8 -*-
"""
Created on Mon May 27 12:19:20 2019

@author: koray
"""

import time

def UEye420_Snapper(Exposure,Gain,File_Location,pixel_clock):
    from pyueye import ueye
    import ctypes
    import time
    
    saved=False
    while saved==False:
        #CCD Settings and Start-Up
        hcam = ueye.HIDS(0)
        pccmem = ueye.c_mem_p()
        memID = ueye.c_int()
        hWnd = ctypes.c_voidp()
        ueye.is_InitCamera(hcam, hWnd)
        ueye.is_SetDisplayMode(hcam, 0)
        sensorinfo = ueye.SENSORINFO()
        ueye.is_GetSensorInfo(hcam, sensorinfo)
        ueye.is_AllocImageMem(hcam, sensorinfo.nMaxWidth, sensorinfo.nMaxHeight,24, pccmem, memID)
        ueye.is_SetImageMem(hcam, pccmem, memID)
        ueye.is_SetDisplayPos(hcam, 100, 100)


        PIXELCLOCK_CMD_SET=6 
        PIXELCLOCK_CMD_GET=4        
        
        pixel=ctypes.c_uint(pixel_clock)
        ueye.is_PixelClock(hcam, PIXELCLOCK_CMD_SET, pixel, ctypes.sizeof(pixel)) 
        print ('PX=',pixel)
        
        exposure_time=ctypes.c_double(Exposure) #Exposure time in miliseconds
        value=ctypes.c_int(Gain)
        ueye.is_SetHWGainFactor(hcam, ueye.IS_SET_MASTER_GAIN_FACTOR, value)
        ueye.is_Exposure(hcam,ueye.IS_EXPOSURE_CMD_SET_EXPOSURE,exposure_time,ctypes.sizeof(ctypes.c_double))        
        
        print ('Exposure (ms) =',exposure_time)
        print ('Gain = ',Gain)
        time.sleep(float(Exposure*1e-4)*1.0+0.2) #Some time for CCD to set new exposure time
        #initially set to float(Exposure*1e-4)*1.0+1.0 and it works then
        nret = ueye.is_FreezeVideo(hcam, ueye.IS_WAIT) #Freeze/Snap

        #Save Parameters       
        FileParams = ueye.IMAGE_FILE_PARAMS()
        FileParams.pwchFileName = (File_Location)
        FileParams.nFileType = ueye.IS_IMG_BMP
        FileParams.ppcImageMem = None
        FileParams.pnImageID = None
    
        #IF nret is '1' Image is not saved if nret is "0" Image is saved
        nret = ueye.is_ImageFile(hcam, ueye.IS_IMAGE_FILE_CMD_SAVE, FileParams, ueye.sizeof(FileParams))
        if nret==0:
            saved=True
            print ('Image Saved!')
        if nret==1:
            print ('Error Image is not Saved!')
            
        #Shutting the CCD-Down.
        ueye.is_FreeImageMem(hcam, pccmem, memID)
        ueye.is_ExitCamera(hcam)   
        
        

    
