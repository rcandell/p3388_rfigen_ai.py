import numpy as np
from gereactor import GEReactor

class RFIReactor(GEReactor):
    """
    Class for modeling radio frequency interference (RFI) reactors.

    This class represents an RFI reactor that generates interference patterns
    based on specified bandwidth and power distributions. It is used in the
    context of simulating RFI for wireless communication systems, particularly
    for compliance with the IEEE 3388 standard.

    Each reactor models the ON/OFF behavior using a Gilbert-Elliot model and
    defines how interference is distributed across frequency bins when ON.

    Attributes:
        name (str): Name of the reactor (not unique).
        centerbin (int): Central frequency bin where interference is centered.
        bw_dist (dict): Dictionary containing bandwidth distribution parameters (type, mean, std).
        power_dist (dict): Dictionary containing power distribution parameters (type, mean, std).
        power_shaping (dict): Dictionary for power shaping (enabled, std).
        nbins (int): Total number of frequency bins.
        J (numpy.ndarray): Interference magnitude vector across all bins, initialized to zeros.

    Methods:
        __init__(nbins, reactor_props): Constructor to initialize the reactor.
        reset_j(): Reset interference vector J to zeros.
        add(x): Add interference to a signal and reset J.
        step(): Update state and generate interference if ON.
        calculate_bin_range(startbin, endbin): Helper to get valid bin range.

    Author: Rick Candell
    """
    
    def __init__(self, nbins, reactor_props):
        """
        Initialize the RFIReactor with the number of bins and reactor properties.

        Args:
            nbins (int): Total number of frequency bins.
            reactor_props (dict): Dictionary containing reactor properties:
                - ge_probs: Gilbert-Elliot probabilities (list or array).
                - Name: Name of the reactor (str).
                - centerbin: Central frequency bin (int).
                - bw_distr: Bandwidth distribution parameters (dict with type, mean, std).
                - pwr_distr: Power distribution parameters (dict with type, mean, std).
                - pwr_shaping: Power shaping parameters (dict with enabled, std).
        """
        ge_probs = np.array(reactor_props['ge_probs']).reshape(2, 2).T
        super().__init__(ge_probs)
        self.name = reactor_props['Name']
        self.centerbin = reactor_props['centerbin']
        self.bw_dist = reactor_props['bw_distr']
        self.power_dist = reactor_props['pwr_distr']
        self.power_shaping = reactor_props['pwr_shaping']
        self.nbins = nbins
        self.J = np.zeros(nbins)
    
    def reset_j(self):
        """Reset interference vector J to zeros."""
        self.J = np.zeros(self.nbins)
    
    def add(self, x):
        """
        Add interference to a signal and reset J.

        Args:
            x (numpy.ndarray): Input signal to add interference to.

        Returns:
            numpy.ndarray: Signal with added interference.
        """
        self.step()
        x = x + self.J
        self.reset_j()
        return x
    
    def step(self):
        """
        Update the reactor state and generate interference magnitude if ON.

        Updates the internal state of the reactor using the Gilbert-Elliot model
        and, if the state is ON, calculates the interference magnitude across the
        frequency bins based on the defined distributions and shaping.
        """
        super().step()  # Call parent class's step method
        if self.state == 1:
            # Number of bins for interference
            if self.bw_dist['type'] == "normal":
                u = self.bw_dist['mean']
                s = self.bw_dist['std']
                if u <= 1 and s == 0:
                    L = 1
                else:
                    L = 2 * np.ceil((u + s * np.abs(np.random.randn())) / 2) + 1  # Always odd
                offset = (L - 1) / 2
                startbin = self.centerbin - offset
                endbin = self.centerbin + offset
                I = self.calculate_bin_range(startbin, endbin)
            elif self.bw_dist['type'] == "flat":
                I = np.arange(self.nbins)
            else:
                raise ValueError(f"Unknown bw distribution type {self.bw_dist['type']}")

            # Amplitude level
            if self.power_dist['type'] == "normal":
                u = self.power_dist['mean']
                s = self.power_dist['std']
                p = u + s * np.random.randn()
                plin = 10 ** (p / 10)  # Convert to linear power
                a = np.sqrt(plin)  # Convert to volts
                Lr = len(I)
                r = a * np.ones(Lr)

                # Apply shaping
                if self.power_shaping['enabled']:
                    ps_x = np.arange(self.nbins)
                    ps_pdf = np.exp(-0.5 * ((ps_x - self.centerbin) / self.power_shaping['std'])**2)
                    ps_pdf = ps_pdf[I] / np.max(ps_pdf[I])
                    r = r * ps_pdf

                # Add reactor component
                self.J[I] = r
            else:
                raise ValueError(f"Unknown pwr distribution type {self.power_dist['type']}")
        return self
    
    def calculate_bin_range(self, startbin, endbin):
        """
        Helper method to get valid bin range.

        Args:
            startbin (float): Starting bin index.
            endbin (float): Ending bin index.

        Returns:
            numpy.ndarray: Array of valid bin indices.
        """
        Ilow = max([startbin, 1])
        Ihigh = min([endbin, self.nbins])
        return np.arange(int(Ilow), int(Ihigh) + 1)
    