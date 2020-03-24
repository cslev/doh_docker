# doh_docker
Docker container for DoH traffic analysis

# What is this repository all about?
This containerized bundle uses Selenium and Firefox to use DNS-over-HTTPS (provided by Firefox) for name resolution when visiting the websites of Alexa's list of the top 1M websites. For every website visit, the browser is closed to flush the DNS cache, and the corresponding traffic trace (i.e., a pcap file), as well as the SSL keys are logged. Then, using these two, in the image the pcap files are analyzed and the relevant information will be saved in CSV files (pcap files will be deleted afterwards as they consume a huge amount of space).


# Obtaining the container
Even though, we have released the Dockerfile and the related source code here on Github, if you are not familiar with building your own Docker image you can obtain and run it by our automatically built image at [DockerHub](https://hub.docker.com/repository/docker/cslev/doh_docker).

## Requirements
You have to have a running docker subsystem installed. If you have not done that before, go to here [https://docs.docker.com/install/linux/docker-ce/debian/](https://docs.docker.com/install/linux/docker-ce/debian/) and pick your distribution on the left hand side.

## Building on your own
Clone the repository first, then build the image.
```
 git clone https://github.com/cslev/doh_docker
 cd doh_docker
 sudo docker build -t cslev/doh_docker:latest -f Dockerfile  .
```
In the last command `-t` specifies the tag (default `latest`) used for our image! Feel free to use another tag, but to be sync with a possible update at DockerHub, we do not recommend to change any part of this command.

## Install from DockerHub
Ain't nobody got time for that! You can simply get the very same image from DockerHub as it is connected to this repository and automatically rebuilt once a change has been made to this source.
```
sudo docker pull cslev/doh_docker
```

# Running the container
To run the container, we have to specify some extra parameters for a swift run.
```
sudo docker run -d --name doh_docker --shm-size 4g cslev/doh_docker:latest
```

`--name` just assigns the same name to the container to make it easier (in the future) to refer to it.

`--shm-size 4g` is some extra memory assignment needed for selenium and firefox, otherwise the whole process becomes extremely slow (if starts at all).


# Getting the data
The container will exit once the data gathering is complete! In order to get the relevant csv files, we need to get our hands a little bit dirty (better workarounds are on their way). 
We have to restart the container, (get into it,) compress the csv files, and copy them to the host.

First, restart (recall the name we have set via `--name` above):
```
sudo docker start doh_docker
```
Get into the container:
```
sudo docker exec -it doh_docker bash
```

Compress data (cannot be done via `docker exec` as it would require to manually type all csv files instead of using `*`):
```
[NUS-Singtel][DoH_Docker] root /doh_project#  tar -czvf doh_data.tar.gz csvfile* 
```
You can simply exit from the container by typing `exit` or pressing `Ctrl+D`, the container will not stop.

Copy compressed file to the host:
```
sudo docker cp doh_docker:/doh_project/doh_data.tar.gz ./
```

**And we would need this file! If you consider to contribute to our project, please share your data with us <cs.lev@gmx.com>**



## Possible arguments (for first time runners, skip this!)
The run command does not differ to the usual ones, however, our bundled script can be parameterized. Therefore, running our container can be done in multiple ways according to your needs.

`RESOLVER` - The DoH resolver intended to be used! By default Cloudflare is set (value of `1`), but you can use Google (`2`), CleanBrowsing (`3`) and Quad9 (`4`). More built-in resolver are not supported *yet*.

`START` - The rank of the **first** website to start the browsing from (according to Alexa's `top-1m.csv` file in the source). Default is set to `1`.

`END` - The rank of the **last** website to finish the browsing at (according to Alexa's `top-1m.csv` file in the source). Default is set to `5,000`.

`BATCH` - The desired batch size in one iteration. Default is set to `500`, which means that for every 500 website-visits, we will have a separate PCAP file (TBH, at the end they will be CSV files) for managability reasons (still not too big and can be analyzed in reasonable time). We do not recommend to change this value unless you know what you are doing.

You don't have to change any of the values here, and we only recommend to *might* play with the first argument only! The rest can always remain the same.

Example for running our container with Google's DoH resolver for the first 10,000 websites
```
sudo docker run -d --name doh_docker --shm-size 4g cslev/doh_docker:latest 2 1 10000
```

