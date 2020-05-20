FROM debian:bullseye
LABEL maintainer="cslev <cslev@gmx.com>, HimanshuSinghGH <heman.sam@gmail.com>"

#packages needed for compilation
ENV DEPS  tshark \
          tcpdump \
          nano \
          tar \
          bzip2 \
          tar \
          bzip2 \
          wget \
          gconf-service \
          libasound2 \
         libatk1.0-0 \
         libc6 libcairo2 \
         libcups2 \
         libdbus-1-3 \
         libexpat1 \
         libfontconfig1 \
         libgcc1 \
         libgconf-2-4 \
         libgdk-pixbuf2.0-0 \
         libglib2.0-0 \
         libgtk-3-0 \
         libnspr4 \
         libpango-1.0-0 \
         libpangocairo-1.0-0 \
         libstdc++6 \
         libx11-6 \
         libx11-xcb1 \
         libxcb1 \
         libxcomposite1 \
         libxcursor1 \
         libxdamage1 \
         libxext6 \
         libxfixes3 \
         libxi6 \
         libxrandr2 \
         libxrender1 \
         libxss1 \
         libxtst6 \
         ca-certificates \
         fonts-liberation \
         libappindicator1 \
         libnss3 \
         lsb-release \
         xdg-utils \
         libxt6 \
         procps \
         jq \
         ethtool

ENV PYTHON_DEPS python3 \
                python3-six \
                python3-pandas \
                python3-simplejson \
                libpython3-dev
#		 python3-selenium
# we downgrade selenium to 3.14.1 as bullseye debian has the alpha 4.0, which does not work properly now.


COPY source /doh_project
WORKDIR /doh_project
SHELL ["/bin/bash", "-c"]
RUN apt-get update && \
    apt-get install -y --no-install-recommends $DEPS && \
    apt-get install -y --no-install-recommends $PYTHON_DEPS && \
    dpkg -i selenium/python3-urllib3_1.24.1.deb && \
    dpkg -i selenium/python3-selenium_3.14.1.deb && \
    apt-get autoremove --purge -y && \
    wget -q https://ftp.mozilla.org/pub/firefox/releases/74.0/linux-x86_64/en-US/firefox-74.0.tar.bz2 && \
    tar -xjf firefox-74.0.tar.bz2 && \
    tar -xzf geckodriver-v0.26.0-linux64.tar.gz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf selenium/ && \
    rm -rf firefox-74.0.tar.bz2 && \
    rm -rf geckodriver-v0.26.0-linux64.tar.gz && \
    chmod +x geckodriver && \
    chmod +x doh_capture.py && \
    chmod +x start_doh_capture.sh && \
    cp geckodriver /usr/bin && \
    mkdir -p /usr/lib/firefox && \
    ln -s /doh_project/firefox/firefox /usr/lib/firefox/firefox && \
    mv others/bashrc_template /root/.bashrc && \
    source /root/.bashrc && \
    mkdir -p pcap && \
    mkdir -p archives && \
    mv /usr/sbin/tcpdump /usr/bin/tcpdump
#This latter is necessary if container is supposed to run in priviledged mode,
#otherwise tcpdump complains about not being able to set ownerships to the output file

# We start the script automatically
ENTRYPOINT ["/doh_project/start_doh_capture.sh"]
#CMD ["bash", "start_doh_capture.sh"]
