from zipfile import ZipFile
import urllib.request
import requests
import os
import datetime
import numpy as np
import pandas as pd



def main():

    os.chdir('data')

    url='https://www150.statcan.gc.ca/n1/pub/71m0001x/2021001/'

    latest_version = get_latest(url)

    version_path = 'data_version.txt'


    if os.path.exists(version_path):

        current_version = np.loadtxt(version_path)

        if (all(current_version == latest_version)):

            return

    else:

        update_data(latest_version,url)
        """Sets the GitHub Action output.
    
        Keyword arguments:
        output_name - The name of the output
        value - The value of the output
        """
        output_status = 'status'
        value = 'updated'
            
        if "GITHUB_OUTPUT" in os.environ :
            with open(os.environ["GITHUB_OUTPUT"], "a") as f :
                print("{0}={1}".format(output_status, value), file=f)

    os.chdir('..')

    return 




def update_data(date,url):

    path = '../data'

    dir_list = os.listdir()
    for item in dir_list:
        os.remove(os.path.join(path,item))
        

    file_name = str(date[1]) + '-' + '{:02d}'.format(date[0]) + '-CSV' + '.zip'


    urllib.request.urlretrieve(url+file_name, file_name)
    unzip(file_name)

    os.rename('pub'+'{:02d}'.format(date[0])+str(date[1])[-2:]+'.csv', 'raw_lfs_data.csv')
    np.savetxt('data_version.txt', date, fmt="%s")


    return 



#Searches for the most recently updated LFS microdata file from Statscan going back max_months = 3 .
def get_latest(url):


    max_months = 3

    date = datetime.datetime.now()
    month = date.month
    year = date.year

    for i in range(max_months):

        year = year if month > 1 else year - 1
        month = month-1 if month > 1 else 12


        file_name = str(year) + '-' + '{:02d}'.format(month) + '-CSV' + '.zip'

        if exists(url + file_name):

            return [month, year]

    
    raise Exception(f"No LFS data found at source in past {max_months} months")


    return




def exists(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok



def unzip(zip_file):
    
    with ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall()
    
    
    return 


# run script
if __name__ == "__main__":
    # run main function
    main()


