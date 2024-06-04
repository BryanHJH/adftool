#!/bin/bash

analyze_outguess() {
    file="$1"
    result_dir="$2"
    
    # Error handling
    error_file="$result_dir/errors.txt"
    exec 2> "$error_file"

    outguess_output=$(outguess -r "$file" /dev/null 2>&1 | grep -v "No data extracted")
    echo -e "\nOutguess results:" >> "$result_dir/results.txt"
    echo "$outguess_output" >> "$result_dir/results.txt"
}

analyze_outguess "$1" "$2"