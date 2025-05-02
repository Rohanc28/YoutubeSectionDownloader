# YTCutter

This is a simple script that allows you to download specific segments from YouTube videos. Instead of downloading entire videos, you can specify the exact start and end times for the segments you want.

## Features

- Download specific time segments from any YouTube video
- Automatically uses the best available video quality
- Two download methods:
  - Primary: Using yt-dlp (faster and more reliable)
  - Fallback: Using youtube-dl with ffmpeg (if yt-dlp fails)
- Avoids PATH-related issues by using Python modules directly
- Clean error handling and informative output

## Requirements

- Python 3.6+
- One of the following:
  - yt-dlp (recommended): `pip install yt-dlp`
  - youtube-dl + ffmpeg: `pip install youtube-dl` and install [FFmpeg](https://ffmpeg.org/download.html)

## Installation

1. Clone this repository or download the `ytcutter.py` file
2. Install the required dependencies:
   ```bash
   pip install yt-dlp
   ```
   Or for the fallback method:
   ```bash
   pip install youtube-dl
   ```
   and install FFmpeg according to your operating system

## Usage

1. Open the `ytcutter.py` file in a text editor
2. Edit the `URL` variable to your desired YouTube video:
   ```python
   URL = "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
   ```
3. Edit the timestamps for the segments you want to download:
   ```python
   # For segment 1
   start_time="00:29:50",  # edit here for timestamps
   end_time="00:30:50",    # edit here for timestamps
   
   # For segment 2
   start_time="01:10:00",  # edit here for timestamps
   end_time="01:10:40",    # edit here for timestamps
   ```
4. Run the script:
   ```bash
   python ytcutter.py
   ```

## Example

To download two segments from a video:
- Segment 1: 29:50 to 30:50 (1 minute)
- Segment 2: 1:10:00 to 1:10:40 (40 seconds)

Configure the script as follows:

```python
URL = "https://www.youtube.com/watch?v=VIDEO_ID"

# In the main() function:
# First segment
start_time="00:29:50",
end_time="00:30:50",
output_file="segment1_29m50s-30m50s.mp4"

# Second segment
start_time="01:10:00",
end_time="01:10:40",
output_file="segment2_1h10m00s-1h10m40s.mp4"
```

## Customization

You can easily modify the script to download additional segments or change the output file names by adding more calls to `download_segment()` or `download_with_ffmpeg()` in the `main()` function.

## Troubleshooting

If you encounter issues:

1. Make sure you have the latest version of yt-dlp:
   ```bash
   pip install --upgrade yt-dlp
   ```
2. Try the fallback method with youtube-dl and ffmpeg
3. Check your internet connection
4. Verify that the YouTube video is available in your region

## Why?

Because usual ytdownloader sites were unable to download live streams' sections and videos' clips. Same issue with using py-tube so I used yt-dlp.

## Acknowledgements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp): The main tool used for downloading YouTube videos
- [youtube-dl](https://github.com/ytdl-org/youtube-dl): Fallback downloader
- [FFmpeg](https://ffmpeg.org/): Used for video processing in the fallback method
