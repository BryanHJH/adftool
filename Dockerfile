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

# Create a directory to store the files that will be analysed
RUN mkdir /home/data && chown -R root:root /home/data && chmod -R 775 /home/data

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
COPY scripts/mergedChecking.py /home/scripts
COPY scripts/pyMagicBytes.py /home/scripts
COPY scripts/DB.txt /home/scripts

# Make the scripts executable
RUN chmod +x /home/scripts/*

# Set the working directory
WORKDIR /home/scripts
