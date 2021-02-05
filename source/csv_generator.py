#!/usr/bin/python3
# coding: utf-8

import pandas as pd
import numpy as np
import os
import argparse
import sys

#getting the ENV files for the SSLKEYLOG
SSLKEY   = os.getenv('SSLKEYLOGFILE')
SSLDEBUG = os.getenv('SSLDEBUGFILE')
WORKDIR_PREFIX="work_dir/"

# ## tshark -r capture-1-200 -Y "http2" -o tls.keylog_file:sslkey1.log -T fields -e frame.number -e _ws.col.Time -e ip.src -e ip.dst -e _ws.col.Protocol -e frame.len -e _ws.col.Info -E header=y -E separator="," -E quote=d -E occurrence=f > test1.csv

parser = argparse.ArgumentParser(description="csv_generator script")
parser.add_argument('-l', 
                    '--logfile', 
                    dest="logfile",
                    nargs=1,
                    help="Specify the log_file that has been used by doh_capture.py",
                    required=True)
parser.add_argument('-i',
                    '--input',
                    dest="input",
                    nargs=1,
                    help="Specify path to pcap file(s). \n" + 
                    "Use /path/to/csvfiles/capture.csv to process capture.csv\n" +
                    "Use /path/to/csvfiles/ to process all .csv files in "+
                    "in the directory.")

# parser.add_argument('-a', '--assembly-segments', action="store_true", dest="tso_on",
#                     help="Specify if reassembly IS desired in the csv files (Default: False)")
# parser.set_defaults(tso_on=False)
parser.add_argument('-k', '--keep-pcaps', action="store_true", dest="keep_pcaps",
                    help="Specify if pcap files SHOULD BE KEPT (Default: False)")
parser.set_defaults(keep_pcaps=False)



args = parser.parse_args()
log_file = args.logfile
PATH=args.input
# TSO_ON=args.tso_on
KEEP_PCAPS=args.keep_pcaps

# opening the same log file for further logging
logs = open(log_file, 'a')


#we only store the filenames without the exact path in the files list
if(os.path.isdir(PATH)):
  directory_prefix=PATH
  for _,_,files in os.walk(str("{}/".format(PATH))) :
    print(files)
else:
  f = os.path.basename(PATH)
  files = [f]
  directory_prefix = PATH.split(f)[0]

)
## here in the parameter of os.walk, specify the location of the folder containing the pcaps
# for _,_,files in os.walk(str(WORKDIR_PREFIX)+"/pcap/") :
#     print(files)


total = len(files)
count = 1
print("Converting .pcap files to .csv")
logs.write("Converting .pcap files to .csv\n")
logs.flush()
for f in files :
  file_name = directory_prefix + f
  try:
    output_file_name = directory_prefix+"csvfile-"+f.split('-')[1] + "-" + f.split('-')[2] +".csv"
  except:
    print("Unrecognized file naming pattern for filename {}\nSkipping".format(output_file_name))
    logs.write(str("Unrecognized file naming pattern for filename {}\nSkipping\n".format(output_file_name)))
    continue
  print(output_file_name)
  logs.write(str(output_file_name)+"\n")
  logs.flush()

  ## here in tls.keylog_file: speciy location and name of sslkeylogfile
  # extra_filter=' -o tcp.desegment_tcp_streams:false '
  # if(TSO_ON):
      # extra_filter=' '
  csv_command = 'tshark -r ' + file_name +' -Y "(http2)||(dns and tls)" -o tls.keylog_file:'+ SSLKEY +' -T fields -e frame.number -e _ws.col.Time -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e _ws.col.Protocol -e frame.len -e _ws.col.Info -E header=y -E separator="," -E quote=d -E occurrence=f > '+ output_file_name
  print("tshark cmd: "+ csv_command)
  logs.write("tshark cmd: "+ csv_command+"\n")
  logs.flush()

  remove_file = "rm -rf "+ directory_prefix + file_name
  try:
    os.system(csv_command)
    print(str(count) + " of " + str(total) + " completed!")
    logs.write(str(count) + " of " + str(total) + " completed!\n\n")
    logs.flush()
  except:
    print("Something went wrong with tshark...")

  if(not KEEP_PCAPS):
    try:
      sys.stdout.write(str("Removing pcap file {}...\r".format(file_name)))
      os.system(remove_file)
      sys.stdout.write(str("Removing pcap file {}...[DONE]\n".format(file_name)))
      sys.stdout.flush()
      logs.write(str("Removing pcap file {}...[DONE]\n".format(file_name)))
      logs.flush()

    except:
      sys.stdout.write(str("Removing pcap file {}...[FAILED]\n".format(file_name)))
      print("Could not delete pcap file...")
      logs.write(str("Removing pcap file {}...[FAILED]\n".format(file_name)))
      logs.flush()


  count+=1

print("csv_generator has finished!")
logs.write("csv_generator has finished!\n\n")
logs.flush()
logs.close()
