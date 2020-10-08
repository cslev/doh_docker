#!/usr/bin/python3
# coding: utf-8


import os
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException , WebDriverException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary # for specifying the path to firefox binary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep,ctime
import multiprocessing
import time
import datetime
import argparse
from argparse import RawTextHelpFormatter
import json


def getDateFormat(timestamp):
    '''
    This simple function converts traditional UNIX timestamp to YMD_HMS format
    timestamp int - unix timestamp to be converted
    return String - the YMD_HMS format as a string
    '''
    return datetime.datetime.\
        fromtimestamp(float(timestamp)).strftime('%Y%m%d_%H%M%S')


#get current timestamp and convert it
ts = time.time()
timestamp = getDateFormat(str(ts))


# parser for the command line arguements
parser = argparse.ArgumentParser(description="DoH packet capture and .csv conversion script!",formatter_class=RawTextHelpFormatter)

parser.add_argument('-s', action="store", default=1, type=int, dest="start" , help="Specify rank of the starting website")
parser.add_argument('-e', action="store", default=5000, type=int, dest="end" , help="Specify rank of the ending website")
parser.add_argument('-b', action="store", default=200, type=int, dest="batch" , help="Batch Size (range must be a multiple of batch size!)")
parser.add_argument('-r', action="store", default=1, type=int, dest="doh_resolver" ,
                    help="DoH resolver:\n" +\
                    "\t 1 = Cloudflare\n" +\
                    "\t 2 = Google\n" +\
                    "\t 3 = CleanBrowsing\n" +\
                    "\t 4 = Quad9\n" +\
                    "\t 5 = PowerDNS\n" +\
                    "\t 6 = doh.li\n" +\
                    "\t 7 = AdGuard\n" +\
                    "\t 8 = OpenDNS\n" +\
                    "\t 9 = Comcast\n" +\
                    "\t10 = cz.nic\n" +\
                    "\t11 = dnslify\n" +\
                    "\t12 = blahdns\n" +\
                    "\t13 = ffmuc.net\n" +\
                    "\t14 = ContainerPI\n" +\
                    "\t15 =Tiarap\n" +\
                    "\t16 = DNS.SB\n" +\
                    "\t17 = Association 42l\n" +\
                    "\t18 = Andrews and Arnold\n" +\
                    "\t19 = TWNIC\n" +\
                    "\t20 = Digital Gesellschaft\n" +\
                    "\t21 = LibreDNS\n" +\
                    "\t22 = PI-DNS\n" +\
                    "\t23 = dns.flatuslifir.is\n" +\
                    "\t24 = he.net")
parser.add_argument('-i', '--interface', nargs=1,
                    help="Specify the interface to use for capturing",
                    required=False,
                    default=['eth0'])
parser.add_argument('-t', '--timeout', action="store", default=16, type=int, dest="timeout",
                    help="Specify the timeout for a webpage to load (Default: 16)")
# parser.add_argument('-a', '--assembly-segments', action="store_true", dest="tso_on",
#                     help="Specify if reassembly IS desired in the csv files (Default: False)")
# parser.set_defaults(tso_on=False)
parser.add_argument('-k', '--keep-pcaps', action="store_true", dest="keep_pcaps",
                    help="Specify if pcap files SHOULD BE KEPT (Default: False)")
parser.set_defaults(keep_pcaps=False)


results = parser.parse_args()


# setup logging features
log_file = "log_"+str(timestamp)
print("Creating log file "+log_file)
logs = open(log_file, 'a')
logs.write("Logging for doh_capture.py started on "+timestamp+"\n\n")

# remove previous symlink if there was any
if os.system("rm -rf progress.log") == 0:
    print("symlink to previous log file has been deleted")
    logs.write("symlink to previous log file has been deleted\n")
else:
    print("symlink to previous log file could NOT be deleted")
    logs.write("symlink to previous log file could NOT be deleted\n")

