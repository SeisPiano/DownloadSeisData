import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from glob import glob
from obspy import read
from obspy import UTCDateTime
from obspy.io.sac import SACTrace
from obspy.taup import TauPyModel
from obspy.clients.fdsn import Client
from obspy.geodetics import gps2dist_azimuth
from obspy.geodetics import kilometer2degrees



def channel_sort(channels,priority_order):
    """
    Sort by channel priority

    Yuechu Wu
    12131066@mail.sustech.edu.cn
    2025-08-03
    """

    total_channels_seis = [channel.code for channel in channels if channel.code[1] == 'H']
    total_channels_pres = [channel.code for channel in channels if channel.code[-1] == 'H']

    total_channels_seis.sort(key=lambda x: priority_order.get(x[0]))
    total_channels_pres.sort(key=lambda x: priority_order.get(x[0]))

    total_channels_str = ','.join([channel.code for channel in channels])

    if total_channels_seis and total_channels_pres:
        channels_seis_str = ','.join(total_channels_seis[:3])  
        channel_pres = total_channels_pres[0]
        channels_str = f'{channels_seis_str},{channel_pres}'
    elif not total_channels_pres:
        channels_str = ','.join(total_channels_seis[:3])
    elif not total_channels_seis:
        channels_str = total_channels_pres[0]
    else:
        channels_str = ''

    return channels_str,total_channels_str



def get_metadata(output_dir,network_code,start_time,end_time,channel_query,priority_order):
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

    client = Client('IRIS')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    inventory = client.get_stations(network=network_code,channel=channel_query,
                                    starttime=start_time,endtime=end_time,level='channel')

    for network in inventory:
        
        networks       = []
        stations       = []
        starttimes     = []
        endtimes       = []
        channels       = []
        total_channels = []
        sites          = []
        latitudes  = np.empty(len(network))
        longitudes = np.empty(len(network))
        elevations = np.empty(len(network))
        
        for ista, station in enumerate(network):
            
            station_code = station.code
            starttime = station.start_date
            endtime   = station.end_date
            site      = station.site.name
            latitude  = station.latitude
            longitude = station.longitude
            elevation = station.elevation

            channels_str,total_channels_str = channel_sort(station.channels,priority_order)
            
            networks.append(network_code)
            stations.append(station_code)
            sites.append(site)
            starttimes.append(str(starttime))
            endtimes.append(str(endtime))
            channels.append(channels_str)
            total_channels.append(total_channels_str)
            latitudes[ista]  = latitude
            longitudes[ista] = longitude
            elevations[ista] = elevation

        df = pd.DataFrame({'network':networks,'station':stations,'starttime':starttimes,'endtime':endtimes,
                           'latitude':latitudes,'longitude':longitudes, 'elevation': elevations,
                           'channel':channels,'channels':total_channels,'site': sites})

        filename = f'{output_dir}/{network_code}_fdsn_metadata.csv'

        df.to_csv(filename, sep='\t', float_format='%.6f')



def get_catalog(output_dir,metadata,stations_download,minmag_local,
                maxmag_local,maxradius_local,minmag_global):
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

    client = Client('IRIS')

    network = metadata.iloc[0, 0] 

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    if not os.path.exists(f'{output_dir}/{network}'):
        os.makedirs(f'{output_dir}/{network}')
        
    stations   = metadata['station']
    starttimes = metadata['starttime']
    endtimes   = metadata['endtime']
    latitudes  = metadata['latitude']
    longitudes = metadata['longitude']

    for station,starttime,endtime,sta_lat,sta_lon in tqdm(zip(stations,starttimes,endtimes,latitudes,longitudes), total=len(stations)):
        
        if not station in stations_download:
            continue

        try:
            cata_local = client.get_events(starttime=starttime,endtime=endtime,minmagnitude=minmag_local,
                                           maxmagnitude=maxmag_local,latitude=sta_lat,longitude=sta_lon,maxradius=maxradius_local)
            
            cata_global = client.get_events(starttime=starttime,endtime=endtime,minmag=minmag_global)

            catalog = cata_local + cata_global
            
            eventids         = []
            otimes_str       = []
            magnitude_types  = []
            descriptions     = []
            events_latitude  = np.empty(len(catalog))
            events_longitude = np.empty(len(catalog))
            events_depth     = np.empty(len(catalog))
            magnitudes       = np.empty(len(catalog))

            for ievt, event in enumerate(catalog):
                
                eventid         = event.resource_id.id.split('eventid=')[-1]
                origin          = event.origins[0]      
                otime_str       = str(origin.time)
                event_latitude  = origin.latitude
                event_longitude = origin.longitude     
                event_depth     = origin.depth * 0.001   # The unit of depth is km      
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
            
            df = pd.DataFrame({'event id':eventids,'origin time':otimes_str,'latitude':events_latitude,'longitude': events_longitude,
                               'depth':events_depth,'magnitude type':magnitude_types,'magnitude':magnitudes,'description': descriptions})
            
            filename = f'{output_dir}/{network}/{network}_{station}_catalog.csv'
            df.to_csv(filename, sep='\t', float_format='%.6f')

        except Exception as e:
            print(e)
            print(f'Unable to download {filename}. Skip!')
            


