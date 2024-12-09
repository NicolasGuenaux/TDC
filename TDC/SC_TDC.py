#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from library.scTDC  import Device
import time
from dataBuffer import BufDataCB5
from ast import Param
import threading
from PySide6.QtCore import Signal,QObject
import numpy as np


class AcquisitionThread(threading.Thread):
    """Call a function after a specified number of seconds:

            t = Timer(30.0, f, args=[], kwargs={})
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting

    """
    def __init__(self, function, args=[], kwargs={}):
        threading.Thread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = threading.Event()
    def cancel(self):
        """Stop the timer if it hasn't finished yet"""
        self.finished.set()

    def run(self):
        repeats = 0
        while not self.finished.is_set():
            # print(repeats)
            repeats += 1
            # print('launching acq')
            self.function(*self.args, **self.kwargs)
            # print('finishing acq')
        # self.finished.set()


class SC_TDC(QObject,):
    isDeviceInitialized_Signal = Signal(bool)

    def __init__(self,parent=None,adress=r'o:\\lidyl\\atto\\Asterix\\NicolasG\\TDC\\library'
                ,filename="tdc_gpx3.ini",exposureTime=100):
        QObject.__init__(self)
        # super(SC_TDC, self).__init__(parent)
        # self.setupUi(self)    
        self.libPath = adress+filename
        self.device = None
        # Initialize device
        try:
            self.initializeDevice()        
            # open a BUFFERED_DATA_CALLBACKS pipe
            if self.device is not None:
                self.openPipe()
        except:
            print('Error')
            self.device = None
            self.bufdatacb = None
        self._event_callback=None
        self.exposureTime = exposureTime
        self._data_thread = None
        self.dataCallback = self.onData
        # self.start_thread(exposureTime=self.exposureTime)
        
        # self._data_thread = threading.Thread(target=self.data_thread)
        # self._data_thread.start()
        # self.bufdatacb.dataCallback = self.onData


    def getData(self,exposureTime):
        #self.openPipe()
        
        if self.device is not None:
            retcode = self.bufdatacb.start_measurement(exposureTime) # Starting measurements
            self.errorcheck(retcode) # Checking error
            while True:
                eventtype, data = self.bufdatacb.queue.get()  # waits until element available
                # print(f'eventtype = {eventtype}')
                # print(f'data = {data}')
                #
                self._event_callback(eventtype,data)
                if eventtype==0:
                    return data 
                '''
                else:
                    self.closePipe()
                    break
                '''
        #self.closePipe()
                        
        '''
                if eventtype==0:
                    return data                
                # self.onData(eventtype,data)
                # self.dataCallback(eventtype,data)
                #print(self.onData==self._event_callback)
                #print(self.dataCallback==self._event_callback)
                if data is None:
                    break   
            

                      
        else:
            time.sleep(exposureTime*1e-3)
            events = np.random.poisson(5, exposureTime)
            #print(events)
            ms_indices = np.cumsum(events)
            counts = np.zeros((np.sum(events),))
            counter = 0
            for event in events:
                counts[counter:counter+event] = np.random.rand(event)
                counter += event
            eventtype=0
            data = {'time': counts*1e6,'ms_indices':ms_indices}            
            # eventtype,data = (0,(np.arange(L),np.random.rand(L)))
            self._event_callback(eventtype,data)
        '''
        
        '''
        data={'event_index': 0, 'data_len': 74, 'subdevice': np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0]), 'channel':np.array( [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0]), 'start_counter':np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0]), 'time':np.array([939387, 942631, 947348, 954241, 968161, 968513, 969222, 935004,
       936929, 939388, 942730, 947172, 954273, 955512, 967966, 935132,
       936981, 939374, 942746, 947362, 954313, 969001, 935107, 937146,
       939444, 942748, 947338, 954383, 967881, 968373, 968649, 968869,
       969141, 936818, 939337, 942579, 947228, 954091, 968064, 968750,
       935162, 936955, 939462, 942771, 947433, 954495, 968775, 937027,
       939455, 942744, 947353, 954333, 934977, 936847, 939274, 942656,
       947190, 954186, 935099, 936927, 937746, 939440, 942605, 947099,
       954208, 968528, 969033, 969305, 935143, 936956, 939414, 942706,
       947312, 954207]), 'som_indices': [0], 'ms_indices':np.array([ 7, 15, 22, 33, 40, 47, 52, 58, 68, 74])}
        print('XXXX')

        return data
        
        if eventtype==0:
            return data
        '''
        
    def stop_thread(self,):    
        print('Stopping thread:')
        if self._data_thread is not None:
            self._data_thread.cancel()
            self._data_thread = None
            print('Thread is stopped')
        else:
            print('No active thread to be stopped')
    def start_thread(self,):  
        print('Starting thread:')  
        if self._data_thread is not None:
            self._data_thread.cancel()
            self._data_thread = None
        self._data_thread = AcquisitionThread(self.getData,(self.exposureTime,))
        self._data_thread.start()
        print('Thread is started') 


    def connectDevice(self,):
        error = self.initializeDevice()
        if not error:
            self.openPipe()        
            self.isDeviceInitialized_Signal.emit(True)
            print('Connected')
    def disconnectDevice(self,):
        self.closePipe()
        error = self.deinitializeDevice()
        if not error:
            print('Disconnected')
            self.isDeviceInitialized_Signal.emit(False)

    def deinitializeDevice(self,):
        if self.device is not None:
            self.closePipe()
            retcode,errmsg = self.device.deinitialize()
            if retcode < 0:
                print("error during deinit:", retcode, errmsg)
                return -1
            else:
                print("successfully deinitialized")
                self.device = None
                return 0

    def onData(self,event_type,data):
        print(f'Event_type={event_type}')
        print(f'Data={data}')
        
        # # print(timeit.default_timer())
        # #Measure continously
        # check_update = time.time()

        # #Refresh rate
        # if self._frame_time >=0 and (check_update-self._last_frame) > self._frame_time:
        #     self.refreshNow.emit()
        #     self._last_frame = time.time()
        # if event_type == 0:
        #     # print('Data')            
        #     self.onTof.emit(data)

        # # elif event_type == 1:
        # #     print('Measurement')

        # if (check_update-self._last_update) > self._display_rate:            
        #     self.displayNow.emit()
        #     self._last_update = time.time()    
    def initializeDevice(self,):
        if self.device is None:        
            import os
            folder,filename_withext = os.path.split(self.libPath)
            if self.libPath:
                folder_init = os.getcwd()                
                os.chdir(folder)
            else:
                print('No library path given')
                return -1
            device = Device(inifilepath=self.libPath,autoinit=False)
            # initialize TDC --- and check for error!
            retcode, errmsg = device.initialize()
            if retcode < 0:
                print("error during init:", retcode, errmsg)
                return -1
            else:
                print("successfully initialized")
            os.chdir(folder_init)
            self.device=device    
            return 0
        else:
            print('Device still initialized')
            return -1
    @property
    def exposureTime(self):
        """Exposure time in volts"""
        return self._exposure_time
    
    @exposureTime.setter
    def exposureTime(self,value):
        self._exposure_time = value

    @property
    def libPath(self):
        """Exposure time in volts"""
        return self._libPath
    
    @libPath.setter
    def libPath(self,value):
        self._libPath = value

    @property
    def dataCallback(self):
        """Function to call when data is recieved from a timepix device
        This has the effect of disabling polling. 
        """
        return self._event_callback
    @dataCallback.setter
    def dataCallback(self,value):
        self._event_callback = value

    # define a closure that checks return codes for errors and does clean up
    def errorcheck(self,retcode):
        if retcode < 0:
            print(self.device.lib.sc_get_err_msg(retcode))
            self.closeDevice()
            return -1
        else:
            return 0        
    def closePipe(self):
        if self._data_thread is not None:
            self.stop_thread()
        if self.bufdatacb is not None:
            self.bufdatacb.close() # closes the user callbacks pipe, method inherited from base class
        self.bufdatacb = None           
        print('Pipe is closed')        

    def openPipe(self,):
        if self.device is not None:
            self.bufdatacb = BufDataCB5(self.device.lib, self.device.dev_desc)
            print('Pipe is created')
        else:
            self.bufdatacb = None
            print('Pipe is not created')
    def closeDevice(self):
        # clean up
        self.closePipe() # Closing pipe        
        self.deinitializeDevice() # Deinitialize device
        
    def openDevice(self):
        # clean up
               
        self.initializeDevice() # Deinitialize device
        self.openPipe() # Closing pipe 

    def resetDevice(self):
        self.closeDevice()
        self.device = self.initializeDevice()
        self.openPipe()
        # clean up

def main():
    import sys
    import logging
    import numpy as np
    logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')    
    config = SC_TDC()
    config.connectDevice()

    data=config.getData(exposureTime=5)
    #data_hist = np.histogram(data['time'],np.linspace(0,1e6,1000))
    #print('yyyyyyyyyyyyyyyyyyyy')
    #print(data_hist)

    #print(data['ms_indices'])
    
    config.closeDevice()
if __name__=="__main__":
    main()