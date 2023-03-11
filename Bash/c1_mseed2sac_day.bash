#!/bin/bash
# Convert miniSEED day data to SAC data
# Write station location information into SAC header
#
# Yuechu Wu
# 12131066@mail.sustech.edu.cn
# 2023-02-26

export SAC_DISPLAY_COPYRIGHT=0 # hide version information


network=XO # network name
filesuff=SAC # suffix of SAC data

INPUTdir="DATA/mseed_day" # miniSEED day data directory
OUTPUTdir="DATA/SAC_day"  # SAC day data directory

metadata=DATA/METADATA/${network}_metadata.txt # match the station metadata


##### END OF USER INPUT #####
for station in `ls ${INPUTdir}/${network}` # begin station loop
do
if [ ! -d "${INPUTdir}/${network}/${station}" ];then
    continue
fi
echo ${station}

# make SAC data folder
if [ ! -d "${OUTPUTdir}/${network}/${station}" ];then
    mkdir -p "${OUTPUTdir}/${network}/${station}"
fi

# read station metadata
latitude=`cat ${metadata} | grep -n ${station} | awk '{print $6}'`
longitude=`cat ${metadata} | grep -n ${station} | awk '{print $7}'`
elevation=`cat ${metadata} | grep -n ${station} | awk '{print $8}'`

for mseedfile in `ls ${INPUTdir}/${network}/${station}/*.mseed` # begin day loop
do

mseed2sac ${mseedfile}
mseedname=${mseedfile##*/}

for sactemp in `ls *.SAC` # begin channel loop
do
channel=`echo $sactemp | awk -F"." '{print $4}'`
time=`echo $sactemp | awk -F"." '{print $8}'`
sacfile=${mseedname:0:8}${time:0:4}_${network}_${station}_${channel}.${filesuff} # sac data name

mv ${sactemp} ${sacfile} # rename

# add station location information
sac << EOF
read ${sacfile}
chnhdr STLA ${latitude} STLO ${longitude} STEL ${elevation}
wh
q
EOF

mv ${sacfile} ${OUTPUTdir}/${network}/${station} # move sac data to sac folder

done # end channel loop

done # end day loop
done # end station loop