def download_daydata(output_dir,metadata,location,stations_download,
                     output_units_seis,output_units_pres,sample_rate=None):
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
    
    client = Client('IRIS')

    network = metadata.iloc[0, 0] 

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(f'{output_dir}/{network}'):
        os.makedirs(f'{output_dir}/{network}')

    stations    = metadata['station']
    start_times = metadata['starttime']
    end_times   = metadata['endtime']
    latitudes   = metadata['latitude']
    longitudes  = metadata['longitude']
    elevations  = metadata['elevation']
    stations_channels = metadata['channel']

    # Calculate the total number of files
    data_numbers = 0
    for station,start_time,end_time,channels_str in zip(stations,start_times,end_times,stations_channels):

        if not station in stations_download:
            continue
              
        channels = channels_str.split(',')
        delta = UTCDateTime(end_time).datetime - UTCDateTime(start_time).datetime

        data_number = len(channels) * delta.days
        data_numbers = data_number + data_numbers

    pbar = tqdm(total = data_numbers)

    for station,start_time,end_time,latitude,longitude,elevation,channels_str in zip(
        stations,start_times,end_times,latitudes,longitudes,elevations,stations_channels):

        if not station in stations_download:
            continue
          
        if not os.path.exists(f'{output_dir}/{network}/{station}'):
            os.makedirs(f'{output_dir}/{network}/{station}')

        channels = channels_str.split(',')

        current_time = UTCDateTime(start_time)

        while current_time <= end_time: # Begin day loop
            
            next_time = current_time + 86400
            
            dayid = current_time.strftime('%Y%m%d_%H%M%S')

            starttime_str = current_time.strftime('%Y-%m-%dT%H:%M:%S')
            endtime_str   = next_time.strftime('%Y-%m-%dT%H:%M:%S')

            starttime = current_time
            endtime   = next_time

            for channel in channels: # Begin channel loop
                pbar.update(1)

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
                    # If full preprocessing is not required, you can comment out the corresponding lines.

                    # Remove response 
                    if channel[1] == 'H':  # seismometer
                        st.remove_response(output=output_units_seis)
                    elif channel[-1] == 'H':  # DPG or hydrophone
                        st.remove_response(output=output_units_pres)

                    # Downsampling
                    if sample_rate:
                        st.resample(sample_rate)

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
                    
                    sac.stla = latitude
                    sac.stlo = longitude
                    sac.stel = elevation
                    
                    # write header-only, file must exist
                    sac.write(filename, headonly=True)
                    
                except Exception as e:
                    print(e)
                    print(f'Unable to download {filename}. Skip!')

            current_time += 86400    # 加一天（单位是秒）

    pbar.close()