# create symlink to the new log file
if os.system("ln -s "+str(log_file)+" progress.log") == 0:
    print("creating symlink progress.log to "+str(log_file)+" is successfull")
    logs.write("creating symlink progress.log to "+str(log_file)+" is successfull\n")
else:
    print("creating symlink progress.log to "+str(log_file)+" was NOT successfull")
    logs.write("creating symlink progress.log to "+str(log_file)+" was NOT successfull\n")


def get_resolver_details(resolver) :
    with open('r_config.json') as f:
        resolver_config = json.load(f)
        # print(resolver_config)
    try:
        return resolver_config[resolver]["name"], resolver_config[resolver]["uri"], resolver_config[resolver]["bootstrap"]
    except:
        print("Uknown resolver ID {}".format(resolver))
        print("Exiting...")
        exit(-1)



start = results.start
stop = results.end
batch_size = results.batch
time_out = batch_size * 15
interface = results.interface[0]
webpage_timeout = int(results.timeout)
resolver=str(results.doh_resolver)

#counters for future references to log how many domains failed and did not resolver properly
error=0
timeout=0

#arguments to be passed to csv_generator.py
# if(results.tso_on):
#     TSO_OFF = ' -a '
# else:
#     TSO_OFF = ' '
if(results.keep_pcaps):
    KEEP_PCAPS=' -k '
else:
    KEEP_PCAPS=' '
#-------------------------------------------

resolver_name, uri , bootstrap = get_resolver_details(resolver)


# Fine-tune batch size if it is bigger than stop-start
max_possible_batch_size = stop-start+1
if (batch_size > max_possible_batch_size):
    batch_size = max_possible_batch_size


print("Printing script Parameters: ")
logs.write("Printing script Parameters: \n")
print("Start = "+str(start))
logs.write("Start = "+str(start)+"\n")
print("End = "+str(stop))
logs.write("End = "+str(stop)+"\n")
print("(Adjusted) Batch_Size = "+str(batch_size))
logs.write("(Adjusted) Batch_Size = "+str(batch_size)+"\n")
print("DoH:")
print("\tResolver:"+str(resolver_name))
print("\tURI:"+str(uri))
logs.write("DoH:\n")
logs.write("\tResolver:"+str(resolver_name)+"\n")
logs.write("\tURI:"+str(uri)+"\n")


data = pd.read_csv('top-1m.csv' , names = ['rank','website'])

print("Process started: " + str(time.ctime()))
logs.write("Process started: " + str(time.ctime())+"\n\n\n")

options = Options()
options.headless = True


## specifying the binary path
binary = FirefoxBinary('./firefox/firefox')



## DesiredCapabilities
#cap = DesiredCapabilities().FIREFOX
#cap['marionette'] = False

#profile = webdriver.FirefoxProfile('/home/user/.mozilla/firefox/0b5055qu.Doh_profile')
## setting the firefox profile to use DoH
profile = webdriver.FirefoxProfile()
profile.set_preference("network.trr.mode", 3)
profile.set_preference("network.trr.uri", uri)
profile.set_preference("network.trr.bootstrapAddress", bootstrap)

logs.flush()



