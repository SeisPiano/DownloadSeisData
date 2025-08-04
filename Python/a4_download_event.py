"""
Download seismic event data and write station 
and event information into SAC header.

The start time of the event is the origin time + btime.

Basic preprocessing is also completed.
Preprocessing steps included here are:
- Response Removal
- Downsampling
- demean, detrend and taper

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
from download_seisdata import download_event


output_dir = 'DATA/sacdata_event'  # seismic event data directory
catalog_dir = 'DATA/catalog'  # seismic event catalog directory

network  = 'XO'  # network name
location = '--'  # for OBS, location is '--'
stations_download = ['WD58','WS75']  # list of stations to download

# Unit after removing instrument response,
# one of 'DISP','VEL','ACC' and 'DEF'
output_units_seis = 'DISP'
output_units_pres = 'DEF'

sample_rate = 5  # new sample rate

# Length of seismic event (unit: seconds)
event_length = 7200
# The start time of the event file (in seconds relative to the origin time of event)
btime = -600
# The lower and upper limits of Rayleigh wave velocity (km/s)
Rayleigh_velocity = [3, 4.5]

metadatafile = f'DATA/{network}_fdsn_metadata.csv'  # metadata file name
metadata = pd.read_csv(metadatafile, sep='\t', index_col=0)

download_event(output_dir,catalog_dir,metadata,location,stations_download,
               output_units_seis,output_units_pres,event_length,btime,Rayleigh_velocity)