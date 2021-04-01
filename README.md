# Dissemination
This repository has also been made for our [research paper](https://github.com/cslev/doh_ml/raw/main/DNS_over_HTTPS_identification.pdf) titled **Privacy of DNS-over-HTTPS: Requiem for a Dream?** to appear at [IEEE Euro S&P](http://www.ieee-security.org/TC/EuroSP2021/).
When using the repo, please use the full reference to our paper as follows:
```
@inproceedings{doh_identification_ml,
 author = {Levente Csikor and Himanshu Singh and Min Suk Kang and Dinil Mon Divakaran},
 title = {{Privacy of DNS-over-HTTPS: Requiem for a Dream?}},
 booktitle = {IEEE Euro Security and Privacy},
 year = {2021}

} 
```


# What is this repository all about?
This containerized bundle uses Selenium and Firefox to use DNS-over-HTTPS (provided by Firefox) for name resolution when visiting the websites of Alexa's list of the top 1M websites (an older version from 2018 is part of the repository). 
For every website visit, the browser is closed to flush the DNS cache, and the corresponding traffic trace (i.e., a pcap file), as well as the SSL keys are logged. 
Then, using these two, in this docker container, the pcap files are analyzed and the relevant information will be saved in CSV files (pcap files will be deleted afterwards as they consume a huge amount of space).
Such relevant information is as follows:
 - frame number
 - timestamp 
 - Source IP
 - Destination IP
 - Source Port
 - Destination Port (although, it is 443 all the time)
 - Protocol (labeled by Wireshark)
 - frame length
 - payload information

The `.csv` files can be processed by the [machine learning application written for this purpose](https://github.com/cslev/doh_ml).


## Requirements
Being a docker container, you have to have a running docker subsystem installed. If you have no such subsystem, first, go to [https://docs.docker.com/install/linux/docker-ce/debian/](https://docs.docker.com/install/linux/docker-ce/debian/), pick your distribution on the left hand side, and follow the instructions to install it.

# Obtaining the container

## <a name="autobuild"></a>Auto-builds at DockerHub
You can obtain an auto-built up-to-date image from [DockerHub](https://hub.docker.com/repository/docker/cslev/doh_docker).
Do do so, just do the following:
```
sudo docker pull cslev/doh_docker:latest
```
This will download the container and you are ready to use it (see parameters and configurations for docker-compose below).

## <a name="build"></a> Build your own image
Clone the repository first, then build the image.
```
git clone https://github.com/cslev/doh_docker
cd doh_docker
sudo docker build -t cslev/doh_docker:latest -f Dockerfile  .
```
In the last command `-t` specifies the tag (default `latest`) used for our image! Feel free to use another tag, but to be sync with a possible future update might be coming from DockerHub later, we do not recommend to change any part of this command.


# Running the container
The container and the scripts inside can be parametrized by environment variables. You can either set these variables by definint `-e VARNAME=value` everytime, or create and environment file that you pass to the container when started.
For simplicity, we discuss the first approach only, but let's see first the ENV variables

## All Environment variables
`DOH_DOCKER_NAME` the name of the container
`DOH_DOCKER_RESOLVER` the resolver intended to use. `doh_docker` container supports almost all resolvers publicly available. See a complete list [here](https://raw.githubusercontent.com/cslev/doh_docker/master/source/r_config.json). This `json` file is used in the program when deciding the resolver related parameters. Default is *cloudflare*.
`DOH_DOCKER_START` **first** domain to visit in the Alexa's domain list or whatever domain list file you use (see `DOH_DOCKER_DOMAIN_LIST`). Default is: *1*

`DOH_DOCKER_END` **last** domain to visit in the Alexa's domain list or whatever domain list file you use (see `DOH_DOCKER_DOMAIN_LIST`). Default is: *5000*

`DOH_DOCKER_BATCH` The desired batch size in one iteration. Default is set to *200*, which means that for every 200 website-visits, we will have a separate PCAP file for managability reasons (still not too big and can be analyzed in reasonable time). Although, at the end, they will be CSV files. We do not recommend to change this value unless you know what you are doing.

`DOH_DOCKER_INTF` the used interface in the container. Default is *eth0* and if you don't have any special configuration, you don't have to change this at all.

`DOH_DOCKER_DOMAIN_LIST` this is the file describing the domains to visit in the form of how the provided [top-1m.csv](https://github.com/cslev/doh_docker/blob/master/source/top-1m.csv) looks like. If you want to use your own file, the easiest way is to store it in your `<PATH_TO_YOUR_RESULTS_DIR>`, which you will mount into the container at `/doh_project/archives`. Accordingly, you can specify the path to your domain list file as `/doh_project/archives/my_list_of_domains.csv`.

`DOH_DOCKER_META` any meta information you would like to pass. This information will be appended to the final compressed file's name; again for easier identification. So, be short and meaningful. Default is *sg*; we simply use our locations as an extra information.

`DOH_DOCKER_WEBPAGE_TIMEOUT` this indicates the program how many seconds it should wait for a webpage to load. Since, not all domains work (or might not be resolved by a filter), we have to have a timeout. Default is *20* (do not reduce it much more than below 15 seconds. Inside the container, the browser needs this time to effectively load all the contents.)

`DOH_DOCKER_ARCHIVE_PATH` define it to the mount point, i.e., `/doh_project/archives`. This path is set by default. Only change if you intend to use different path inside the container for archives.

## Running with `docker run`
To run the container, the command looks as follows:
```
sudo docker run -d --name my_doh -e DOH_DOCKER_NAME=my_doh [-e FURTHER_ENV_VARS] -v <PATH_TO_YOUR_RESULTS_DIR>:/doh_project/archives:rw --shm-size 4g cslev/doh_docker:latest
```

`--name` just assigns a simple name to the container to make it easier (in the future) to refer to it when listing running containers via `docker ps` (instead of the docker subsystem's random image names).

`--shm-size 4g` is some extra memory assignment needed for Selenium and Firefox, otherwise the whole process becomes extremely slow (if starts at all).

`-v <PATH_TO_YOUR_RESULTS_DIR>:/doh_project/archives:rw` will mount your `<PATH_TO_YOUR_RESULTS_DIR>` to the container, and it will store the final archive there. (Yes, all results will be in a compressed archive, you can later uncompress and analyze.)

`-e DOH_DOCKER_NAME=` sets environmental variable to `my_doh`. This variable is used in `.bashrc` to set `$NAME` in the promp, i.e., when logged into/attached to the container and `$NAME=cloudflare`, you will see `root@cloudflare`.
This is also for simplyfing things; it can help a lot to identify which one is doing what experiment as complete run with 5,000 websites can take around 24-48 hours.

**Define the other environment variables if needed**

## Running with `docker-compose`
We also provide a docker-compose YAML file to ease the management of the containers, and also let you to easily run multiple containers with one command.
If you are unfamiliar with docker-compose and you don't have it installed, refer to [this](https://docs.docker.com/compose/).
It is worth having a look...docker-compose can ease your life.

### Obtain docker-compose quickly
A quick howto for Linux. 
#### Get the correct variant for your distro:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.28.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
#### Add the correct permissions
```
sudo chmod +x /usr/local/bin/docker-compose
```
And you are good to go :)

### docker-compose
The repository contains a `docker-compose.yml.template` file. It looks quite simple and straightforward:
```
---
version: '3.3'

services:
  doh1:
    image: 'cslev/doh_docker:latest'
    container_name: ${R1}  #rename according to you scenario for easier identification

    volumes:
      - './container_data/MY_CONTAINER:/doh_project/archives:rw'

    
    shm_size: '4g'

    environment:
      DOH_DOCKER_NAME: 'MY_CONTAINER'  #should be same as container_name
      DOH_DOCKER_RESOLVER: 'cloudflare' # resolver to use
      DOH_DOCKER_START: '1' #first domain to visit in the domain list
      DOH_DOCKER_END: '5000' #last domain to visit in the domain list
      DOH_DOCKER_BATCH: '200' #how many domains to visit within a batch (don't change unless you know what you are doing)
      DOH_DOCKER_INTF: 'eth0' #change this if your container would not have eth0 as a default interface
      DOH_DOCKER_DOMAIN_LIST: 'top-1m.csv' #the relative path inside the container pointing to the list of domains to visit (in Alexa list style: id, domain <-one each line)
      DOH_DOCKER_META: 'sg' #any meta info to affix your final output files for easier identification
      DOH_DOCKER_WEBPAGE_TIMEOUT: '20' #how many seconds we wait for a website to load before throwing timeout error and skip
      DOH_DOCKER_ARCHIVE_PATH: '/doh_project/archives' #where to store the compressed output. Should be the same as defined by the 'volume'

```
As you can see everything has a comment to help you defining the environment variables easily. Besides, other container related settings are defined including `shm-size` and also the volume to mount to `/doh_project/archives`.
The only interesting part is the variable `$R1`. 

`docker-compose` can use variables in the YAML files if those variables are defined in the `.env` file located in the same directory.
If you check the file we provided, each `RX` defines a resolver that we support.
```
R1=cloudflare
R2=google
R3=cleanbrowsing
R4=quad9
R5=powerdns
R6=dohli
R7=adguard
R8=opendns
R9=CZNIC
R10=DNSlify
...
```
You can either use these variables, or you can explicity say `cloudflare` in the docker-compose.yml file instead of the `${R1}`.
However, this `RX` thingy becomes handy if you simply want to change your setup after a successful run.
For instance, let's say your experiment with `cloudflare` is done. You just simply replace the variables to `google` in order to run the experiment by using Google's resolver via a simple `sed`:
```
sed -i "s/R1/R2/g" docker-compose.yml
```

#### Run (finally)
```
sudo docker-compose -f docker-compose.yml up -d
```
`-d` puts everything into a daemonized mode to supress container output.
However, you can see after this command right away when your service is up and running.
`-f` is only needed if your compose file has a different name than `docker-compose.yml`

Note, simply multiplying the service descriptor `doh1` with different names in the docker-compose.yml, you can easily define multiple different containers, and by the `docker-compose up` command, you fire up all of them in one shot.


# Getting the data
The container will exit once the data gathering is complete and all relevant data will be saved in a compressed archive, called `doh_data_<USED_RESOLVER>_<MORE_META>.tar.gz`!
If you HAVE used the command above with the `-v` option, or defined the `volume` in the `docker-compose.yml` file, you will have the data on your host machine.

Otherwise, to get the data we need to restart the container (as it has exited) and copy the compressed archive to the host.

First, restart (recall the name we have set via `--name` above):
```
sudo docker start my_doh
```
Copy compressed file to the host:
```
sudo docker cp my_doh:/doh_project/archives/doh_data_<USED_RESOLVER>_<MORE_META>.tar.gz ./
```

**And, we would need this file! If you consider to contribute to our project, please share your data with us <cs.lev@gmx.com>**

Don't forget to stop and/or remove your container if not needed anymore (i.e., if you have `doh_data_<USED_RESOLVER>_<MORE_META>.tar.gz`):
```
sudo docker stop my_doh
sudo docker rm my_doh
```



# Monitoring/Logging
Easiest way to see whether the process is finished is to check the status of the container itself. If it is exited, then it's done.
```
sudo docker ps -a -f name=my_doh
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS               NAMES
de77210d2748        cslev/doh_docker    "/doh_project/start_…"   3 minutes ago       Up 3 minutes                            my_doh
```
The example above shows that the container is still running.

If a little bit more granular status update is required, we can monitor at which (number of) website our container is visiting at the moment.
```
docker exec -it my_doh tail -f progess.log

11 https://www.taobao.com
12 https://www.twitter.com
13 https://www.tmall.com
14 https://www.google.co.jp
15 https://www.live.com
16 https://www.vk.com
17 https://www.instagram.com
18 https://www.sohu.com
Message: Timeout loading page after 25000ms

19 https://www.sina.com.cn
```
As you can see, some websites are not loaded due to a timeout!



# Troubleshooting
It might happen that the script inside the container crashes due to several reasons (e.g., running out of memory, selenium error, which is not handled properly, etc.).
One of the most obvious things that can point this out is the size of the archive file! It is normally around 70-100 MB. So, if your compressed archive is below 50MB, there is a high chance that something was not working properly.

This can result in that some batches might not have finished. For instance, having a serious issue at the 45th website would mean that the first batch of 200 websites will be stopped at the 45th website, and jumps to the next batch (i.e., continues from website no. 201).

## Look for batches
By looking into the log files, one can see when the processing has been started and what was the last website in that batch. If it is not 200,400, ..., 5000 (in case of websites between 1-5000 and batch size of 200, i.e., in the default setting), then there was an error.

To quickly check this out during processing, let's count the successful batches that ends with `00`.
```
sudo docker exec my_doh cat /doh_project/progress.log |grep batch -B 10 |grep ^[0-9]|awk '{print $1}'|grep 00$|wc -l
```
If the result is *25*, you are good!
There is another problem!

Note, once the measurement is done, container is stopped. If restarted afterwards, the `progess.log` SYMLINK will point to the new, almost empty file. In this case, use the explicit path to the log file, or copy-paste the archive from the container to your host, decompress it, and issue the above command on the `doh_log.log` file.

## TimeoutException
To quickly check this out, let's count the unsuccessful connection attempts:
```
sudo docker exec my_doh cat /doh_project/progress.log |grep -i timeoutexception |wc -l
```
This means that the preset seconds for timeout was not enough! Usually, it is not your problem, it can be the problem of the DoH resolver used. If you set timeout to a considerably long interval (e.g., 50 sec), then you can rest assured that timeouts are not because of you, but because of the DoH resolver!

