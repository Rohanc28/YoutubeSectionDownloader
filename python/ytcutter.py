import os
import sys
import tempfile
import subprocess

def download_segment(url, start_time, end_time, output_file):
    """
    Download a specific segment from a YouTube video using yt-dlp via Python module.
    
    Args:
        url: YouTube video URL
        start_time: Start time in format HH:MM:SS
        end_time: End time in format HH:MM:SS
        output_file: Output file name
    """
    try:
        print(f"Downloading segment from {start_time} to {end_time}...")
        
        # Create Python command that uses yt-dlp as a module
        python_exe = sys.executable
        cmd = [
            python_exe,
            "-m", "yt_dlp",
            "--no-warnings",
            "--force-overwrites",
            "--no-playlist",
            f"--download-sections", f"*{start_time}-{end_time}",
            "-o", output_file,
            url
        ]
        
        # Run the command
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        # Check if the command was successful
        if process.returncode == 0:
            print(f"Successfully downloaded segment to: {output_file}")
            return True
        else:
            print(f"Error downloading segment: {process.stderr}")
            # Print stdout too as it might contain useful information
            print(f"Output: {process.stdout}")
            return False
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

# Alternative approach using ffmpeg if yt-dlp fails
def download_with_ffmpeg(url, start_time, end_time, output_file):
    """
    Download a video segment using youtube-dl and ffmpeg
    """
    try:
        # First download the best format with youtube-dl
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"full_video_temp.mp4")
        
        # Use python -m youtube_dl to ensure we're using the installed module
        dl_cmd = [
            sys.executable,
            "-m", "youtube_dl",
            "-f", "best",
            "-o", temp_file,
            url
        ]
        
        print("Downloading full video (this might take a while)...")
        dl_process = subprocess.run(dl_cmd, capture_output=True, text=True)
        
        if dl_process.returncode != 0:
            print(f"Error downloading video: {dl_process.stderr}")
            return False
            
        # Calculate duration for ffmpeg
        def time_to_seconds(t):
            parts = t.split(":")
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            else:
                return int(t)
                
        duration = time_to_seconds(end_time) - time_to_seconds(start_time)
        
        # Use ffmpeg to cut the segment
        cut_cmd = [
            "ffmpeg",
            "-i", temp_file,
            "-ss", start_time,
            "-t", str(duration),
            "-c:v", "copy",
            "-c:a", "copy",
            output_file,
            "-y"
        ]
        
        print(f"Cutting segment from {start_time} to {end_time}...")
        cut_process = subprocess.run(cut_cmd, capture_output=True, text=True)
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        if cut_process.returncode == 0:
            print(f"Successfully saved segment to: {output_file}")
            return True
        else:
            print(f"Error cutting video: {cut_process.stderr}")
            return False
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

# URL for the video
URL = "https://www.youtube.com/live/????"

def main():
    # First check if yt-dlp is installed as a Python package
    try:
        import yt_dlp
        print("yt-dlp is installed as a Python package.")
        use_yt_dlp = True
    except ImportError:
        print("yt-dlp is not installed as a Python package.")
        print("Checking for youtube-dl and ffmpeg as fallback...")
        try:
            import youtube_dl
            # Check for ffmpeg
            ffmpeg_check = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
            if ffmpeg_check.returncode == 0:
                print("Using youtube-dl + ffmpeg as fallback.")
                use_yt_dlp = False
            else:
                print("ffmpeg is not installed. Please install it to use the fallback method.")
                sys.exit(1)
        except ImportError:
            print("Neither yt-dlp nor youtube-dl are installed.")
            print("Please install one with: pip install yt-dlp")
            sys.exit(1)
    
    # Download first segment: ex: 29:50 to 30:50
    print("\n--- Downloading Segment 1 (29:50 to 30:50) ---")
    if use_yt_dlp:
        success1 = download_segment(
            url=URL,
            start_time="00:29:50",  # edit here for timestamps
            end_time="00:30:50",    # edit here for timestamps
            output_file="segment1_29m50s-30m50s.mp4"
        )
    else:
        success1 = download_with_ffmpeg(
            url=URL,
            start_time="00:29:50",  # edit here for timestamps
            end_time="00:30:50",    # edit here for timestamps
            output_file="segment1_29m50s-30m50s.mp4"
        )
    
    # Download second segment: 1:10:00 to 1:10:40
    print("\n--- Downloading Segment 2 (1:10:00 to 1:10:40) ---")
    if use_yt_dlp:
        success2 = download_segment(
            url=URL,
            start_time="01:10:00",  # edit here for timestamps
            end_time="01:10:40",    # edit here for timestamps
            output_file="segment2_1h10m00s-1h10m40s.mp4"
        )
    else:
        success2 = download_with_ffmpeg(
            url=URL,
            start_time="01:10:00",  # edit here for timestamps
            end_time="01:10:40",    # edit here for timestamps
            output_file="segment2_1h10m00s-1h10m40s.mp4"
        )
    
    if success1 and success2:
        print("\nBoth segments downloaded successfully!")
    else:
        print("\nThere were some issues downloading the segments.")
        
if __name__ == "__main__":
    main()