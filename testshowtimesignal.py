"""testshowtimesignal.py: test script to show the time signal."""

__author__ = "Richard Candell"
__copyright__ = "Copyright 2025, Richard Candell"
__credits__ = ["Rick Candell"]
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Rick Candell"
__email__ = "rick dot candell at gmail dot com"
__status__ = "Research"

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from rfiprops import RFIProps
from iffttimechunk import IFFTTimeChunk

# Clear any existing matplotlib figures (equivalent to MATLAB's 'close all')
plt.close('all')

# File info
#tsfile = "./outputs/timesignal.csv"
tsfile = "./outputs_p3388/1_general_rfi_light_ts.csv"

# JSPEC configuration
jspecpath = "./outputs_p3388/1_general_rfi_light.json"
with open(jspecpath, 'r') as file:
    config = json.load(file)

# Initialize properties and time chunk generator
props = RFIProps(jspecpath)
tsgen = IFFTTimeChunk(props)
Fs = tsgen.fs
Ts = 1 / Fs
L = round(tsgen.tau * Fs)

# Loop through N samples
for ii in range(1025 * 4 + 1):
    # Define range for reading CSV (MATLAB's 1-based indexing adjusted to 0-based)
    # MATLAB: I = [ii*L+1 1 ii*L+L 2] -> start_row, start_col, end_row, end_col
    start_row = ii * L  # 0-based indexing for pandas
    end_row = ii * L + L
    X = pd.read_csv(tsfile, skiprows=start_row, nrows=L, header=None).values
    X = X[:, 0] + 1j * X[:, 1]  # Combine real and imaginary parts

    # Time vector in milliseconds
    tt = 1000 * np.arange(0, Ts * L, Ts)  # Equivalent to 0:Ts:Ts*(L-1)

    # Plot real and imaginary parts
    plt.figure(figsize=(10, 8))
    plt.subplot(3, 1, 1)
    plt.plot(tt, X.real)
    plt.xlabel('time (ms)')
    plt.title('Real Part')

    plt.subplot(3, 1, 2)
    plt.plot(tt, X.imag)
    plt.xlabel('time (ms)')
    plt.title('Imaginary Part')

    # Frequency spectrum
    ff = 1e-6 * np.linspace(-Fs / 2, Fs / 2, L)  # Frequency in MHz
    plt.subplot(3, 1, 3)
    plt.stem(ff, np.fft.fftshift(np.abs(np.fft.fft(X))))
    plt.xlabel('freq (MHz)')
    plt.title('Frequency Spectrum')

    plt.tight_layout()
    plt.show()