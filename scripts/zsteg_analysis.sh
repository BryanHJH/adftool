#!/bin/bash

analyze_zsteg() {
    file="$1"
    result_dir="$2"
    
    # Error handling
    error_file="$result_dir/errors.txt"
    exec 2> "$error_file"

    zsteg_output=$(zsteg "$file" | grep -E "extradata|text|UTF-8")
    echo -e "\nzsteg results:" >> "$result_dir/results.txt"
    echo "$zsteg_output" >> "$result_dir/results.txt"
}

analyze_zsteg "$1" "$2"