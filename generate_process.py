import os
import time
import subprocess

from text_to_audio import text_to_speech_file

def text_to_audio(folder):
    print("TTA -", folder)
    desc_path = f"user_uploads/{folder}/desc.txt"
    
    if not os.path.exists(desc_path):
        raise FileNotFoundError(
            f"❌ Missing {desc_path}\n"
            f"Each upload folder must include:\n"
            f"  - desc.txt (narration text)\n"
            f"  - input.txt (image list)\n"
            f"  - images (jpg/png)"
        )
    
    with open(desc_path, encoding="utf-8") as f:
        text = f.read().strip()
    
    if not text:
        raise ValueError(f"❌ desc.txt in {folder} is empty!")
    
    print("Description:", text)
    text_to_speech_file(text, folder)  
    

def create_reel(folder):
    os.makedirs("static/reels", exist_ok=True)

    output_file = f"static/reels/{folder}.mp4"  

    command = f'''ffmpeg -y -f concat -safe 0 -i user_uploads/{folder}/input.txt \
    -i user_uploads/{folder}/audio.mp3 \
    -vf "scale=1080:1920:force_original_aspect_ratio=decrease,\
    pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
    -c:v libx264 -c:a aac -shortest -r 30 -pix_fmt yuv420p {output_file}'''

    print("Running FFmpeg for", folder)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print("FFmpeg failed:", result.stderr)
        raise RuntimeError(f"FFmpeg failed for {folder}")

    print("✅ Created reel:", output_file)


if __name__ == "__main__":
    while True:
        print("processing queue...")

        if os.path.exists("done.txt"):
            with open("done.txt", "r") as f:
                done_folders = [line.strip() for line in f.readlines()]
        else:
            done_folders = []

        upload_folders = os.listdir("user_uploads")

        for folder in upload_folders:
            if folder not in done_folders:
                try:
                    text_to_audio(folder)
                    create_reel(folder)
                    with open("done.txt", "a") as f:
                        f.write(folder + "\n")
                except Exception as e:
                    print(f"Error processing {folder}: {e}")

        time.sleep(30)
