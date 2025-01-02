# TikTok Comment Dumper

A Python tool for extracting metadata and comments from TikTok videos.

## Features

- Extract video metadata (ID, author, description, statistics)
- Download video comments
- Multiple output formats supported (JSON, CSV, TXT)
- Configurable comment limit
- Command-line interface

## Requirements

```
requests
urllib3
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/bud1mu/tt-dumper.git
cd tt-dumper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py -u <tiktok_url> [-o output_file] [-c comment_count] [-f file_type]
```

### Arguments

- `-u, --url`: TikTok video URL (required)
- `-o, --output`: Output filename (default: output.json)
- `-c, --comment`: Number of comments to retrieve (optional)
- `-f, --file-type`: Output format (json/csv/txt, default: json)

### Example

```bash
python main.py -u https://www.tiktok.com/@user/video/1234567890 -o results.csv -c 100 -f csv
```

## Output Format

### JSON
```json
{
    "metadata": {
        "idVideo": "1234567890",
        "uniqueId": "username",
        "nickname": "User Name",
        "description": "Video description",
        "totalLike": 1000,
        "totalComment": 50,
        "totalShare": 100,
        "createTime": "2024-01-02 12:34:56",
        "duration": "00:00:30"
    },
    "comments": [
        {
            "username": "commenter1",
            "comment": "Comment text"
        }
    ]
}
```

## Disclaimer

This tool is for educational purposes only. Please respect TikTok's terms of service and API usage guidelines.

## Author

@bud1mu
