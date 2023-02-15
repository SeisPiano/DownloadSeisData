# DownloadSeisData
`DownloadSeisData` is a program package that automatically downloads seismic data. Now, shell versions are available. There may be more versions in the future.

## Shell version manual
Automatic batch download of seismic data by using `FetchMetaData`, `FetchEvent` and `FetchData`.

### Preparation
Download the IRIS DMC's Fetch scripts from [http://service.iris.edu/clients](http://service.iris.edu/clients/). Rename and give executable permissions.

```shell
mv FetchMetadata-2014.316 FetchMetadata
mv FetchEvent-2014.340 FetchEvent
mv FetchData-2020.314 FetchData
chmod +x FetchMetadata FetchEvent FetchData
```

Add the following statement to `~/.zshrc` of Mac OS user (or `~/.bashrc` of Linux user) to configure environment variables.
```shell
export PATH=your/path/of/Fetch/scripts:$PATH
```

### Get metadata
Set network, station, location and channel in `a1_get_metadata` for follow-up seismic data download.

```shell
network=XO
stations=WD52,WD55
location=--,00
allchannel=HH?,BH?,HDH,EDH

```
Run `a1_get_metadata.bash`
```shell
bash a1_get_metadata.bash
```
Then a metadata text file will be generated, and users can change the fourth column (start) and fifth column (end) to the required time.

```
XO WD52 HDH,HH1,HH2,HHZ 2018-07-18 2019-09-03 54.046622 -159.346215 -2563.6
XO WD55 HDH,HH1,HH2,HHZ 2018-07-20 2019-09-01 55.761625 -153.662817 -1283.5
```

### Download day data
Set the network in `b1_download_daydata`, and this script will automatically match the corresponding metadata file to download the daily seismic data. The instrument response file will also be downloaded.

```shell
bash b1_download_daydata.bash
```

### Download event data
Set network and event filter conditions in `a2_get_event_info` to get event information.

```shell
network=XO

maxradius=180
minradius=30
minmag=5.5
maxmag=10
```
Run `a2_get_event_info.bash`
```shell
bash a2_get_event_info.bash
```
Then this script `a2_get_event_info` will automatically match the corresponding metadata file to download the event information for each station.

Set the network and event_length in `b2_download_eventdata`. The `event_length` means length of time series after each start time in seconds.
```shell
network=XO

event_length=7200
```
Run `b2_download_eventdata`, this script will automatically match the corresponding metadata file and event information file to download the event seismic data. And the instrument response file will also be downloaded.
```shell
bash b2_download_eventdata.bash
```
