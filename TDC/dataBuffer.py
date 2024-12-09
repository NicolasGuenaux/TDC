from library.scTDC import *
from queue import Queue
import numpy as np


DATA_FIELD_SEL1 = \
      SC_DATA_FIELD_TIME \
    | SC_DATA_FIELD_CHANNEL \
    | SC_DATA_FIELD_SUBDEVICE \
    | SC_DATA_FIELD_START_COUNTER

class BufDataCB5(buffered_data_callbacks_pipe):
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
            # print(f'key:{k}')
            # print(f'data:{d[k]}')
            if isinstance(d[k], np.ndarray):
                dcopy[k] = d[k].copy()
            else:
                dcopy[k] = d[k]
        # QUEUE_DATA = 0
        self.queue.put((0, dcopy))
        # QUEUE_ENDOFMEAS = 1
        if self.end_of_meas:
            self.end_of_meas = False
            self.queue.put((1, None))

    def on_end_of_meas(self):
        self.end_of_meas = True
        # setting end_of_meas, we remember that the next on_data delivers the
        # remaining data of this measurement
        return True

# -----------------------------------------------------------------------------