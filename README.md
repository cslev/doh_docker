# What is this repository all about?
This containerized bundle uses Selenium and Firefox to use DNS-over-HTTPS (provided by Firefox) for name resolution when visiting the websites of Alexa's list of the top 1M websites. For every website visit, the browser is closed to flush the DNS cache, and the corresponding traffic trace (i.e., a pcap file), as well as the SSL keys are logged. Then, using these two, in the image the pcap files are analyzed and the relevant information will be saved in CSV files (pcap files will be deleted afterwards as they consume a huge amount of space).


# Obtaining the container
Even though, we have released the Dockerfile and the related source code here on Github, if you are not familiar with [building your](#build) own Docker image you can obtain and [obtain it](#download) by our automatically built image at [DockerHub](https://hub.docker.com/repository/docker/cslev/doh_docker).

## Requirements
You have to have a running docker subsystem installed. If you have not done that before, go to here [https://docs.docker.com/install/linux/docker-ce/debian/](https://docs.docker.com/install/linux/docker-ce/debian/) and pick your distribution on the left hand side.

## <a name="build"></a> Building on your own
Clone the repository first, then build the image.
```
git clone https://github.com/cslev/doh_docker
cd doh_docker
sudo docker build -t cslev/doh_docker:latest -f Dockerfile  .
```
In the last command `-t` specifies the tag (default `latest`) used for our image! Feel free to use another tag, but to be sync with a possible update at DockerHub, we do not recommend to change any part of this command.

##  <a name="download"></a> Install from DockerHub
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

*A complete run with 5,000 websites takes around 24 hours, so be patient :)*

# Getting the data
The container will exit once the data gathering is complete and all relevant data will be saved in a compressed archive, called `doh_data.tar.gz`! In order to get the data we need to restart the container (as it has exited) and copy the compressed archive to the host.

First, restart (recall the name we have set via `--name` above):
```
sudo docker start doh_docker
```
Copy compressed file to the host:
```
sudo docker cp doh_docker:/doh_project/doh_data_<USED_RESOLVER>_.tar.gz ./
```

**And, we would need this file! If you consider to contribute to our project, please share your data with us <cs.lev@gmx.com>**

Don't forget to stop and/or remove your container if not needed anymore (i.e., if you have `doh_data.tar.gz`):
```
sudo docker stop doh_docker
sudo docker rm doh_docker
```

## Monitoring/Logging
Easiest way to see whether the process is finished is to check the status of the container itself. If it is exited, then it's done.
```
sudo docker ps -a -f name=doh_docker
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS               NAMES
de77210d2748        cslev/doh_docker    "/doh_project/start_…"   3 minutes ago       Up 3 minutes                            doh_docker
```
The example above shows that the container is still running.

If a little bit more granular status update is required, we can monitor at which (number of) website our container is visiting at the moment.
```
docker exec -it doh_docker tail -f progess.log

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


## Further arguments (for first time runners, skip this!)
The run command does not differ to the usual ones, however, our bundled script can be parameterized. Therefore, running our container can be done in multiple ways according to your needs.

`RESOLVER` - The DoH resolver intended to be used! By default Cloudflare is set (value of `1`), but you can use Google (`2`), CleanBrowsing (`3`), Quad9 (`4`), and more. For all built-in resolvers, check [this out](https://raw.githubusercontent.com/cslev/doh_docker/master/source/r_config.json). The list is in the same order as our scripts wait for it, e.g., `5` means the usage of PowerDNS.

`START` - The rank of the **first** website to start the browsing from (according to Alexa's `top-1m.csv` file in the source). Default is set to `1`.

`END` - The rank of the **last** website to finish the browsing at (according to Alexa's `top-1m.csv` file in the source). Default is set to `5,000`.

`BATCH` - The desired batch size in one iteration. Default is set to `500`, which means that for every 500 website-visits, we will have a separate PCAP file (TBH, at the end they will be CSV files) for managability reasons (still not too big and can be analyzed in reasonable time). We do not recommend to change this value unless you know what you are doing.

`META` - Any desired metadata for the measurements (as one *string* without whitespaces or within quotes) that will be used in the final archive's name for easier identification. For instance, using `usa_texas` as a META, the final archive will be `doh_data_<USED_RESOLVER>_usa_texas.tar.gz`

`INTF` - Although, in most of the cases containers have one interface connected to the internet (`eth0`), if for some reason your is different, you can specify that as the last argument. Default is set to `eth0`.

You don't have to change any of the values here, and we only recommend to *play* with the first argument only! The rest can always remain the same and the *order* is **important**, so if you want to use `META` then define (even the default values again for) all others before it!

Example for running our container with Google's DoH resolver for the first 10,000 websites (`START=1`, `END=10000`) connected via an interface called `enp3s0f0`, with the default `BATCH` size of 200 and using *usa_texas* as `META`:
```
sudo docker run -d --name doh_docker --shm-size 4g cslev/doh_docker:latest 2 1 10000 200 usa_texas enp3s0f0
```


# Troubleshooting
It might happen that the script inside the container crashes due to several reasons (e.g., running out of memory, selenium error, which is not handled properly, etc.).
One of the most obvious things that can point this out is the size of the archive file! It is normally around 70-100 MB. So, if your compressed archive is below 50MB, there is a high chance that something was not working properly.

This can result in that some batches might not have finished. For instance, having a serious issue at the 45th website would mean that the first batch of 200 websites will be stopped at the 45th website, and jumps to the next batch (i.e., continues from website no. 201).

## Look for batches
By looking into the log files, one can see when the processing has been started and what was the last website in that batch. If it is not 200,400, ..., 5000 (in case of websites between 1-5000 and batch size of 200, i.e., in the default setting), then there was an error.

To quickly check this out, let's count the successful batches that ends with `00`.
```
sudo docker exec <YOUR_CONTAINER_NAME> cat /doh_project/progress.log |grep batch -B 10 |grep ^[0-9]|awk '{print $1}'|grep 00$|wc -l
```
If the result is *25*, you are good!
There is another problem!

## TimeoutException
To quickly check this out, let's count the successful batches that ends with `00`.
```
sudo docker exec <YOUR_CONTAINER_NAME> cat /doh_project/progress.log |grep -i timeoutexception |wc -l
```
This means that the preset seconds for timeout was not enough! Usually, it is not your problem, it can be the problem of the DoH resolver used. If you set timeout to a considerably long interval (e.g., 50 sec), then you can rest assured that timeouts are not because of you, but because of the DoH resolver!
