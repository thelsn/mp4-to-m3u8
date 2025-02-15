import os
import subprocess
import sys
import re

def check_ffmpeg():
    if subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        print("ffmpeg is not installed.")
        sys.exit(1)

def create_directory(input_file):
    directory = os.path.splitext(input_file)[0]
    os.makedirs(directory, exist_ok=True)
    convert_to_m3u8(input_file, directory)
    return input_file, directory

def progress_bar(current, total, length=40):
    percent = (current / total) * 100
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r[{bar}] {percent:.2f}%')
    sys.stdout.flush()

def ffmpeg_progress_bar(command):
    process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True, bufsize=1)
    duration = None
    duration_pattern = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2})")
    time_pattern = re.compile(r"time=(\d{2}):(\d{2}):(\d{2})")
    
    for line in process.stderr:
        if not duration:
            match = duration_pattern.search(line)
            if match:
                hours, minutes, seconds = map(int, match.groups())
                duration = hours * 3600 + minutes * 60 + seconds
        
        match = time_pattern.search(line)
        if match:
            hours, minutes, seconds = map(int, match.groups())
            progress_bar(hours * 3600 + minutes * 60 + seconds, duration)
    
    process.wait()
    print("\nConversion Complete!")

def convert_to_m3u8(input_file, directory):
    command = [
        "ffmpeg", "-i", input_file,
        "-c:v", "libx264", "-c:a", "aac",
        "-hls_time", "3", "-hls_list_size", "0",
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
