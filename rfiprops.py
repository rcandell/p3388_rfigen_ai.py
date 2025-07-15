import json

class RFIProps:
    """
    Class for handling RFI configuration properties.

    This class is responsible for loading and storing configuration properties
    from a JSON file. These properties are used to configure RFI (Radio Frequency
    Interference) generation systems, likely for testing wireless communication
    systems under the IEEE 3388 standard. The class provides a way to load
    configuration data and store it for use in other parts of the system.

    Attributes:
        config (dict): Parsed JSON configuration object (a Python dictionary).
        path_to_config_file (str): Path to the JSON configuration file.
        ge_probs_bb_rfi (list or numpy.ndarray): Gilbert-Elliot probabilities for broadband RFI.
            Transition probs: col1 (11), col2 (12), col1 (21), col2 (22).
            (Note: This property is declared but not initialized here;
            it may be set elsewhere or extracted from the config.)

    Methods:
        __init__(path_to_config_file): Initialize with the configuration file path.
        load_configuration(): Load and parse the JSON configuration.

    Author: Rick Candell
    (c) Copyright Rick Candell All Rights Reserved
    """
    
    def __init__(self, path_to_config_file):
        """
        Initialize the RFIProps with the path to a JSON configuration file.

        Args:
            path_to_config_file (str): Path to the JSON configuration file.
        """
        self.config = None  # Parsed JSON configuration object
        self.path_to_config_file = path_to_config_file  # Path to the JSON configuration file
        self.ge_probs_bb_rfi = None  # Gilbert-Elliot probabilities for broadband RFI
        self.load_configuration()
    
    def load_configuration(self):
        """
        Load and parse the JSON configuration file.

        Reads the JSON file specified by path_to_config_file and stores the parsed
        data in the config attribute as a Python dictionary.
        """
        with open(self.path_to_config_file, 'r') as file:
            json_data = file.read()
            self.config = json.loads(json_data)
        return self
    