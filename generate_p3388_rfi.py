import os 
import shutil
import pandas as pd
from jspec_csvtojson import jspec_csvtojson
from rfigenerator import RFIGenerator
import matplotlib.pyplot as plt

# Clear any existing matplotlib figures (equivalent to MATLAB's commented 'close all')
plt.close('all')

# Base template for JSPECs
config_file_template = "./config_p3388/jspec_config_template.json"

# Output location
output_dir_path = "./outputs_p3388"

# Open test vector manifest
manifest_path = "./config_p3388/tv_generation_catalog.xlsx"
T = pd.read_excel(manifest_path, na_values=['NA'], keep_default_na=False)
Tst = T.to_dict('records')  # Convert DataFrame to list of dictionaries (equivalent to table2struct)

# Operations
SPECTGOP = False  # Equivalent to MATLAB's SPECTGOP = 1
TIMESERIESOP = True  # Equivalent to MATLAB's TIMESERIESOP = 0

# Loop through the manifest
for record in Tst:
    # Get metadata
    ID = record['ID']
    make = record['Make']
    name = record['Name']
    fft_config_csv_file = record['JSPECConfigPath']

    if make:
        print(f"Making ID: {ID} Name: {name}")
    else:
        print(f"Skipping ID: {ID} Name: {name}")
        continue

    # JSPEC output file path
    jspec_path = os.path.join(output_dir_path, f"{ID}_{name}.json")
    print(f"JSPEC PATH: {jspec_path}")

    # Make JSPEC
    jspec_csvtojson(config_file_template, fft_config_csv_file, jspec_path)
    print("jspec json file created")

    # Spectrogram output file path
    specg_path = os.path.join(output_dir_path, f"{ID}_{name}_specg.csv")
    print(f"SPECTROGRAM PATH: {specg_path}")

    if SPECTGOP:
        # Recalculate formulas in the Excel file (placeholder)
        # Note: MATLAB uses actxserver('Excel.Application') for Windows-specific Excel interaction.
        # In Python, this can be achieved with libraries like `win32com` (Windows only) or `openpyxl` (limited formula support).
        # Since formula recalculation is specific, we'll skip it or require a library like `win32com` on Windows.
        # Uncomment the following if running on Windows with `pywin32` installed:
        """
        import win32com.client
        excel = win32com.client.Dispatch('Excel.Application')
        workbook = excel.Workbooks.Open(os.path.abspath(fft_config_csv_file))
        excel.Calculate()
        workbook.Save()
        workbook.Close()
        excel.Quit()
        """
        print(f"Warning: Excel formula recalculation skipped. Ensure {fft_config_csv_file} is up-to-date.")

        # Make spectrogram
        rfi = RFIGenerator(jspec_path)
        if os.path.exists(specg_path):
            os.remove(specg_path)
        rfi.make_spectrogram()
        print("spectrogram created")

        # Move spectrogram interim file to final file location
        interim_spectg_path = rfi.rfi_props.config['spectrogram']['PathToOutputSpectrogram']
        shutil.copyfile(interim_spectg_path, specg_path)
        print("spectrogram final file copied")

        # Show the spectrogram
        rfi.show_spectrum(interim_spectg_path)
        name_s = name.replace("_", " ")
        plt.title(f"Spectrogram for {name_s}")
        plt.show()

        # Save the spectrogram plot
        specg_fig_path = os.path.splitext(specg_path)[0] + ".jpg"
        plt.savefig(specg_fig_path)
        plt.close()

    # Time signal output file path
    ts_path = os.path.join(output_dir_path, f"{ID}_{name}_ts.csv")
    print(f"TIME SERIES PATH: {ts_path}")

    if TIMESERIESOP:
        # Make time signal
        rfi = RFIGenerator(jspec_path)
        if os.path.exists(ts_path):
            os.remove(ts_path)
        rfi.make_time_signal()
        print("time series final file copied")

        # Move time signal interim file to final file location
        interim_ts_path = rfi.rfi_props.config['ifft']['PathToOutputTimeSignal']
        shutil.copyfile(interim_ts_path, ts_path)
        print("spectrogram final file copied")  # Note: MATLAB script has a typo; likely meant "time series"
        print("*****************************************")

    # Delete interim files
    if SPECTGOP and os.path.exists(interim_spectg_path):
        os.remove(interim_spectg_path)
    if TIMESERIESOP and os.path.exists(interim_ts_path):
        os.remove(interim_ts_path)
