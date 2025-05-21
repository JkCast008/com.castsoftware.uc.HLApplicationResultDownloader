# com.castsoftware.uc.HLApplicationResultDownloader

CAST Highlight Results Downloader
This extension is used to download application result CSVs from CAST Highlight by providing a list of application names in a CSV file. An example applications.csv is included in the extension.

Prerequisites
Python: Version 3.6 or later is required.
pip: Install the required Python packages by running the following command:
pip install requests pandas

Excel/CSV Reader: Required to read application names from the CSV file.
API Key: A valid CAST Highlight API token is required.
Setup Instructions
Edit the config.json file with the following fields: image
domainId: CAST Highlight domainId where all the apps are attached

HighlightAPIKey: API token from CAST Highlight instance

csv_file: Path to the applications.csv file where all the applications are listed

outpu_csv: Path to the .csv file which has results id for each app

output_parent_folder: Path to the directory where all the apps’ results are exported

Run the Python script:
python HL_CSV_Automation.py

Results
All application result CSVs will be downloaded into the exported_csvs root folder. Each application’s results will be stored as a separate ZIP file within its own subfolder
