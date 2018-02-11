import numpy as np
import scipy.signal as signal

def local_maxs (values):
    return signal.argrelmin(values)[0]
    #return signal.argrelmax(values)[0]
    #return signal.argrelextrema(values, np.greater)[0][1:-1]