def download_event(output_dir,catalog_dir,metadata,location,stations_download,output_units_seis,
                   output_units_pres,event_length,btime,Rayleigh_velocity,sample_rate=None):
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

    client = Client('IRIS')
    model = TauPyModel(model='iasp91')

    network = metadata.iloc[0, 0]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    stations           = metadata['station']
    stations_latitude  = metadata['latitude']
    stations_longitude = metadata['longitude']
    stations_elevation = metadata['elevation']
    stations_channels  = metadata['channel']

    data_numbers = 0
    for station,channels_str in zip(stations,stations_channels):
        
        if not station in stations_download:
            continue
             
        channels = channels_str.split(',')
        
        # station catalog file name
        catalogfile = f'{catalog_dir}/{network}/{network}_{station}_catalog.csv'
        catalog = pd.read_csv(catalogfile, sep='\t', index_col=0)

        data_number = len(channels) * len(catalog)
        data_numbers = data_number + data_numbers

    pbar = tqdm(total=data_numbers)


    for station,sta_lat,sta_lon,sta_ele,channels_str in zip(stations,stations_latitude,stations_longitude,
                                                            stations_elevation,stations_channels):
        if not station in stations_download:
            continue
        
        channels = channels_str.split(',')

        # station catalog file name
        catalogfile = f'{catalog_dir}/{network}/{network}_{station}_catalog.csv'
        catalog = pd.read_csv(catalogfile, sep='\t', index_col=0)
    
        otimes_str       = catalog['origin time']
        events_latitude  = catalog['latitude']
        events_longitude = catalog['longitude']
        events_depth     = catalog['depth']
        magnitude_types  = catalog['magnitude type']
        magnitudes       = catalog['magnitude']
        
        for otime_str,evt_lat,evt_lon,evt_dep,magnitude,magnitude_type in zip(otimes_str,
            events_latitude,events_longitude,events_depth,magnitudes,magnitude_types):
            
            otime = UTCDateTime(otime_str)
        
            eventid = otime.strftime('%Y%m%d_%H%M%S')

            if not os.path.exists(f'{output_dir}/{eventid}'):
                os.makedirs(f'{output_dir}/{eventid}')

            for channel in channels:
                pbar.update(1)

                filename = f'{output_dir}/{eventid}/{eventid}_{network}_{station}_{channel}.SAC'

                if os.path.isfile(filename):
                    print(f'{filename} exist. Skip!')
                    continue
                
                starttime = otime + btime
                endtime   = otime + event_length + btime

                starttime_str = starttime.strftime('%Y-%m-%dT%H:%M:%S')
                endtime_str   = endtime.strftime('%Y-%m-%dT%H:%M:%S')

                # Fetch waveform from IRIS FDSN web service into a ObsPy stream object
                # and automatically attach correct response
                print(f'Downloading station: {station} channel: {channel} from: {starttime_str} to: {endtime_str}')
                try:
                    st = client.get_waveforms(network=network,station=station,location=location,channel=channel,
                                              starttime=starttime,endtime=endtime,attach_response=True)

                    ##### PREPROCESSING #####
                    # If full preprocessing is not required, you can comment out the corresponding lines.

                    # Remove response 
                    if channel[1] == 'H':  # seismometer
                        st.remove_response(output=output_units_seis)
                    elif channel[-1] == 'H':  # DPG or hydrophone
                        st.remove_response(output=output_units_pres)

                    # Downsampling
                    if sample_rate:
                        st.resample(sample_rate)

                    # Demean, detrend and taper
                    st.detrend('demean')
                    st.taper(max_percentage=0.05)

                    st.write(filename, format='SAC')

                    distance_in_m, baz, az = gps2dist_azimuth(sta_lat, sta_lon, evt_lat, evt_lon)
                    distance_in_km = distance_in_m * 0.001
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
                    sac.kevnm = (otime_str[0:4] + otime_str[5:7] + otime_str[8:10] + 
                                otime_str[10:13] + otime_str[14:16] + otime_str[17:19])
                    # decimal of seconds
                    sac.kuser0 = otime_str[19:27]
                    
                    # magnitude_type
                    sac.kuser1 = magnitude_type
        
                    # write header-only, file must exist
                    sac.write(filename, headonly=True)
                    
                except Exception as e:
                    print(e)
                    print(f'Unable to download {filename}. Skip!')

    pbar.close()



