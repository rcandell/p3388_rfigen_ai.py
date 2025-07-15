import json
import pandas as pd

def jspec_csvtojson(conf_file, csv_file, output_file):
    """
    Convert CSV file to JSON for RFI reactors.

    Reads a configuration file and a CSV file containing reactor properties, and generates
    a JSON file (JSPEC) for use in RFI generation systems, likely supporting the IEEE 3388
    standard for industrial wireless testing. The output JSON includes the configuration
    header and an array of reactors.

    The CSV file must have the following columns in this order:
    1. Name
    2. type
    3. centerbin
    4. ge_prob_11
    5. ge_prob_12
    6. ge_prob_21
    7. ge_prob_22
    8. bw_distr_type
    9. bw_distr_mean
    10. bw_distr_std
    11. pwr_distr_type
    12. pwr_distr_mean
    13. pwr_distr_std
    14. pwr_shaping
    15. pwr_shaping_std

    Args:
        conf_file (str): Path to the configuration JSON file.
        csv_file (str): Path to the CSV file with reactor properties.
        output_file (str): Path to the output JSON file.

    Author: Rick Candell
    (c) Copyright Rick Candell All Rights Reserved
    """
    # Read the configuration file
    with open(conf_file, 'r') as file:
        config = json.load(file)

    # Write the configuration part of the JSON file
    hdr = json.dumps(config, indent=2)
    hdr = hdr[:-2] + ","  # Remove closing brace and add comma
    with open(output_file, 'w') as fid:
        fid.write(hdr)

    # Read the CSV file into a DataFrame
    T = pd.read_excel(csv_file)

    # Initialize the "Reactors" array in the JSON
    J = "\n\"Reactors\": [\n"
    N = len(T)
    for ii in range(N):
        r = T.iloc[ii]
        J = add_reactor(J, r)
        if ii != N - 1:
            J = add_comma_newline(J)
    J = J + "]\n}"

    # Append the "Reactors" array to the JSON file
    with open(output_file, 'a') as fid:
        fid.write(J)

    # Read the JSON file back for pretty printing
    with open(output_file, 'r') as fid:
        json_data = json.load(fid)
    jtxt = json.dumps(json_data, indent=2)

    # Rewrite the file with pretty-printed JSON
    with open(output_file, 'w') as fid:
        fid.write(jtxt)

def add_reactor(s, r):
    """
    Convert a DataFrame row to a JSON object for a reactor.

    Appends the JSON representation of a reactor to the current JSON string
    based on the row data.

    Args:
        s (str): Current JSON string.
        r (pandas.Series): DataFrame row with reactor properties.

    Returns:
        str: Updated JSON string.
    """
    s = s + "{\n"
    s = add_string(s, "Name", r['Name'])
    s = add_comma_newline(s)
    s = add_string(s, "type", r['type'])
    s = add_comma_newline(s)
    s = add_double(s, "centerbin", r['centerbin'])
    s = add_comma_newline(s)
    ge_probs = r[['ge_prob_11', 'ge_prob_12', 'ge_prob_21', 'ge_prob_22']].values
    s = add_array(s, "ge_probs", ge_probs)
    s = add_comma_newline(s)
    s = begin_section(s, "bw_distr")
    s = add_string(s, "type", r['bw_distr_type'])
    s = add_comma_newline(s)
    s = add_double(s, "mean", r['bw_distr_mean'])
    s = add_comma_newline(s)
    s = add_double(s, "std", r['bw_distr_std'])
    s = end_section(s)
    s = add_comma_newline(s)
    s = begin_section(s, "pwr_distr")
    s = add_string(s, "type", r['pwr_distr_type'])
    s = add_comma_newline(s)
    s = add_double(s, "mean", r['pwr_distr_mean'])
    s = add_comma_newline(s)
    s = add_double(s, "std", r['pwr_distr_std'])
    s = end_section(s)
    s = add_comma_newline(s)
    s = begin_section(s, "pwr_shaping")
    s = add_double(s, "enabled", int(r['pwr_shaping']))  # Convert boolean to int (0 or 1)
    s = add_comma_newline(s)
    s = add_double(s, "std", r['pwr_shaping_std'])
    s = end_section(s)
    s = s + "}"
    return s

def begin_section(s, name):
    """
    Start a new JSON section.

    Adds a key-value pair where the value is an object.

    Args:
        s (str): Current JSON string.
        name (str): Name of the section.

    Returns:
        str: Updated JSON string.
    """
    return s + f'"{name}": {{\n'

def end_section(s):
    """
    Close the current JSON section.

    Args:
        s (str): Current JSON string.

    Returns:
        str: Updated JSON string.
    """
    return s + "}"

def add_string(s, name, value):
    """
    Add a string field to the JSON.

    Formats the field as a quoted string.

    Args:
        s (str): Current JSON string.
        name (str): Field name.
        value (str): Field value.

    Returns:
        str: Updated JSON string.
    """
    return s + f'"{name}": "{value}"'

def add_double(s, name, value):
    """
    Add a numeric field to the JSON.

    Adds the number without quotes.

    Args:
        s (str): Current JSON string.
        name (str): Field name.
        value (float or int): Field value.

    Returns:
        str: Updated JSON string.
    """
    return s + f'"{name}": {value}'

def add_array(s, name, value):
    """
    Add an array field to the JSON.

    Converts the array to a string with four decimal places.

    Args:
        s (str): Current JSON string.
        name (str): Field name.
        value (numpy.ndarray or list): Array values.

    Returns:
        str: Updated JSON string.
    """
    sx = ', '.join(f'{x:.4f}' for x in value)
    return s + f'"{name}": [{sx}]'

def add_comma_newline(s):
    """
    Add a comma and newline for readability.

    Args:
        s (str): Current JSON string.

    Returns:
        str: Updated JSON string.
    """
    return s + ",\n"