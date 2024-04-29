# DownloadSeisData
`DownloadSeisData` is a software package that automatically downloads seismic data. We strongly recommend using the Python version based on [ObsPy](https://github.com/obspy/obspy). It can automatically download station metadata, daily waveform data, and instrument responses. In addition, it can also download earthquake catalogs and waveform data of earthquake events based on station metadata. All waveform data is saved in `SAC` format. Since the corresponding response file is downloaded, We can convert the units of the waveform to displacement, velocity, acceleration (seismometer), or pressure (pressure gauge). At the same time, `DownloadSeisData` also saves station information and event information in the SAC header for subsequent use.



## Python version manual
The Python version is based on [ObsPy](https://github.com/obspy/obspy), very concise and easy to read. It is strongly recommended to use this version, and the Bash version will no longer be maintained.

### Requirements
- python 3.8+
- `obspy` installation instructions can be found in the [wiki](https://github.com/obspy/obspy/wiki#installation).
- [numpy](https://github.com/numpy/numpy)
- [pandas](https://github.com/pandas-dev/pandas) to read and write table file.
- [tqdm](https://github.com/tqdm/tqdm) to get progressbars.



## Shell version manual
Automatic download of seismic data by using `FetchMetaData`, `FetchEvent` and `FetchData`.

(Optional) Data preprocessing by using `mseed2sac` and `SAC`.

### Chinese introduction
[被动源OBS数据处理（1）：下载地震数据](https://mp.weixin.qq.com/s/GmxilrDyoDM29OMEzBoSRw)

[被动源OBS数据处理（2）：地震数据预处理](https://mp.weixin.qq.com/s/kVvvKB2QE_1ZgR6mXHAkPQ)

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
### Optional preparation
Install [mseed2sac](https://github.com/iris-edu/mseed2sac) and [SAC](https://ds.iris.edu/ds/nodes/dmc/forms/sac/) if using scripts `c1_mseed2sac_day` and `c2_mseed2sac_event`.

#### Install mseed2sac
```shell
tar -zxvf mseed2sac-2.3.tar.gz
cd mseed2sac-2.3/
make
sudo cp mseed2sac /usr/local/bin/
```

#### [Install SAC](https://seisman.github.io/SAC_Docs_zh/install/)

Install `SAC` if using scripts `d1_daydata_preprocess` and `d2_eventdata_preprocess`.


### Get metadata
Set network, station, location and channel in `a1_get_metadata` for seismic data download.

```shell
network=XO
stations=WD52,WD55
location=--,00
allchannel=HH?,BH?,HDH,BDH,EDH

```
Run `a1_get_metadata.bash`
```shell
bash a1_get_metadata.bash
```
Then a metadata text file will be generated, and users can change the fourth column (start) and fifth column (end) to download the data of the corresponding time interval.

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

Set the network and event_length in `b2_download_eventdata`. The `event_length` means length of time series after each origin time in seconds.
```shell
network=XO

event_length=7200
```
Run `b2_download_eventdata`, this script will automatically match the corresponding metadata file and event information file to download the event seismic data. And the instrument response file will also be downloaded.
```shell
bash b2_download_eventdata.bash
```

### Convert miniSEED data to SAC format
SAC format is one of the standard data formats of seismology. In order to convert miniSEED time series data to SAC format, the `mseed2sac` software needs to be installed.
In order to write the station location information and event information into the SAC file, the `SAC` software also needs to be installed.

Run `c1_mseed2sac_day.bash` and `c2_mseed2sac_event.bash`, the scripts will convert miniSEED day data and event data to SAC format, respectively. Besides, the scripts will automatically match the corresponding station metadata and event information to write station location and event information into the SAC header.

```shell
bash c1_mseed2sac_day.bash
bash c2_mseed2sac_event.bash
```

### Data preprocessing
Run `d1_daydata_preprocess.bash` and `d2_eventdata_preprocess.bash`, the scripts will automatically match the SAC file and the corresponding instrument response file to remove the instrument response and perform the following preprocessing.

Pre-procssing steps included here are:
- Response removal
- Downsampling
- rmean, rtrend and taper

```shell
bash d1_daydata_preprocess.bash
bash d2_eventdata_preprocess.bash
```
**Note:** The default unit of SAC is nm, but the unit of instrument response removed data by these two scripts is m.

I hope the `DownloadSeisData` package will help you. If you have any questions or suggestions, please contact me at <12131066@mail.sustech.edu.cn> (Yuechu Wu).
