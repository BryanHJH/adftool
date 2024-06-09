#!/bin/bash

analyze_outguess() {
    file="$1"
    result_dir="$2"
    verbose="$3"
    
    # Error handling
    error_file="$result_dir/errors.txt"
    exec 2> "$error_file"

    outguess_output=$(outguess -r "$file" /dev/null 2>&1 | grep -v "No data extracted")
    ["$verbose" = true] && echo -e "Outguess results:\n"
    ["$verbose" = true] && echo -e "$outguess_output"
    echo -e "\nOutguess results:" >> "$result_dir/results.txt"
    echo "$outguess_output" >> "$result_dir/results.txt"
}

verbose=false
if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
    verbose=true
    shift
elif [ "${!#}" = "-v" ] || [ "${!#}" = "--verbose" ]; then
    verbose=true
    unset "$#"
fi

analyze_outguess "$1" "$2" "$verbose"