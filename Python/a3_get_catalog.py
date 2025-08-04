"""
Get earthquake catalog.

Yuechu Wu
12131066@mail.sustech.edu.cn
2024-02-03

Added progress bar
Yuechu Wu
2024-05-06

Encapsulate the main modules into functions.
Yuechu Wu
2025-08-03
"""


import pandas as pd
from download_seisdata import get_catalog


output_dir = 'DATA/catalog'  # earthquake catalog file directory

network = 'XO'  # network name
stations_download = ['WD58','WS75']  # list of stations to download

# Local and Global event information will be automatically merged.
# Local: With the station as the center of the circle,
# download event information from 'minmag_local' to 'maxmag_local'
# within the range of 0 to 'maxradius_local'.
minmag_local = 5.5
maxmag_local = 6
maxradius_local = 90

# Global: Download event information globally that is greater than 'minmag_global'.
minmag_global = 6

metadatafile = f'DATA/{network}_fdsn_metadata.csv'  # metadata file name
metadata = pd.read_csv(metadatafile, sep='\t', index_col=0)

get_catalog(output_dir,metadata,stations_download,minmag_local,
            maxmag_local,maxradius_local,minmag_global)