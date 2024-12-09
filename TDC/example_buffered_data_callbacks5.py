#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2021 Surface Concept GmbH

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

-------------------------------------------------------------------------------

Created on Wed Jun 16 17:15:00 2021

WARNING: This example can potentially create a very large text file.
Tune down the EXPOSURE_MS variable and the NR_OF_MEASUREMENTS, if you
run this example with hardware with a high rate of events.

Test of the buffered-data callbacks interface for *** TDC events ***
(suitable if you have a "stand-alone" TDC without delay-line detector
or if you operate a delay-line detector with "SD_Format=-1" setting
and you are interested in the TDC events on the individual channels).
Write event data to a text file (no matplotlib needed).
Similarly to example_buffered_data_callbacks3.py, the processing is
delegated to the main thread which is recommended over processing in the
'on_data' callback.
Here, we request data at the end of every measurement. This makes it
easier to include measurement separator lines in the output file.
The logic is still a bit tricky. When the 'end_of_meas' callback is
invoked, and we return True, the next 'on_data' callback will deliver
the remaining buffered data of the current measurement. The order of
last data chunk and end-of-measurement notification is sorted in the
BufDataCB4 class, so the main thread will receive them in a sensible
order.
Formatting the arrays to a textual form via the savetxt function
of numpy seems to take quite some computational time. For productive
use cases, other forms of data export are recommended that provide a
higher performance in speed and disk space.
(However for demo purposes, the text file export allows to view the
output with an ordinary editor).
"""

import scTDC
import time
import timeit
import numpy as np
from queue import Queue
import os

# os.chdir(r'C:/Users/attose1_VMI/Desktop/maxence_folder/TDC_perso/ajout_perso')
# os.chdir(r'o:\\lidyl\\atto\\Asterix\\NicolasG\\TDC\\ajout_perso')
os.chdir(r'C:/Users/attose1_VMI/Desktop/maxence_folder/TDC_perso/ajout_perso')
#

# -----------------------------------------------------------------------------
# example 4 of deriving from buffered_data_callbacks_pipe

NR_OF_MEASUREMENTS = 1    # number of measurements
EXPOSURE_MS = 1        # exposure duration in milliseconds
OUTPUT_TEXTFILE_NAME = "tmp_textfile1357_1.txt" # this file will be overwritten!

DATA_FIELD_SEL1 = \
      scTDC.SC_DATA_FIELD_TIME \
    | scTDC.SC_DATA_FIELD_CHANNEL \
    | scTDC.SC_DATA_FIELD_SUBDEVICE \
    | scTDC.SC_DATA_FIELD_START_COUNTER

# define some constants to distinguish the type of element placed in the queue
QUEUE_DATA = 0
QUEUE_ENDOFMEAS = 1

class BufDataCB5(scTDC.buffered_data_callbacks_pipe):
    def __init__(self, lib, dev_desc,
                 data_field_selection=DATA_FIELD_SEL1,
                 max_buffered_data_len=500000,
                 dld_events=False):
        super().__init__(lib, dev_desc, data_field_selection,  # <-- mandatory!
                         max_buffered_data_len, dld_events)    # <-- mandatory!

        self.queue = Queue()
        self.end_of_meas = False

    def on_data(self, d):
        # make a dict that contains copies of numpy arrays in d ("deep copy")
        # start with an empty dict, insert basic values by simple assignment,
        # insert numpy arrays using the copy method of the source array
        dcopy = {}
        for k in d.keys():
            if isinstance(d[k], np.ndarray):
                dcopy[k] = d[k].copy()
            else:
                dcopy[k] = d[k]
        self.queue.put((QUEUE_DATA, dcopy))
        if self.end_of_meas:
            self.end_of_meas = False
            self.queue.put((QUEUE_ENDOFMEAS, None))

    def on_end_of_meas(self):
        self.end_of_meas = True
        # setting end_of_meas, we remember that the next on_data delivers the
        # remaining data of this measurement
        return True

# -----------------------------------------------------------------------------

class DataToTextfile(object):
    """ This class is created to handle the data processing. Using a class for
    such a task has the advantage that we can maintain a state across multiple
    hand-overs of data chunks and the variables holding this state are visibly
    grouped together in the class. Besides, this class is written as a
    context manager by implementing __enter__ and __exit__ methods. This
    helps with automatically closing the file."""
    def __init__(self, filename):
        self.file_object = open(filename, "w")
        # write a header
        self.file_object.write(
          "{:>3} {:>3} {:>16} {:>16}\n".format(
            "#sd", "ch", "start_counter", "time"))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        print("closing file.")
        self.close()

    def close(self):
        self.file_object.close()

    def write_measurement_separator(self):
        self.file_object.write("# next measurement\n")

    def process_data(self, d):
        """ d is the same data structure as in BufDataCB4.on_data(...)
            i.e. a dictionary containing 1D arrays (and some integer values)
        """
        print("processing data chunk of length: {}".format(d["data_len"]))
        # At this point, data could be modified and filtered before
        # exporting. A thorough study of numpy's capabilities is
        # most useful.
        np.savetxt(self.file_object,
                   np.c_[d["subdevice"], d["channel"], d["start_counter"],
                         d["time"]],
                   fmt = ["%3d", "%3d", "%16d", "%16d"])


def test5():
    device = scTDC.Device(autoinit=False)

    # initialize TDC --- and check for error!
    retcode, errmsg = device.initialize()
    if retcode < 0:
        print("error during init:", retcode, errmsg)
        return -1
    else:
        print("successfully initialized")

    # open a BUFFERED_DATA_CALLBACKS pipe
    bufdatacb = BufDataCB5(device.lib, device.dev_desc)

    # define a closure that checks return codes for errors and does clean up
    def errorcheck(retcode):
        if retcode < 0:
            print(device.lib.sc_get_err_msg(retcode))
            bufdatacb.close()
            device.deinitialize()
            return -1
        else:
            return 0

    start = timeit.default_timer()

    # start a first measurement
    retcode = bufdatacb.start_measurement(EXPOSURE_MS)
    if errorcheck(retcode) < 0:
        return -1

    # enter a scope where the text file is open
    with DataToTextfile(OUTPUT_TEXTFILE_NAME) as data_to_textfile:
        # event loop
        meas_remaining = NR_OF_MEASUREMENTS
        while True:
            eventtype, data = bufdatacb.queue.get()  # waits until element available
            if eventtype == QUEUE_DATA:
                data_to_textfile.process_data(data)
            elif eventtype == QUEUE_ENDOFMEAS:
                data_to_textfile.write_measurement_separator()
                meas_remaining -= 1
                if meas_remaining > 0:
                    retcode = bufdatacb.start_measurement(EXPOSURE_MS)
                    if errorcheck(retcode) < 0:
                        return -1
                else:
                    break
            else: # unknown event
                break # break out of the event loop

    end = timeit.default_timer()
    print("\ntime elapsed : ", end-start, "s")

    time.sleep(0.1)
    # clean up
    bufdatacb.close() # closes the user callbacks pipe, method inherited from base class
    device.deinitialize()

    return 0

if __name__ == "__main__":
    test5()
