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
fi

if [ ! -z "$END" ]
then
  E="-e ${END}"
else
  E=""
fi

if [ ! -z "$BATCH" ]
then
  B="-b ${BATCH}"
else
  B=""
fi

if [ ! -z "$INTF" ]
then
  I="-i ${INTF}"
else
  I=""
fi

declare -A resolvers
resolvers=(
		[1]="cloudflare"
		[2]="google"
		[3]="cleanbrowsing"
		[4]="quad9"
		   )

echo -e "+------------------------------------------------+"
echo -e "|     ${bold} Passed Arguments to the Container ${none}        |"
echo -e "+------------------------------------------------+"
echo -e "RESOLVER = ${green}$R${none}"
echo -e "START = ${green}$S${none}"
echo -e "END = ${green}$E${none}"
echo -e "BATCH = ${green}$B${none}"
echo -e "META = ${green}$META${none}"
echo -e "INTF = ${green}$INTF${none}"
echo -e "+================================================+"


#get date
d=$(date +"%Y%m%d_%H%M%S")

echo 0 > done
python3 doh_capture.py $R $S $E $B $I > raw_${d}.log

echo -ne "${yellow}Compressing data...${none}" >> $log_file
cd /doh_project/
# copy the symlink target to have it in the compressed data as well
cp -Lr $log_file doh_log.log
# $RESOLVER is an INT so will be good for accessing the resolver name from the array
archive_name="doh_data_${resolvers[${RESOLVER}]}_${META}_${START}-${END}_${d}.tar.gz"
tar -czf $archive_name csvfile* doh_log.log
echo -e "\t${green}[DONE]${none}" >> $log_file

echo -ne "${yellow}Removing csv files${none}" >> $log_file
rm -rf csvfile*
rm -rf doh_log.log
echo -e "\t${green}[DONE]${none}\n\n" >> $log_file
echo 1 > done
