# ADFTool

This is a Final Year Project for APD3F2311CS(CYB). This tool is mainly developed from my own needs when tackling Digital Forensics CTF challenges. The main aim for this tool is to have all the Digital Forensics-related tools in one 'toolbox'. The tool is aimed to be offline/desktop-based, however, due to certain limitations, it will be running at localhost in a browser instead of a standalone desktop application.

## Tools to include

### Steganalysis tools

- [x] zsteg
- [x] stegoveritas
- [x] outguess
- [x] binwalk

### Network Packet analysis tools

- [x] tshark

### Memory analysis

- [ ] Volatility
- [ ] The Sleuth Kit

## User Interface

This tool will include a Graphical User Interface (GUI), mainly to satisfy my FYP requirement. The GUI is to be built using Python Flask. However, if the user prefers using the command line to interact with the tool, they can do so too. 

### TODO

None for now

## USAGE

To use ADFTool, you can either clone the GitHub repo and then build the Docker image from there or pull the Docker image directly from Docker hub. We will explore both options below.

### Cloning the GitHub repo

To obtain the docker image via GitHub, you can run the command below to clone the repository to your current working directory

`git clone https://github.com/BryanHJH/adftool.git`


### Obtaining the Docker image

To use ADFTool, you will need to first pull the image from Docker using the command below.

`docker pull docker push bryanhor/adftool:latest`

### CMD Usage

Once the docker image has been pulled into your local machine, you can run start the docker container by using the
commands below:

```bash
cd ADFTool/
```

```docker
docker build -t bryanhor/adftool:latest .
docker run -it -v /your/local/path/to/files_to_analyse:/home/data -v /your/local/path/for/results/:/home/data bryanhor/adftool:latest bash
```

There are 2 `-v` flags because the first one is to load the folder that has the files that you wish to analyze. This folder is bound to the `/home/data` in the docker container. The second `-v`` flag is to bind the results generated in the docker container to one of your local folders.

Optional flags are `--name` and `-v`:

- The `--name` flag will provide a specific name to the new container (however, if this flag is not provided, a name will be randomly generated).
- The `--rm` flag will automatically remove the container when you exit from the docker container.

Once you are inside the docker container, you will be in the `/home` directory. In there, you can see multiple folders and files. In here, you can do multiple things:

1. You can start the Flask application to use the GUI. 
2. You can navigate to the `bin` folder to use the all-in-one scripts
3. You can navigate to the `scripts` folder to use specific scripts.

If you choose option 1, you can move to the [GUI USAGE](#gui-usage).

If you choose option 2, you can navigate to the directory by using `cd bin/`. Then once inside the directory, you will see 3 different Python scripts, which are:

1. full_analyze.py: All-in-one script that will perform magic bytes analysis, steganalysis and network capture analysis.
2. image_analyze.py: Script that will perform steganalysis only.
3. pcap_analyze.py: Script that will perform network packet capture analysis only.

If you choose option 3, you can navigate to the directory by using `cd scripts/`. Then once inside the directory, you will see multiple bash scripts and some Python scripts. 

Each bash script will use a specific tool to perform a specific task. The name of the tool is already mentioned in the name of the file. For example `binwalk_analysis.sh` uses the tool `binwalk` to extract files hidden in an image. 

All files to be analysed will be stored in the `/home/data` directory.

All output will be stored in the `/home/results/` directory.

Once you're done using the tool, you can just type `exit` on the command line to exit the docker container.

### GUI Usage

To use the GUI for ADFTool, you will need to execute the following commands after cloning the docker image from the GitHub repository or Docker hub.

```bash
cd adftool
```

```docker
docker build -t bryanhor/adftool:latest
docker run -p 5001:5001 bryanhor/adftool:latest
```

Once the commands above have been executed, you can go to your browser and type in `http://localhost:5001/` to access the GUI.

Once inside the GUI, it will like the image below:

![ADFTool main page](/README_pictures/ADFTool_main_page.png)

You can upload a single file by clicking on the "Browse" button and selecting the file you want to upload. Currently, the GUI for ADFTool can only accept one file each time. 

Once uploaded, the file will go through magic byte analysis and the output will be displayed as text on the same page, as shown in the picture below:

![Magic byte analysis output](/README_pictures/ADFTool_magic_byte_output.png)

If the uploaded file passes the magic byte analysis, it will be further analysed depending on the file type. Currently only image and network packet captures will be further analysed. The picture below shows an example of a successfuly analysis and the page containing all the results.

![ADFTool preliminary results page](/README_pictures/ADFTool_initial_analysis_output.png)

![ADFTool in depth results page](/README_pictures/ADFTool_indepth_analysis_output.png)

Once you're done and happy with the analysis, you can choose to download all the files or specific files. If you only want the specific files, you can just click on the file name that is displayed at the top of the In Depth results page shown in the picture above. 

Once you are satisfied and want to exit from the GUI, you can just close the browser.

## REMOVAL

To remove the docker container, you can use the following steps:

### Step1

This step is to remove the docker container that was being used. This step is necessary if the `--rm` was not included in the `docker run` command above.

```bash
docker ps -a # To obtain the CONTAINER ID, 
docker rm <CONTAINER ID>
```

### Step 2

This step is to remove the docker image from your system.

```bash
docker images # To obtain the IMAGE ID
docker rmi <IMAGE ID>
```

## IMAGES

![Docker Images](README_pictures/docker_images.png)

![Docker Containers](README_pictures/docker_container_1.png)

![Docker Build](README_pictures/docker_build.png)

![Docker Analyze Directory](README_pictures/docker_analyze_directory.png)

![Docker Results](README_pictures/docker_results.png)
