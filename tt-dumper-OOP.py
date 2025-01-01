import requests as REQUEST
import json as JSON
import argparse
from time import sleep
import datetime
import time
import csv
import os
import re as RE
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ASCII Art
print(r'''
  __  __         __                       
 / /_/ /________/ /_ ____ _  ___  ___ ____
/ __/ __/___/ _  / // /  ' \/ _ \/ -_) __/
\__/\__/    \_,_/\_,_/_/_/_/ .__/\__/_/   
                          /_/             
        With Object Oriented Programming
                         @bud1mu
''')

class TikTokExtractor:
    def __init__(self, url, output='output.json', comment_count=None, file_type='json'):
        self.url = url
        self.output = output
        self.comment_count = comment_count
        self.file_type = file_type
        self.metadata = {
            'metadata': {},
            'comments': []
        }
        self.headers = {
            'Host': 'www.tiktok.com',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Priority': 'u=0, i'
        }

    @staticmethod
    def convert(n):
        return str(datetime.timedelta(seconds=n))

    def extract_metadata(self):
        match = RE.search(r"(\d+)$", self.url)
        if not match:
            raise ValueError("Video ID Not Found")

        self.metadata["metadata"]["idVideo"] = match.group(1)
        first_url = f'https://www.tiktok.com/@tiktok/video/{self.metadata["metadata"]["idVideo"]}'

        response = REQUEST.get(first_url, headers=self.headers, allow_redirects=True, verify=False)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch page, Status Code: {response.status_code}")

        html_content = response.text
        match = RE.search(r'<script\s+id="__UNIVERSAL_DATA_FOR_REHYDRATION__"\s+type="application/json">(.*?)</script>', html_content)
        if not match:
            raise ValueError("JSON Data Not Found")

        json_data = JSON.loads(match.group(1))
        video_data = json_data["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]

        self.metadata["metadata"].update({
            "idVideo": video_data.get("id"),
            "uniqueId": video_data["author"].get("uniqueId"),
            "nickname": video_data["author"].get("nickname"),
            "description": video_data.get("desc"),
            "totalLike": video_data["stats"].get("diggCount"),
            "totalComment": video_data["stats"].get("commentCount"),
            "totalShare": video_data["stats"].get("shareCount"),
            "createTime": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(video_data.get("createTime", 0)))),
            "duration": self.convert(int(video_data["video"].get("duration", 0)))
        })

    def extract_comments(self):
        total_comments = self.metadata["metadata"].get("totalComment", 0)
        for cursor in range(0, total_comments, 50):
            api_url = f'https://www.tiktok.com/api/comment/list/?aid=1988&app_language=en&app_name=tiktok_web&aweme_id={self.metadata["metadata"]["idVideo"]}&count=50&cursor={cursor}&os=windows&region=ID&screen_height=768&screen_width=1366&user_is_login=false'

            response = REQUEST.get(api_url, headers=self.headers, verify=False)
            data = JSON.loads(response.text)

            sleep(1)
            if data.get("has_more") == 0 or (self.comment_count and len(self.metadata["comments"]) >= self.comment_count):
                break

            for comment in data.get("comments", []):
                username = comment["user"].get("nickname")
                text = comment.get("text")
                if username and text:
                    self.metadata["comments"].append({"username": username, "comment": text})

    def save_to_file(self):
        if self.file_type == 'json':
            with open(self.output, 'w', encoding="utf-8") as file:
                JSON.dump(self.metadata, file, ensure_ascii=False, indent=4)
        elif self.file_type == 'csv':
            with open(self.output, 'w', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["username", "comment"])
                for comment in self.metadata['comments']:
                    writer.writerow([comment["username"], comment["comment"]])
        elif self.file_type == 'txt':
            with open(self.output, 'w', encoding="utf-8") as file:
                for comment in self.metadata['comments']:
                    file.write(f"{comment['username']}: {comment['comment']}\n")
                    file.write(" ")
        else:
            raise ValueError("Unsupported file type")

    def run(self):
        self.extract_metadata()
        self.extract_comments()
        self.save_to_file()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract metadata and comments from a TikTok video.")
    parser.add_argument('-u', '--url', type=str, required=True, help="Specify the TikTok video URL.")
    parser.add_argument('-o', '--output', type=str, default='output.json', help="Define the name of the output file.")
    parser.add_argument('-c', '--comment', type=int, help="Set the number of comments to retrieve.")
    parser.add_argument('-f', '--file-type', type=str, default='json', help="Specify the format of the output file: json, csv, or txt.")
    args = parser.parse_args()

    try:
        extractor = TikTokExtractor(args.url, args.output, args.comment, args.file_type)
        extractor.run()
        print(f"Data successfully saved to {args.output}")
    except Exception as e:
        print(f"Error: {e}")
