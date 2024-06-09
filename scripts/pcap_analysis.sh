#!/bin/bash

analyze_pcap() {
    file="$1"
    result_dir="$2"
    verbose="$3"
    
    # Extracting objects using tshark
    [ "$verbose" = true ] && echo -e "Extracting objects using tshark:"
    tshark_output=$(tshark -r "$file" --export-objects "http,$result_dir/http_objects" \
                                       --export-objects "imf,$result_dir/imf_objects" \
                                       --export-objects "smb,$result_dir/smb_objects" \
                                       --export-objects "tftp,$result_dir/tftp_objects" 2>/dev/null)
    [ "$verbose" = true ] && echo "$tshark_output"
    echo -e "\nExtracting objects using tshark:" >> "$result_dir/results.txt"
    echo "$tshark_output" >> "$result_dir/results.txt"
    
    # Following TCP streams
    [ "$verbose" = true ] && echo -e "Following TCP streams:"
    tcp_streams=$(tshark -r "$file" -Y "tcp" -T fields -e tcp.stream 2>/dev/null | sort -n 2>/dev/null | uniq 2>/dev/null)
    for stream in $tcp_streams; do
        stream_output=$(tshark -r "$file" -q -z follow,tcp,ascii,$stream 2>/dev/null | sed '/===================================================================/d' 2>/dev/null | sed '1,5d' 2>/dev/null | tr -d '\n' 2>/dev/null | sed 's/1//g' 2>/dev/null)
        {
            tshark -r "$file" -q -z follow,tcp,ascii,$stream 2>/dev/null | sed -n '/==/,/Node 1:/p' 2>/dev/null
            echo -e "\n$stream_output"
            echo "==================================================================="
        } > "$result_dir/tcp_stream_$stream.txt" 2>/dev/null
        {
            tshark -r "$file" -q -z follow,tcp,ascii,$stream 2>/dev/null | sed -n '/==/,/Node 1:/p' 2>/dev/null
            echo -e "\n$stream_output"
            echo "==================================================================="
        } | jq -R -s '{stream: .}' > "$result_dir/tcp_stream_$stream.json" 2>/dev/null
        [ "$verbose" = true ] && echo "TCP stream $stream saved to $result_dir/tcp_stream_$stream.txt (ASCII) and $result_dir/tcp_stream_$stream.json (JSON)"
    done
    echo -e "\nFollowing TCP streams:" >> "$result_dir/results.txt"
    echo "TCP streams saved to individual files in $result_dir (ASCII and JSON formats)" >> "$result_dir/results.txt"
    
    # Following UDP streams
    [ "$verbose" = true ] && echo -e "Following UDP streams:"
    udp_streams=$(tshark -r "$file" -Y "udp" -T fields -e udp.stream 2>/dev/null | sort -n 2>/dev/null | uniq 2>/dev/null)
    for stream in $udp_streams; do
        stream_output=$(tshark -r "$file" -q -z follow,udp,ascii,$stream 2>/dev/null | sed '/===================================================================/d' 2>/dev/null | sed '1,5d' 2>/dev/null | tr -d '\n' 2>/dev/null | sed 's/1//g' 2>/dev/null)
        {
            tshark -r "$file" -q -z follow,udp,ascii,$stream 2>/dev/null | sed -n '/==/,/Node 1:/p' 2>/dev/null
            echo -e "\n$stream_output"
            echo "==================================================================="
        } > "$result_dir/udp_stream_$stream.txt" 2>/dev/null
        {
            tshark -r "$file" -q -z follow,udp,ascii,$stream 2>/dev/null | sed -n '/==/,/Node 1:/p' 2>/dev/null
            echo -e "\n$stream_output"
            echo "==================================================================="
        } | jq -R -s '{stream: .}' > "$result_dir/udp_stream_$stream.json" 2>/dev/null
        [ "$verbose" = true ] && echo "UDP stream $stream saved to $result_dir/udp_stream_$stream.txt (ASCII) and $result_dir/udp_stream_$stream.json (JSON)"
    done
    echo -e "\nFollowing UDP streams:" >> "$result_dir/results.txt"
    echo "UDP streams saved to individual files in $result_dir (ASCII and JSON formats)" >> "$result_dir/results.txt"
}

verbose=false
if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
    verbose=true
    shift
elif [ "${!#}" = "-v" ] || [ "${!#}" = "--verbose" ]; then
    verbose=true
    unset "$#"
fi

analyze_pcap "$1" "$2" "$verbose"