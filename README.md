# Labour Force Survey Analysis #

This repository contains a data project using monthly updated Statscan labour force survey public use microdata files. The main objective of the analysis is to determine the primary factors influencing income amount by exploring and modelling hourly earnings to derive feature importance. A second objective is to provide a demonstration of an automated data processing pipeline using Github actions with conditional run-time parameters. 

The LFS-analysis notebook contains the initial exploration, analysis, and machine learning predictions. Codes contained in the pipeline-scripts folder are used to run an automated data pipeline using a Github actions workflow on a cron schedule. During execution the scripts check the current version with the latest available from Statscan. If the versions do not match, the data is retrieved, extracted, decoded, modelled, and the desired results are saved to the log folder. If the versions do match there is no updated and the pipeline exits successfully. 



Disclaimer:
This work is for personal interest and is shown for demonstrative purposes only. Only publicly available, open-license data from Statistics Canada is used. No attempt to is made to reverse engineer the data or identify individuals. I have no contact with Statistics Canada nor does this work constitute an endorsement by Statistics Canada in any way. The data are not aggreggated with other datasets in any way. 

Data source:
https://www150.statcan.gc.ca/n1/en/catalogue/71M0001X

See the open license:
https://www.statcan.gc.ca/en/reference/licence



