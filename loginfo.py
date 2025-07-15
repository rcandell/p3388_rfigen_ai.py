def loginfo(s):
    """
    Conditionally print a log message.

    Prints the input string if logging is enabled.

    Args:
        s (str): Message to be logged.

    Author: Rick Candell
    (c) Copyright Rick Candell All Rights Reserved
    """

    __author__ = "Richard Candell"
    __copyright__ = "Copyright 2025, Richard Candell"
    __credits__ = ["Rick Candell"]
    __license__ = "MIT"
    __version__ = "1.0.1"
    __maintainer__ = "Rick Candell"
    __email__ = "rick dot candell at gmail dot com"
    __status__ = "Research"

    loginfo_on = False
    if loginfo_on:
        print(s)