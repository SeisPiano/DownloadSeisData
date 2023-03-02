#!/bin/bash
# get event information by using FetchEvent
# Yuechu Wu
# 12131066@mail.sustech.edu.cn
# 2022-04-25
#
# read metadata and batch download
# 2023-02-11, Yuechu Wu

OStype="MacOS"  # "MacOS" for Mac OS user, "Linux" for Linux user

network=XO

OUTPUTdir="DATA/EVENTINFO" # event information directory
metadata=DATA/METADATA/${network}_metadata.txt

maxradius=180  # specify circular region
minradius=30   # specify circular region with optional minimum radius, can be 0
minmag=5.5     # minimum magnitude
maxmag=10      # maximum magnitude


##### END OF USER INPUT #####
if [ ! -d ${OUTPUTdir}/${network} ]; then
    mkdir -p ${OUTPUTdir}/${network}
fi

for mdata in `cat $metadata | awk '{print $1"_"$2"_"$3"_"$4"_"$5"_"$6"_"$7}'` # begin station loop
do

station=`echo $mdata | awk -F "_" '{print$2}'`
startdate=`echo $mdata | awk -F "_" '{print$4}'`
enddate=`echo $mdata | awk -F "_" '{print$5}'`
latitude=`echo $mdata | awk -F "_" '{print$6}'`
longitude=`echo $mdata | awk -F "_" '{print$7}'`
stdate=$startdate
if [ "${OStype}"x == "MacOS"x ]; then
    eddate=`date -v +1d -j -f %Y-%m-%d "${enddate}" +%Y-%m-%d`
elif [ "${OStype}"x == "Linux"x ]; then
    eddate=`date -d "+1 day ${enddate}" +%Y-%m-%d`
else
    echo "Unsupported system type! Please input MacOS or Linux."
    exit 1
fi
    
eventinfo=${OUTPUTdir}/${network}/${network}_${station}_info.txt       # event information file name
eventlist=${OUTPUTdir}/${network}/${network}_${station}_list.txt       # event information file name
eventtime=${OUTPUTdir}/${network}/${network}_${station}_time.txt       # event time file name
eventlocmag=${OUTPUTdir}/${network}/${network}_${station}_locmag.txt   # event location and magnitude file name
    
echo Downloading event information of $network-$station from ${stdate}T00:00:00 to ${eddate}T00:00:00    
FetchEvent -s ${stdate},00:00:00 -e ${eddate},00:00:00 --radius $latitude:$longitude:$maxradius:$minradius --mag $minmag:$maxmag -o $eventinfo

cat $eventinfo | awk -F"|" '{print $2}' | awk -F"/" '{print $1,$2,$3}' | awk -F":" '{print $1,$2,$3}' | awk '{print $1$2$3$4$5$6}' > $eventtime
cat $eventinfo | awk -F"|" '{print $3,$4,$5,$9}' | awk -F"," '{print $1,$2}' | awk '{print $1,$2,$3,$5}' > $eventlocmag
cat $eventinfo | awk -F"|" '{print $2,$3,$4,$5,$9}' | awk -F"/" '{print $1,$2,$3}' | awk -F":" '{print $1,$2,$3}' | awk -F"," '{print $1,$2}' | awk '{print $1$2$3$4$5$6,$7,$8,$9,$11}' > $eventlist

done # end station loop
