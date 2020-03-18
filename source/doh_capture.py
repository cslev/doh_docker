import os 
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException , WebDriverException
from selenium.webdriver.firefox.options import Options
from time import sleep,ctime
import multiprocessing
import time

start = 990001 
stop = 995000
batch_size = 200
time_out = batch_size * 15

data = pd.read_csv('top-1m.csv' , names = ['rank','website']) 

print(time.ctime())

options = Options()
options.headless = True
profile = webdriver.FirefoxProfile('/home/user/.mozilla/firefox/0b5055qu.Doh_profile')

"""profile.set_preference("network.trr.mode", 2)
profile.set_preference("network.trr.uri", "https://mozilla.cloudflare-dns.com/dns-query")
profile.set_preference("network.trr.bootstrapAddress", '1.1.1.1.')"""

def open_website(url):
    #driver = webdriver.Firefox(firefox_profile=profile)
    driver = webdriver.Firefox(options=options, firefox_profile=profile)
    driver.set_page_load_timeout(25) 
    try :
        driver.get(url)
        sleep(1)
        driver.close() 
    except TimeoutException as ex1 :
        print("Exception has been thrown "+ str(ex1))
        driver.close()
    except WebDriverException as ex2 :
        print("Exception has been thrown "+ str(ex2))
        driver.close()

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
    filename = 'capture-'+str(s)+'-'+str(e)
    shell_command = "sudo timeout 4400 tcpdump port 443 -i enp1s0f0 -w " + filename

#NOTE : to run this first execute anything using sudo .... and then 
#execute this code using using python3 doh_capture.py
#This is because tcp dump reuqires sudo but selenium and geckodriver do not allwo that due to some security issues.

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

    move_command = "sudo mv "+filename+" /mnt/debianDoH_images/DoH_Pcaps/debianDoH2/"+filename
    os.system(move_command)
    print("File moved to /mnt") 
