#!/usr/bin/env python3
"""
qdMovie/imdbinfo Poster Enrichment Script
Uses the imdbinfo package (powers qdMovieAPI) to fetch poster URLs from IMDb
More reliable than web scraping as it's a structured API wrapper
"""

import json
import sys
import time
from typing import Dict, Optional
from datetime import datetime

try:
    from imdbinfo import get_movie
except ImportError:
    print("❌ Missing required package: imdbinfo")
    print("\n💡 Install: pip3 install imdbinfo")
    sys.exit(1)


class QDMoviePosterEnricher:
    """Enriches content with poster URLs using imdbinfo package"""

    def __init__(self, input_file='movies_enriched.json'):
        self.input_file = input_file
        self.data = []
        self.full_data = None
        self.enriched_count = 0
        self.failed_count = 0
        self.skipped_count = 0

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

    def get_qdmovie_poster(self, imdb_id: str) -> Optional[str]:
        """
        Fetch poster URL using imdbinfo package

        Args:
            imdb_id: IMDb ID (e.g., 'tt1234567' or '1234567')

        Returns:
            Poster URL or None if not found
        """
        if not imdb_id:
            return None

        # Remove 'tt' prefix if present, imdbinfo handles both
        clean_id = imdb_id.replace('tt', '')

        try:
            # Retry logic for network issues
            for attempt in range(3):
                try:
                    movie = get_movie(clean_id)
                    if movie and hasattr(movie, 'cover_url') and movie.cover_url:
                        return movie.cover_url
                    return None
                except (ConnectionError, TimeoutError):
                    if attempt < 2:
                        time.sleep((attempt + 1) * 2)
                        continue
                    else:
                        return None
                except Exception:
                    return None

        except Exception as e:
            return None

    def enrich_item(self, item: Dict) -> bool:
        """
        Enrich a single item with qdMovie poster

        Returns:
            True if poster was added/updated
        """
        imdb_id = item.get('imdb_id')
        if not imdb_id:
            return False

        title = item.get('title', 'Unknown')
        has_poster = bool(item.get('posters') or item.get('poster_path'))

        # Get qdMovie poster
        qdmovie_poster_url = self.get_qdmovie_poster(imdb_id)

        if qdmovie_poster_url:
            # Add qdMovie poster URL to item
            if 'qdmovie_poster_url' not in item:
                item['qdmovie_poster_url'] = qdmovie_poster_url

            # If item has no poster, use qdMovie poster as primary
            if not has_poster:
                if 'posters' not in item:
                    item['posters'] = {}

                # Set qdMovie poster as primary
                item['posters']['qdmovie'] = qdmovie_poster_url
                item['poster_url_medium'] = qdmovie_poster_url
                item['poster_url_large'] = qdmovie_poster_url

                # Also store in standard fields
                if 'cover_url' not in item:
                    item['cover_url'] = qdmovie_poster_url

                print(f" → ✅ Added qdMovie poster (no other poster)")
                return True
            else:
                # Item has poster, store qdMovie as alternative
                if 'posters' not in item:
                    item['posters'] = {}
                item['posters']['qdmovie'] = qdmovie_poster_url

                if 'cover_url' not in item:
                    item['cover_url'] = qdmovie_poster_url

                print(f" → ℹ️  qdMovie poster stored as alternative")
                return True
        else:
            print(f" → ❌ No poster found via qdMovie")
            return False

    def run(self, prioritize_missing=True, enrich_all=False):
        """
        Run the enrichment process

        Args:
            prioritize_missing: Process items without posters first
            enrich_all: Enrich all items with IMDb IDs, not just missing posters
        """
        start_time = time.time()

        print("\n" + "="*70)
        print("qdMOVIE/IMDBINFO POSTER ENRICHMENT")
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

        # Process items without posters
        if items_without_posters:
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

                # Rate limiting to be respectful
                time.sleep(0.5)

        # Optionally process items with existing posters
        if enrich_all and items_with_posters:
            print("\n" + "="*70)
            print("PROCESSING ITEMS WITH EXISTING POSTERS (Adding qdMovie as Alternative)")
            print("="*70 + "\n")

            for i, item in enumerate(items_with_posters, 1):
                title = item.get('title', 'Unknown')
                imdb_id = item.get('imdb_id', 'N/A')

                # Skip if already has qdmovie poster
                if item.get('qdmovie_poster_url'):
                    print(f"[{i}/{len(items_with_posters)}] {title[:50]} ({imdb_id}) → ⊙ Already has qdMovie poster")
                    self.skipped_count += 1
                    continue

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
        print(f"   • Skipped (already had qdMovie poster): {self.skipped_count}")
        print(f"   • Total processed: {self.enriched_count + self.failed_count + self.skipped_count}")
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
        description='Enrich movie/TV data with qdMovie/imdbinfo poster URLs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 enrich_posters_qdmovie.py                 # Process missing posters only
  python3 enrich_posters_qdmovie.py --all           # Enrich all items with IMDb IDs
  python3 enrich_posters_qdmovie.py --file data.json # Use custom input file

Features:
  - Uses imdbinfo package (powers qdMovieAPI)
  - More reliable than direct web scraping
  - Provides structured Pydantic models
  - Automatic retry logic for network issues
  - Rate limiting to be respectful
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
        help='Enrich all items with IMDb IDs, not just those missing posters'
    )

    args = parser.parse_args()

    enricher = QDMoviePosterEnricher(input_file=args.file)

    try:
        enricher.run(enrich_all=args.all)
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
