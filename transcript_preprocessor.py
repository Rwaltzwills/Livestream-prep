import pprint as pp
import csv
import json
import subprocess
import os
from zipfile import ZipFile
import yt_dlp
from yt_dlp import YoutubeDL

'''
Steps
-----
1. Download highest audio from playlist via yt-dlp
2. Grab JSON from video
3. Process JSON to add to CSV file
4. Zip audio
5. Repeat
'''

class Transcript_Preprocessor:
    playlist_url = ""
    zip_path = ""
    csv_path = ""
    audio_format = ""

    class ZipPP(yt_dlp.postprocessor.PostProcessor):
        # Custom PostProcessor to zip up the audio files as we download each one
        # Prevents a playlist from taking up too much space
        zip_path = ""

        def run(self, info):
            self.to_screen('Zipping ' + info['filepath'])
            Transcript_Preprocessor.zip_up(self.zip_path, info['filepath'])
            
            return [], info


    def __init__(self, playlist_url, zip_path, csv_path, audio_format="m4a"):
        # Check for FFMPEG, needed for audio conversion later on
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            raise Exception("FFMPEG not found. Ending process.")
        
        self.playlist_url = playlist_url
        self.zip_path = zip_path
        self.csv_path = csv_path
        self.audio_format = audio_format

    def run(self):
        json_info = self.download_audio(self.playlist_url)
        self.process_json(json_info, self.csv_path)

    def download_audio(self, url):
        options = {
            "format": self.audio_format,
            'postprocessors': [{  
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.audio_format,
                }],
        }
        with YoutubeDL(options) as ydl:
            ZipPP = self.ZipPP()
            ZipPP.zip_path = self.zip_path
            ydl.add_post_processor(ZipPP)
            info = ydl.extract_info(url, download=True)

        return info

    def process_json(self, json_dict, csv_file):
        entries = json_dict["entries"]

        sample = "" # Sample is used for testing purposes

        with open(csv_file, "a", newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(["title", "url", "upload date"])
            for entry in entries:
                writer.writerow([entry["title"], entry["webpage_url"], entry["upload_date"]])
                
        with open(csv_file, "r") as f: # Can be safely ignored if not running tests
            sample = sample + f.readline()
            sample = sample + f.readline()

        return sample
    
    @staticmethod
    def zip_up(zip_path, zip_target):
        with ZipFile(zip_path, 'a') as zip:
            zip.write(zip_target)
        os.remove(zip_target)



if __name__ == "__main__":
    url = input("Enter YouTube URL: ")
    tp = Transcript_Preprocessor(url,"Results/audioFiles.zip", "Results/livestreamInfo.csv")
    tp.run()