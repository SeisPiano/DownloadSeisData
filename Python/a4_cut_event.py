"""
Cut earthquake event data from day data.
As an alternative to a4_download_eventdata, 
it can save a lot of time and needs to be used after a2_download_daydata.

Yuechu Wu
12131066@mail.sustech.edu.cn
2024-02-05

Encapsulate the main modules into functions.
Yuechu Wu
2025-08-03
"""


import pandas as pd
from download_seisdata import cut_event


input_dir  = 'DATA/sacdata_day'  # seismic day data directory
output_dir = 'DATA/sacdata_event'  # seismic event data directory
catalog_dir = 'DATA/catalog'  # seismic event catalog directory

network  = 'XO'  # network name
stations_download = ['WD58','WS75']  # list of stations to download

sample_rate = 5  # new sample rate

# Length of seismic event (unit: seconds)
event_length = 7200
# The start time of the event file (in seconds relative to the origin time of event)
btime = -600
# The lower and upper limits of Rayleigh wave velocity (km/s)
Rayleigh_velocity = [3, 4.5]

metadatafile = f'DATA/{network}_fdsn_metadata.csv'  # metadata file name
metadata = pd.read_csv(metadatafile, sep='\t', index_col=0)

cut_event(input_dir,output_dir,catalog_dir,metadata,stations_download,
          event_length,btime,Rayleigh_velocity)