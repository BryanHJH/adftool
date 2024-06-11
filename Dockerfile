FROM kalilinux/kali-rolling

# Update and install necessary packages
RUN apt update && apt install -y \
    outguess \
    python3 \
    python3-pip \
    ruby \
    tshark

# Install binwalk
RUN pip3 install binwalk
RUN apt install -y mtd-utils gzip bzip2 tar arj lhasa p7zip p7zip-full cabextract squashfs-tools sleuthkit default-jdk lzop srecord

# Install zsteg
RUN gem install zsteg

# Install stegoveritas
RUN pip3 install stegoveritas
RUN stegoveritas_install_deps

# Create a directory for the scripts
RUN mkdir /home/scripts  

# Create a directory for the python executable file
RUN mkdir /home/bin

# Create a directory for the magic bytes sources
RUN mkdir /home/src

# Installing python libraries
COPY requirements.txt /home
WORKDIR /home
RUN pip3 install -r requirements.txt

# Copy the scripts to the container
COPY scripts/outguess_analysis.sh /home/scripts
COPY scripts/binwalk_analysis.sh /home/scripts
COPY scripts/pcap_analysis.sh /home/scripts
COPY scripts/stegoveritas_analysis.sh /home/scripts
COPY scripts/zsteg_analysis.sh /home/scripts
COPY bin/analyze.py /home/bin
COPY src/pyMagicBytes.py /home/src
COPY src/DB.txt /home/src

# Make the scripts executable
RUN chmod +x /home/scripts/*

# Set the working directory
WORKDIR /home/bin