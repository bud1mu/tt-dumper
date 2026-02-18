# tt-dumper 

**tt-dumper** is a lightning-fast, multi-threaded CLI tool written in Python to extract video metadata and scrape comments from TikTok videos without requiring a login or session token !.

## ⚡ Performance

Scraped **~12,000 comments** in just **7.5 seconds**!

```text
  __  __         __                       
 / /_/ /________/ /_ ____ _  ___  ___ ____
/ __/ __/___/ _  / // /  ' \/ _ \/ -_) __/
\__/\__/    \_,_/\_,_/_/_/_/ .__/\__/_/   
                          /_/             
                         @bud1mu 

  [*] Fetching metadata...
  ____________________________________________________________
  :: URL        : [https://tiktok.com/@detikcom/video/7601404250039553301](https://tiktok.com/@detikcom/video/7601404250039553301)
  :: Author     : detik.com (@detikcom)
  :: Likes      : 219600
  :: Comments   : 14100 (Total Available)
  :: Posted     : 2026-01-31 06:10:51
  ____________________________________________________________

  [+] Starting multithreaded dump for approx 14100 comments...
  [+] Progress: 12229 comments retrieved... (100.0%)
  [+] Done! Extracted 12229 comments in 7.51 seconds.
```

## 🚀 Features

- **⚡ Multi-threaded Scraping**: Fetches multiple comment batches simultaneously for maximum speed.
- **📊 Comprehensive Metadata**: Extracts video stats (Views, Likes, Comments, Shares), Author info, and Upload Date.
- **📂 Multiple Formats**: Supports exporting data to **JSON**, **CSV**, or **TXT**.
- **🛡️ Robust & Safe**: Includes error handling, session management, and retries to prevent crashes during extraction.
- **🔓 No Login Required**: Works with public video URLs.

## 📋 Requirements

- Python3

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bud1mu/tt-dumper.git
   cd tt-dumper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

Run the script using Python. The only required argument is `-u` (URL).

### 1. Basic Usage (Default to .txt)
Extract comments to a text file named `output.txt`.
```bash
python tt-dumper.py -u "https://www.tiktok.com/@user/video/1234567890"
```

### 2. Export to JSON (Recommended)
Best for developers who want to parse the data later.
```bash
python tt-dumper.py -u "https://www.tiktok.com/@user/video/1234567890" -f json -o result.json
```

### 3. Export to CSV
Best for data analysis (Excel, Google Sheets).
```bash
python tt-dumper.py -u "https://www.tiktok.com/@user/video/1234567890" -f csv -o data.csv
```

### 4. Limit Number of Comments
Only fetch the first 100 comments (useful for testing).
```bash
python tt-dumper.py -u "https://www.tiktok.com/@user/video/1234567890" -c 100
```

---

## ⚙️ Arguments / Options

| Flag | Long Flag | Required | Description | Default |
| :--- | :--- | :---: | :--- | :--- |
| `-u` | `--url` | ✅ | The TikTok video URL to scrape. | N/A |
| `-o` | `--output` | ❌ | Filename for the output result. | `output.txt` |
| `-f` | `--file-type` | ❌ | Format of the output file (`json`, `csv`, `txt`). | `txt` |
| `-c` | `--comment` | ❌ | Limit the number of comments to retrieve. | All |

---

## 📄 Output Structure

### JSON Example
If you choose `-f json`, the output will look like this:

```json
{
    "metadata": {
        "id": "740...",
        "desc": "Video Description here...",
        "createTime": "2024-02-17 10:00:00",
        "author_id": "unique_id",
        "author_name": "Nickname",
        "stats": {
            "likes": 15000,
            "comments": 300,
            "shares": 500,
            "views": 200000
        },
        "duration": "0:00:59"
    },
    "comments_count": 300,
    "comments": [
        {
            "username": "user123",
            "comment": "This is an amazing video!"
        },
        {
            "username": "fan_account",
            "comment": "First comment!"
        }
    ]
}
```