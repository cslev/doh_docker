#!/bin/bash
#COLORIZING
none='\033[0m'
bold='\033[01m'
disable='\033[02m'
underline='\033[04m'
reverse='\033[07m'
strikethrough='\033[09m'
invisible='\033[08m'

black='\033[30m'
red='\033[31m'
green='\033[32m'
orange='\033[33m'
blue='\033[34m'
purple='\033[35m'
cyan='\033[36m'
lightgrey='\033[37m'
darkgrey='\033[90m'
lightred='\033[91m'
lightgreen='\033[92m'
yellow='\033[93m'
lightblue='\033[94m'
pink='\033[95m'
lightcyan='\033[96m'

#cp others/bashrc_template /root/.bashrc
source /root/.bashrc
echo -e "+-------------------------------------------------------------+"
echo -e "|${bold}   Found ENV variables${none}    "
echo -e "|${bold}${yellow}PATH:${green} ${PATH}${none}"
echo -e "|${bold}${yellow}SSLKEYLOGFILE:${green} ${SSLKEYLOGFILE}${none}"
echo -e "|${bold}${yellow}SSLDEBUGFILE:${green} ${SSLDEBUGFILE}${none}"
echo -e "+-------------------------------------------------------------+"


log_file="progress.log"

# ------------ INPUT ARGS ------------
RESOLVER=$1
START=$2
END=$3
BATCH=$4
META=$5  # used for extra information in the archive_name
INTF=$6     # interface to use (default: eth0)
WEBPAGE_TIMEOUT=$7 #set here the timeout for a website to load in seconds
ARCHIVE_PATH=$8 #set here the 'mounted' path in container where the archive will be saved
# ------------------------------------

if [ ! -z "$RESOLVER" ]
then
  R="-r ${RESOLVER}"
else
  R=""
fi

if [ ! -z "$START" ]
then
  S="-s ${START}"
else
  S=""
  START=1
fi

if [ ! -z "$END" ]
then
  E="-e ${END}"
else
  E=""
  END=5000
fi

if [ ! -z "$BATCH" ]
then
  B="-b ${BATCH}"
else
  B=""
  BATCH=200
fi

if [ ! -z "$INTF" ]
then
  I="-i ${INTF}"
else
  I=""
  INTF="eth0"
fi

if [ ! -z "$WEBPAGE_TIMEOUT" ]
then
  T="-t ${WEBPAGE_TIMEOUT}"
else
  T=""
  WEBPAGE_TIMEOUT=16
fi

if [ ! -z "$ARCHIVE_PATH" ]
then
  ARCHIVE_PATH="/doh_project/archives"
fi



resolver=$(cat r_config.json |jq  '{name: ."${RESOLVER}".name}'|grep name|cut -d ':' -f 2|sed "s/\"//g"|sed "s/ //g")

echo -e "+------------------------------------------------+" >> $log_file
echo -e "|     ${bold} Passed Arguments to the Container ${none}        |" >> $log_file
echo -e "+------------------------------------------------+" >> $log_file
echo -e "RESOLVER = ${green}${resolver}${none}" >> $log_file
echo -e "START = ${green}$S${none}" >> $log_file
echo -e "END = ${green}$E${none}" >> $log_file
echo -e "BATCH = ${green}$B${none}" >> $log_file
echo -e "META = ${green}$META${none}" >> $log_file
echo -e "INTF = ${green}$INTF${none}" >> $log_file
echo -e "WEBPAGE_TIMEOUT = ${green}$WEBPAGE_TIMEOUT${none}" >> $log_file
echo -e "ARCHIVE PATH = ${green}$ARCHIVE_PATH${none}" >> $log_file
echo -e "+================================================+" >> $log_file

echo -ne "${yellow}Disabling offloading features...${none}" >> $log_file
ethtool -K $INTF rx off tx off gso off gro off tso off 2>> $log_file
retval=$(echo $?)
if [ $retval -eq 0 ]
then
  echo -e "\t${green}[DONE]${none}" >> $log_file
else
  echo -e "\t${yellow}[FAILED]${none}" >> $log_file
  echo -e "\t${yellow}Container not in privileged mode? (SKIPPING)${none}" >> $log_file

fi

#get date
d=$(date +"%Y%m%d_%H%M%S")

echo 0 > done
python3 doh_capture.py $R $S $E $B $I $T

echo -ne "${yellow}Compressing data...${none}" >> $log_file
cd /doh_project/
# copy the symlink target to have it in the compressed data as well
cp -Lr $log_file doh_log.log
# $RESOLVER is an INT so will be good for accessing the resolver name from the array
archive_name="doh_data_${resolver}_${META}_${START}-${END}_${d}.tar.gz"
tar -czf $archive_name csvfile* doh_log.log
echo -e "\t${green}[DONE]${none}" >> $log_file

echo -ne "${yellow}Removing csv files${none}" >> $log_file
rm -rf csvfile*
rm -rf doh_log.log
echo -ne "${yellow}Copying ${archive_name} to $ARCHIVE_PATH/ ${none}" >> $log_file
cp /doh_project/$archive_name $ARCHIVE_PATH/ >> $log_file
echo -e "\t${green}[DONE]${none}\n\n" >> $log_file
echo 1 > done
