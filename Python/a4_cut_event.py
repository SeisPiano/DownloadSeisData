"""
Cut earthquake event data from day data.
As an alternative to a4_download_eventdata, 
it can save a lot of time and needs to be used after a2_download_daydata.

Yuechu Wu
12131066@mail.sustech.edu.cn
2024-02-05
"""


import os
import glob
import numpy as np
import pandas as pd
from tqdm import tqdm
from obspy import read
from obspy import UTCDateTime
from obspy.taup import TauPyModel
from obspy.io.sac import SACTrace
from obspy.geodetics import gps2dist_azimuth
from obspy.geodetics import kilometer2degrees



input_dir  = 'DATA/sacdata_day'
output_dir = 'DATA/sacdata_event'
catlog_dir = 'catalog'

network  = 'XO'  # network name
location = '--'  # for OBS, location is '--'
stations_download = ['WD58','WS75']  # list of stations to download


# samprate = 5  # new sample rate

# Length of seismic event (unit: seconds)
event_length = 7200
# The start time of the event file (in seconds relative to the origin time of event)
btime = -600
# The lower and upper limits of Rayleigh wave velocity (km/s)
Rayleigh_velocity = [3, 4.5]


metadatafile = network + '_fdsn_metadata.txt'  # metadata file name





##### END OF USER INPUT #####
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

metadata = pd.read_csv(metadatafile, sep='\t', index_col=0)

stations           = metadata['station']
stations_starttime = metadata['starttime']
stations_endtime   = metadata['endtime']
stations_latitude  = metadata['latitude']
stations_longitude = metadata['longitude']
stations_elevation = metadata['elevation']
stations_channels  = metadata['channel']


model = TauPyModel(model='iasp91')

data_numbers = 0
ista = -1
for station in stations:
    ista += 1
    if not station in stations_download:
        continue
    
    channels_str = stations_channels[ista]        
    channels = channels_str.split(',')
    
    # station catalog file name
    catalogfile = f'catalog/{network}/{network}_{station}_catalog.txt'
    catalog = pd.read_csv(catalogfile, sep='\t', index_col=0)

    data_number = len(channels)*len(catalog)
    data_numbers = data_number + data_numbers

pbar = tqdm(total=data_numbers)

