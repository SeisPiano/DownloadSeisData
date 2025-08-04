"""
Download seismic day data and write 
station information into SAC header.

Basic preprocssing is also completed.
Preprocssing steps included here are:
- Response Removal
- Downsampling
- demean and detrend

Yuechu Wu
12131066@mail.sustech.edu.cn
2024-03-28

Added progress bar
Yuechu Wu
2024-05-06

Encapsulate the main modules into functions.
Yuechu Wu
2025-08-03
"""


import pandas as pd
from download_seisdata import download_daydata


output_dir = 'DATA/sacdata_day'  # seismic day data directory

network  = 'XO'  # network name
location = '--'  # for OBS, location is '--'
stations_download = ['WD58','WS75']  # list of stations to download

# Unit after removing instrument response,
# one of 'DISP','VEL','ACC' and 'DEF'
output_units_seis = 'DISP'
output_units_pres = 'DEF'

sample_rate = 5  # new sample rate

metadatafile = f'DATA/{network}_fdsn_metadata.csv'  # metadata file name
metadata = pd.read_csv(metadatafile, sep='\t', index_col=0)

download_daydata(output_dir,metadata,location,stations_download,
                 output_units_seis,output_units_pres)