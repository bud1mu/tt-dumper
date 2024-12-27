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
                        
                         @bud1mu
''')

def convert(n):
    return str(datetime.timedelta(seconds = n))

# PARSING ARGUMENT
parser = argparse.ArgumentParser(description="Extract metadata and comments from a TikTok video.")
parser.add_argument('-u', '--url', type=str, required=True, help="Specify the TikTok video URL.")
parser.add_argument('-o', '--output', type=str, default='output.txt', help="Define the name of the output file.")
parser.add_argument('-c', '--comment', type=int, help="Set the number of comments to retrieve.")
parser.add_argument('-f', '--file-type', type=str, help="Specify the format of the output file: json, csv, or txt.")
args = parser.parse_args()


# LIST ARGUMENT
URL=args.url
OUTPUT=args.output
LEN_COMMENT=args.comment
FILE_TYPE=args.file_type

METADATA={}
METADATA['metadata']={}
METADATA["comments"]=[]

HEADERS = {
    'Host': 'www.tiktok.com',
    'Cache-Control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Priority': 'u=0, i'
}

MATCH=RE.search(r"(\d+)$", URL)
if MATCH:
    METADATA["metadata"]["idVideo"]=MATCH.group(1)
else:
    print('  [!] Video ID Not Found ')
    exit()

FIRST_URL=f'https://www.tiktok.com/@tiktok/video/{METADATA["metadata"]["idVideo"]}'

FIRST_RESPONSE=REQUEST.get(
    FIRST_URL,
    headers=HEADERS,
    allow_redirects=True,
    verify=False,
)

if FIRST_RESPONSE.status_code == 200:
    HTML_CONTENT=FIRST_RESPONSE.text

    MATCH=RE.search(r'<script\s+id="__UNIVERSAL_DATA_FOR_REHYDRATION__"\s+type="application/json">(.*?)</script>', HTML_CONTENT)
    if MATCH:
        JSON_DATA=MATCH.group(1)
        JSON_DATA= JSON.loads(JSON_DATA)
    else:
        print("  [!] 'JSON_DATA' Not Found")
    
    # ===================== idVideo =======================
    VIDEO_ID=JSON_DATA["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["id"]
    if VIDEO_ID:
        METADATA["metadata"]["idVideo"]=VIDEO_ID
    else:
        print('  [!] Video ID Not Found ')
        exit()

    # ==================== uniqueId ==========================
    GET_UNIQ_ID=JSON_DATA["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["author"]["uniqueId"]
    if GET_UNIQ_ID:
        METADATA["metadata"]["uniqueId"]=GET_UNIQ_ID
    else:
        print("  [!] 'uniqueId' Not Found")
        exit()

    # ==================== nickname ==================  ========
    GET_NICKNAME=JSON_DATA["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["author"]["nickname"]
    if GET_NICKNAME:
        METADATA["metadata"]["nickname"]=GET_NICKNAME
    else:
        print("  [!] 'nickname' Not Found")
        exit()
        
    # ==================== descVideo ==========================
    GET_DESC=JSON_DATA["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["desc"]
    if GET_DESC:
        METADATA["metadata"]["description"]=GET_DESC
    else:
        print("  [!] 'desc' Not Found")
        exit

    # ==================== diggCount ==========================
    GET_LIKE=JSON_DATA["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["stats"]["diggCount"]
    if GET_LIKE:
        METADATA["metadata"]["totalLike"]=GET_LIKE
    else:
        print("  [!] 'diggCount' Not Found")
        exit()

    # ==================== commentCount ==========================
    GET_COMMENT=JSON_DATA["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["stats"]["commentCount"]
    if GET_COMMENT:
        METADATA["metadata"]["totalComment"]=GET_COMMENT
    else:
        print("  [!] 'commentCount' Not Found")
        exit()
    
    # ==================== shareCount ==========================
    GET_SHARE=JSON_DATA["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["stats"]["shareCount"]
    if GET_SHARE:
        METADATA["metadata"]["totalShare"]=GET_SHARE
    else:
        print("  [!] 'shareCount' Not Found")
        exit()
    
    # ==================== createTime ==========================
    GET_TIME=JSON_DATA["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["createTime"]
    if GET_TIME:
        TIME_POST=GET_TIME
        METADATA["metadata"]["createTime"]=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(TIME_POST)))
    else:
        print("  [!] 'createTime' Not Found")
        exit()

    # ==================== duration ==========================
    GET_DURATION=JSON_DATA["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["video"]["duration"]
    if GET_DURATION:
        DURATION=GET_DURATION
        METADATA["metadata"]["duration"]=convert(int(DURATION)) 
    else:
        print("  [!] 'duration' Not Found")
        exit()
     
    print('________________________________________________________________________\n')
    print(f"  :: URL : {URL}\n  :: Total Like : {METADATA['metadata']['totalLike']}\n  :: Total Comments : {METADATA['metadata']['totalComment']}\n  :: Total Share : {METADATA['metadata']['totalShare']}\n  :: Duration : {METADATA['metadata']['duration']}\n  :: Posted at : {METADATA['metadata']['createTime']}")
    print('________________________________________________________________________\n')
    #kemarin error disini, f"metadata"metadata"" / bagian double quote sama single quote nya

    try:
        cwd = os.getcwd()  
        for CURSOR in range(0, int(METADATA["metadata"]["totalComment"]), 50):
            API_URL = f'https://www.tiktok.com/api/comment/list/?aid=1988&app_language=en&app_name=tiktok_web&aweme_id={METADATA["metadata"]["idVideo"]}&count=50&cursor={CURSOR}&os=windows&region=ID&screen_height=768&screen_width=1366&user_is_login=false'
            
            SEC_RESPONSE=REQUEST.get(API_URL, headers=HEADERS, verify=False)
            DATA=JSON.loads(SEC_RESPONSE.text)

            sleep(1)
            if DATA["has_more"] == 0:
                break
            if LEN_COMMENT == len(METADATA["comments"]):
                break
            for COUNT in range(0, 55):
                try:
                    USERNAME=DATA["comments"][COUNT]["user"]["nickname"]
                    COMMENT=DATA["comments"][COUNT]["text"]
                    METADATA["comments"].append({"username":USERNAME, "comment":COMMENT})
                    print(f"  :: Progress: [{len(METADATA["comments"])}/{METADATA["metadata"]["totalComment"]}]", end='\r') 
                    if LEN_COMMENT == len(METADATA["comments"]):
                        break
                except IndexError:
                    pass
      
        if FILE_TYPE == 'json':
            with open(OUTPUT, 'w', encoding="utf-8") as file:
                JSON.dump({"metadata": METADATA['metadata'],"comments": METADATA['comments']}, file, ensure_ascii=False, indent=4)

        elif FILE_TYPE == 'csv':
            with open(OUTPUT, 'w', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["username", "comment"])
                for comment in METADATA['comments']:
                    writer.writerow([comment["username"], comment["comment"]])
        
        elif FILE_TYPE == 'txt':
            with open(OUTPUT, 'w', encoding="utf-8") as file:
                for comment in METADATA['comments']:
                    file.write(f"{comment['username']}: {comment['comment']}\n")

        print(fr"  [+] Result | Saved in {cwd}\{OUTPUT}                                      ", end="\r")
        print(f'\n\n     | Total Comments : {METADATA["metadata"]["totalComment"]}\n',
        f'    | Received Comments : {len(METADATA["comments"])}\n')
    except KeyboardInterrupt:
        print(fr"  [+] Result | Saved in {cwd}\{OUTPUT}                                      ", end="\r")
        print(f'\n\n     | Total Comments : {METADATA["metadata"]["totalComment"]}\n',
        f'    | Received Comments : {len(METADATA["comments"])}\n')
        print('  [!] Keyboard Interrupt by User/ Bye')
else:
    print(f"Gagal mengambil halaman, Status Code: {FIRST_RESPONSE.status_code}")
