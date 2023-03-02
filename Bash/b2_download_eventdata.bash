#!/bin/bash
# download seismic event data by using FetchData
# Yuechu Wu
# 12131066@mail.sustech.edu.cn
# 2022-04-28
#
# read metadata and event information, and batch download
# 2023-02-15, Yuechu Wu

OStype="MacOS"  # "MacOS" for Mac OS user, "Linux" for Linux user

network=XO

DATAdir="DATA/mseed_event"  # seismic data directory
IRdir="DATA/response"       # instrument response directory

metadata=DATA/METADATA/${network}_metadata.txt
EVENTINFOdir="DATA/EVENTINFO" # event information directory

location=-- # for OBS, location=--; for land stations, location=00
event_length=7200  # The length of seismic event data, in second


##### END OF USER INPUT #####
for mdata in `cat $metadata | awk '{print $1"_"$2"_"$3}'` # begin station loop
do

station=`echo $mdata | awk -F "_" '{print$2}'`
channel=`echo $mdata | awk -F "_" '{print$3}'`

timeinfo=${EVENTINFOdir}/${network}/${network}_${station}_time.txt

for starttime in `cat $timeinfo` # begin event time loop
do

eventid="${starttime:0:4}${starttime:4:2}${starttime:6:2}${starttime:8:2}${starttime:10:2}" # yyyymmddHHMM
stime="${starttime:0:4}-${starttime:4:2}-${starttime:6:2},${starttime:8:2}:${starttime:10:2}:${starttime:12:2}.${starttime:15:3}" # yyyymmddTHH:MM:SS.sss
msec="${starttime:15:3}"

if [ "${OStype}"x == "MacOS"x ]; then
    validstime="${starttime:0:4}-${starttime:4:2}-${starttime:6:2}T${starttime:8:2}:${starttime:10:2}:${starttime:12:2}" # yyyymmddTHH:MM:SS
    etime=`date -v +${event_length}S -j -f %Y-%m-%dT%H:%M:%S "${validstime}" +%Y-%m-%d,%H:%M:%S`.${msec}
elif [ "${OStype}"x == "Linux"x ]; then
    validstime="${starttime:0:4}-${starttime:4:2}-${starttime:6:2} ${starttime:8:2}:${starttime:10:2}:${starttime:12:2}" # yyyymmdd HH:MM:SS
    etime=`date -d "+${event_length} second ${validstime}" +%Y-%m-%d,%H:%M:%S`.${msec}
else
    echo "Unsupported system type! Please input MacOS or Linux."
    exit 1
fi

mseedfile=${DATAdir}/${network}/${eventid}/${eventid}_${network}_${station}.mseed
sacpzdir=${IRdir}/sacpz_event/${network}/${eventid}
respdir=${IRdir}/resp_event/${network}/${eventid}

if [ ! -d ${DATAdir}/${network}/${eventid} ]; then
    mkdir -p ${DATAdir}/${network}/${eventid}
fi
if [ ! -d $sacpzdir ]; then
    mkdir -p $sacpzdir
fi
if [ ! -d $respdir ]; then
    mkdir -p $respdir
fi

# Download seismic data and corresponding instrument response
if [ -f ${mseedfile} ] && ! [ "`ls -A $sacpzdir`" = "" ] && ! [ "`ls -A $respdir`" = "" ]; then
    echo Exist: ${mseedfile} Skip!
else
    echo Downloading station: $station From: ${stime/,/T} To ${etime/,/T}
    FetchData -N $network -S $station -L $location -C $channel -s $stime -e $etime -o $mseedfile -sd $sacpzdir -rd $respdir
fi

done # end event time loop
done # end station loop
