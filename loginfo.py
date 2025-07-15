def loginfo(s):
    """
    Conditionally print a log message.

    Prints the input string if logging is enabled.

    Args:
        s (str): Message to be logged.

    Author: Rick Candell
    (c) Copyright Rick Candell All Rights Reserved
    """
    loginfo_on = False
    if loginfo_on:
        print(s)
        