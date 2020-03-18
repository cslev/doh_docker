import os 
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException , WebDriverException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary # for specifying the path to firefox binary
from time import sleep,ctime
import multiprocessing
import time

start = 1 
stop = 5000
batch_size = 200
time_out = batch_size * 15

data = pd.read_csv('top-1m.csv' , names = ['rank','website']) 

print(time.ctime())

options = Options()
options.headless = True


## specifying the binary path
binary = FirefoxBinary('./firefox/firefox')

#profile = webdriver.FirefoxProfile('/home/user/.mozilla/firefox/0b5055qu.Doh_profile')
## setting the firefox profile to use DoH
profile = webdriver.FirefoxProfile()
profile.set_preference("network.trr.mode", 2)
profile.set_preference("network.trr.uri", "https://mozilla.cloudflare-dns.com/dns-query")
profile.set_preference("network.trr.bootstrapAddress", '1.1.1.1.')

def open_website(url):
    #driver = webdriver.Firefox(firefox_profile=profile)

    ## in the executabel path you need to specify the location of geckodriver location.
    driver = webdriver.Firefox(executable_path='./geckodriver',firefox_binary=binary, options=options, firefox_profile=profile)
    driver.set_page_load_timeout(25) 
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
    filename = 'capture-'+str(s)+'-'+str(e)

    ## here after -i you need to add the ethernet port. which i guess is eth0
    shell_command = "sudo timeout 4400 tcpdump port 443 -i eth0 -w " + filename

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

    # this part is for moving the files to another location which is not needed in case of the docker container.
    """move_command = "sudo mv "+filename+" /mnt/debianDoH_images/DoH_Pcaps/debianDoH2/"+filename
    os.system(move_command)
    print("File moved to /mnt") """
