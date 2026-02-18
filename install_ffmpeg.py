
# Download ffmpeg (essential for audio conversion)
import os
import urllib.request
import zipfile

def install_ffmpeg():
    if os.path.exists("ffmpeg.exe"):
        print("ffmpeg already exists.")
        return

    print("Downloading ffmpeg (essential for web audio)...")
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = "ffmpeg.zip"
    
    urllib.request.urlretrieve(url, zip_path)
    
    print("Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(".")
        
    # Move exe to current folder
    for root, dirs, files in os.walk("."):
        if "ffmpeg.exe" in files:
            source = os.path.join(root, "ffmpeg.exe")
            os.rename(source, "ffmpeg.exe")
            break
            
    print("ffmpeg installed locally.")

if __name__ == "__main__":
    install_ffmpeg()