def open_website(url,count):
    #driver = webdriver.Firefox(firefox_profile=profile)
    # logs = open('Progress.txt', 'a')
    tmp_ts = time.time()
    tmp_timestamp = getDateFormat(str(tmp_ts))
    global error
    global timeout

    print(str(count)+" "+url+" (visited: "+str(tmp_timestamp)+")")
    logs.write(str(count)+" "+url+" (visited: "+str(tmp_timestamp)+")\n")

    ## in the executabel path you need to specify the location of geckodriver location.
    try:
        driver = webdriver.Firefox(options=options, firefox_profile=profile)
        driver.set_page_load_timeout(webpage_timeout)
    except WebDriverException as ex:
        print("Error during loading the driver (website skipped): " + str(ex))
        logs.write("Error during loading the driver (website skipped): " + str(ex) + "\n")
    try :
        driver.get(url)
        sleep(2)
    except TimeoutException as ex1 :
        print("TimeoutException Exception has been thrown "+ str(ex1))
        sleep(2)
        logs.write("TimeoutException Exception has been thrown \n"+str(ex1)+"\n")
        timeout = timeout + 1 #increase timeout counter
        print("Timeouts so far: " + str(timeout))
        logs.write("Timeouts so far: "+str(timeout)+"\n")
    except WebDriverException as ex2 :
        print("WebDriverException Exception has been thrown "+ str(ex2))
        sleep(2)
        logs.write("WebDriverException Exception has been thrown \n"+str(ex2)+"\n")
        error = error + 1 #increase error counter 
        print("Errors so far: " + str(error))
        logs.write("Errors so far: "+str(error)+"\n")
    except Exception as ex3:
        print("Unknown exception has been thrown "+ str(ex3))
        sleep(2)
        logs.write("Unknown exception has been thrown \n"+str(ex3)+"\n")
    logs.flush()
    try:
        driver.close()
        sleep(1)
    except WebDriverException as ex:
        print("Error during closing the driver (continue): " + str(ex))
        logs.write("Error during closing the driver (continue): " + str(ex) + "\n")


def main_driver(s,e) :
    count = s
    df = data.iloc[s-1:e]
    for domain in df['website'] :
        url = 'https://www.' + domain
        open_website(url,count)
        count = count + 1

    print("batch completed")
    logs.write("batch completed"+"\n")
    logs.flush()


s = start
e = s+batch_size-1



def capture_packets(shell_command):
    os.system(shell_command)



while(s<=stop) :
    if(e>stop) :
        e=stop

    filename = 'pcap/capture-'+str(s)+'-'+str(e)

    ## here after -i you need to add the ethernet port. which i guess is eth0
    shell_command = "/usr/bin/tcpdump port 443 -i " + interface + " -w " + filename

    t1 = multiprocessing.Process(target=main_driver, args=(s,e,))
    t2 = multiprocessing.Process(target=capture_packets, args=(shell_command,))

    t2.start()
    sleep(3)
    t1.start()

    t1.join()
    sleep(5)
    t2.terminate()
    print("Killing tcpdump via pkill...")
    logs.write("Killing tcpdump via pkill...\n")
    os.system("pkill tcpdump")

    print("Done")
    logs.write("Done"+"\n")
    logs.flush()
    sleep(2)
    print(time.ctime())
    logs.write(time.ctime())
    logs.flush()
    s = s+batch_size
    e = e+batch_size

    print("Running pcap file analyser to create csv files...")
    logs.write("Running pcap file analyser to create csv files...\n")

    # csv_command = "python3 csv_generator.py -l "+log_file + TSO_OFF + KEEP_PCAPS
    csv_command = "python3 csv_generator.py -l "+log_file + KEEP_PCAPS
    os.system(csv_command)
    sleep(1)

print("Re-printing script Parameters: ")
logs.write("Re-printing script Parameters: \n")
print("Start = "+str(start))
logs.write("Start = "+str(start)+"\n")
print("End = "+str(stop))
logs.write("End = "+str(stop)+"\n")
print("(Adjusted) Batch_Size = "+str(batch_size))
logs.write("(Adjusted) Batch_Size = "+str(batch_size)+"\n")
print("DoH:")
print("\tResolver:"+str(resolver_name))
print("\tURI:"+str(uri))
logs.write("DoH:\n")
logs.write("\tResolver:"+str(resolver_name)+"\n")
logs.write("\tURI:"+str(uri)+"\n")

print("\nNumber of webpages failed to load/resolve the domain for: "+str(error))
logs.write("\nNumber of webpages failed to load: "+str(error)+"\n")
print("\nNumber of webpages timed out: "+str(timeout))
logs.write("\nNumber of webpages timed out: "+str(timeout)+"\n")


logs.close()
