import os
import sys
import tempfile
import subprocess

def parse_time_string_to_hms(time_str: str) -> str:
    """
    Parses a time string (MM:SS or HH:MM:SS) and formats it as HH:MM:SS.
    Assumes if only two parts, it's MM:SS.
    """
    parts = list(map(int, time_str.split(':')))

    if len(parts) == 2: # MM:SS format
        minutes, seconds = parts
        hours = minutes // 60
        minutes = minutes % 60
    elif len(parts) == 3: # HH:MM:SS format
        hours, minutes, seconds = parts
    else:
        raise ValueError(f"Invalid time string format: {time_str}. Expected MM:SS or HH:MM:SS.")

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def download_segment_yt_dlp(url: str, start_time: str, end_time: str, output_file: str) -> bool:
    """
    Download a specific segment from a video using yt-dlp.
    """
    print(f"Downloading segment from {start_time} to {end_time} using yt-dlp...")
    python_exe = sys.executable
    cmd = [
        python_exe,
        "-m", "yt_dlp",
        "--no-warnings",
        "--force-overwrites",
        "--no-playlist", # Ensure we're not dealing with playlists if URL is part of one
        f"--download-sections", f"*{start_time}-{end_time}",
        "-o", output_file,
        url
    ]

    try:
        process = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Successfully downloaded segment to: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error downloading segment with yt-dlp: {e}")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred with yt-dlp: {e}")
        return False

def download_segment_ffmpeg(url: str, start_time: str, end_time: str, output_file: str) -> bool:
    """
    Download a video segment using youtube-dl (to get full video) and ffmpeg (to cut).
    """
    print(f"Downloading segment from {start_time} to {end_time} using youtube-dl + ffmpeg...")
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, f"full_video_temp_{os.getpid()}.mp4") # Use PID for unique temp file

    # Download full video first
    dl_cmd = [
        sys.executable,
        "-m", "youtube_dl",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", # Prioritize mp4 or best overall
        "-o", temp_file,
        url
    ]

    print("Downloading full video (this might take a while)...")
    try:
        dl_process = subprocess.run(dl_cmd, capture_output=True, text=True, check=True)
        print("Full video downloaded to temporary file.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading full video with youtube-dl: {e}")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during full video download: {e}")
        return False

    # Calculate duration for ffmpeg
    def time_to_seconds_calc(t):
        parts = t.split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        else:
            raise ValueError(f"Invalid time format for calculation: {t}")

    try:
        duration_seconds = time_to_seconds_calc(end_time) - time_to_seconds_calc(start_time)
        if duration_seconds <= 0:
            print(f"Error: End time ({end_time}) must be after start time ({start_time}).")
            return False
    except ValueError as e:
        print(f"Error calculating duration: {e}")
        return False

    # Use ffmpeg to cut the segment
    cut_cmd = [
        "ffmpeg",
        "-i", temp_file,
        "-ss", start_time,
        "-t", str(duration_seconds),
        "-c:v", "copy",
        "-c:a", "copy",
        output_file,
        "-y" # Overwrite output file if it exists
    ]

    print(f"Cutting segment with ffmpeg...")
    try:
        cut_process = subprocess.run(cut_cmd, capture_output=True, text=True, check=True)
        print(f"Successfully saved segment to: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error cutting video with ffmpeg: {e}")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred with ffmpeg: {e}")
        return False
    finally:
        # Clean up the temporary full video file
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"Removed temporary file: {temp_file}")


def main():
    # Determine which downloader to use
    use_yt_dlp = False
    use_youtube_dl_ffmpeg = False

    try:
        import yt_dlp
        use_yt_dlp = True
        print("Using yt-dlp for downloading.")
    except ImportError:
        print("yt-dlp not found. Checking for youtube-dl + ffmpeg fallback...")
        try:
            import youtube_dl
            # Check for ffmpeg
            ffmpeg_check = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
            use_youtube_dl_ffmpeg = True
            print("Using youtube-dl + ffmpeg for downloading.")
        except ImportError:
            print("youtube-dl not found.")
            print("Please install yt-dlp (`pip install yt-dlp`) or youtube-dl (`pip install youtube_dl`) and ensure ffmpeg is in your PATH.")
            sys.exit(1)
        except FileNotFoundError:
            print("ffmpeg command not found.")
            print("Please ensure ffmpeg is installed and its directory is added to your system's PATH.")
            sys.exit(1)
        except subprocess.CalledProcessError:
            print("Failed to run ffmpeg. Please check your ffmpeg installation.")
            sys.exit(1)
    
    if not use_yt_dlp and not use_youtube_dl_ffmpeg:
        print("No suitable video downloader found. Exiting.")
        sys.exit(1)

    # Get URL from user
    video_url = input("Paste the video URL (YouTube, etc.): ").strip()
    if not video_url:
        print("URL cannot be empty. Exiting.")
        sys.exit(1)

    # Get number of sections from user
    try:
        num_sections = int(input("How many sections do you want to download? "))
        if num_sections <= 0:
            print("Number of sections must be positive. Exiting.")
            sys.exit(1)
    except ValueError:
        print("Invalid input for the number of sections. Please enter a number. Exiting.")
        sys.exit(1)

    # Collect start and end times for each section
    sections_to_download = []
    for i in range(1, num_sections + 1):
        print(f"\n--- Section #{i} ---")
        start_time_str = input(f"Enter start time for section #{i} (HH:MM:SS or MM:SS, e.g., 00:12:30 or 1:40:59): ").strip()
        end_time_str = input(f"Enter end time for section #{i} (HH:MM:SS or MM:SS, e.g., 00:12:30 or 1:40:59): ").strip()

        try:
            # Parse and format times to HH:MM:SS
            formatted_start = parse_time_string_to_hms(start_time_str)
            formatted_end = parse_time_string_to_hms(end_time_str)
            sections_to_download.append({"start": formatted_start, "end": formatted_end})
        except ValueError as e:
            print(f"Invalid time format for section #{i}: {e}. This section will be skipped.")
            sections_to_download.append(None) # Mark this section as invalid

    # Process each section
    all_downloads_successful = True
    for idx, section_data in enumerate(sections_to_download):
        if section_data is None:
            print(f"\nSkipping section {idx + 1} due to previous input error.")
            all_downloads_successful = False
            continue

        start = section_data["start"]
        end = section_data["end"]
        # Create a cleaner output filename
        output_filename = f"segment_{idx + 1}_{start.replace(':', '-')}_to_{end.replace(':', '-')}.mp4"

        print(f"\n--- Processing Section {idx + 1} ({start} to {end}) ---")
        if use_yt_dlp:
            success = download_segment_yt_dlp(video_url, start, end, output_filename)
        elif use_youtube_dl_ffmpeg:
            success = download_segment_ffmpeg(video_url, start, end, output_filename)
        else:
            print("Error: No suitable downloader found. This shouldn't happen.")
            success = False # Should be caught earlier, but as a safeguard

        if not success:
            all_downloads_successful = False

    if all_downloads_successful:
        print("\nAll requested video segments have been downloaded successfully!")
    else:
        print("\nSome video segments could not be downloaded due to errors. Please check the console output for details.")

if __name__ == "__main__":
    main()