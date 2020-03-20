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

python3 doh_capture.py

