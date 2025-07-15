"""rfigenerator.py: class for generating RFI test vectors."""

__author__ = "Richard Candell"
__copyright__ = "Copyright 2025, Richard Candell"
__credits__ = ["Rick Candell"]
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Rick Candell"
__email__ = "rick dot candell at gmail dot com"
__status__ = "Research"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from rfiprops import RFIProps
from rfireactor import RFIReactor

class RFIGenerator:
    """
    Class for generating RFI test vectors.
    """
    
    def __init__(self, path_to_config_file):
        self.rfi_props = RFIProps(path_to_config_file)
        self.rfi_state_reactors = []
        self._p_fft = None
        reactors = self.rfi_props.config['Reactors']
        if isinstance(reactors, dict):
            reactors = [reactors]
        for reactor_props in reactors:
            new_reactor = RFIReactor(self.rfi_props.config['spectrogram']['NFreqBins'], reactor_props)
            self.rfi_state_reactors.append(new_reactor)

    def make_spectrogram(self):
        """
        Generate the spectrogram for the RFI scenario.
        """
        print(f"Number of frequency bins: {self.rfi_props.config['spectrogram']['NFreqBins']}")
        print(f"Number of reactors: {len(self.rfi_state_reactors)}")
        print(f"Output file path: {self.rfi_props.config['spectrogram']['PathToOutputSpectrogram']}")
        t = 0
        W = self.rfi_props.config['spectrogram']['WindowSize_s']
        print(f"Window size (sec): {W} for replication")
        dur = self.rfi_props.config['spectrogram']['Duration_s']
        print(f"Duration (sec): {dur} for replication")
        N = len(self.rfi_state_reactors)
        L = self.rfi_props.config['spectrogram']['NFreqBins']
        if L % 2 == 0:
            raise ValueError("Number of frequency bins must be odd")
        NF = self.rfi_props.config['spectrogram']['NoiseFloorPower_dB']
        nfv = 10 ** (NF / 20)
        first_write = True
        while t < dur:
            J = nfv * np.ones(L)
            for reactor in self.rfi_state_reactors:
                J = reactor.add(J)
            J = 20 * np.log10(J)
            mode = 'a' if not first_write else 'w'
            pd.DataFrame(J.reshape(1, -1)).to_csv(self.rfi_props.config['spectrogram']['PathToOutputSpectrogram'], 
                                                  mode=mode, header=False, index=False)
            first_write = False
            t += W

    def show_spectrum(self, pspec_file):
        """
        Show the generated spectrogram.
        """
        J = pd.read_csv(pspec_file, header=None).values
        X = np.arange(1, self.rfi_props.config['spectrogram']['NFreqBins'] + 1)
        Y = np.arange(0, self.rfi_props.config['spectrogram']['Duration_s'] + 
                      self.rfi_props.config['spectrogram']['WindowSize_s'], 
                      self.rfi_props.config['spectrogram']['WindowSize_s'])
        plt.figure()
        plt.imshow(J, aspect='auto', origin='lower', 
                  extent=[X[0], X[-1], Y[0], Y[-1]])
        plt.ylabel('Time (s)')
        plt.xlabel('Freq Bin')
        plt.colorbar()
        plt.show()

    def make_time_signal(self):
        """
        Convert spectrogram to time-domain signal.
        """
        ifile_name = self.rfi_props.config['spectrogram']['PathToOutputSpectrogram']
        ofile_name = self.rfi_props.config['ifft']['PathToOutputTimeSignal']
        with open(ifile_name, 'r') as fid_in:
            first_write = True
            for line in fid_in:
                v_dB = np.array([float(x) for x in line.strip().split(',')])
                from iffttimechunk import IFFTTimeChunk
                Tchunk = IFFTTimeChunk(self.rfi_props)
                Tchunk = Tchunk + v_dB
                X = Tchunk.X.flatten()
                Z = np.column_stack((X.real, X.imag))
                mode = 'a' if not first_write else 'w'
                pd.DataFrame(Z).to_csv(ofile_name, mode=mode, header=False, index=False)
                first_write = False
                if False:
                    t = np.linspace(0, Tchunk.tau, int(Tchunk.N * Tchunk.U * Tchunk.M))
                    plt.figure()
                    plt.subplot(2, 1, 1)
                    plt.plot(t, Z[:, 0])
                    plt.subplot(2, 1, 2)
                    plt.plot(t, Z[:, 1])
                    plt.show()
                    plt.close()
