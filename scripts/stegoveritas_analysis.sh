#!/bin/bash

analyze_stegoveritas() {
    file="$1"
    result_dir="$2"
    
    # Error handling
    error_file="$result_dir/errors.txt"
    exec 2> "$error_file"
    
    stegoveritas_output=$(stegoveritas -out "$result_dir" "$file")
    echo -e "\nstegoveritas results:" >> "$result_dir/results.txt"
    echo "$stegoveritas_output" >> "$result_dir/results.txt"
}

analyze_stegoveritas "$1" "$2"