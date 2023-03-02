#!/bin/bash
# download seismic day data by using FetchData
# Yuechu Wu
# 12131066@mail.sustech.edu.cn
# 2022-01-09
#
# read metadata and batch download
# 2023-02-12, Yuechu Wu

OStype="MacOS"  # "MacOS" for Mac OS user, "Linux" for Linux user

network=XO

DATAdir="DATA/mseed_day"  # seismic data directory
IRdir="DATA/response"     # instrument response directory

metadata=DATA/METADATA/${network}_metadata.txt

location=-- # for OBS, location=--; for land stations, location=00


##### END OF USER INPUT #####
for mdata in `cat $metadata | awk '{print $1"_"$2"_"$3"_"$4"_"$5}'` # begin station loop
do

station=`echo $mdata | awk -F "_" '{print$2}'`
channel=`echo $mdata | awk -F "_" '{print$3}'`
startdate=`echo $mdata | awk -F "_" '{print$4}'` # startdate:yyyy-mm-dd
enddate=`echo $mdata | awk -F "_" '{print$5}'`   # enddate:yyyy-mm-dd

if [ ! -d ${DATAdir}/${network}/${station} ]; then  # make station directory
    mkdir -p ${DATAdir}/${network}/${station}
fi    

stdate=$startdate # stdate:yyyy-mm-dd

if [ "${OStype}"x == "MacOS"x ]; then
    sdate=`date -j -f %Y-%m-%d "${stdate}" +%Y%m%d`  # sdate:yyyymmdd
    edate=`date -j -f %Y-%m-%d "${enddate}" +%Y%m%d` # edate:yyyymmdd
elif [ "${OStype}"x == "Linux"x ]; then
    sdate=`date -d "${stdate}" +%Y%m%d`    # sdate:yyyymmdd
    edate=`date -d "${enddate}" +%Y%m%d`   # edate:yyyymmdd
else
    echo "Unsupported system type! Please input MacOS or Linux."
    exit 1
fi

while [ "$sdate" -le "$edate" ] # begin date loop
do

mseedfile=${DATAdir}/${network}/${station}/${sdate}0000_${network}_${station}.mseed
sacpzdir=${IRdir}/sacpz_day/${network}/${station}/${sdate}
respdir=${IRdir}/resp_day/${network}/${station}/${sdate}

if [ ! -d $sacpzdir ]; then
    mkdir -p $sacpzdir
fi
if [ ! -d $respdir ]; then
    mkdir -p $respdir
fi

if [ "${OStype}"x == "MacOS"x ]; then
    nextdate=`date -v +1d -j -f %Y-%m-%d "${stdate}" +%Y-%m-%d` # nextdate:yyyy-mm-dd
elif [ "${OStype}"x == "Linux"x ]; then
    nextdate=`date -d "+1 day ${stdate}" +%Y-%m-%d`  # nextdate:yyyy-mm-dd
else
    echo "Unsupported system type! Please input MacOS or Linux."
    exit 1
fi

# Download seismic data and corresponding instrument response
if [ -f ${mseedfile} ] && ! [ "`ls -A $sacpzdir`" = "" ] && ! [ "`ls -A $respdir`" = "" ]; then
    echo Exist: ${mseedfile} Skip!
else
    echo Downloading station: $station From: ${stdate}T00:00:00 To ${nextdate}T00:00:00
    FetchData -N $network -S $station -L $location -C $channel -s ${stdate},00:00:00 -e ${nextdate},00:00:00 -o $mseedfile -sd $sacpzdir -rd $respdir
fi

if [ "${OStype}"x == "MacOS"x ]; then
    stdate=`date -v +1d -j -f %Y-%m-%d "${stdate}" +%Y-%m-%d`
    sdate=`date -j -f %Y-%m-%d "${stdate}" +%Y%m%d`
elif [ "${OStype}"x == "Linux"x ]; then
    stdate=`date -d "+1 day ${stdate}" +%Y-%m-%d`
    sdate=`date -d "${stdate}" +%Y%m%d`
else
    echo "Unsupported system type! Please input MacOS or Linux."
    exit 1
fi

done # end date loop
done # end station loop
