from zipfile import ZipFile
import urllib.request
import requests
import os
import datetime
import pathlib as Path
import json

def main():

    config = load_config('config.json')

    try:
        SOURCE_URL = config['SOURCE_URL']
        VERSION_PATH = Path(config['VERSION_PATH'])
        DATA_DIRECTORY = Path(config['DATA DIRECTORY'])
        MAX_LOOKBACK_MONTHS = config['MAX_LOOKBACK_MONTHS']
    except Exception as e:
        print(f'Error parsing config: {e}' )
        exit(1)

    # date-year stamps for versions
    latest_version = get_latest(SOURCE_URL, MAX_LOOKBACK_MONTHS)
    current_version = read_version(VERSION_PATH)

    if current_version == latest_version:
        return  # Exit early if the data is up-to-date.

    update_data(latest_version, SOURCE_URL, DATA_DIRECTORY)
        
    # If running in GitHub Actions, set output    
    if "GITHUB_OUTPUT" in os.environ :
        set_github_output('status', 'updated')
   

def load_config(config_path):
    try: 
        with open(config_path, 'r') as cfg:
            config = json.load(cfg)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return None


def set_github_output(output_name, value):
    """Sets the GitHub Action output."""
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f"{output_name}={value}\n")


def read_version(version_path):
    """Read version from the JSON version file."""
    try:
        with open(version_path, 'r') as f:
            version_data = json.load(f)
            return version_data['version'].split('-')
    except FileNotFoundError:
        print(f"Version file not found")
        return None  
    except Exception as e:
        print(f"Unexpected error reading version file: {e}")
        return None  
    

def write_version(date, version_path):
    """Write the current version to the JSON version file."""
    version_data = {
        'version': f"{date[0]}-{date[1]}"
    }
    with open(version_path, 'w') as f:
        json.dump(version_data, f)


def update_data(date, source_url, data_directory):
    """Download and unzip the most recent data file."""

    data_directory.mkdir(parents=True, exist_ok=True)

    # Clear existing data
    for item in data_directory.iterdir():
        if item.is_file():
            item.unlink()

    file_name = f"{date[1]}-{date[0]:02d}-CSV.zip"
    file_url = source_url + file_name

    urllib.request.urlretrieve(file_url, file_name)
    unzip(file_name)

    csv_path =  f"pub{date[0]:02d}{str(date[1])[-2:]}.csv"
    os.rename(csv_path, data_directory / 'raw_data.csv')
    
    write_version(date)


def get_latest(url, lookback_months):
    """ Searches StatCan for the most recent LFS microdata file"""
    current_date = datetime.datetime.now()
    month = current_date.month
    year = current_date.year

    for _ in range(lookback_months):
        year, month = (year, month-1) if month > 1 else (year-1, 12)
        file_name = f"{year}-{month:02d}-CSV.zip"
        if url_exists(url + file_name):
            return [month, year]
    
    raise Exception(f"No LFS data found at source in past {lookback_months} months")


def url_exists(path):
    """Check if the file exists at the given URL."""
    try:
        response = requests.head(path)
        return response.status_code == requests.codes.ok
    except requests.RequestException as e:
        print(f"Error accessing url file: {e}")
        return False
    

def unzip(zip_file):
    with ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall()
    os.remove(zip_file)
    return 


# run script
if __name__ == "__main__":
    # run main function
    main()


