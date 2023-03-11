#!/bin/bash
# Preprocess SAC day data
#
# Pre-procssing steps included here are:
# - Response Removal
# - Downsampling
# - rmean and rtrend
#
# Yuechu Wu
# 12131066@mail.sustech.edu.cn
# 2023-02-28

export SAC_DISPLAY_COPYRIGHT=0 # hide version information


network=XO # network name

irrm="resp" # method of removing instrument response, "sacpz" or "resp"
oneir=0 # 1 means each component of each station only corresponds to one instrument response file, which should be in the IRdir/network/station directory. 0 means instrument response file in the IRdir/network/station/date directory.
freqlimits=(0.001 0.005 10 20)  #  low-pass and high-pass taper in the frequency domain (specifying the four corner frequencies of the frequency taper).

samplerate=5 # new sample rate

INPUTdir="DATA/SAC_day"                 # SAC day data directory
OUTPUTdir="DATA/datacache_day_preproc"  # preprocessed SAC day data directory


##### END OF USER INPUT #####
if [ "${irrm}"x = "sacpz"x ]; then
    IRdir="DATA/response/sacpz_day"
elif [ "${irrm}"x = "resp"x ]; then
    IRdir="DATA/response/resp_day"
else
    echo "Unsupported instrument response type! Please input sacpz or resp."
    exit 1
fi

for station in `ls ${INPUTdir}/${network}` # begin station loop
do
if [ ! -d "${INPUTdir}/${network}/${station}" ]; then
    continue
fi

# make preprocessed data folder
if [ ! -d "${OUTPUTdir}/${network}/${station}" ]; then
    mkdir -p "${OUTPUTdir}/${network}/${station}"
fi

for sacfile in `ls ${INPUTdir}/${network}/${station}/*.SAC` # begin day loop
do
sacname=${sacfile##*/}
outsac=${OUTPUTdir}/${network}/${station}/${sacname}
cp ${sacfile} ${OUTPUTdir}/${network}/${station}
date=${sacname:0:8}
channel=`echo ${sacname} | awk -F"_" '{print $4}' | awk -F"." '{print $1}'`

# The value range of the downsampling factor is 2-7, so the downsampling may not be completed at one time
# dt=`saclst DELTA f ${sacfile} | awk '{print $2}'` # delta of sac data
# downfactor=$(printf "%.0f\n" `echo 1 ${dt} ${samplerate} | awk '{printf("%f",$1/$2/$3)}'`)
# samplerate_old=`echo 1 ${dt} | awk '{printf("%d",$1/$2)}'`
# downfactor=`echo ${samplerate_old} ${samplerate} | awk '{printf("%d",$1/$2)}'`

if [ ${oneir} -eq 1 ];then
    irpath=${IRdir}/${network}/${station}
else
    irpath=${IRdir}/${network}/${station}/${date}
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
trans from polezero subtype ${irfile} to none freq ${freqlimits[0]} ${freqlimits[1]} ${freqlimits[2]} ${freqlimits[3]} prew on
mul 1.0e9
interpolate delta ${dt_new}
write over
quit
EOF
elif [ "${irrm}"x = "resp"x ]; then
sac << EOF
read ${outsac}
rmean; rtrend
trans from evalresp fname ${irfile} to none freq ${freqlimits[0]} ${freqlimits[1]} ${freqlimits[2]} ${freqlimits[3]} prew on
interpolate delta ${dt_new}
write over
quit
EOF
else
echo "Unsupported instrument response type! Please input sacpz or resp."
exit 1
fi

done # end day loop

done # end station loop
