#!/bin/bash
# Download seismic daily miniseed data from iris
#
# Yuechu Wu
# 12131066@mail.sustech.edu.cn
# 2022-01-09
#
# Downloading data from multiple stations
# Updated 2022-05-10, Yuechu Wu 


workPath=${PWD}

# station information, refer to https://ds.iris.edu/mda
network=XO
stations=(WD52 WD55)
startdate=2018-11-01
enddate=2019-01-31
channel=HH? # Sometimes need to use HH?, refer to the specific station on IRIS-MDA
pressure=HDH
location=--
OBS=true   # for OBS, OBS=true; for land stations, OBS=others


### end user input parameters ###

DATAdir="$workPath/DATA/mseed/datacache_day" # data directory
IRdir="$workPath/DATA/PZs"     	             # instrument response directory

# make day data and PZs folder
for station in ${stations[@]}
do
if [ -d "$DATAdir/$network/$station" ];then
    echo "Station directory exists!"
else
    mkdir -p "$DATAdir/$network/$station"
fi
if [ -d "$IRdir/$network/$station" ];then
    echo "Instrument response directory exists!"
else
    mkdir -p "$IRdir/$network/$station"
fi
done   

for station in ${stations[@]} # begin station loop
do
stdate=`date -d "$startdate" +%Y%m%d`
eddate=`date -d "$enddate" +%Y%m%d`
while [ "$stdate" -le "$eddate" ] # begin date loop
do

mkdir $IRdir/$network/$station/$stdate # make PZs daily file

# Download seismic data and PZs
echo Downloading seismic data
echo Downloading station: $station From: `date -d $stdate +%Y-%m-%d`T00:00:00 To `date -d "1 day $stdate" +%Y-%m-%d`T00:00:00
./FetchData -N $network -S $station -L $location -C $channel -s `date -d $stdate +%Y-%m-%d`T00:00:00 -e `date -d "1 day $stdate" +%Y-%m-%d`T00:00:00 -o $DATAdir/$network/$station/${stdate}0000_${network}_${station}.mseed -sd $IRdir/$network/$station/$stdate

# For OBS, download pressure data and corresponding PZs
if [ "$OBS"x = "true"x ];then
echo Downloading pressure data
echo Downloading station: $station From: `date -d $stdate +%Y-%m-%d`T00:00:00 To `date -d "1 day $stdate" +%Y-%m-%d`T00:00:00
./FetchData -N $network -S $station -L $location -C $pressure -s `date -d $stdate +%Y-%m-%d`T00:00:00 -e `date -d "1 day $stdate" +%Y-%m-%d`T00:00:00 -o $DATAdir/$network/$station/${stdate}0000_${network}_${station}_p.mseed -sd $IRdir/$network/$station/$stdate
fi
let stdate=`date -d "1 day ${stdate}" +%Y%m%d`

done # end date loop

done # end station loop


