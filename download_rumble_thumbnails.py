# download_rumble_thumbnails.py

import requests
import argparse
from typing import Any, Dict, List, Optional, Tuple, Set

# Size code mapping for URL transformation
# These codes can be discovered by:
# 1. Getting any thumbnail URL from the JSON feed
# 2. The URL will contain one of these codes (e.g., 'qR4e' for 1280×720)
# 3. By replacing that code with another (e.g., 'OvCc'), you get a different size
THUMBNAIL_SIZES = {
    # Square formats
    "Q_v": (90, 90),      # Tiny square
    "O-xb": (360, 360),   # Large square
    
    # Landscape formats (16:9 and similar)
    "qR4e": (1280, 720),  # HD
    "uQ4e": (1280, 660),  # Wide HD
    "OvCc": (640, 360),   # Standard
    "kvCc": (640, 330),   # Wide standard
    "oq1b": (480, 270),   # Medium
    "4p1b": (480, 248),   # Wide medium
    "0kob": (320, 180),   # Small
    "Gkob": (320, 160),   # Wide small
    
    # Portrait formats
    "aiEB": (720, 1280),  # Vertical HD
    "adyb": (360, 640),   # Vertical medium
    
    # Other aspect ratios
    "GWF": (130, 80),     # Thumbnail
    "UHP": (170, 94),     # Small preview
    "ibH": (135, 240),    # Vertical small
    "ajN": (160, 320),    # Vertical thumbnail
    "8KP": (170, 300),    # Vertical preview
    "GbS": (180, 320),    # Vertical standard
    "8N6": (240, 124),    # Wide thumbnail
    "hO6": (240, 135),    # 16:9 thumbnail
    "qccb": (270, 480),   # Vertical medium-small
    "49bb": (270, 200),   # Preview
    "7rjb": (300, 155),   # Wide preview
    "ksjb": (300, 170),   # Standard preview
    "axjb": (300, 480),   # Vertical medium
    "Lkob": (320, 165),   # Wide small
    "67xb": (360, 186),   # Wide medium-small
    "l8xb": (360, 203),   # Wide medium-small
    "Sq1b": (480, 300),   # Standard medium
    "Or1b": (480, 360),   # 4:3 medium
}

def load_json_from_url(json_url: str) -> Dict[str, Any]:
    """
    Downloads and returns JSON data from the specified URL.
    Uses custom headers to mimic a browser request.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        ),
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }
    try:
        response = requests.get(json_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as err:
        print(f"Error loading JSON from {json_url}: {err}")
        return {}

def find_thumbnail_by_dimensions(thumbnails: List[Dict[str, Any]], target_width: int, target_height: int) -> Optional[str]:
    """
    Find a thumbnail URL with exact dimensions from the thumbnails list.
    """
    for thumb in thumbnails:
        if thumb.get("w") == target_width and thumb.get("h") == target_height:
            return thumb.get("url")
    return None

def modify_thumbnail_url(url: str, target_width: int, target_height: int) -> Optional[str]:
    """
    Modify a thumbnail URL to get the desired dimensions using size codes.
    Returns None if no matching size code is found.
    """
    # Find the target size code
    target_code = None
    for code, (w, h) in THUMBNAIL_SIZES.items():
        if w == target_width and h == target_height:
            target_code = code
            break
    
    if not target_code:
        return None

    # Find and replace the current size code
    for code in THUMBNAIL_SIZES:
        if code in url:
            return url.replace(code, target_code)
    
    return None

def get_latest_thumbnails(data: Dict[str, Any], target_width: int = 1280, target_height: int = 720, download_limit: Optional[int] = 20) -> List[str]:
    """
    Extracts the URLs of thumbnails with the specified dimensions.
    First tries to find exact matches in the JSON, then falls back to URL modification.

    Args:
        data: The JSON data from Rumble playlist
        target_width: Desired thumbnail width (default: 1280)
        target_height: Desired thumbnail height (default: 720)
        download_limit: Maximum number of thumbnails to download. If None, downloads all available.
    """
    thumbnail_urls: List[str] = []
    results = data.get("results", [])
    # Sort results by uploadDate (latest first) if not already sorted
    results.sort(key=lambda r: r.get("uploadDate", ""), reverse=True)

    for result in results:
        thumbnails = result.get("thumbnails", [])
        url = None

        # First try: find exact match in JSON
        url = find_thumbnail_by_dimensions(thumbnails, target_width, target_height)

        # Second try: modify URL using size codes
        if not url and thumbnails:
            first_thumb_url = thumbnails[0].get("url")
            if first_thumb_url:
                url = modify_thumbnail_url(first_thumb_url, target_width, target_height)

        if url:
            thumbnail_urls.append(url)
            if download_limit is not None and len(thumbnail_urls) >= download_limit:
                return thumbnail_urls

    return thumbnail_urls

def download_file(url: str, filename: str) -> None:
    """
    Downloads the file at the given URL and saves it with the specified filename.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {url} to {filename}")
    except requests.RequestException as err:
        print(f"Error downloading {url}: {err}")

