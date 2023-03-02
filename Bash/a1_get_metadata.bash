#!/bin/bash
# get stations metadata by using FetchMetadata
# Yuechu Wu
# 12131066@mail.sustech.edu.cn
# 2023-02-08

OStype="MacOS"  # "MacOS" for Mac OS user, "Linux" for Linux user

OUTPUTdir="DATA/METADATA" # stations metadata directory
outdata=${OUTPUTdir}/${network}_metadata.txt
origindata=${OUTPUTdir}/${network}_origin_metadata.txt
tempdata=${OUTPUTdir}/${network}_temp_metadata.txt

# station information can be obtained from https://ds.iris.edu/mda
network=XO  # network name to download metadata
stations=WD52,WD55 # list of stations to download

location=--,00 # for OBS,location code=--; for land stations, only download the instrument which location code=00
allchannel=HH?,BH?,HDH,EDH # list of channels to download


##### END OF USER INPUT #####
if [ ! -d $OUTPUTdir ]; then
    mkdir -p $OUTPUTdir
fi

if [ -f $outdata ]; then
    rm $outdata
fi
echo Downloading station metadata of $network-$stations
FetchMetadata -N $network -S $stations -L $location -C $allchannel -o $origindata

cat $origindata | awk -F"|" '{print $1,$2,$4,$16,$17,$5,$6,$7}' > $tempdata

if [ "${OStype}"x == "MacOS"x ]; then
    sed -i "" "1d" $tempdata # delete the first row
elif [ "${OStype}"x == "Linux"x ]; then
    sed -i '1d' $tempdata    # delete the first row
else
    echo "Unsupported system type! Please input MacOS or Linux."
    exit 1
fi

# make metadata for next download
for station in `echo ${stations//,/ }` # begin station loop
do
    starttime=`grep $station $tempdata | awk '{print $4}' | awk 'NR==1 {print}'` # select only the first row
    startdate=${starttime:0:10}
    endtime=`grep $station $tempdata | awk '{print $5}' | awk 'NR==1 {print}'`
    enddate=${endtime:0:10}
    latitude=`grep $station $tempdata | awk '{print $6}' | awk 'NR==1 {print}'`
    longitude=`grep $station $tempdata | awk '{print $7}' | awk 'NR==1 {print}'`
    elevation=`grep $station $tempdata | awk '{print $8}' | awk 'NR==1 {print}'`
    i=0
for channel in `grep $station $tempdata | awk '{print $3}'` # begin channel loop
do
    ((i=$i+1))
if [ $i == 1 ]; then
    channels=$channel
else
    channels=`echo $channels $channel | awk '{print $1","$2}'`
fi
done # end channel loop
echo $network $station $channels $startdate $enddate $latitude $longitude $elevation >> $outdata
done # end station loop

# rm $origindata $tempdata
