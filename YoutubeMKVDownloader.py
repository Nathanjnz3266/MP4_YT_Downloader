import subprocess
import os
import shutil

def list_formats(url):
    subprocess.run(['yt-dlp', '-F', url])

def try_download(url, format_selector, filename_template):
    try:
        completed = subprocess.run([
            'yt-dlp',
            '-f', format_selector,
            '--merge-output-format', 'mkv',  # เปลี่ยนเป็น mkv เพื่อรองรับ codec หลากหลาย
            '-k',  # เก็บไฟล์แยกไว้ ไม่ลบอัตโนมัติ
            '-o', filename_template,
            url
        ], check=True, capture_output=True, text=True)

        print(completed.stdout)
        print(completed.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error occurred:\n{e.stderr}")
        return False

def download_1080p60fps(url, output_path='.'):
    filename_template = os.path.join(output_path, '%(title)s.%(ext)s')
    print("▶ Downloading 1080p60fps (merged video+audio)...")
    fmt = 'bestvideo[height=1080][fps=60]+bestaudio/best[height=1080][fps=60]'
    if try_download(url, fmt, filename_template):
        print("✅ Downloaded 1080p60fps merged video+audio.")
        return True
    else:
        print("❌ 1080p60fps format not available.")
        return False

def download_progressive_1080p_or_720p(url, output_path='.'):
    filename_template = os.path.join(output_path, '%(title)s.%(ext)s')
    print("▶ Downloading best progressive format (1080p or 720p, single file)...")
    fmt_1080p = 'best[ext=mp4][height<=1080]'
    if try_download(url, fmt_1080p, filename_template):
        print("✅ Downloaded progressive video up to 1080p.")
        return True

    print("🔁 1080p not available. Trying 720p progressive...")
    fmt_720p = 'best[ext=mp4][height<=720]'
    if try_download(url, fmt_720p, filename_template):
        print("✅ Downloaded progressive video up to 720p.")
        return True

    print("❌ No suitable progressive format found.")
    return False

def manual_download(url, output_path='.'):
    list_formats(url)
    video_code = input("🎥 Enter VIDEO format code (e.g. 248): ").strip()
    audio_code = input("🔊 Enter AUDIO format code (e.g. 251): ").strip()
    fmt = f"{video_code}+{audio_code}"
    filename_template = os.path.join(output_path, '%(title)s.%(ext)s')
    if try_download(url, fmt, filename_template):
        print("✅ Downloaded manual format successfully.")
        return True
    else:
        print("❌ Download manual format failed.")
        return False

def main():
    if not shutil.which("ffmpeg"):
        print("⚠️ ffmpeg not found! Please install ffmpeg and add it to your PATH.")
        return

    url = input("📺 Enter YouTube video URL: ").strip()
    print("\nChoose download option:")
    print("1: 1080p60fps (separate streams merged automatically)")
    print("2: Progressive download (1080p or 720p single file)")
    print("3: Manual format selection (choose format codes yourself)")
    choice = input("Enter 1, 2 or 3: ").strip()

    if choice == '1':
        success = download_1080p60fps(url)
        if not success:
            print("Falling back to progressive download (1080p/720p)...")
            download_progressive_1080p_or_720p(url)
    elif choice == '2':
        success = download_progressive_1080p_or_720p(url)
        if not success:
            print("Try option 1 for 1080p60fps separate streams.")
    elif choice == '3':
        manual_download(url)
    else:
        print("Invalid choice. Exiting.")

if __name__ == '__main__':
    main()
