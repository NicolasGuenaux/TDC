# -*- coding: utf-8 -*-
"""
Copyright 2019 Surface Concept GmbH

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

Test 1D time histogram pipe I(time) for a stand-alone TDC.

"""

def test_tdc_histo_pipe():
    """ opens a 1D time histogram pipe for a stand-alone TDC and shows the plot
    after 1+ measurement(s)"""
    import scTDC
    import numpy as np
    from matplotlib import pyplot as plt
    import os

    # os.chdir(r'C:/Users/attose1_VMI/Desktop/maxence_folder/TDC_perso/ajout_perso')
    os.chdir(r'o:\\lidyl\\atto\\Asterix\\NicolasG\\TDC\\ajout_perso')


    assert "scTDC1.dll" in os.listdir()
    device = scTDC.Device(autoinit=False)
    print("[INFO] Module initialize")
    retcode, errmsg = device.initialize()
    if retcode < 0:
        print("Error during initialization : ({}) {}".format(errmsg, retcode))
        return
    
    # help(device.add_tdc_histo_pipe)
    pipeid, pipe = device.add_tdc_histo_pipe(
        depth = scTDC.BS16, channel = 2, modulo = 0, binning = 1, 
        offset = 0, size = 5000000)
    
    print("Starting 1+ measurement(s)")
    for i in range(1):
        retcode, errmsg = device.do_measurement(time_ms=1, synchronous=True)
        if retcode < 0:
            print("Error while starting measurement : ({}) {}".format(
                errmsg, retcode))
    print("Finished measurements")    
    data = pipe.get_buffer_view()
    print("shape of the data array :", data.shape)
    print("total intensity in roi :", np.sum(data))
    
    fig = plt.figure(figsize=(10,7))
    ax1 = fig.add_subplot(111)
    ax1.plot(data)
    ax1.set_xlabel("time (digital units)")
    ax1.set_ylabel("counts")
    
    plt.show()
    
    device.deinitialize()
    
    
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    test_tdc_histo_pipe()
