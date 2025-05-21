# download_rumble_thumbnails.py
import json
import requests
import argparse
from typing import Any, Dict, List, Optional

def get_latest_thumbnails(data: Dict[str, Any], download_limit: Optional[int] = 20) -> List[str]:
    """
    Extracts the URLs of thumbnails that are exactly 1280x720.

    Args:
        data: The JSON data from Rumble playlist
        download_limit: Maximum number of thumbnails to download. If None, downloads all available.

    Assumes results are sorted by uploadDate descending.
    If not, it sorts them.
    """
    thumbnail_urls: List[str] = []
    results = data.get("results", [])
    # Sort results by uploadDate (latest first) if not already sorted.
    results.sort(key=lambda r: r.get("uploadDate", ""), reverse=True)

    for result in results:
        for thumb in result.get("thumbnails", []):
            if thumb.get("w") == 1280 and thumb.get("h") == 720:
                thumbnail_urls.append(thumb["url"])
                if download_limit is not None and len(thumbnail_urls) >= download_limit:
                    return thumbnail_urls
                break  # Move to next video after finding the right thumbnail
    return thumbnail_urls

def download_file(url: str, filename: str) -> None:
    """
    Downloads the file at the given URL and saves it with the specified filename.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {url} to {filename}")
    except requests.RequestException as err:
        print(f"Error downloading {url}: {err}")

def load_json_from_url(json_url: str) -> Dict[str, Any]:
    """
    Downloads and returns JSON data from the specified URL.
    Uses custom headers to mimic a browser request.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }
    try:
        response = requests.get(json_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as err:
        print(f"Error loading JSON from {json_url}: {err}")
        return {}

def main(json_url: str, download_limit: Optional[int] = 20) -> None:
    """
    Loads JSON data from a URL, retrieves the latest thumbnails,
    and downloads each thumbnail.

    Args:
        json_url (str): The URL of the Rumble JSON playlist
        download_limit (Optional[int]): Maximum number of thumbnails to download. 
                                      If None, downloads all available.
    """
    data = load_json_from_url(json_url)
    if not data:
        print("No data to process.")
        return

    thumbnail_urls = get_latest_thumbnails(data, download_limit)
    total_available = sum(1 for r in data.get("results", []) 
                         for t in r.get("thumbnails", []) 
                         if t.get("w") == 1280 and t.get("h") == 720)
    
    print(f"Found {len(thumbnail_urls)} thumbnails to download (out of {total_available} available).")

    for url in thumbnail_urls:
        # Use the last segment of the URL as filename
        filename = url.split("/")[-1]
        download_file(url, filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download thumbnails from a Rumble JSON playlist.')
    parser.add_argument('json_url', type=str, help='The URL of the Rumble JSON playlist')
    parser.add_argument('--limit', type=str, default='20', 
                      help='Maximum number of thumbnails to download (default: 20, use "all" for all available)')
    
    args = parser.parse_args()
    
    # Handle the limit argument
    if args.limit.lower() == 'all':
        download_limit = None
    else:
        try:
            download_limit = int(args.limit)
            if download_limit <= 0:
                parser.error("Limit must be a positive number or 'all'")
        except ValueError:
            parser.error("Limit must be a positive number or 'all'")
    
    main(args.json_url, download_limit)
