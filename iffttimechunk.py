import numpy as np
from scipy import signal
from scipy.interpolate import Akima1DInterpolator as makima
import matplotlib.pyplot as plt
from rfiprops import RFIProps
from loginfo import loginfo

class IFFTTimeChunk:
    """
    Class for handling time-domain chunks of RFI signals.

    This class converts a frequency-domain spectrogram to a time-domain signal using
    inverse Fast Fourier Transform (IFFT). It is designed for radio frequency interference
    (RFI) simulation, supporting the IEEE 3388 standard for testing industrial
    wireless systems under interference conditions. The class manages configuration
    parameters, applies random phase noise, and repeats or upsamples the signal as needed.

    Attributes:
        rfi_props (RFIProps): Configuration properties.
        tau (float): Duration of the time chunk (seconds).
        fs (float): Sample rate of the output signal (Hz).
        N (int): Number of points in the IFFT (two-sided).
        U (int): Upsample rate.
        M (float): Number of times to repeat the IFFT output.
        dF (float): Frequency resolution (Hz).
        dT (float): Time resolution (seconds).
        apply_poffset (bool): Flag to apply random phase offset.
        pnoisestd (float): Standard deviation of phase noise (radians).
        X (numpy.ndarray): Time-domain signal (complex).

    Methods:
        __init__(rfi_props): Initialize with RFI properties.
        __add__(y): Overloaded + operator to process spectrogram and compute time signal.
        rep(): Repeat the time chunk to match desired duration.
        ifft(YdB): Perform IFFT with spectrogram reordering and phase addition.

    Author: Rick Candell
    (c) Copyright Rick Candell All Rights Reserved
    """

    def __init__(self, rfi_props):
        """
        Initialize the IFFTTimeChunk with RFI properties.

        Args:
            rfi_props (RFIProps): Configuration properties object.
        """
        self.rfi_props = rfi_props
        fft_params = rfi_props.config['spectrogram']
        ifft_params = rfi_props.config['ifft']

        # Chunk Duration
        if ifft_params['DurationPerChunk_s'] < 0:
            self.tau = fft_params['WindowSize_s']
        else:
            self.tau = ifft_params['DurationPerChunk_s']
        loginfo(f"Using time chunk size as {self.tau}")

        # IFFT size
        self.N = fft_params['NFreqBins']
        loginfo(f"Number of points in original single-sided FFT are {fft_params['NFreqBins']}")
        loginfo(f"Number of points in output two-sided IFFT are {self.N}")

        # Desired bandwidth of output signal
        self.fs = ifft_params['StartingSampleRate_Hz']
        if self.fs:
            self.fs = self.N / self.tau
        loginfo(f"Starting sample rate is {self.fs}")

        # Desired time resolution
        self.dF = self.fs / self.N
        loginfo(f"Frequency resolution is {self.dF}")
        self.dT = 1 / self.dF
        loginfo(f"Time resolution is {self.dT}")

        # Number of times to repeat signal
        self.M = self.tau / self.dT

        # Uniform phase size
        self.apply_poffset = ifft_params['Phase']['ApplyRandomPhaseOffset']
        self.pnoisestd = ifft_params['Phase']['PhaseNoise_rads']

        # Upsample rate after the IFFT
        self.U = ifft_params['UpsampleRate']
        self.X = None

    def __add__(self, y):
        """
        Overloaded + operator to process spectrogram.

        Takes a spectrogram y (in dB) and computes the time-domain signal by performing
        IFFT, repeating the signal, and upsampling.

        Args:
            y (numpy.ndarray): Spectrogram magnitude in dB (vector).

        Returns:
            IFFTTimeChunk: Updated object with time-domain signal in self.X.
        """
        self.ifft(y)
        self.rep()
        self.X = signal.resample_poly(self.X, self.U, 1)
        return self

    def rep(self):
        """
        Repeat the time-domain signal.

        Repeats the time-domain signal (self.X) to match the desired duration (self.tau).
        Handles both integer and fractional repetitions.

        Logic:
            - m: Integer number of full repetitions
            - fp: Fractional part of repetitions
            - Repeats X m times, then appends a fraction of X
        """
        X0 = self.X
        exp_method = self.rfi_props.config['ifft']['Expansion']['ExpansionMethod'].lower()

        if exp_method == "repeat":
            m = int(np.floor(self.M))
            if m < 1:
                raise ValueError("Number of repetitions must be at least 1")
            fp = self.M - m
            self.X = np.tile(self.X.flatten(), m)
            I = np.arange(round(fp * self.N), dtype=int)
            self.X = np.concatenate((self.X, self.X[I]))

        elif exp_method == "interpolation":
            i0 = np.linspace(1, self.N, self.N)
            ii = np.linspace(1, self.N, int(round(self.M * self.N)))
            self.X = np.interp(ii, i0, self.X)

            if False:
                plt.figure()
                plt.subplot(2, 1, 1)
                plt.plot(np.arange(1, self.N + 1), self.X.real)
                plt.title("Original")
                plt.axis('tight')
                plt.subplot(2, 1, 2)
                plt.plot(np.arange(1, len(self.X) + 1), self.X.real)
                plt.title("Interpolated")
                plt.axis('tight')
                plt.show()

        elif exp_method == "upsample":
            self.X = np.fft.fftshift(self.X)
        else:
            raise ValueError(f"Unsupported expansion method {exp_method}")

        if self.rfi_props.config['ifft']['Plots']['InFnREP']:
            L0 = len(X0)
            f0 = np.linspace(-self.fs / 2, self.fs / 2, L0)
            L1 = len(self.X)
            f1 = np.linspace(-self.fs / 2, self.fs / 2, L1) / 1e6

            Y0 = np.fft.fftshift(np.abs(np.fft.fft(X0)))
            Y1 = np.fft.fftshift(np.abs(np.fft.fft(self.X, L1)))
            Y1s = np.fft.fftshift(np.abs(np.fft.fft(self.X, L0)))
            f = np.linspace(-self.fs / 2, self.fs / 2, L0) / 1e6

            plt.figure()
            plt.subplot(3, 1, 1)
            plt.stem(f0, Y0)
            plt.title('Original two-sided FFT')
            plt.subplot(3, 1, 2)
            plt.stem(f1, Y1)
            plt.title('FFT of new expanded time series')
            plt.subplot(3, 1, 3)
            plt.stem(f, Y1s)
            plt.title('FFT of new time series, original length')
            plt.show()

    def ifft(self, YdB):
        """
        Convert spectrogram to time-domain signal.

        Converts a spectrogram magnitude (in dB) to a time-domain signal using IFFT.
        Reorders the spectrum, adds random phases, and performs IFFT.

        Args:
            YdB (numpy.ndarray): Spectrogram magnitude in dB (vector).

        Steps:
            1. Convert dB to linear magnitude
            2. Reorder spectrum to standard FFT order for IFFT
            3. Apply random phase noise
            4. Compute IFFT

        Note:
            The reordering assumes YdB is in two-sided spectrum order (negative to
            positive frequencies). It shifts the spectrum to match NumPy's IFFT
            expected order (DC, positive, negative frequencies).
        """
        Y0 = 10 ** (YdB / 20)  # Convert dB to linear

        exp_method = self.rfi_props.config['ifft']['Expansion']['ExpansionMethod'].lower()
        if exp_method == "upsample":
            interpmethod = self.rfi_props.config['ifft']['Expansion']['UpsampleInterpolationMethod']
            i0 = np.linspace(1, self.N, self.N)
            ii = np.linspace(1, self.N, int(round(self.M * self.N)))
            if interpmethod != "makima":
                print("only the modified akima interpolation is currently supported.")
                print("switching to makima.")
            makima_interp = makima(i0, Y0, method='makima')
            Y0 = makima_interp(ii)

            if False:
                plt.figure()
                plt.subplot(2, 1, 1)
                plt.stem(np.arange(1, self.N + 1), Y0)
                plt.axis('tight')
                plt.subplot(2, 1, 2)
                plt.stem(np.arange(1, len(Y0) + 1), Y0)
                plt.axis('tight')
                plt.show()

        # Reorder the spectrogram for IFFT
        Im = int(np.ceil(len(Y0) / 2))
        Y1 = np.concatenate(([Y0[Im-1]], Y0[Im:], Y0[:Im-1]))

        if self.rfi_props.config['ifft']['Phase']['Enabled']:
            if self.apply_poffset:
                poff = np.pi * np.random.rand()
            else:
                poff = 0
            ri = np.random.rand(*Y1.shape)
            theta_v = self.pnoisestd * ri + poff - np.pi / 2
            phase_shift = np.exp(1j * theta_v)
            Y2 = Y1 * phase_shift
        else:
            Y2 = Y1

        self.X = np.fft.ifft(Y2)

        if self.rfi_props.config['ifft']['Plots']['InFnIFFT']:
            t = np.linspace(0, self.tau, len(self.X))
            f = np.linspace(-self.fs / 2, self.fs / 2, len(self.X)) / 1e6

            plt.figure()
            plt.subplot(4, 1, 1)
            plt.plot(t, self.X.real)
            plt.title('Time series output real')
            plt.subplot(4, 1, 2)
            plt.plot(t, self.X.imag)
            plt.title('Time series output imag')
            plt.subplot(4, 1, 3)
            plt.stem(f, np.fft.fftshift(np.abs(np.fft.fft(self.X))))
            plt.title('FFT of new time series')
            plt.subplot(4, 1, 4)
            plt.stem(f, Y0)
            plt.title('Original two-sided FFT')
            plt.show()
            