ista = -1
for station in stations:
    ista += 1
    if not station in stations_download:
        continue
    
    sta_lat = stations_latitude[ista]
    sta_lon = stations_longitude[ista]
    sta_ele = stations_elevation[ista]
    channels_str = stations_channels[ista]
    
    channels = channels_str.split(',')

    # station catalog file name
    catalogfile = f'catalog/{network}/{network}_{station}_catalog.txt'
    catalog = pd.read_csv(catalogfile, sep='\t', index_col=0)
   
    otimes_str       = catalog['origin time']
    events_latitude  = catalog['latitude']
    events_longitude = catalog['longitude']
    events_depth     = catalog['depth']
    magnitude_types  = catalog['magnitude type']
    magnitudes       = catalog['magnitude']
    
    
    ievt = -1    
    for otime_str in otimes_str:
        ievt += 1

        otime = UTCDateTime(otime_str)
        evt_lat        = events_latitude[ievt]
        evt_lon        = events_longitude[ievt]
        evt_dep        = events_depth[ievt]
        magnitude      = magnitudes[ievt]
        magnitude_type = magnitude_types[ievt]
    
        eventid = otime.datetime.strftime('%Y%m%d_%H%M%S')

        if not os.path.exists(f'{output_dir}/{eventid}'):
            os.makedirs(f'{output_dir}/{eventid}')

        starttime = otime + btime
        endtime   = otime + event_length + btime

        start_date = starttime.datetime.strftime('%Y%m%d')
        end_date   = endtime.datetime.strftime('%Y%m%d')

        starttime_str = starttime.datetime.strftime('%Y-%m-%dT%H:%M:%S')
        endtime_str   = endtime.datetime.strftime('%Y-%m-%dT%H:%M:%S')


        for channel in channels:

            pbar.update(1)

            print(f'Cutting station: {station} channel: {channel} from: {starttime_str} to: {endtime_str}')

            filename = f'{output_dir}/{eventid}/{eventid}_{network}_{station}_{channel}.SAC'

            if os.path.isfile(filename):
                print(f'{filename} exist. Skip!')
                continue
            
               
            if start_date == end_date:
                
                day_filename = glob.glob(f'{input_dir}/{network}/{station}/*{start_date}*{channel}.SAC')
                
                if not day_filename:
                    print('The day data does not exist. Skip!')
                    continue
                st = read(day_filename[0])
            else:
                start_filename = glob.glob(f'{input_dir}/{network}/{station}/*{start_date}*{channel}.SAC')
                end_filename   = glob.glob(f'{input_dir}/{network}/{station}/*{end_date}*{channel}.SAC')
                if not start_filename or not end_filename:
                    print('The day data does not exist. Skip!')
                    continue
                st = read(start_filename[0])
                st += read(end_filename[0])
                st.merge()
                
    
            if st[0].stats.starttime > starttime or st[0].stats.endtime < endtime:
                print('The day data does not include event data. Skip!')
                continue
            
            if np.ma.is_masked(st[0].data):
                st[0].data = st[0].data.filled()

            tr = st[0]
            dt = tr.stats.delta
            st_event = st.trim(starttime=starttime, endtime=endtime-dt)

            ##### PREPROCESSING #####
            # If you don't need all or part of the preprocessing, 
            # you can comment out the corresponding lines.   
            # Downsampling
            # st_event.resample(samprate)
            # Demean, detrend and taper
            st_event.detrend('demean')
            st_event.taper(max_percentage=0.1)


            st_event.write(filename, format='SAC')
            
                                                                    
            distance_in_m, baz, az = gps2dist_azimuth(sta_lat, sta_lon, evt_lat, evt_lon)
            distance_in_km = distance_in_m*0.001
            distance_in_degree = kilometer2degrees(distance_in_km)
    
            P_arrivals = model.get_travel_times(source_depth_in_km=evt_dep, distance_in_degree=distance_in_degree, phase_list='P')
            S_arrivals = model.get_travel_times(source_depth_in_km=evt_dep, distance_in_degree=distance_in_degree, phase_list='S')
                                                    
            # Rayleigh wave window
            Rayleigh_begin = distance_in_km / Rayleigh_velocity[1]
            Rayleigh_end   = distance_in_km / Rayleigh_velocity[0]
            
            
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
            
            sac.evla = evt_lat
            sac.evlo = evt_lon
            sac.evdp = evt_dep
            sac.mag  = magnitude
            
            
            sac.gcarc = distance_in_degree
            sac.dist  = distance_in_km            
            sac.az    = az
            sac.baz   = baz
            
            
            sac.o      = otime
            sac.iztype = 'io'    
            sac.ko     = 'O'       

            # P and S prediction arrival
            if P_arrivals:    
                sac.a   = otime + P_arrivals[0].time
                sac.t0  = otime + S_arrivals[0].time
                sac.ka  = 'P'
                sac.kt0 = 'S'
            
            # Rayleigh wave window
            sac.t1  = otime + Rayleigh_begin
            sac.t2  = otime + Rayleigh_end
            sac.kt1 = 'RayStart'
            sac.kt2 = 'RayEnd'
            
            ##### WRITE ORIGIN TIME INTO SAC HEADER #####
            # date, hour, minute, integer of seconds
            sac.kevnm = otime_str[0:4] + otime_str[5:7] + otime_str[8:10] + \
                        otime_str[10:13] + otime_str[14:16] + otime_str[17:19]
            # decimal of seconds
            sac.kuser0 = otime_str[19:27]
            
            # magnitude_type
            sac.kuser1 = magnitude_type


            # write header-only, file must exist
            sac.write(filename, headonly=True)


pbar.close()
