import requests
import json
import argparse
import time
import datetime
import csv
import os
import re
import sys
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BANNER = r'''
  __  __         __                       
 / /_/ /________/ /_ ____ _  ___  ___ ____
/ __/ __/___/ _  / // /  ' \/ _ \/ -_) __/
\__/\__/    \_,_/\_,_/_/_/_/ .__/\__/_/
                          /_/             
                         @bud1mu 
'''

class TikTokDumper:
    def __init__(self, url, output, limit=None, file_type='txt'):
        self.url = url
        self.output = output
        self.limit = limit  
        self.file_type = file_type
        self.metadata = {}
        self.comments = []
        self.video_id = ""
        self.session = requests.Session()
        self.lock = Lock() 

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.session.headers.update(self.headers)

    def convert_duration(self, seconds):
        return str(datetime.timedelta(seconds=seconds))

    def extract_video_id(self):
        """Ekstrak ID Video dari URL dengan Regex yang lebih aman."""
        match = re.search(r'/video/(\d+)', self.url)
        if match:
            self.video_id = match.group(1)
            return True
        return False

    def fetch_metadata(self):
        """Mengambil Metadata Video dari HTML."""
        print("  [*] Fetching metadata...")
        try:
            clean_url = f'https://www.tiktok.com/@tiktok/video/{self.video_id}'
            response = self.session.get(clean_url, verify=False, timeout=10)
            
            if response.status_code != 200:
                print(f"  [!] Failed to connect. Status: {response.status_code}")
                return False

            match = re.search(r'<script\s+id="__UNIVERSAL_DATA_FOR_REHYDRATION__"\s+type="application/json">(.*?)</script>', response.text)
            
            if not match:
                 match = re.search(r'<script id="SIGI_STATE" type="application/json">(.*?)</script>', response.text)

            if not match:
                print("  [!] Failed to extract JSON data from HTML.")
                return False

            data = json.loads(match.group(1))
            
            try:
                default_scope = data.get("__DEFAULT_SCOPE__", {})
                item_struct = default_scope.get("webapp.video-detail", {}).get("itemInfo", {}).get("itemStruct", {})
                
                if not item_struct:
                     pass

                self.metadata = {
                    "id": item_struct.get("id"),
                    "desc": item_struct.get("desc"),
                    "createTime": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(item_struct.get("createTime", 0)))),
                    "author_id": item_struct.get("author", {}).get("uniqueId"),
                    "author_name": item_struct.get("author", {}).get("nickname"),
                    "stats": {
                        "likes": item_struct.get("stats", {}).get("diggCount"),
                        "comments": item_struct.get("stats", {}).get("commentCount"),
                        "shares": item_struct.get("stats", {}).get("shareCount"),
                        "views": item_struct.get("stats", {}).get("playCount")
                    },
                    "duration": self.convert_duration(int(item_struct.get("video", {}).get("duration", 0)))
                }
                
                if not self.metadata["id"]:
                    raise ValueError("Empty ID parsed")
                    
                return True

            except Exception as e:
                print(f"  [!] Error parsing JSON path: {e}")
                return False

        except Exception as e:
            print(f"  [!] Error fetching metadata: {e}")
            return False

    def fetch_comment_batch(self, cursor, count=50):
        """Worker function untuk mengambil satu batch komentar."""
        try:
            params = {
                'aid': '1988',
                'app_language': 'en',
                'app_name': 'tiktok_web',
                'aweme_id': self.video_id,
                'count': count,
                'cursor': cursor,
                'os': 'windows',
                'region': 'ID',
                'screen_height': '768',
                'screen_width': '1366'
            }
            url = "https://www.tiktok.com/api/comment/list/"
            
            response = self.session.get(url, params=params, verify=False, timeout=10)
            data = response.json()
            
            comments_extracted = []
            if "comments" in data and isinstance(data["comments"], list):
                for c in data["comments"]:
                    username = c.get("user", {}).get("nickname", "Unknown")
                    text = c.get("text", "")
                    comments_extracted.append({"username": username, "comment": text})
            
            return comments_extracted

        except Exception as e:
            return []

    def run(self):
        print(BANNER)
        
        if not self.extract_video_id():
            print("  [!] Invalid TikTok URL.")
            return

        if not self.fetch_metadata():
            print("  [!] Cannot proceed without metadata.")
            return

        print('  ' + '_' * 60)
        print(f"\n  :: URL        : https://tiktok.com/@{self.metadata['author_id']}/video/{self.metadata['id']}")
        print(f"  :: Author     : {self.metadata['author_name']} (@{self.metadata['author_id']})")
        print(f"  :: Likes      : {self.metadata['stats']['likes']}")
        print(f"  :: Comments   : {self.metadata['stats']['comments']} (Total Available)")
        print(f"  :: Posted     : {self.metadata['createTime']}")
        print('  ' + '_' * 60 + '\n')

        total_comments_available = int(self.metadata['stats']['comments'])
        
        target_count = total_comments_available
        if self.limit and self.limit < total_comments_available:
            target_count = self.limit
        
        print(f"  [+] Starting multithreaded dump for approx {target_count} comments...")

        batch_size = 50
        cursors = range(0, target_count, batch_size)
        
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_cursor = {executor.submit(self.fetch_comment_batch, c, batch_size): c for c in cursors}
            
            processed = 0
            for future in as_completed(future_to_cursor):
                batch_data = future.result()
                if batch_data:
                    self.comments.extend(batch_data)
                
                processed += batch_size
                
                percent = min(100, (processed / target_count) * 100)
                sys.stdout.write(f"\r  [+] Progress: {len(self.comments)} comments retrieved... ({percent:.1f}%)")
                sys.stdout.flush()

                if self.limit and len(self.comments) >= self.limit:
                    break

        print(f"\n  [+] Done! Extracted {len(self.comments)} comments in {round(time.time() - start_time, 2)} seconds.")

        self.save_data()

    def save_data(self):
        cwd = os.getcwd()
        filepath = os.path.join(cwd, self.output)
        
        if self.limit:
            final_data = self.comments[:self.limit]
        else:
            final_data = self.comments

        try:
            if self.file_type == 'json':
                output_data = {
                    "metadata": self.metadata,
                    "comments_count": len(final_data),
                    "comments": final_data
                }
                with open(filepath, 'w', encoding="utf-8") as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=4)

            elif self.file_type == 'csv':
                with open(filepath, 'w', newline='', encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["username", "comment"])
                    for item in final_data:
                        writer.writerow([item["username"], item["comment"]])

            else: # txt
                with open(filepath, 'w', encoding="utf-8") as f:
                    f.write(f"Source: {self.url}\n")
                    f.write(f"Total Extracted: {len(final_data)}\n")
                    f.write("-" * 50 + "\n")
                    for item in final_data:
                        f.write(f"{item['username']}: {item['comment']}\n")

            print(f"  [+] Saved successfully to: {filepath}")

        except Exception as e:
            print(f"\n  [!] Error saving file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="High Performance TikTok Comment Dumper")
    parser.add_argument('-u', '--url', type=str, required=True, help="TikTok Video URL")
    parser.add_argument('-o', '--output', type=str, default='output.txt', help="Output filename")
    parser.add_argument('-c', '--comment', type=int, help="Limit number of comments (optional)")
    parser.add_argument('-f', '--file-type', type=str, default='txt', choices=['json', 'csv', 'txt'], help="Output format")
    
    args = parser.parse_args()

    dumper = TikTokDumper(args.url, args.output, args.comment, args.file_type)
    dumper.run()