def get_available_sizes(thumbnails: List[Dict[str, Any]]) -> Set[Tuple[int, int]]:
    """
    Extract all available sizes from a list of thumbnails.
    """
    sizes = set()
    for thumb in thumbnails:
        if (w := thumb.get("w")) and (h := thumb.get("h")):
            sizes.add((w, h))
    return sizes

def main(json_url: str, target_width: int = 1280, target_height: int = 720, download_limit: Optional[int] = 20) -> None:
    """
    Loads JSON data from a URL, retrieves the latest thumbnails,
    and downloads each thumbnail.

    Args:
        json_url (str): The URL of the Rumble JSON playlist
        target_width (int): Desired thumbnail width
        target_height (int): Desired thumbnail height
        download_limit (Optional[int]): Maximum number of thumbnails to download. 
                                      If None, downloads all available.
    """
    data = load_json_from_url(json_url)
    if not data:
        print("No data to process.")
        return

    # Get a sample of available sizes from the first video
    if results := data.get("results", []):
        if thumbnails := results[0].get("thumbnails", []):
            print("\nAvailable sizes in the feed:")
            sizes = get_available_sizes(thumbnails)
            for w, h in sorted(sizes):
                print(f"- {w}×{h}")
            print(f"\nProceeding with requested size: {target_width}×{target_height}\n")

    thumbnail_urls = get_latest_thumbnails(data, target_width, target_height, download_limit)
    total_available = len(data.get("results", []))
    
    print(f"Found {len(thumbnail_urls)} thumbnails to download (out of {total_available} available).")

    for url in thumbnail_urls:
        # Use the last segment of the URL as filename
        filename = url.split("/")[-1]
        download_file(url, filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download thumbnails from a Rumble JSON playlist.')
    parser.add_argument('json_url', type=str, help='The URL of the Rumble JSON playlist')
    parser.add_argument('--width', type=int, default=1280, 
                      help='Desired thumbnail width (default: 1280)')
    parser.add_argument('--height', type=int, default=720,
                      help='Desired thumbnail height (default: 720)')
    parser.add_argument('--limit', type=str, default='20', 
                      help='Maximum number of thumbnails to download (default: 20, use "all" for all available)')
    parser.add_argument('--list-sizes', action='store_true',
                      help='List all known thumbnail sizes')
    
    args = parser.parse_args()

    # Show size list if requested
    if args.list_sizes:
        print("Known thumbnail sizes:")
        print("\nFormat      Width × Height")
        print("-" * 40)
        
        # Group sizes by aspect ratio for better organization
        by_ratio: Dict[str, List[Tuple[int, int]]] = {
            "Square": [],
            "Landscape": [],
            "Portrait": [],
            "Other": []
        }
        
        for w, h in sorted(set(THUMBNAIL_SIZES.values())):
            if w == h:
                by_ratio["Square"].append((w, h))
            elif w > h and w/h >= 1.7:
                by_ratio["Landscape"].append((w, h))
            elif h > w and h/w >= 1.7:
                by_ratio["Portrait"].append((w, h))
            else:
                by_ratio["Other"].append((w, h))
        
        for format_name, sizes in by_ratio.items():
            if sizes:
                print(f"\n{format_name}:")
                for w, h in sorted(sizes):
                    print(f"  {w:4d} × {h:4d}")
        exit(0)
    
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
    
    main(args.json_url, args.width, args.height, download_limit)
