#!/usr/bin/python3
# coding: utf-8


<<<<<<< HEAD
import os 
=======
import os
>>>>>>> 5d7ed0a5b764af4aa437261355c5997ee46677f4
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException , WebDriverException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary # for specifying the path to firefox binary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep,ctime
import multiprocessing
import time
import argparse

# parser for the command line arguements
parser = argparse.ArgumentParser(description="DoH packet capture and .csv conversion script!")

parser.add_argument('-s', action="store", default=1, type=int, dest="start" , help="Specify rank of the starting website")
<<<<<<< HEAD
parser.add_argument('-e', action="store", default=200, type=int, dest="end" , help="Specify rank of the ending website")
=======
parser.add_argument('-e', action="store", default=5000, type=int, dest="end" , help="Specify rank of the ending website")
>>>>>>> 5d7ed0a5b764af4aa437261355c5997ee46677f4
parser.add_argument('-b', action="store", default=200, type=int, dest="batch" , help="Batch Size (range must be a multiple of batch size!)")
parser.add_argument('-r', action="store", default=1, type=int, dest="doh_resolver" , help="DoH resolver :\n1=Cloudflare; \n2=Google;\n3=CleanBrowsing;\n4=Quad9;")

results = parser.parse_args()

print("Printing script Parameters: ")
print("Start = "+str(results.start))
print("End = "+str(results.end))
print("Batch_Size = "+str(results.batch))

if(results.doh_resolver==1) :
    uri="https://cloudflare-dns.com/dns-query"
elif(results.doh_resolver==2) :
    uri="https://dns.google/dns-query"
elif(results.doh_resolver==3) :
    uri="https://doh.cleanbrowsing.org/doh/family-filter/"
elif(results.doh_resolver==4) :
    uri="https://dns.quad9.net/dns-query"
else :
    print("Invalid choice for DoH resolver!\nExiting...")
    exit(0)

print("DoH_Resolver = "+uri)


<<<<<<< HEAD
start = results.start 
=======
start = results.start
>>>>>>> 5d7ed0a5b764af4aa437261355c5997ee46677f4
stop = results.end
batch_size = results.batch
time_out = batch_size * 15

data = pd.read_csv('top-1m.csv' , names = ['rank','website'])

print(time.ctime())

options = Options()
options.headless = True


## specifying the binary path
binary = FirefoxBinary('./firefox/firefox')

## DesiredCapabilities
<<<<<<< HEAD
##cap = DesiredCapabilities().FIREFOX
##cap['marionette'] = False
=======
#cap = DesiredCapabilities().FIREFOX
#cap['marionette'] = False
>>>>>>> 5d7ed0a5b764af4aa437261355c5997ee46677f4

#profile = webdriver.FirefoxProfile('/home/user/.mozilla/firefox/0b5055qu.Doh_profile')
## setting the firefox profile to use DoH
profile = webdriver.FirefoxProfile()
profile.set_preference("network.trr.mode", 2)
profile.set_preference("network.trr.uri", uri)
#profile.set_preference("network.trr.bootstrapAddress", '1.1.1.1.')

def open_website(url):
    #driver = webdriver.Firefox(firefox_profile=profile)

    ## in the executabel path you need to specify the location of geckodriver location.
    driver = webdriver.Firefox(options=options, firefox_profile=profile)
<<<<<<< HEAD
    driver.set_page_load_timeout(25) 
=======
    driver.set_page_load_timeout(25)
>>>>>>> 5d7ed0a5b764af4aa437261355c5997ee46677f4
    try :
        driver.get(url)
        sleep(2)
        driver.close()
    except TimeoutException as ex1 :
        print("Exception has been thrown "+ str(ex1))
        driver.close()
        sleep(2)
    except WebDriverException as ex2 :
        print("Exception has been thrown "+ str(ex2))
        driver.close()
        sleep(2)

def main_driver(s,e) :
    count = s
    df = data.iloc[s-1:e]
    for domain in df['website'] :
        url = 'https://www.' + domain
        print(str(count) + " " + url )
        open_website(url)
        count = count + 1
    print("batch completed")



s = start
e = s+batch_size-1



def capture_packets(shell_command) :
    os.system(shell_command)

while(e<=stop) :
    filename = 'pcap/capture-'+str(s)+'-'+str(e)

    ## here after -i you need to add the ethernet port. which i guess is eth0
    shell_command = "timeout 4400 tcpdump port 443 -i eth0 -w " + filename

    t1 = multiprocessing.Process(target=main_driver, args=(s,e,))
    t2 = multiprocessing.Process(target=capture_packets, args=(shell_command,))

    t2.start()
    sleep(3)
    t1.start()

    t1.join()
    sleep(5)
    t2.terminate()

    print("Done")
    sleep(2)
    print(time.ctime())
    s = s+batch_size
    e = e+batch_size
<<<<<<< HEAD
    
=======

>>>>>>> 5d7ed0a5b764af4aa437261355c5997ee46677f4
    csv_command = "python3 csv_generator.py"
    os.system(csv_command)
    sleep(1)
    # this part is for moving the files to another location which is not needed in case of the docker container.
    """move_command = "mv "+filename+" /mnt/debianDoH_images/DoH_Pcaps/debianDoH2/"+filename
    os.system(move_command)
    print("File moved to /mnt") """
