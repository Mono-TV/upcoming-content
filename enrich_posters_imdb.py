#!/usr/bin/env python3
"""
IMDb Poster Enrichment Script
Enriches movie/TV show data with poster URLs from IMDb
Prioritizes items missing posters, uses IMDb as fallback source
"""

import json
import sys
import time
import requests
from typing import Dict, Optional, List
from datetime import datetime

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Missing required package: beautifulsoup4")
    print("\n💡 Install: pip3 install beautifulsoup4")
    sys.exit(1)


class IMDbPosterEnricher:
    """Enriches content with IMDb poster URLs"""

    def __init__(self, input_file='movies_enriched.json'):
        self.input_file = input_file
        self.data = []
        self.full_data = None
        self.enriched_count = 0
        self.failed_count = 0

    def load_data(self):
        """Load enriched data from JSON file"""
        print(f"\n📂 Loading data from {self.input_file}...")
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                loaded = json.load(f)

            # Handle both flat list and OTTPlay structure
            if isinstance(loaded, list):
                self.data = loaded
                self.full_data = None
            elif isinstance(loaded, dict) and 'content' in loaded:
                self.data = loaded['content']
                self.full_data = loaded
            else:
                print(f"❌ Unexpected JSON structure in {self.input_file}")
                sys.exit(1)

            print(f"✅ Loaded {len(self.data)} items")
        except FileNotFoundError:
            print(f"❌ File not found: {self.input_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {self.input_file}: {e}")
            sys.exit(1)

    def get_imdb_poster(self, imdb_id: str) -> Optional[str]:
        """
        Fetch poster URL from IMDb page

        Args:
            imdb_id: IMDb ID (e.g., 'tt1234567')

        Returns:
            Poster URL or None if not found
        """
        if not imdb_id or not imdb_id.startswith('tt'):
            return None

        try:
            url = f"https://www.imdb.com/title/{imdb_id}/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            # Retry logic for connection issues
            for attempt in range(3):
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    response.raise_for_status()
                    break
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    if attempt < 2:
                        time.sleep((attempt + 1) * 2)
                        continue
                    else:
                        return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Method 1: Look for poster image in hero section
            poster_img = soup.find('img', class_='ipc-image')
            if poster_img and poster_img.get('src'):
                poster_url = poster_img['src']
                # IMDb poster URLs often have resolution parameters, get high-res version
                # Example: https://m.media-amazon.com/images/M/...._V1_QL75_UX380_CR0,0,380,562_.jpg
                # Remove resolution params to get original
                if '@' in poster_url:
                    poster_url = poster_url.split('@')[0] + '@.jpg'
                elif '_V1_' in poster_url:
                    # Keep _V1_ but remove specific dimension params
                    base_url = poster_url.split('_V1_')[0]
                    poster_url = base_url + '_V1_.jpg'
                return poster_url

            # Method 2: Look for og:image meta tag
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                return og_image['content']

            # Method 3: Look for poster div
            poster_div = soup.find('div', class_='poster')
            if poster_div:
                img = poster_div.find('img')
                if img and img.get('src'):
                    return img['src']

            return None

        except Exception as e:
            print(f"\n⚠️  Error fetching IMDb poster for {imdb_id}: {e}")
            return None

    def enrich_item(self, item: Dict) -> bool:
        """
        Enrich a single item with IMDb poster

        Returns:
            True if poster was added/updated
        """
        imdb_id = item.get('imdb_id')
        if not imdb_id:
            return False

        title = item.get('title', 'Unknown')
        has_poster = bool(item.get('posters') or item.get('poster_path'))

        # Get IMDb poster
        imdb_poster_url = self.get_imdb_poster(imdb_id)

        if imdb_poster_url:
            # Add IMDb poster URL to item
            if 'imdb_poster_url' not in item:
                item['imdb_poster_url'] = imdb_poster_url

            # If item has no TMDB poster, use IMDb poster as primary
            if not has_poster:
                if 'posters' not in item:
                    item['posters'] = {}

                # Set IMDb poster as fallback
                item['posters']['imdb'] = imdb_poster_url
                item['poster_url_medium'] = imdb_poster_url
                item['poster_url_large'] = imdb_poster_url

                print(f" → ✅ Added IMDb poster (no TMDB poster)")
                return True
            else:
                print(f" → ℹ️  IMDb poster stored as alternative")
                return True
        else:
            print(f" → ❌ No poster found on IMDb")
            return False

    def run(self, prioritize_missing=True):
        """
        Run the enrichment process

        Args:
            prioritize_missing: Process items without posters first
        """
        start_time = time.time()

        print("\n" + "="*70)
        print("IMDb POSTER ENRICHMENT")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        self.load_data()

        # Separate items by poster status
        items_without_posters = []
        items_with_posters = []

        for item in self.data:
            if item.get('imdb_id'):
                has_poster = bool(item.get('posters') or item.get('poster_path'))
                if has_poster:
                    items_with_posters.append(item)
                else:
                    items_without_posters.append(item)

        print(f"\n📊 Analysis:")
        print(f"   • Total items: {len(self.data)}")
        print(f"   • Items with IMDb ID: {len(items_without_posters) + len(items_with_posters)}")
        print(f"   • Missing posters (with IMDb ID): {len(items_without_posters)}")
        print(f"   • Have posters (with IMDb ID): {len(items_with_posters)}")

        # Process items
        print("\n" + "="*70)
        print("PROCESSING ITEMS WITHOUT POSTERS (Priority)")
        print("="*70 + "\n")

        for i, item in enumerate(items_without_posters, 1):
            title = item.get('title', 'Unknown')
            imdb_id = item.get('imdb_id', 'N/A')

            print(f"[{i}/{len(items_without_posters)}] {title[:50]} ({imdb_id})", end='')

            if self.enrich_item(item):
                self.enriched_count += 1
            else:
                self.failed_count += 1

            # Rate limiting
            time.sleep(0.5)

        # Optionally process items with existing posters
        if not prioritize_missing:
            print("\n" + "="*70)
            print("PROCESSING ITEMS WITH EXISTING POSTERS (Adding IMDb as Alternative)")
            print("="*70 + "\n")

            for i, item in enumerate(items_with_posters, 1):
                title = item.get('title', 'Unknown')
                imdb_id = item.get('imdb_id', 'N/A')

                print(f"[{i}/{len(items_with_posters)}] {title[:50]} ({imdb_id})", end='')

                if self.enrich_item(item):
                    self.enriched_count += 1
                else:
                    self.failed_count += 1

                # Rate limiting
                time.sleep(0.5)

        # Save enriched data
        self.save_data()

        # Summary
        elapsed = time.time() - start_time

        print("\n" + "="*70)
        print("✅ ENRICHMENT COMPLETE!")
        print("="*70)
        print(f"\n📊 Results:")
        print(f"   • Successfully enriched: {self.enriched_count}")
        print(f"   • Failed to enrich: {self.failed_count}")
        print(f"   • Total processed: {self.enriched_count + self.failed_count}")
        print(f"\n⏱️  Time elapsed: {elapsed:.1f} seconds")
        print(f"📁 Updated file: {self.input_file}")
        print("="*70 + "\n")

    def save_data(self):
        """Save enriched data back to JSON file"""
        backup_file = f"{self.input_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create backup
        print(f"\n💾 Creating backup: {backup_file}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            with open(self.input_file, 'r', encoding='utf-8') as original:
                f.write(original.read())

        # Save enriched data (handle both structures)
        print(f"💾 Saving enriched data to {self.input_file}...")
        with open(self.input_file, 'w', encoding='utf-8') as f:
            if self.full_data:
                # OTTPlay structure - update content array
                self.full_data['content'] = self.data
                self.full_data['enriched_at'] = datetime.now().isoformat()
                json.dump(self.full_data, f, indent=2, ensure_ascii=False)
            else:
                # Flat list structure
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        print("✅ Saved successfully")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Enrich movie/TV data with IMDb poster URLs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 enrich_posters_imdb.py                    # Process items missing posters only
  python3 enrich_posters_imdb.py --all              # Process all items with IMDb IDs
  python3 enrich_posters_imdb.py --file custom.json # Use custom input file
        """
    )

    parser.add_argument(
        '--file',
        default='movies_enriched.json',
        help='Input JSON file (default: movies_enriched.json)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all items with IMDb IDs, not just those missing posters'
    )

    args = parser.parse_args()

    enricher = IMDbPosterEnricher(input_file=args.file)

    try:
        enricher.run(prioritize_missing=not args.all)
    except KeyboardInterrupt:
        print("\n\n⚠️  Enrichment interrupted by user")
        print(f"Progress: {enricher.enriched_count} enriched, {enricher.failed_count} failed")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
