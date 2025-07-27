import subprocess
import os
import shutil
import sys #SSS

def run_command(cmd):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error:", result.stderr)
        return None
    return result.stdout.strip()

def get_filename(url, format_selector, output_template='%(title)s.%(ext)s'):
    cmd = ['yt-dlp', '--get-filename', '-f', format_selector, '-o', output_template, url]
    filename = run_command(cmd)
    if filename:
        print(f"Filename for format '{format_selector}': {filename}")
    else:
        print(f"Failed to get filename for format '{format_selector}'")
    return filename

def get_video_title(url):
    cmd = ['yt-dlp', '--get-title', url]
    title = run_command(cmd)
    if title:
        print(f"Video title: {title}")
    else:
        print("Failed to get video title")
    return title or "Unknown Title"

def try_download(url, format_selector, filename_template):
    try:
        completed = subprocess.run([
            'yt-dlp',
            '-f', format_selector,
            '--merge-output-format', 'mp4',
            '-o', filename_template,
            url
        ], check=True, capture_output=True, text=True)
        print(completed.stdout)
        print(completed.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error occurred:\n{e.stderr}")
        return False

def try_download_and_convert(url, output_path=r'C:\Users\lasto\Desktop\MP4_YoutubeDownload'):
    # สร้างโฟลเดอร์ถ้ายังไม่มี
    os.makedirs(output_path, exist_ok=True)

    video_title = get_video_title(url)
    if not video_title:
        print("❌ Cannot get video title.")
        return False

    # ทำความสะอาดชื่อไฟล์
    invalid_chars = '<>:"/\\|?*'
    for ch in invalid_chars:
        video_title = video_title.replace(ch, '_')

    output_template = os.path.join(output_path, video_title)

    video_fmt = 'bestvideo[height<=1080]'
    audio_fmt = 'bestaudio'

    video_filename = get_filename(url, video_fmt, output_template + '_video.%(ext)s')
    audio_filename = get_filename(url, audio_fmt, output_template + '_audio.%(ext)s')

    if not video_filename or not audio_filename:
        print("❌ Cannot get filenames for video or audio")
        return False

    if not try_download(url, video_fmt, output_template + '_video.%(ext)s'):
        print("❌ Video download failed")
        return False

    if not try_download(url, audio_fmt, output_template + '_audio.%(ext)s'):
        print("❌ Audio download failed")
        return False

    if not os.path.isfile(video_filename) or not os.path.isfile(audio_filename):
        print("❌ Downloaded files not found:")
        print("Video:", video_filename)
        print("Audio:", audio_filename)
        return False

    output_file = output_template + '.mp4'

    cmd_merge = [
        'ffmpeg',
        '-y',
        '-i', video_filename,
        '-i', audio_filename,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-preset', 'fast',
        '-movflags', '+faststart',
        '-metadata', f'title={video_title}',
        output_file
    ]

    print(f"Merging and converting to mp4 with title metadata: {output_file}")
    result = subprocess.run(cmd_merge, capture_output=True, text=True)
    if result.returncode != 0:
        print("FFmpeg error:", result.stderr)
        return False

    try:
        os.remove(video_filename)
        os.remove(audio_filename)
    except Exception as e:
        print(f"Warning: could not delete temp files: {e}")

    print(f"✅ Download and merge completed: {output_file}")
    return True


def main():
    if not shutil.which('ffmpeg'):
        print("⚠️ ffmpeg not found! Please install ffmpeg and add it to your PATH.")
        sys.exit(1)

    url = input("📺 Enter YouTube video URL: ").strip()

    print("\nStarting download video + audio and convert to MP4...")
    success = try_download_and_convert(url)

    if not success:
        print("❌ Download failed or formats not available.")

if __name__ == '__main__':
    main()