def cut_event(input_dir,output_dir,catalog_dir,metadata,stations_download,
              event_length,btime,Rayleigh_velocity,sample_rate=None):
    """
    Cut earthquake event data from day data.
    As an alternative to a4_download_eventdata, 
    it can save a lot of time and needs to be used after a2_download_daydata.

    Yuechu Wu
    12131066@mail.sustech.edu.cn
    2024-02-05

    Added progress bar
    Yuechu Wu
    2024-05-06

    Encapsulate the main modules into functions.
    Yuechu Wu
    2025-08-03
    """

    model = TauPyModel(model='iasp91')

    network = metadata.iloc[0, 0] 

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    stations           = metadata['station']
    stations_latitude  = metadata['latitude']
    stations_longitude = metadata['longitude']
    stations_elevation = metadata['elevation']
    stations_channels  = metadata['channel']

    data_numbers = 0
    for station,channels_str in zip(stations,stations_channels):
        if not station in stations_download:
            continue
             
        channels = channels_str.split(',')
        
        # station catalog file name
        catalogfile = f'{catalog_dir}/{network}/{network}_{station}_catalog.csv'
        catalog = pd.read_csv(catalogfile, sep='\t', index_col=0)

        data_number = len(channels) * len(catalog)
        data_numbers = data_number + data_numbers

    pbar = tqdm(total=data_numbers)

    for station,sta_lat,sta_lon,sta_ele,channels_str in zip(stations,stations_latitude,stations_longitude,
                                                            stations_elevation,stations_channels):
        if not station in stations_download:
            continue
        
        channels = channels_str.split(',')

        # station catalog file name
        catalogfile = f'{catalog_dir}/{network}/{network}_{station}_catalog.csv'
        catalog = pd.read_csv(catalogfile, sep='\t', index_col=0)
    
        otimes_str       = catalog['origin time']
        events_latitude  = catalog['latitude']
        events_longitude = catalog['longitude']
        events_depth     = catalog['depth']
        magnitude_types  = catalog['magnitude type']
        magnitudes       = catalog['magnitude']
        
        for otime_str,evt_lat,evt_lon,evt_dep,magnitude,magnitude_type in zip(otimes_str,
            events_latitude,events_longitude,events_depth,magnitudes,magnitude_types):
            
            otime = UTCDateTime(otime_str)
        
            eventid = otime.strftime('%Y%m%d_%H%M%S')

            if not os.path.exists(f'{output_dir}/{eventid}'):
                os.makedirs(f'{output_dir}/{eventid}')

            starttime = otime + btime
            endtime   = otime + event_length + btime

            start_date = starttime.strftime('%Y%m%d')
            end_date   = endtime.strftime('%Y%m%d')

            starttime_str = starttime.strftime('%Y-%m-%dT%H:%M:%S')
            endtime_str   = endtime.strftime('%Y-%m-%dT%H:%M:%S')

            for channel in channels:
                pbar.update(1)

                filename = f'{output_dir}/{eventid}/{eventid}_{network}_{station}_{channel}.SAC'

                if os.path.isfile(filename):
                    print(f'{filename} exist. Skip!')
                    continue
                
                print(f'Cutting station: {station} channel: {channel} from: {starttime_str} to: {endtime_str}')
                
                if start_date == end_date:
                    
                    day_filename = glob(f'{input_dir}/{network}/{station}/*{start_date}*{channel}.SAC')
                    
                    if not day_filename:
                        print('The day data does not exist. Skip!')
                        continue

                    st = read(day_filename[0])
                else:

                    start_filename = glob(f'{input_dir}/{network}/{station}/*{start_date}*{channel}.SAC')
                    end_filename   = glob(f'{input_dir}/{network}/{station}/*{end_date}*{channel}.SAC')

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
                location = tr.stats.location

                st_event = st.trim(starttime=starttime, endtime=endtime-dt)

                ##### PREPROCESSING #####
                # If full preprocessing is not required, you can comment out the corresponding lines.

                # Downsampling
                if sample_rate:
                    st_event.resample(sample_rate)

                # Demean, detrend and taper
                st_event.detrend('demean')
                st_event.taper(max_percentage=0.05)

                st_event.write(filename, format='SAC')
                                                                        
                distance_in_m, baz, az = gps2dist_azimuth(sta_lat, sta_lon, evt_lat, evt_lon)
                distance_in_km = distance_in_m * 0.001
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