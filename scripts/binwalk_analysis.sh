#!/bin/bash

analyze_binwalk() {
    file="$1"
    result_dir="$2"
    verbose="$3"

    # Error handling
    error_file="$result_dir/errors.txt"

    binwalk_output=$(binwalk -e -M -C "$result_dir" "$file" 2> "$error_file")
    [ "$verbose" = true ] && echo -e "Binwalk Results:\n"
    [ "$verbose" = true ] && echo -e "$binwalk_output"
    echo -e "\nbinwalk results:" >> "$result_dir/results.txt"
    echo "$binwalk_output" >> "$result_dir/results.txt"
}

verbose=false
if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
    verbose=true
    shift
elif [ "${!#}" = "-v" ] || [ "${!#}" = "--verbose" ]; then
    verbose=true
    unset "$#"
fi

analyze_binwalk "$1" "$2" "$verbose"