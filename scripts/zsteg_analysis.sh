#!/bin/bash

analyze_zsteg() {
    file="$1"
    result_dir="$2"
    verbose="$3"

    # Error handling
    error_file="$result_dir/errors.txt"
    exec 2> "$error_file"

    zsteg_output=$(zsteg "$file" | grep -E "extradata|text|UTF-8")
    [ "$verbose" = true ] && echo -e "zsteg results:\n"
    [ "$verbose" = true ] && echo -e "$zsteg_output"    
    echo -e "\nzsteg results:" >> "$result_dir/ZSTEG.txt"
    echo "$zsteg_output" >> "$result_dir/ZSTEG.txt"
}

verbose=false
if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
    verbose=true
    shift
elif [ "${!#}" = "-v" ] || [ "${!#}" = "--verbose" ]; then
    verbose=true
    unset "$#"
fi

analyze_zsteg "$1" "$2" "$verbose"