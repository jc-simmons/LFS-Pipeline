from zipfile import ZipFile
import urllib.request
import requests
import os
import datetime
import numpy as np

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

    return 



def update_data(date,url):

    path = '../data'

    dir_list = os.listdir()
    for item in dir_list:
        os.remove(os.path.join(path,item))
        

    file_name = str(date[1]) + '-' + '{:02d}'.format(date[0]) + '-CSV' + '.zip'

    url = 'https://www150.statcan.gc.ca/n1/pub/71m0001x/2021001/'

    urllib.request.urlretrieve(url+file_name, file_name)
    unzip(file_name)

    os.rename('pub'+'{:02d}'.format(date[0])+str(date[1])[-2:]+'.csv', 'data_current.csv')
    np.savetxt('data_version.txt', date,fmt="%s")


    return 


#if lasts month's data doesn't exist yet, report date two months ago
def get_latest(url):

    date = previous_date(1)

    file_name = str(date[1]) + '-' + '{:02d}'.format(date[0]) + '-CSV' + '.zip'

    

    if exists(url + file_name):

        return date

    else:

        date = previous_date(2)

        return date


def exists(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok
   

def previous_date(months):

    date = datetime.datetime.now()
    last_month = date.month-months if date.month > months else 13-months
    last_year = date.year if date.month > months else date.year - 1

    return [last_month, last_year]




def unzip(zip_file):
    
    with ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall()
    
    
    return 


# run script
if __name__ == "__main__":
    # run main function
    main()


