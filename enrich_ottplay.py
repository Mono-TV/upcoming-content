#!/usr/bin/env python3
"""
OTTPlay Content Enrichment Script using qdMovieAPI
Enriches ottplay_complete_no_deeplink.json with IMDB data via qdMovieAPI

Prerequisites:
1. Clone and run qdMovieAPI:
   git clone https://github.com/tveronesi/qdMovieAPI.git
   cd qdMovieAPI
   docker compose up --build

   OR without Docker:
   pip install -r requirements.txt
   python api.py

2. Ensure the API is running on http://127.0.0.1:5000

Usage:
    python3 enrich_ottplay.py [--api-url URL] [--test] [--force]

    --test: Process only first 5 items
    --force: Re-enrich all items, even if already enriched
"""

import json
import re
import time
import argparse
from typing import Dict, List, Optional
import requests
from datetime import datetime


class OTTPlayEnricher:
    """Enrich OTTPlay content using qdMovieAPI (IMDB-based)"""

    def __init__(self, api_url="http://127.0.0.1:5000", test_mode=False, force=False):
        self.api_url = api_url.rstrip('/')
        self.test_mode = test_mode
        self.force = force
        self.data = {}
        self.content_list = []

        # Test API connection
        self._test_connection()

    def _test_connection(self):
        """Test if qdMovieAPI is accessible"""
        try:
            print(f"Testing connection to {self.api_url}...")
            response = requests.get(f"{self.api_url}/", timeout=5)
            response.raise_for_status()
            print("✓ API connection successful\n")
        except requests.exceptions.ConnectionError:
            print("\n" + "="*60)
            print("❌ ERROR: Cannot connect to qdMovieAPI")
            print("="*60)
            print("\nThe qdMovieAPI service is not running or not accessible.")
            print("\n💡 To start qdMovieAPI:")
            print("\n  Option 1: With Docker")
            print("    git clone https://github.com/tveronesi/qdMovieAPI.git")
            print("    cd qdMovieAPI")
            print("    docker compose up --build")
            print("\n  Option 2: Without Docker")
            print("    git clone https://github.com/tveronesi/qdMovieAPI.git")
            print("    cd qdMovieAPI")
            print("    pip install -r requirements.txt")
            print("    python api.py")
            print("\nThen run this script again.")
            print("="*60 + "\n")
            exit(1)
        except Exception as e:
            print(f"❌ Error testing API: {e}")
            exit(1)

    def _fetch_with_retry(self, url, max_retries=3):
        """Fetch URL with retry logic"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                    continue
                else:
                    raise
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    return None
                raise
            except Exception:
                raise

    def _clean_title_for_search(self, title):
        """Clean up title for better search results"""
        if not title:
            return title

        cleaned = title
        # Remove content in parentheses
        cleaned = re.sub(r'\([^)]*\)', '', cleaned)
        # Remove season information
        cleaned = re.sub(r'\s+Season\s+\d+.*', '', cleaned, flags=re.IGNORECASE)
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        # Remove trailing punctuation
        cleaned = cleaned.strip(' -:')

        return cleaned

    def _search_qdmovie(self, title: str) -> Optional[Dict]:
        """Search for content using qdMovieAPI"""
        try:
            clean_title = self._clean_title_for_search(title)

            # Try multiple search strategies
            search_queries = [clean_title]

            # Also try original title if different
            if clean_title != title:
                search_queries.append(title)

            for query in search_queries:
                try:
                    url = f"{self.api_url}/search?q={requests.utils.quote(query)}"
                    data = self._fetch_with_retry(url)

                    if data and isinstance(data, dict):
                        # qdMovieAPI returns {titles: [...]}
                        if 'titles' in data and len(data['titles']) > 0:
                            return data['titles'][0]
                        # Check if we have results (other format)
                        elif 'results' in data and len(data['results']) > 0:
                            return data['results'][0]
                        # Some APIs might return data directly
                        elif 'id' in data or 'imdb_id' in data:
                            return data
                    elif data and isinstance(data, list) and len(data) > 0:
                        return data[0]

                except:
                    continue

            return None
        except Exception as e:
            print(f"    Search error: {str(e)[:50]}")
            return None

    def _get_movie_details(self, imdb_id: str) -> Optional[Dict]:
        """Get full content details from qdMovieAPI"""
        try:
            # Clean the IMDB ID (remove 'tt' prefix if present)
            clean_id = imdb_id.replace('tt', '')

            url = f"{self.api_url}/movie/{clean_id}"
            data = self._fetch_with_retry(url)

            return data if data else None
        except Exception as e:
            print(f"    Details error: {str(e)[:50]}")
            return None

    def _extract_poster_from_details(self, details: Dict) -> Optional[str]:
        """Extract poster URL from content details"""
        # Try common fields where poster might be stored
        poster_fields = ['cover_url', 'poster', 'poster_url', 'image', 'cover', 'coverUrl', 'Poster']

        for field in poster_fields:
            if field in details and details[field]:
                poster = details[field]
                if isinstance(poster, str) and poster.startswith('http'):
                    return poster

        return None

    def load_data(self, filename='ottplay_complete_no_deeplink.json'):
        """Load OTTPlay data from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            # Extract content array
            self.content_list = self.data.get('content', [])

            print(f"✓ Loaded {len(self.content_list)} items from {filename}")
            print(f"  Source: {self.data.get('source_url', 'Unknown')}")
            print(f"  Scraped at: {self.data.get('scraped_at', 'Unknown')}\n")
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
            exit(1)

    def enrich_content(self):
        """Enrich content with qdMovieAPI (IMDB) data"""
        print("="*60)
        print("ENRICHING OTTPLAY CONTENT WITH QDMOVIEAPI (IMDB DATA)")
        if self.force:
            print(" (FORCE MODE - Re-enriching all items)")
        print("="*60 + "\n")

        # Find items that need enrichment
        if self.force:
            items_to_enrich = self.content_list
        else:
            items_to_enrich = [
                item for item in self.content_list
                if not item.get('posters') or not item.get('imdb_id')
            ]

        print(f"Total items: {len(self.content_list)}")
        print(f"Items {'to re-enrich' if self.force else 'needing enrichment'}: {len(items_to_enrich)}\n")

        if not items_to_enrich:
            print("✅ All items already enriched!")
            return

        enriched_count = 0
        poster_count = 0
        imdb_count = 0
        metadata_count = 0

        for i, item in enumerate(items_to_enrich, 1):
            title = item.get('title', 'Unknown')
            title_type = item.get('title_type', 'unknown')

            print(f"[{i}/{len(items_to_enrich)}] {title[:45]}... ({title_type}) ", end='', flush=True)

            try:
                # Track what we already have (unless force mode)
                has_imdb = bool(item.get('imdb_id')) and not self.force
                has_poster = bool(item.get('posters')) and not self.force

                # Step 1: Search for the content
                search_result = self._search_qdmovie(title)

                if not search_result:
                    print("✗ Not found")
                    continue

                # Extract IMDB ID from search result
                imdb_id = None
                for field in ['id', 'imdb_id', 'imdbID', 'imdbId']:
                    if field in search_result and search_result[field]:
                        imdb_id = str(search_result[field])
                        break

                if not imdb_id:
                    print("✗ No IMDB ID")
                    continue

                # Ensure IMDB ID has 'tt' prefix
                if not imdb_id.startswith('tt'):
                    imdb_id = f"tt{imdb_id}"

                # Store IMDB ID if we don't have it
                if not has_imdb:
                    item['imdb_id'] = imdb_id
                    imdb_count += 1

                # Try to get poster from search result first (faster)
                poster_url = None
                if not has_poster:
                    poster_url = self._extract_poster_from_details(search_result)
                    if poster_url:
                        item['posters'] = {
                            'thumbnail': poster_url,
                            'small': poster_url,
                            'medium': poster_url,
                            'large': poster_url,
                            'xlarge': poster_url,
                            'original': poster_url
                        }
                        item['poster_url_medium'] = poster_url
                        item['poster_url_large'] = poster_url
                        item['poster_source'] = 'imdb'
                        poster_count += 1
                        has_poster = True

                # Step 2: Get full content details
                details = self._get_movie_details(imdb_id)

                if details:
                    # Extract various metadata
                    added_metadata = False

                    # Description/Plot (only if better than current)
                    for field in ['plot', 'overview', 'description', 'Plot']:
                        if field in details and details[field]:
                            plot = details[field]
                            # Only update if current description is generic OTTplay template
                            current_desc = item.get('description', '')
                            if 'Watch' in current_desc and 'full movie online in HD on OTTplay' in current_desc:
                                item['description'] = plot
                                item['overview'] = plot
                                added_metadata = True
                                break
                            elif not current_desc:
                                item['description'] = plot
                                item['overview'] = plot
                                added_metadata = True
                                break

                    # Genres (merge with existing if present)
                    for field in ['genres', 'genre', 'Genre']:
                        if field in details and details[field]:
                            genres = details[field]
                            if isinstance(genres, str):
                                item['genres'] = [g.strip() for g in genres.split(',')]
                            elif isinstance(genres, list):
                                item['genres'] = genres
                            added_metadata = True
                            break

                    # Rating
                    for field in ['rating', 'imdbRating', 'imdb_rating', 'Rating']:
                        if field in details and details[field]:
                            try:
                                item['imdb_rating'] = float(details[field])
                                added_metadata = True
                            except:
                                pass
                            break

                    # Runtime
                    for field in ['runtime', 'Runtime', 'duration']:
                        if field in details and details[field]:
                            item['runtime'] = details[field]
                            added_metadata = True
                            break

                    # Year
                    for field in ['year', 'Year', 'releaseDate', 'release_date']:
                        if field in details and details[field]:
                            item['year'] = details[field]
                            added_metadata = True
                            break

                    # Director
                    for field in ['director', 'Director', 'directors']:
                        if field in details and details[field]:
                            directors = details[field]
                            if isinstance(directors, str):
                                item['directors'] = [d.strip() for d in directors.split(',')]
                            elif isinstance(directors, list):
                                item['directors'] = directors
                            added_metadata = True
                            break

                    # Cast/Actors
                    for field in ['actors', 'Actors', 'cast']:
                        if field in details and details[field]:
                            actors = details[field]
                            if isinstance(actors, str):
                                item['actors'] = [a.strip() for a in actors.split(',')]
                            elif isinstance(actors, list):
                                item['actors'] = actors
                            added_metadata = True
                            break

                    # Poster - only if we don't have one
                    if not has_poster:
                        poster_url = self._extract_poster_from_details(details)

                        if poster_url:
                            item['posters'] = {
                                'thumbnail': poster_url,
                                'small': poster_url,
                                'medium': poster_url,
                                'large': poster_url,
                                'xlarge': poster_url,
                                'original': poster_url
                            }
                            item['poster_url_medium'] = poster_url
                            item['poster_url_large'] = poster_url
                            item['poster_source'] = 'imdb'
                            poster_count += 1

                    if added_metadata:
                        metadata_count += 1

                    enriched_count += 1

                    status_parts = []
                    if not has_imdb:
                        status_parts.append("IMDB")
                    if poster_url:
                        status_parts.append("poster")
                    if added_metadata:
                        status_parts.append("metadata")

                    print(f"✓ {' + '.join(status_parts) if status_parts else 'enriched'}")
                else:
                    if not has_imdb:
                        print("✓ IMDB ID only")
                    else:
                        print("⊙ No details")

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"✗ Error: {str(e)[:40]}")

        # Update the data structure
        self.data['content'] = self.content_list
        self.data['enriched_at'] = datetime.now().isoformat()

        print(f"\n✅ Enriched {enriched_count}/{len(items_to_enrich)} items")
        print(f"   • Added IMDB IDs: {imdb_count}")
        print(f"   • Added posters: {poster_count}")
        print(f"   • Added metadata: {metadata_count}")

    def save(self, filename='ottplay_complete_enriched.json'):
        """Save enriched data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved: {filename}")

        # Final summary
        total_with_imdb = sum(1 for item in self.content_list if item.get('imdb_id'))
        total_with_posters = sum(1 for item in self.content_list if item.get('posters'))
        total_with_rating = sum(1 for item in self.content_list if item.get('imdb_rating'))

        print(f"\n📊 Final status:")
        print(f"   • Total items: {len(self.content_list)}")
        print(f"   • Items with IMDB IDs: {total_with_imdb}/{len(self.content_list)}")
        print(f"   • Items with posters: {total_with_posters}/{len(self.content_list)}")
        print(f"   • Items with IMDB ratings: {total_with_rating}/{len(self.content_list)}")


def main():
    parser = argparse.ArgumentParser(description='Enrich OTTPlay content using qdMovieAPI')
    parser.add_argument('--api-url', default='http://127.0.0.1:5000',
                        help='qdMovieAPI URL (default: http://127.0.0.1:5000)')
    parser.add_argument('--input', default='ottplay_complete_no_deeplink.json',
                        help='Input JSON file (default: ottplay_complete_no_deeplink.json)')
    parser.add_argument('--output', default='ottplay_complete_enriched.json',
                        help='Output JSON file (default: ottplay_complete_enriched.json)')
    parser.add_argument('--test', action='store_true',
                        help='Test mode: process only first 5 items')
    parser.add_argument('--force', action='store_true',
                        help='Force re-enrichment of all items, even if already enriched')

    args = parser.parse_args()

    print("\n" + "="*60)
    print("OTTPLAY CONTENT ENRICHER WITH QDMOVIEAPI")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    enricher = OTTPlayEnricher(api_url=args.api_url, test_mode=args.test, force=args.force)
    enricher.load_data(args.input)

    if args.test and len(enricher.content_list) > 5:
        print(f"🧪 TEST MODE: Processing only first 5 items (out of {len(enricher.content_list)})\n")
        enricher.content_list = enricher.content_list[:5]
        enricher.data['content'] = enricher.content_list

    enricher.enrich_content()
    enricher.save(args.output)

    print("\n" + "="*60)
    print("✅ ENRICHMENT COMPLETE")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
