#!/usr/bin/env python3
"""
Download uniform streaming platform logos
"""
import urllib.request
import os

# Logo URLs from various sources (SVG preferred for scalability)
LOGO_URLS = {
    'Netflix.svg': 'https://www.svgrepo.com/show/303341/netflix-1-logo.svg',
    'Amazon_Prime_Video.svg': 'https://www.svgrepo.com/show/349310/amazon.svg',
    'Sony_LIV.svg': 'https://www.svgrepo.com/show/452093/sony.svg',
    'JioHotstar.svg': 'https://www.svgrepo.com/show/452064/hotstar.svg',
    'Sun_NXT.png': '',  # Will use existing
    'Manorama_MAX.png': '',  # Will use existing
}

def download_logo(url, filename):
    """Download logo from URL"""
    if not url:
        print(f"Skipping {filename} - using existing")
        return False

    try:
        print(f"Downloading {filename}...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        request = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(request, timeout=10) as response:
            data = response.read()
            with open(filename, 'wb') as f:
                f.write(data)
        print(f"✓ Downloaded {filename}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False

def main():
    os.chdir('/Users/mono/Documents/Programs/Circuit House')

    print("Downloading streaming platform logos...")
    print("=" * 50)

    for filename, url in LOGO_URLS.items():
        download_logo(url, filename)

    print("=" * 50)
    print("Logo download complete!")

if __name__ == '__main__':
    main()
