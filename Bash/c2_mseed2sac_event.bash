#!/bin/bash
# Convert miniSEED event data to SAC data
# Write station location and event information into SAC header
#
# Yuechu Wu
# 12131066@mail.sustech.edu.cn
# 2023-02-26


export SAC_DISPLAY_COPYRIGHT=0 # hide version information


network=XO # network name
filesuff=SAC # suffix of SAC data

INPUTdir="DATA/mseed_event"   # miniSEED event data directory
OUTPUTdir="DATA/SAC_event"    # SAC event data directory

EVENTINFOdir="DATA/EVENTINFO" # match the event information directory
metadata=DATA/METADATA/${network}_metadata.txt # match the station metadata


##### END OF USER INPUT #####
for eventid in `ls ${INPUTdir}/${network}` # begin event loop
do
if [ ! -d "${INPUTdir}/${network}/${eventid}" ];then
    continue
fi

echo ${eventid}

if [ "`ls -A ${INPUTdir}/${network}/${eventid}`" = "" ]; then # skip empty folder
   echo "No miniSEED data. Skip!"
   continue
fi

# make SAC data folder
if [ ! -d "${OUTPUTdir}/${network}/${eventid}" ];then
    mkdir -p "${OUTPUTdir}/${network}/${eventid}"
fi

for mseedfile in `ls ${INPUTdir}/${network}/${eventid}/*.mseed` # begin station loop
do

mseed2sac ${mseedfile}
# mseedname=${mseedfile##*/}

for sactemp in `ls *.SAC` # begin channel loop
do
station=`echo $sactemp | awk -F"." '{print $2}'`
channel=`echo $sactemp | awk -F"." '{print $4}'`
# echo $station $channel

# read station metadata
latitude=`cat ${metadata} | grep -n ${station} | awk '{print $6}'`
longitude=`cat ${metadata} | grep -n ${station} | awk '{print $7}'`
elevation=`cat ${metadata} | grep -n ${station} | awk '{print $8}'`

# read event information
eventlist=${EVENTINFOdir}/${network}/${network}_${station}_list.txt

event_latitude=`cat ${eventlist} | grep -n ${eventid} | awk '{print $2}'`
event_longitude=`cat ${eventlist} | grep -n ${eventid} | awk '{print $3}'`
event_depth=`cat ${eventlist} | grep -n ${eventid} | awk '{print $4}'`
event_magnitude=`cat ${eventlist} | grep -n ${eventid} | awk '{print $5}'`

sacfile=${eventid}_${network}_${station}_${channel}.${filesuff} # sac data name

mv ${sactemp} ${sacfile} # rename

# add station location and event information
sac << EOF
read ${sacfile}
chnhdr STLA ${latitude} STLO ${longitude} STEL ${elevation}
chnhdr EVLA ${event_latitude} EVLO ${event_longitude} EVDP ${event_depth} MAG ${event_magnitude}
wh
q
EOF

mv ${sacfile} ${OUTPUTdir}/${network}/${eventid} # move sac data to sac folder

done # end channel loop

done # end station loop

done # end event loop
