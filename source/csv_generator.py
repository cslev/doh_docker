#!/usr/bin/python3
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import os

#getting the ENV files for the SSLKEYLOG
SSLKEY   = os.getenv('SSLKEYLOGFILE')
SSLDEBUG = os.getenv('SSLDEBUGFILE')

# ## tshark -r capture-1-200 -Y "http2" -o tls.keylog_file:sslkey1.log -T fields -e frame.number -e _ws.col.Time -e ip.src -e ip.dst -e _ws.col.Protocol -e frame.len -e _ws.col.Info -E header=y -E separator="," -E quote=d -E occurrence=f > test1.csv




## here in the parameter of os.walk, specify the location of the folder containing the pcaps
for _,_,files in os.walk("./pcap/") :
    print(files)


total = len(files)
count = 1 
print("Converting .pcap files to .csv")
for f in files :
    file_name = "./pcap/" + f ;
    output_file_name = "csvfile-"+f.split('-')[1] + "-" + f.split('-')[2] +".csv"
    print(output_file_name)
    
    ## here in tls.keylog_file: speciy location and name of sslkeylogfile
    csv_command = 'tshark -r ' + file_name +' -Y "http2" -o tls.keylog_file:'+SSLKEY+' -T fields -e frame.number -e _ws.col.Time -e ip.src -e ip.dst -e _ws.col.Protocol -e frame.len -e _ws.col.Info -E header=y -E separator="," -E quote=d -E occurrence=f > '+ output_file_name
    remove_file = "rm "+file_name
    os.system(csv_command)
    print(str(count) + " of " + str(total) + " completed!")
    os.system(remove_file)
    count+=1
print("finished!")





