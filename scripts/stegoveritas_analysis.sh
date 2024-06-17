#!/bin/bash

analyze_stegoveritas() {
    file="$1"
    result_dir="$2"
    verbose="$3"
    
    # Error handling
    error_file="$result_dir/errors.txt"
    exec 2> "$error_file"
    
    stegoveritas_output=$(stegoveritas -out "$result_dir" "$file")
    [ "$verbose" = true ] && echo -e "Stegoveritas results:\n"
    [ "$verbose" = true ] && echo "$stegoveritas_output"
    echo -e "\nstegoveritas results:" >> "$result_dir/STEGOVERITAS.txt"
    echo "$stegoveritas_output" >> "$result_dir/STEGOVERITAS.txt"
}

verbose=false
if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
    verbose=true
    shift
elif [ "${!#}" = "-v" ] || [ "${!#}" = "--verbose" ]; then
    verbose=true
    unset "$#"
fi

analyze_stegoveritas "$1" "$2" "$verbose"