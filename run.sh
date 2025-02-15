#!/bin/bash

check_ffmpeg() {
    if ! command -v ffmpeg &> /dev/null; then
        echo "ffmpeg is not installed."
        exit 1
    fi
}

create_directory() {
    local input_file="$1"
    local directory="${input_file%.*}"
    mkdir -p "$directory"
    convert_to_m3u8 "$input_file" "$directory"
}

progress_bar() {
    local current=$1
    local total=$2
    local length=40
    local percent=$((current * 100 / total))
    local filled_length=$((length * current / total))
    local bar=$(printf '█%.0s' $(seq 1 $filled_length))
    local empty=$(printf '-%.0s' $(seq 1 $((length - filled_length))))
    printf "\r[%s%s] %d%%" "$bar" "$empty" "$percent"
}

ffmpeg_progress_bar() {
    local input_file="$1"
    local output_dir="$2"
    local duration
    
    duration=$(ffmpeg -i "$input_file" 2>&1 | grep "Duration" | awk '{print $2}' | tr -d ,)
    IFS=: read -r hours minutes seconds <<< "$duration"
    total_seconds=$((10#${hours} * 3600 + 10#${minutes} * 60 + 10#${seconds%.*}))
    
    ffmpeg -i "$input_file" -c:v libx264 -c:a aac -hls_time 3 -hls_list_size 0 \
        -hls_segment_filename "$output_dir/${output_dir}-segment_%03d.ts" \
        "$output_dir/${input_file%.*}.m3u8" 2>&1 | \
    while IFS= read -r line; do
        if [[ $line =~ time=([0-9]{2}):([0-9]{2}):([0-9]{2}) ]]; then
            current_time=$((10#${BASH_REMATCH[1]} * 3600 + 10#${BASH_REMATCH[2]} * 60 + 10#${BASH_REMATCH[3]}))
            progress_bar "$current_time" "$total_seconds"
        fi
    done
    echo "\nConversion Complete!"
}

convert_to_m3u8() {
    local input_file="$1"
    local directory="$2"
    ffmpeg_progress_bar "$input_file" "$directory"
}

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 input-filename.mp4"
    exit 1
fi

input_file="$1"

check_ffmpeg

if [[ ! -f "$input_file" ]]; then
    echo "Input file does not exist."
    exit 1
fi

create_directory "$input_file"
