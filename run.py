import os
import subprocess
import sys
import re
from tqdm import tqdm

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("ffmpeg is not installed.")
        sys.exit(1)

def create_directory(input_file):
    directory = os.path.splitext(input_file)[0]
    if not os.path.exists(directory):
        os.makedirs(directory)
    convert_to_m3u8(input_file, directory)
    return input_file, directory

def ffmpeg_progress_bar(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)
    duration = None
    pattern_duration = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2})\.\d{2}")
    pattern_time = re.compile(r"time=(\d{2}):(\d{2}):(\d{2})\.\d{2}")
    while True:
        line = process.stderr.readline()
        if not line:
            break
        if duration is None:
            match = pattern_duration.search(line)
            if match:
                hours, minutes, seconds = map(int, match.groups())
                duration = hours * 3600 + minutes * 60 + seconds
                pbar = tqdm(total=duration, desc="Converting", unit='s')
        match = pattern_time.search(line)
        if match:
            hours, minutes, seconds = map(int, match.groups())
            current_time = hours * 3600 + minutes * 60 + seconds
            pbar.n = current_time
            pbar.refresh()

    process.wait()
    pbar.close()

def convert_to_m3u8(input_file, directory):
    command = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-hls_time", "3",
        "-hls_list_size", "0",
        "-hls_segment_filename", f"{directory}/{directory}-segment_%03d.ts",
        f"{directory}/{os.path.splitext(os.path.basename(input_file))[0]}.m3u8"
    ]
    ffmpeg_progress_bar(command)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run.py input-filename.mp4")
        sys.exit(1)

    input_file = sys.argv[1]
    
    check_ffmpeg()
    
    if not os.path.exists(input_file):
        print("Input file does not exist.")
        sys.exit(1)
    create_directory(input_file)