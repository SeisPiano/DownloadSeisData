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
"""


import os
import pandas as pd
from obspy import UTCDateTime
from obspy.io.sac import SACTrace
from obspy.clients.fdsn import Client
from datetime import datetime,timedelta



network  = 'XO'  # network name
location = '--'  # for OBS, location is '--'
stations_download = ['WD58','WS75']  # list of stations to download


# Unit after removing instrument response,
# one of 'DISP','VEL','ACC' and 'DEF'
output_units_seis = 'DISP'
output_units_pres = 'DEF'

# samprate = 5  # new sample rate

output_dir = 'DATA/sacdata_day'  # seismic day data directory


metadatafile = network + '_fdsn_metadata.txt'  # metadata file name





##### END OF USER INPUT #####
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


if not os.path.exists(f'{output_dir}/{network}'):
    os.makedirs(f'{output_dir}/{network}')


metadata = pd.read_csv(metadatafile, sep='\t', index_col=0)

stations           = metadata['station']
stations_starttime = metadata['starttime']
stations_endtime   = metadata['endtime']
stations_latitude  = metadata['latitude']
stations_longitude = metadata['longitude']
stations_elevation = metadata['elevation']
stations_channels  = metadata['channels']

client = Client('IRIS')


ista = -1
for station in stations:
    ista += 1
    if not station in stations_download:
        continue
    
    if not os.path.exists(f'{output_dir}/{network}/{station}'):
        os.makedirs(f'{output_dir}/{network}/{station}')
    
    sta_lat = stations_latitude[ista]
    sta_lon = stations_longitude[ista]
    sta_ele = stations_elevation[ista]
    channels_str = stations_channels[ista]
    
    channels = channels_str.split(',')
    
    
    start_date = datetime.strptime(stations_starttime[ista][0:10],'%Y-%m-%d')
    end_date = datetime.strptime(stations_endtime[ista][0:10],'%Y-%m-%d')
    idate = start_date
    
    while idate <= end_date:
        
        dayid = datetime.strftime(idate,'%Y%m%d_%H%M%S')

        starttime_str = datetime.strftime(idate,'%Y-%m-%dT%H:%M:%S')
        endtime_str   = datetime.strftime(idate+timedelta(days=1),'%Y-%m-%dT%H:%M:%S')
        starttime = UTCDateTime(starttime_str)
        endtime   = UTCDateTime(endtime_str)

        idate = idate + timedelta(days=1)


        for channel in channels:

            filename = f'{output_dir}/{network}/{station}/{dayid}_{network}_{station}_{channel}.SAC'

            if os.path.isfile(filename):
                print(f'{filename} exist. Skip!')
                continue
            
 
            # Fetch waveform from IRIS FDSN web service into a ObsPy stream object
            # and automatically attach correct response
            print(f'Downloading station: {station} channel: {channel} from: {starttime_str} to: {endtime_str}')
            try:
                st = client.get_waveforms(network=network, station=station, location=location, channel=channel, 
                                          starttime=starttime, endtime=endtime, attach_response=True)
                
                
                ##### PREPROCESSING #####
                # If you don't need all or part of the preprocessing, 
                # you can comment out the corresponding lines.
                # Remove response 
                if channel[1] == 'H':  # seismometer
                    st.remove_response(output=output_units_seis)
                elif channel[-1] == 'H':  # DPG or hydrophone
                    st.remove_response(output=output_units_pres)   
                # Downsampling
                # st.resample(samprate)
                # Demean and detrend
                st.detrend('demean')
     


                st.write(filename, format='SAC')
                
                # read header only
                sac = SACTrace.read(filename, headonly=True)
                
                ##### WRITE SAC HEADER #####
                sac.knetwk = network
                sac.kstnm  = station
                sac.khole  = location
                sac.kcmpnm = channel
                
                
                sac.stla = sta_lat
                sac.stlo = sta_lon
                sac.stel = sta_ele
                
                # write header-only, file must exist
                sac.write(filename, headonly=True)
                
            except Exception as e:
                print(e)
                print(f'Unable to download {filename}. Skip!')

        