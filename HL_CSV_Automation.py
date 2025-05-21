import requests
import pandas as pd
import csv
import os
import json

# Load configuration from JSON
with open('config.json') as config_file:
    config = json.load(config_file)

# Assign values from config
DOMAIN_ID = config['domainId']
API_KEY = config['HighlightAPIKey']
CSV_FILE = config['csv_file']
OUTPUT_CSV = config['output_csv']
OUTPUT_PARENT_FOLDER = config['output_parent_folder']
BASE_URL = config['base_url']

# API endpoints
applications_url = f"{BASE_URL}/WS2/domains/{DOMAIN_ID}/applications"
results_url = f"{BASE_URL}/WS2/domains/{DOMAIN_ID}/applications/{{}}/results"
export_url = f"{BASE_URL}/WS/campaigns/csv/export/all?companySwitch={{}}&applicationResultId={{}}"

# API authentication headers
headers = {"Authorization": f"Bearer {API_KEY}"}

# Ensure the output folder exists
os.makedirs(OUTPUT_PARENT_FOLDER, exist_ok=True)

# Load the CSV file
df = pd.read_csv(CSV_FILE)

# Step 1: Fetch all applications for the domain
try:
    response = requests.get(applications_url, headers=headers)
    response.raise_for_status()

    all_applications = response.json()

    # Step 2: Build a dictionary for application names and their corresponding IDs
    application_dict = {app.get('name', '').lower(): app.get('id') for app in all_applications if app.get('name') and app.get('id')}

except requests.exceptions.RequestException as e:
    print(f"Error fetching application data: {e}")
    exit(1)

# Step 3: Fetch the latest results ID for each application
results = []

for _, row in df.iterrows():
    application_name = row['application_name'].lower().strip()
    application_id = application_dict.get(application_name)

    result_id = None  # Initialize result_id

    if application_id:
        try:
            # Fetch results for the application
            results_response = requests.get(results_url.format(application_id), headers=headers)
            results_response.raise_for_status()

            results_data = results_response.json()

            # Extract latest result based on snapshotDate (or id if snapshotDate is missing)
            if isinstance(results_data, list) and results_data:
                latest_result = max(results_data, key=lambda x: x.get("snapshotDate", x.get("id", 0)))
                result_id = latest_result.get("id")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching results for application {application_name}: {e}")

    results.append({
        'application_name': row['application_name'],
        'application_id': application_id,
        'result_id': result_id
    })

# Write the results to a CSV file
with open(OUTPUT_CSV, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['application_name', 'application_id', 'result_id'])
    writer.writeheader()
    writer.writerows(results)

print(f"Results have been saved to {OUTPUT_CSV}")

# Step 4: Download the CSV.zip for each application
for row in results:
    application_name = row['application_name']
    application_id = row['application_id']
    result_id = row['result_id']

    if pd.notna(application_id) and pd.notna(result_id):
        try:
            application_folder = os.path.join(OUTPUT_PARENT_FOLDER, application_name)
            os.makedirs(application_folder, exist_ok=True)

            export_url_with_params = export_url.format(application_id, result_id)

            export_response = requests.get(export_url_with_params, headers=headers)
            export_response.raise_for_status()

            zip_file_path = os.path.join(application_folder, "csvs.zip")
            with open(zip_file_path, 'wb') as f:
                f.write(export_response.content)

            print(f"CSV.zip for {application_name} saved to {zip_file_path}")

        except requests.exceptions.RequestException as e:
            print(f"Error exporting CSV for {application_name} (ID: {application_id}, Result ID: {result_id}): {e}")

print("Export process completed.")
