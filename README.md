# Rumble Thumbnail Downloader

A Python script to download thumbnails from Rumble playlists.

## Author

**Dallas Crilley**  
Website: [dallascrilley.com](https://dallascrilley.com)

## Features

- Downloads high-quality thumbnails (1280x720)
- Sorts by upload date (newest first)
- Configurable download limit (default: 20)
- Option to download all available thumbnails
- Error handling for failed downloads
- Browser-like request headers to prevent blocking
- Progress reporting with available thumbnail count

## Requirements

- Python 3.6+
- `requests` library

Install dependencies:

```bash
pip install requests
```

## Usage

### Quick Start

Download the 20 most recent thumbnails (default):

```bash
python download_rumble_thumbnails.py https://rumble.com/feeds/syndication/your-playlist-id.json
```

### Custom Number of Thumbnails

Download a specific number of thumbnails:

```bash
python download_rumble_thumbnails.py https://rumble.com/feeds/syndication/your-playlist-id.json --limit 5
```

### Download All Thumbnails

Download all available thumbnails from the playlist:

```bash
python download_rumble_thumbnails.py https://rumble.com/feeds/syndication/your-playlist-id.json --limit all
```

### Command Line Arguments

- `json_url` (required): The URL of the Rumble JSON playlist feed
- `--limit` (optional): Maximum number of thumbnails to download
  - Default: 20
  - Use 'all' to download every available thumbnail
  - Must be a positive number or 'all'

### Getting Your Rumble Playlist JSON Feed URL

1. Go to your Rumble channel
2. Navigate to the playlist you want to download thumbnails from
3. Look for the RSS/JSON feed link
   - Format: `https://rumble.com/feeds/syndication/[playlist-id].json`
   - The playlist ID is unique to each playlist

## Output

- Downloads are saved in the current directory
- Filenames are preserved from the original thumbnail URLs
- Progress is displayed in the terminal:
  - Number of thumbnails found
  - Total available thumbnails
  - Download status for each file

## Rumble JSON Schema

The Rumble playlist JSON feed follows this structure. A typical feed contains 50 most recent videos from the playlist.

```json
{
  "results": [
    {
      "fid": "number", // File ID
      "vid": "string", // Video ID
      "title": "string", // Video title
      "description": "string", // Video description
      "url": "string", // Video URL on Rumble
      "channel": "string", // Channel name
      "date": "string", // Date in YYYY-MM-DD HH:MM:SS format
      "uploadDate": "string", // ISO 8601 date format
      "thumbnails": [
        {
          "url": "string", // Thumbnail URL
          "w": "number", // Width in pixels
          "h": "number", // Height in pixels
          "size": "number" // File size in bytes
        }
      ],
      "video": {
        "iframe": "string", // Embed iframe URL
        "w": "number", // Video width
        "h": "number", // Video height
        "files": [] // Video files array
      },
      "duration": "number" // Video duration in seconds
    }
  ]
}
```

### Thumbnail Sizes

The JSON feed includes multiple thumbnail sizes. This script specifically downloads the 1280x720 version, which is typically the highest quality still image available. Common sizes include:

- 1280x720 (HD)
- 1280x660
- 640x360
- 480x270
- And various other smaller sizes

## Error Handling

The script includes robust error handling for:

- Invalid JSON URLs
- Network connection issues
- Invalid download limits
- Failed downloads
- Missing or malformed data

## License

MIT License
