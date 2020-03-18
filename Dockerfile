FROM debian:bullseye
LABEL maintainer="cslev <cslev@gmx.com>"

#packages needed for compilation
ENV DEPS apt-utils \
	 tshark \
	 tcpdump \
	 nano \
	 net-tools \
         tar \
	 bzip2 \
	 xz-utils \
	 wget

ENV PYTHON_DEPS  python3 \
	         python3-pip \
		 libpython3-dev \
		 python3-pandas \
		 python3-numpy \
		 python3-selenium


COPY source /doh_project
WORKDIR /doh_project

SHELL ["/bin/bash", "-c"]
RUN apt-get update && \
    apt-get install -y --no-install-recommends $DEPS && \
    apt-get install -y --no-install-recommends $PYTHON_DEPS && \
    apt-get autoremove --purge -y && \
    wget -q https://ftp.mozilla.org/pub/firefox/releases/74.0/linux-x86_64/en-US/firefox-74.0.tar.bz2 && \
    tar -xjf firefox-74.0.tar.bz2 && \
    tar -xzf geckodriver-v0.26.0-linux64.tar.gz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    chmod +x geckodriver && \
    chmod +x doh_capture.py && \
    cp bashrc_template /root/.bashrc && \
    source /root/.bashrc && \
    echo "DoH docker image is ready"



