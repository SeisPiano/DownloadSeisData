"""
Get earthquake catalog.

Yuechu Wu
12131066@mail.sustech.edu.cn
2024-02-03
"""

import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from obspy import UTCDateTime
from obspy.clients.fdsn import Client




network = 'XO'  # network name


# Local and Global event information will be
# automatically merged.
#
# Local: With the station as the center of the circle,
# download event information from 'minmag_local' to 'maxmag_local'
# within the range of 0 to 'maxradius_local'.
minmag_local = 6
maxmag_local = 6.5
maxradius_local = 90

# Global: Download event information globally 
# that is greater than 'minmag_global'.
minmag_global = 6.5



output_dir = 'catalog'  # earthquake catalog file directory

metadatafile = network + '_fdsn_metadata.txt'  # metadata file name





##### END OF USER INPUT #####
metadata = pd.read_csv(metadatafile, sep='\t', index_col=0)


stations           = metadata['station']
stations_starttime = metadata['starttime']
stations_endtime   = metadata['endtime']
stations_latitude  = metadata['latitude']
stations_longitude = metadata['longitude']


if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
if not os.path.exists(f'{output_dir}/{network}'):
    os.makedirs(f'{output_dir}/{network}')
    
    
client = Client('IRIS')

for ista in tqdm(range(len(stations))):
    station = stations[ista]
    print(station)
    sta_lat = stations_latitude[ista]
    sta_lon = stations_longitude[ista]
    
    starttime = UTCDateTime(stations_starttime[ista])
    endtime   = UTCDateTime(stations_endtime[ista])
    
    cata_local = client.get_events(starttime=starttime, endtime=endtime, minmagnitude=minmag_local, maxmagnitude=maxmag_local,
                                   latitude=sta_lat, longitude=sta_lon, maxradius=maxradius_local)
    
    cata_global = client.get_events(starttime=starttime, endtime=endtime, minmag=minmag_global)

    catalog = cata_local + cata_global
    
    eventids         = []
    otimes_str       = []
    magnitude_types  = []
    descriptions     = []
    events_latitude  = np.empty(len(catalog))
    events_longitude = np.empty(len(catalog))
    events_depth     = np.empty(len(catalog))
    magnitudes       = np.empty(len(catalog))

    ievt = -1
    for event in catalog:
        ievt += 1
        
        eventid         = event.resource_id.id.split('eventid=')[-1]
        origin          = event.origins[0]      
        otime_str       = origin.time.__unicode__()
        event_latitude  = origin.latitude
        event_longitude = origin.longitude     
        event_depth     = origin.depth*0.001   # The unit of depth is km      
        magnitude_type  = event.magnitudes[0].magnitude_type
        magnitude       = event.magnitudes[0].mag
        description     = event.event_descriptions[0].text
        
        
        eventids.append(eventid)
        otimes_str.append(otime_str)
        magnitude_types.append(magnitude_type)
        descriptions.append(description)
        events_latitude[ievt]  = event_latitude
        events_longitude[ievt] = event_longitude
        events_depth[ievt]     = event_depth
        magnitudes[ievt]       = magnitude
        
        
    
    df = pd.DataFrame({'event id': eventids, 'origin time': otimes_str, 
                       'latitude': events_latitude, 'longitude': events_longitude, 'depth': events_depth, 
                       'magnitude type': magnitude_types, 'magnitude': magnitudes, 'description': descriptions})
    

    filename = f'{output_dir}/{network}/{network}_{station}_catalog.txt'
    df.to_csv(filename, sep='\t', float_format='%.6f')
            
    