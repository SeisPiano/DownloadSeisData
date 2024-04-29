"""
Get station metadata.
station metadata can be obtained from IRIS-MDA: https://ds.iris.edu/mda/
and FDSN: https://www.fdsn.org/

Yuechu Wu
12131066@mail.sustech.edu.cn
2024-03-28
"""

import numpy as np
import pandas as pd
from obspy import UTCDateTime
from obspy.clients.fdsn import Client



network_code  = 'XO'  # AACSE: Alaska Amphibious Community seismic Experiment  XO (2018-01-01 - 2019-12-31)
network_starttime = UTCDateTime('2018-01-01')
network_endtime   = UTCDateTime('2019-12-31')

# Define channel priority: L > B > H
# Usually, L = 1 Hz, B = 20-50 Hz, H = 100 Hz
# Prioritizing downloading the L channel without the need 
# for high-frequency signals can save a lot of time
priority_order = {'L': 0, 'B': 1, 'H': 2, 'E': 3}





##### END OF USER INPUT #####
client = Client('IRIS')

# '?H?' for seismometer, '??H' for pressure channels (DPG or hydrophone)
inventory = client.get_stations(network=network_code,
                                channel='?H?,??H',
                                starttime=network_starttime,
                                endtime=network_endtime,
                                level='channel')


for network in inventory:
    
    stations_code           = []
    stations_starttime      = []
    stations_endtime        = []
    stations_channels       = []
    stations_total_channels = []
    stations_site           = []
    stations_latitude  = np.empty(len(network))
    stations_longitude = np.empty(len(network))
    stations_elevation = np.empty(len(network))
    
    ista = -1
    for station in network:
        ista = ista + 1
        
        station_code      = station.code
        station_site      = station.site.name
        station_starttime = station.start_date.__unicode__()
        station_endtime   = station.end_date.__unicode__()
        station_latitude  = station.latitude
        station_longitude = station.longitude
        station_elevation = station.elevation
        station_channels  = station.channels
        
        total_channels = []
        for station_channel in station_channels:
            channel = station_channel.code
            total_channels.append(channel)
            
        total_channels_str = ','.join(total_channels)
        
        # seismometer channels
        total_channels_seis = [x for x in total_channels if x[1] == 'H']
        # pressure channels (DPG or hydrophone)
        total_channels_pres = [x for x in total_channels if x[-1] == 'H']
        
              
        total_channels_seis.sort(key=lambda x:priority_order.get(x[0]))
        total_channels_pres.sort(key=lambda x:priority_order.get(x[0]))
        if total_channels_seis and total_channels_pres:
            channels_seis_str = ','.join(total_channels_seis[0:3])
            channel_pres = total_channels_pres[0]
            channels_str = ','.join([channels_seis_str,channel_pres])
        elif not total_channels_pres:
            channels_str = ','.join(total_channels_seis[0:3])
        elif not total_channels_seis:
            channels_str = total_channels_pres[0]
        else:
            channels_str = ''
                
            
        
        stations_code.append(station_code)
        stations_starttime.append(station_starttime)
        stations_endtime.append(station_endtime)
        stations_channels.append(channels_str)
        stations_total_channels.append(total_channels_str)
        stations_site.append(station_site)
        stations_latitude[ista]  = station_latitude
        stations_longitude[ista] = station_longitude
        stations_elevation[ista] = station_elevation
        
        
    
df = pd.DataFrame({'station': stations_code,
                   'starttime': stations_starttime, 'endtime': stations_endtime,
                   'latitude': stations_latitude, 'longitude': stations_longitude, 'elevation': stations_elevation,
                   'channels':stations_channels, 'total channels': stations_total_channels, 'site': stations_site})

filename = f'{network_code}_fdsn_metadata.txt'
df.to_csv(filename, sep='\t', float_format='%.6f')
