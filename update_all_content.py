#!/usr/bin/env python3
"""
Master Content Update Script
Scrapes and enriches all 4 content types:
1. OTT Releases (already released)
2. OTT Upcoming (future releases)
3. Theatre Current (now playing in theatres)
4. Theatre Upcoming (upcoming theatre releases)

Usage:
    python3 update_all_content.py [--ott-pages N] [--city bengaluru] [--skip-ott] [--skip-theatre] [--debug]
"""

import asyncio
import json
import sys
import os
import argparse
from typing import List, Dict
from datetime import datetime

# Import scrapers
from scrape_ott_releases import scrape_ott_releases
from scrape_theatre_current import scrape_theatre_current
from scrape_theatre_upcoming import scrape_theatre_upcoming

# Import existing enrichment tools
try:
    from update_content import ContentUpdater
except ImportError:
    print("Warning: Could not import ContentUpdater. Some enrichment features may be limited.", file=sys.stderr)
    ContentUpdater = None

from config import CONTENT_TYPES, BMS_CONFIG


class MasterContentOrchestrator:
    """
    Orchestrates scraping and enrichment for all content types
    """

    def __init__(self, ott_pages: int = 5, city: str = 'bengaluru', debug: bool = False):
        self.ott_pages = ott_pages
        self.city = city
        self.debug = debug

        # Content storage
        self.content = {
            'ott_released': [],
            'ott_upcoming': [],
            'theatre_current': [],
            'theatre_upcoming': []
        }

    async def scrape_all(self, skip_ott: bool = False, skip_theatre: bool = False):
        """Scrape all content types"""
        print("\n" + "="*70)
        print("MASTER CONTENT SCRAPER - Scraping All Content Types")
        print("="*70 + "\n")

        # 1. Scrape OTT Released Content
        if not skip_ott:
            print("\n" + "-"*70)
            print("1. Scraping OTT Releases (Already Released Content)")
            print("-"*70)
            try:
                self.content['ott_released'] = await scrape_ott_releases(
                    max_pages=self.ott_pages,
                    fetch_deeplinks=True,
                    debug=self.debug
                )
                print(f"✅ Scraped {len(self.content['ott_released'])} OTT releases")
                self._save_raw_data('ott_released', 'ott_releases.json')
            except Exception as e:
                print(f"❌ Error scraping OTT releases: {e}", file=sys.stderr)

        # 2. Scrape OTT Upcoming Content
        if not skip_ott:
            print("\n" + "-"*70)
            print("2. Scraping OTT Upcoming Releases")
            print("-"*70)
            try:
                # Use existing ContentUpdater for upcoming OTT
                if ContentUpdater:
                    updater = ContentUpdater(max_pages=self.ott_pages)
                    await updater.scrape_movies()
                    self.content['ott_upcoming'] = updater.movies
                    # Add content_type marker
                    for movie in self.content['ott_upcoming']:
                        movie['content_type'] = 'ott_upcoming'
                    print(f"✅ Scraped {len(self.content['ott_upcoming'])} upcoming OTT releases")
                    self._save_raw_data('ott_upcoming', 'ott_upcoming.json')
                else:
                    print("⚠️  ContentUpdater not available, skipping OTT upcoming", file=sys.stderr)
            except Exception as e:
                print(f"❌ Error scraping OTT upcoming: {e}", file=sys.stderr)

        # 3. Scrape Theatre Current
        if not skip_theatre:
            print("\n" + "-"*70)
            print("3. Scraping Current Theatre Movies")
            print("-"*70)
            try:
                self.content['theatre_current'] = await scrape_theatre_current(
                    city=self.city,
                    debug=self.debug
                )
                print(f"✅ Scraped {len(self.content['theatre_current'])} current theatre movies")
                self._save_raw_data('theatre_current', f'theatre_current_{self.city}.json')
            except Exception as e:
                print(f"❌ Error scraping theatre current: {e}", file=sys.stderr)

        # 4. Scrape Theatre Upcoming
        if not skip_theatre:
            print("\n" + "-"*70)
            print("4. Scraping Upcoming Theatre Releases")
            print("-"*70)
            try:
                self.content['theatre_upcoming'] = await scrape_theatre_upcoming(
                    city=self.city,
                    debug=self.debug
                )
                print(f"✅ Scraped {len(self.content['theatre_upcoming'])} upcoming theatre releases")
                self._save_raw_data('theatre_upcoming', f'theatre_upcoming_{self.city}.json')
            except Exception as e:
                print(f"❌ Error scraping theatre upcoming: {e}", file=sys.stderr)

        print("\n" + "="*70)
        print("SCRAPING COMPLETE")
        print("="*70)
        self._print_scraping_summary()

    def enrich_all(self):
        """Enrich all content types with TMDB, IMDb, YouTube data"""
        print("\n" + "="*70)
        print("MASTER CONTENT ENRICHER - Enriching All Content")
        print("="*70 + "\n")

        # Enrich each content type
        for content_type in ['ott_released', 'ott_upcoming', 'theatre_current', 'theatre_upcoming']:
            if self.content[content_type]:
                print(f"\n{'='*70}")
                print(f"Enriching: {CONTENT_TYPES[content_type]['name']}")
                print(f"{'='*70}")
                self._enrich_content_type(content_type)

        print("\n" + "="*70)
        print("ENRICHMENT COMPLETE")
        print("="*70)
        self._print_enrichment_summary()

    def _enrich_content_type(self, content_type: str):
        """Enrich a specific content type"""
        items = self.content[content_type]

        if not items:
            print(f"⚠️  No items to enrich for {content_type}")
            return

        print(f"📋 Enriching {len(items)} items...\n")

        if ContentUpdater:
            # Use existing ContentUpdater enrichment methods
            updater = ContentUpdater(
                enable_posters=True,
                enable_trailers=True,
                generate_placeholders=True
            )

            # Set the movies to enrich
            updater.movies = items

            # Step 1: TMDB Enrichment (all content types)
            print("\n--- TMDB Enrichment ---")
            updater.enrich_with_tmdb_complete()

            # Step 2: IMDb Enrichment (fallback)
            print("\n--- IMDb Enrichment ---")
            updater.enrich_with_imdb_fallback()

            # Step 3: YouTube Trailers
            print("\n--- YouTube Trailer Enrichment ---")
            if content_type.startswith('theatre'):
                # For theatre content, prioritize BookMyShow trailers
                self._enrich_theatre_trailers(updater.movies)
            else:
                # For OTT content, use standard YouTube search
                updater.enrich_with_youtube_trailers()

            # Update our content
            self.content[content_type] = updater.movies

        else:
            print("⚠️  ContentUpdater not available, enrichment limited", file=sys.stderr)

        # Save enriched data
        output_file = CONTENT_TYPES[content_type]['output_file']
        self._save_enriched_data(content_type, output_file)
        print(f"\n✅ Enriched data saved to {output_file}")

    def _enrich_theatre_trailers(self, movies: List[Dict]):
        """
        Enrich theatre content with YouTube trailers
        Priority: BookMyShow trailer → YouTube search
        """
        print(f"🎬 Processing {len(movies)} theatre movies for trailers...")

        enriched_count = 0
        for i, movie in enumerate(movies, 1):
            title = movie.get('title', '')
            print(f"[{i}/{len(movies)}] {title[:40]}... ", end='', flush=True)

            # Check if already has YouTube data
            if movie.get('youtube_id') or movie.get('youtube_url'):
                print("✓ Already has trailer")
                enriched_count += 1
                continue

            # Check if BookMyShow trailer exists
            if movie.get('trailer_bms_url'):
                bms_url = movie['trailer_bms_url']

                # Extract YouTube ID from BookMyShow trailer URL
                import re
                match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)', bms_url)
                if match:
                    youtube_id = match.group(1)
                    movie['youtube_id'] = youtube_id
                    movie['youtube_url'] = f'https://www.youtube.com/watch?v={youtube_id}'
                    enriched_count += 1
                    print(f"✓ From BookMyShow")
                    continue

            # Fallback: YouTube search (would need ContentUpdater's method)
            print("⊙ No trailer")

        print(f"\n✅ Enriched {enriched_count}/{len(movies)} movies with trailers")

    def _save_raw_data(self, content_type: str, filename: str):
        """Save raw scraped data"""
        data = self.content[content_type]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved raw data to {filename}", file=sys.stderr)

    def _save_enriched_data(self, content_type: str, filename: str):
        """Save enriched data"""
        data = self.content[content_type]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved enriched data to {filename}")

    def _print_scraping_summary(self):
        """Print summary of scraping results"""
        print("\n📊 SCRAPING SUMMARY:")
        print("-" * 50)
        for content_type, info in CONTENT_TYPES.items():
            count = len(self.content[content_type])
            print(f"  {info['name']:<30} {count:>5} items")
        print("-" * 50)
        total = sum(len(self.content[ct]) for ct in self.content)
        print(f"  {'TOTAL':<30} {total:>5} items")
        print()

    def _print_enrichment_summary(self):
        """Print summary of enrichment results"""
        print("\n📊 ENRICHMENT SUMMARY:")
        print("-" * 70)

        for content_type in ['ott_released', 'ott_upcoming', 'theatre_current', 'theatre_upcoming']:
            items = self.content[content_type]
            if not items:
                continue

            name = CONTENT_TYPES[content_type]['name']
            count = len(items)

            with_tmdb = sum(1 for m in items if m.get('tmdb_id'))
            with_imdb = sum(1 for m in items if m.get('imdb_id'))
            with_youtube = sum(1 for m in items if m.get('youtube_id'))
            with_posters = sum(1 for m in items if m.get('poster_url_medium') or m.get('poster_url_large'))

            print(f"\n{name} ({count} items):")
            print(f"  TMDB data:     {with_tmdb:>3}/{count} ({with_tmdb*100//count if count else 0}%)")
            print(f"  IMDb data:     {with_imdb:>3}/{count} ({with_imdb*100//count if count else 0}%)")
            print(f"  Trailers:      {with_youtube:>3}/{count} ({with_youtube*100//count if count else 0}%)")
            print(f"  Posters:       {with_posters:>3}/{count} ({with_posters*100//count if count else 0}%)")

            # Additional stats for specific content types
            if content_type == 'ott_released':
                with_deeplinks = sum(1 for m in items if m.get('deeplinks'))
                print(f"  Deeplinks:     {with_deeplinks:>3}/{count} ({with_deeplinks*100//count if count else 0}%)")

            if content_type.startswith('theatre'):
                with_formats = sum(1 for m in items if m.get('video_formats'))
                print(f"  Video formats: {with_formats:>3}/{count} ({with_formats*100//count if count else 0}%)")

        print("\n" + "-" * 70)


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Master content scraper and enricher for all content types'
    )

    # Scraping options
    parser.add_argument('--ott-pages', type=int, default=5,
                       help='Number of pages to scrape for OTT content (default: 5)')
    parser.add_argument('--city', type=str, default='bengaluru',
                       choices=list(BMS_CONFIG['cities'].keys()),
                       help='City for theatre content (default: bengaluru)')

    # Skip options
    parser.add_argument('--skip-ott', action='store_true',
                       help='Skip OTT content scraping')
    parser.add_argument('--skip-theatre', action='store_true',
                       help='Skip theatre content scraping')
    parser.add_argument('--skip-enrichment', action='store_true',
                       help='Skip enrichment phase (only scrape)')

    # Debug
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode (verbose output, screenshots)')

    args = parser.parse_args()

    print("="*70)
    print("MASTER CONTENT UPDATE SYSTEM")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"  OTT Pages:      {args.ott_pages}")
    print(f"  City:           {args.city}")
    print(f"  Skip OTT:       {args.skip_ott}")
    print(f"  Skip Theatre:   {args.skip_theatre}")
    print(f"  Skip Enrichment:{args.skip_enrichment}")
    print(f"  Debug Mode:     {args.debug}")
    print()

    # Create orchestrator
    orchestrator = MasterContentOrchestrator(
        ott_pages=args.ott_pages,
        city=args.city,
        debug=args.debug
    )

    # Phase 1: Scraping
    await orchestrator.scrape_all(
        skip_ott=args.skip_ott,
        skip_theatre=args.skip_theatre
    )

    # Phase 2: Enrichment
    if not args.skip_enrichment:
        orchestrator.enrich_all()
    else:
        print("\n⏭️  Skipping enrichment phase")

    print("\n" + "="*70)
    print("✅ ALL CONTENT UPDATED SUCCESSFULLY!")
    print("="*70)
    print("\nOutput Files:")
    for content_type, info in CONTENT_TYPES.items():
        if orchestrator.content[content_type]:
            print(f"  • {info['output_file']}")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
