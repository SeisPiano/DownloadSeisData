"""
Get station metadata.
station metadata can be obtained from IRIS-MDA: https://ds.iris.edu/mda/
and FDSN: https://www.fdsn.org/

Yuechu Wu
12131066@mail.sustech.edu.cn
2024-03-28

Encapsulate the main modules into functions.
Yuechu Wu
2025-08-03
"""


from obspy import UTCDateTime
from download_seisdata import get_metadata


output_dir = 'DATA' # output directory

# AACSE: Alaska Amphibious Community seismic Experiment  XO (2018-01-01 - 2019-12-31)
network_code  = 'XO'  
start_time = UTCDateTime('2018-01-01')
end_time   = UTCDateTime('2019-12-31')

# '?H?' for seismometer, '??H' for pressure channels (DPG or hydrophone)
channel_query = '?H?,??H'

# Define channel priority: L > B > H
# Usually, L = 1 Hz, B = 10-50 Hz, H = 100 Hz
# Prioritizing downloading the L channel without the need 
# for high-frequency signals can save a lot of time
priority_order = {'L': 0, 'B': 1, 'H': 2, 'E': 3}

get_metadata(output_dir,network_code,start_time,end_time,channel_query,priority_order)