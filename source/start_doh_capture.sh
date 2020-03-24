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



#function show_help
#{
#  echo -e "${green}Example:./start_doh_capture.sh -s <START> -e <END> -b <BATCH_SIZE> -r <RESOLER> ${none}"
#  echo -e "\t\t-s <START>: [INT] First website from Alexa's top 1M - Default: 1"
#  echo -e "\t\t-e <END>:   [INT] Last website from Alexa's top 1M - Default: 5000"
#  echo -e "\t\t-b <BATCH_SIZE>: [INT] Websites/batch - Default:200"
#  echo -e "\t\t-r <RESOLVER>: [INT] DoH resolver to use - Options: 1 (Cloudflare), 2 (Google), 3 (CleanBrowsing), 4 (Quad4) - Default: 1"
#  exit
#}

#while getopts "h?s:e:b:r:" opt
#do
#  case "$opt" in
#  h|\?)
#    show_help
#    ;;
#  s)
#    START=$OPTARG
#    ;;
#  e)
#    END=$OPTARG
#    ;;
#  b)
#    BATCH=$OPTARG
#    ;;
#  r)
#    RESOLVER=$OPTARG
#    ;;
#  *)
#    show_help
#   ;;
#  esac
#done

RESOLVER=$1
START=$2
END=$3
BATCH=$4

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


echo -e "+------------------------------------------------+"
echo -e "|     ${bold} Passed Arguments to the Container ${none}        |"
echo -e "+------------------------------------------------+"
echo -e "RESOLVER = ${green}$R${none}"
echo -e "START = ${green}$S${none}"
echo -e "END = ${green}$E${none}"
echo -e "BATCH = ${green}$B${none}"
echo -e "+================================================+"

python3 doh_capture.py $R $S $E $B


echo -e "${yellow}Compressing csv files${none}"
tar -czvf doh_data.tar.gz csvfile*
echo -e "${green}[DONE]${none}"

echo -e "${yellow}Removing csv files${none}"
rm -rf csvfile*
echo -ne "$\t{green}[DONE]${none}"

