#!/bin/bash

# Function to perform steganalysis on a single file
analyze_file() {
    file="$1"
    verbose="$2"
    
    # Create a directory to store the results based on the file name
    # result_dir="../results_$(basename "$file")"
    result_dir="$(dirname "$(dirname "$0")")/results/results_$(basename "$file")"
    mkdir -p "$result_dir"
    
    # Generate a unique filename for the result file and error/log file
    result_file="$result_dir/$(basename "$file")_$(date +%Y%m%d_%H%M%S).txt"
    error_file="$result_dir/errors.txt"
    
    # Redirect warnings and errors to the error/log file
    exec 2> "$error_file"
    
    # Check if the file is an image
    if file -b --mime-type "$file" | grep -q "image/"; then
        [ "$verbose" = true ] && echo "Analyzing image file: $file"
        
        [ "$verbose" = true ] && echo "zsteg results:"
        zsteg_output=$(zsteg "$file" | grep -E "extradata|text|UTF-8")
        [ "$verbose" = true ] && echo "$zsteg_output"
        echo -e "\nzsteg results:" >> "$result_file"
        echo "$zsteg_output" >> "$result_file"
        
        [ "$verbose" = true ] && echo "Outguess results:"
        outguess_output=$(outguess -r "$file" /dev/null 2>&1 | grep -v "No data extracted")
        [ "$verbose" = true ] && echo "$outguess_output"
        echo -e "\nOutguess results:" >> "$result_file"
        echo "$outguess_output" >> "$result_file"
        
        [ "$verbose" = true ] && echo "binwalk results:"
        binwalk_output=$(binwalk -e -M -C "$result_dir" "$file")
        [ "$verbose" = true ] && echo "$binwalk_output"
        echo -e "\nbinwalk results:" >> "$result_file"
        echo "$binwalk_output" >> "$result_file"
        
        [ "$verbose" = true ] && echo "stegoveritas results:"
        stegoveritas_output=$(stegoveritas -out "$result_dir" "$file")
        [ "$verbose" = true ] && echo "$stegoveritas_output"
        echo -e "\nstegoveritas results:" >> "$result_file"
        echo "$stegoveritas_output" >> "$result_file"
    # Check if the file is a network packet capture file
    elif file "$file" | grep -q -E "capture|packet|pcap|pcapng"; then
        [ "$verbose" = true ] && echo "Analyzing network packet capture file: $file"
        
        [ "$verbose" = true ] && echo "Extracting objects using tshark:"
        tshark_output=$(tshark -r "$file" --export-objects "http,$result_dir/http_objects" \
                                           --export-objects "imf,$result_dir/imf_objects" \
                                           --export-objects "smb,$result_dir/smb_objects" \
                                           --export-objects "tftp,$result_dir/tftp_objects")
        [ "$verbose" = true ] && echo "$tshark_output"
        echo -e "\nExtracting objects using tshark:" >> "$result_file"
        echo "$tshark_output" >> "$result_file"
        
        [ "$verbose" = true ] && echo "Following TCP streams:"
        tcp_streams=$(tshark -r "$file" -Y "tcp" -T fields -e tcp.stream | sort -n | uniq)
        for stream in $tcp_streams; do
            stream_output=$(tshark -r "$file" -q -z follow,tcp,ascii,$stream | sed '/===================================================================/d' | sed '1,5d' | tr -d '\n' | sed 's/1//g')
            {
                tshark -r "$file" -q -z follow,tcp,ascii,$stream | sed -n '/==/,/Node 1:/p'
                echo -e "\n$stream_output"
                echo "==================================================================="
            } > "$result_dir/tcp_stream_$stream.txt"
            {
                tshark -r "$file" -q -z follow,tcp,ascii,$stream | sed -n '/==/,/Node 1:/p'
                echo -e "\n$stream_output"
                echo "==================================================================="
            } | jq -R -s '{stream: .}' > "$result_dir/tcp_stream_$stream.json"
            [ "$verbose" = true ] && echo "TCP stream $stream saved to $result_dir/tcp_stream_$stream.txt (ASCII) and $result_dir/tcp_stream_$stream.json (JSON)"
        done
        echo -e "\nFollowing TCP streams:" >> "$result_file"
        echo "TCP streams saved to individual files in $result_dir (ASCII and JSON formats)" >> "$result_file"
        
        [ "$verbose" = true ] && echo "Following UDP streams:"
        udp_streams=$(tshark -r "$file" -Y "udp" -T fields -e udp.stream | sort -n | uniq)
        for stream in $udp_streams; do
            stream_output=$(tshark -r "$file" -q -z follow,udp,ascii,$stream | sed '/===================================================================/d' | sed '1,5d' | tr -d '\n' | sed 's/1//g')
            {
                tshark -r "$file" -q -z follow,udp,ascii,$stream | sed -n '/==/,/Node 1:/p'
                echo -e "\n$stream_output"
                echo "==================================================================="
            } > "$result_dir/udp_stream_$stream.txt"
            {
                tshark -r "$file" -q -z follow,udp,ascii,$stream | sed -n '/==/,/Node 1:/p' 
                echo -e "\n$stream_output"
                echo "==================================================================="
            } | jq -R -s '{stream: .}' > "$result_dir/udp_stream_$stream.json"
            [ "$verbose" = true ] && echo "UDP stream $stream saved to $result_dir/udp_stream_$stream.txt (ASCII) and $result_dir/udp_stream_$stream.json (JSON)"
        done
        echo -e "\nFollowing UDP streams:" >> "$result_file"
        echo "UDP streams saved to individual files in $result_dir (ASCII and JSON formats)" >> "$result_file"

    else
        [ "$verbose" = true ] && echo "Skipping $file. Not an image or network packet capture file."
    fi
}

# Check if an argument is provided
if [ $# -eq 0 ]; then
    echo "Please provide an image file, a network packet capture file, or a directory as an argument."
    exit 1
fi

# Check if the verbose flag is provided before or after the file/directory
verbose=false
if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
    verbose=true
    shift
elif [ "${!#}" = "-v" ] || [ "${!#}" = "--verbose" ]; then
    verbose=true
    unset "$#"
fi

# Check if the argument is a file or a directory
if [ -f "$1" ]; then
    # Perform analysis on a single file
    analyze_file "$1" "$verbose"
elif [ -d "$1" ]; then
    # Perform analysis on all files in the directory
    for file in "$1"/*; do
        if [ -f "$file" ]; then
            analyze_file "$file" "$verbose"
        fi
    done
else
    echo "Invalid argument. Please provide a valid image file, network packet capture file, or a directory."
    exit 1
fi
