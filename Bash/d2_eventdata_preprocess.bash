#!/bin/bash
# Preprocess SAC event data
#
# Pre-procssing steps included here are:
# - Response Removal
# - Downsampling
# - rmean, rtrend and taper
#
# Yuechu Wu
# 12131066@mail.sustech.edu.cn
# 2023-02-28

export SAC_DISPLAY_COPYRIGHT=0 # hide version information


network=XO

INPUTdir="DATA/SAC_event"          # SAC event data directory
OUTPUTdir="DATA/datacache_preproc" # preprocessed SAC event data directory

irrm="resp" # method of removing instrument response, "sacpz" or "resp"
oneir=0 # 1 means each component of each station only corresponds to one instrument response file, which should be in the "IRdir/network" directory. 0 means instrument response file in the "IRdir/network/date" directory.
pre_filt=(0.001 0.005 10 20)   #  pre-filtering in the frequency domain (specifying the four corner frequencies of the frequency taper).

samplerate=5 # new sample rate

istaper=0 # 1 means taper, 0 means don't.


##### END OF USER INPUT #####
if [ "${irrm}"x = "sacpz"x ]; then
    IRdir="DATA/response/sacpz_event"
elif [ "${irrm}"x = "resp"x ]; then
    IRdir="DATA/response/resp_event"
else
    echo "Unsupported instrument response type! Please input sacpz or resp."
    exit 1
fi


for eventid in `ls ${INPUTdir}/${network}` # begin event loop
do
if [ ! -d "${INPUTdir}/${network}/${eventid}" ];then
    continue
fi

echo ${eventid}

if [ "`ls -A ${INPUTdir}/${network}/${eventid}`" = "" ]; then # skip empty folder
   echo "No event data. Skip!"
   continue
fi

# make preprocessed data folder
if [ ! -d "${OUTPUTdir}/${network}/${eventid}" ];then
    mkdir -p "${OUTPUTdir}/${network}/${eventid}"
fi

for sacfile in `ls ${INPUTdir}/${network}/${eventid}/*.SAC` # begin station loop
do

sacname=${sacfile##*/}
outsac=${OUTPUTdir}/${network}/${eventid}/${sacname}
cp ${sacfile} ${OUTPUTdir}/${network}/${eventid}

station=`echo ${sacname} | awk -F"_" '{print $3}'`
channel=`echo ${sacname} | awk -F"_" '{print $4}' | awk -F"." '{print $1}'`

if [ ${oneir} -eq 1 ];then
    irpath=${IRdir}/${network}
else
    irpath=${IRdir}/${network}/${eventid}
fi
irfile=`find ${irpath} -maxdepth 1 -name "*${station}*${channel}"`

# call sac for data preprocessing
# rmean; rtrend
# remove instrument response: the default unit of SAC is nm, so it needs to be multiplied by 1.0e9
# downsampling: The product of two downsampling factors = old sample rate / new sample rate

dt_new=`echo 1 ${samplerate} | awk '{printf("%f",$1/$2)}'`

if [ "${irrm}"x = "sacpz"x ]; then
sac << EOF
read ${outsac}
rmean; rtrend
trans from polezero subtype ${irfile} to none freq ${pre_filt[0]} ${pre_filt[1]} ${pre_filt[2]} ${pre_filt[3]} prew on
mul 1.0e9
interpolate delta ${dt_new}
write over
quit
EOF
elif [ "${irrm}"x = "resp"x ]; then
sac << EOF
read ${outsac}
rmean; rtrend
trans from evalresp fname ${irfile} to none freq ${pre_filt[0]} ${pre_filt[1]} ${pre_filt[2]} ${pre_filt[3]} prew on
interpolate delta ${dt_new}
write over
quit
EOF
else
echo "Unsupported instrument response type! Please input sacpz or resp."
exit 1
fi

# taper
if [ ${istaper} -eq 1 ]; then
sac << EOF
read ${outsac}
taper
write over
quit
EOF
fi


done # end station loop

done # end event loop