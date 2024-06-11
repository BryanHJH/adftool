FROM kalilinux/kali-rolling

# Update and install necessary packages
<<<<<<< HEAD
RUN apt-get update && apt-get install -y \
    binwalk \
=======
RUN apt update && apt install -y \
>>>>>>> a5a5a7c9a914292b3d54577c5f1a4b8a04ec6c7e
    outguess \
    python3 \
    python3-pip \
    ruby \
<<<<<<< HEAD
    tshark \
    zsteg

# Install stegoveritas
RUN pip3 install stegoveritas

# Create a directory for the scripts
RUN mkdir /scripts

# Copy the scripts to the container
COPY outguess_analysis.sh /scripts/
COPY binwalk_analysis.sh /scripts/
COPY pcap_analysis.sh /scripts/
COPY stegoveritas_analysis.sh /scripts/
COPY zsteg_analysis.sh /scripts/

# Make the scripts executable
RUN chmod +x /scripts/*

# Set the working directory
WORKDIR /scripts
=======
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
>>>>>>> a5a5a7c9a914292b3d54577c5f1a4b8a04ec6c7e
