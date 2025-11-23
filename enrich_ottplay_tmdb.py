#!/usr/bin/env python3
"""
OTTPlay Content Enrichment Script using TMDB API
Enriches ottplay_complete_no_deeplink.json with TMDB data

Prerequisites:
    export TMDB_API_KEY='your_key_here'

Usage:
    python3 enrich_ottplay_tmdb.py [--test] [--force]

    --test: Process only first 5 items
    --force: Re-enrich all items, even if already enriched
"""

import json
import os
import re
import sys
import time
import argparse
import requests
from typing import Dict, List, Optional
from datetime import datetime


class OTTPlayTMDBEnricher:
    """Enrich OTTPlay content using TMDB API"""

    def __init__(self, test_mode=False, force=False):
        self.test_mode = test_mode
        self.force = force
        self.data = {}
        self.content_list = []

        # TMDB API (required)
        self.tmdb_api_key = os.environ.get('TMDB_API_KEY')
        if not self.tmdb_api_key:
            print("\n❌ TMDB_API_KEY environment variable not set")
            print("💡 Set it with: export TMDB_API_KEY='your_key_here'")
            print("   Or: export TMDB_API_KEY=\"452357e5da52e2ddde20c64414a40637\"")
            sys.exit(1)

        print(f"✓ TMDB API key configured\n")

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

    def _fetch_with_retry(self, url, params, max_retries=3):
        """Fetch URL with retry logic"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                return response.json()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                    continue
                else:
                    raise
            except Exception:
                raise

    def _search_tmdb(self, item: Dict) -> Optional[Dict]:
        """Search TMDB with multiple strategies"""
        title = item.get('title', '')
        title_type = item.get('title_type', 'movie')
        clean_title = self._clean_title_for_search(title)

        # Determine search type based on title_type
        # Use 'multi' for flexible search, or 'movie'/'tv' for specific
        search_type = 'multi'

        # Try multiple search strategies
        search_queries = [clean_title]

        # Also try original title if different
        if clean_title != title:
            search_queries.append(title)

        for query in search_queries:
            try:
                url = f"https://api.themoviedb.org/3/search/{search_type}"
                params = {
                    'api_key': self.tmdb_api_key,
                    'query': query,
                    'language': 'en-US'
                }

                data = self._fetch_with_retry(url, params)

                if data.get('results') and len(data['results']) > 0:
                    # Filter by title_type if specified
                    results = data['results']
                    if title_type == 'movie':
                        movie_results = [r for r in results if r.get('media_type') == 'movie']
                        if movie_results:
                            return movie_results[0]
                    elif title_type == 'show':
                        tv_results = [r for r in results if r.get('media_type') == 'tv']
                        if tv_results:
                            return tv_results[0]

                    # Fallback to first result
                    return results[0]
            except:
                continue

        return None

    def _get_tmdb_details(self, tmdb_id: int, media_type: str) -> Optional[Dict]:
        """Get full content details from TMDB"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
            params = {
                'api_key': self.tmdb_api_key,
                'language': 'en-US'
            }
            return self._fetch_with_retry(url, params)
        except:
            return None

    def _get_tmdb_external_ids(self, tmdb_id: int, media_type: str) -> Optional[Dict]:
        """Get external IDs (IMDb, etc.) from TMDB"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/external_ids"
            params = {'api_key': self.tmdb_api_key}
            return self._fetch_with_retry(url, params)
        except:
            return None

    def _get_tmdb_images(self, tmdb_id: int, media_type: str, image_type: str) -> List[str]:
        """Get all images (posters or backdrops) from TMDB - prefer Indian/English"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/images"
            # Don't specify language to get all images
            params = {'api_key': self.tmdb_api_key}

            data = self._fetch_with_retry(url, params)

            if image_type == 'posters':
                images = data.get('posters', [])
            else:
                images = data.get('backdrops', [])

            # Preferred languages for Indian region (in priority order)
            preferred_languages = ['en', 'hi', 'ta', 'te', 'ml', 'kn', 'mr', None]  # None = no language tag

            # Separate images by language preference
            prioritized_images = []
            other_images = []

            for img in images:
                lang = img.get('iso_639_1')
                if lang in preferred_languages:
                    # Add priority score based on language preference
                    priority = preferred_languages.index(lang) if lang in preferred_languages else 100
                    img['_priority'] = priority
                    prioritized_images.append(img)
                else:
                    # Non-preferred language (e.g., Chinese, Korean, etc.)
                    img['_priority'] = 1000
                    other_images.append(img)

            # Sort prioritized images by: 1) language priority, 2) vote average
            prioritized_images.sort(key=lambda x: (x.get('_priority', 100), -x.get('vote_average', 0)))

            # Sort other images by vote average
            other_images.sort(key=lambda x: x.get('vote_average', 0), reverse=True)

            # Combine: preferred languages first, then others
            all_images = prioritized_images + other_images

            # Return file paths
            return [img['file_path'] for img in all_images if img.get('file_path')]

        except:
            return []

    def _get_tmdb_credits(self, tmdb_id: int, media_type: str) -> Optional[Dict]:
        """Get cast and crew from TMDB"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/credits"
            params = {'api_key': self.tmdb_api_key}
            return self._fetch_with_retry(url, params)
        except:
            return None

    def _get_tmdb_videos(self, tmdb_id: int, media_type: str) -> List[Dict]:
        """Get videos (trailers) from TMDB"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/videos"
            params = {
                'api_key': self.tmdb_api_key,
                'language': 'en-US'
            }
            data = self._fetch_with_retry(url, params)
            return data.get('results', [])
        except:
            return []

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
            sys.exit(1)

    def enrich_content(self):
        """Enrich content with TMDB data"""
        print("="*60)
        print("ENRICHING OTTPLAY CONTENT WITH TMDB DATA")
        if self.force:
            print(" (FORCE MODE - Re-enriching all items)")
        print("="*60 + "\n")

        # Find items that need enrichment
        if self.force:
            items_to_enrich = self.content_list
        else:
            items_to_enrich = [
                item for item in self.content_list
                if not item.get('posters') or not item.get('tmdb_id')
            ]

        print(f"Total items: {len(self.content_list)}")
        print(f"Items {'to re-enrich' if self.force else 'needing enrichment'}: {len(items_to_enrich)}\n")

        if not items_to_enrich:
            print("✅ All items already enriched!")
            return

        enriched_count = 0
        poster_count = 0
        tmdb_count = 0
        imdb_count = 0
        metadata_count = 0

        for i, item in enumerate(items_to_enrich, 1):
            title = item.get('title', 'Unknown')
            title_type = item.get('title_type', 'unknown')

            print(f"[{i}/{len(items_to_enrich)}] {title[:45]}... ({title_type}) ", end='', flush=True)

            try:
                # Track what we already have (unless force mode)
                has_tmdb = bool(item.get('tmdb_id')) and not self.force
                has_imdb = bool(item.get('imdb_id')) and not self.force
                has_poster = bool(item.get('posters')) and not self.force

                # Step 1: Search TMDB
                tmdb_result = self._search_tmdb(item)

                if not tmdb_result:
                    print("✗ Not found")
                    continue

                tmdb_id = tmdb_result['id']
                media_type = tmdb_result.get('media_type', 'movie')

                # Store basic TMDB data
                if not has_tmdb:
                    item['tmdb_id'] = tmdb_id
                    item['tmdb_media_type'] = media_type
                    tmdb_count += 1

                # Step 2: Get full details
                details = self._get_tmdb_details(tmdb_id, media_type)

                if details:
                    added_metadata = False

                    # Description/Overview (only if better than current)
                    overview = details.get('overview', '')
                    if overview:
                        current_desc = item.get('description', '')
                        # Only update if current description is generic OTTplay template
                        if 'Watch' in current_desc and 'full movie online in HD on OTTplay' in current_desc:
                            item['description'] = overview
                            item['overview'] = overview
                            added_metadata = True
                        elif not current_desc:
                            item['description'] = overview
                            item['overview'] = overview
                            added_metadata = True

                    # Genres
                    genres = details.get('genres', [])
                    if genres:
                        item['genres'] = [g['name'] for g in genres]
                        added_metadata = True

                    # Runtime
                    if media_type == 'movie':
                        runtime = details.get('runtime')
                        if runtime:
                            item['runtime'] = runtime
                            added_metadata = True

                    # TV-specific metadata
                    if media_type == 'tv':
                        item['episode_runtime'] = details.get('episode_run_time', [])
                        item['number_of_seasons'] = details.get('number_of_seasons')
                        item['number_of_episodes'] = details.get('number_of_episodes')
                        added_metadata = True

                    # Release dates
                    release_date = details.get('release_date') or details.get('first_air_date')
                    if release_date:
                        item['tmdb_release_date'] = release_date
                        # Extract year
                        try:
                            item['year'] = int(release_date.split('-')[0])
                            added_metadata = True
                        except:
                            pass

                    # Ratings
                    vote_average = details.get('vote_average')
                    if vote_average:
                        item['tmdb_rating'] = vote_average
                        added_metadata = True

                    item['tmdb_vote_count'] = details.get('vote_count')
                    item['status'] = details.get('status')
                    item['original_title'] = details.get('original_title') or details.get('original_name')
                    item['original_language'] = details.get('original_language')

                    if added_metadata:
                        metadata_count += 1

                # Step 3: Get external IDs (IMDb)
                if not has_imdb:
                    external_ids = self._get_tmdb_external_ids(tmdb_id, media_type)
                    if external_ids:
                        imdb_id = external_ids.get('imdb_id')
                        if imdb_id:
                            item['imdb_id'] = imdb_id
                            imdb_count += 1

                # Step 4: Get posters (prefer Indian/English, consistent size)
                if not has_poster:
                    posters = self._get_tmdb_images(tmdb_id, media_type, 'posters')
                    if posters:
                        # Use w500 for consistency (27:40 ratio, ~500x750px)
                        item['posters'] = {
                            'thumbnail': f"https://image.tmdb.org/t/p/w92{posters[0]}",
                            'small': f"https://image.tmdb.org/t/p/w185{posters[0]}",
                            'medium': f"https://image.tmdb.org/t/p/w342{posters[0]}",
                            'large': f"https://image.tmdb.org/t/p/w500{posters[0]}",
                            'xlarge': f"https://image.tmdb.org/t/p/w500{posters[0]}",  # Use w500 for consistency
                            'original': f"https://image.tmdb.org/t/p/w500{posters[0]}"  # Use w500 for consistency
                        }

                        item['all_posters'] = [
                            {
                                'thumbnail': f"https://image.tmdb.org/t/p/w92{p}",
                                'small': f"https://image.tmdb.org/t/p/w185{p}",
                                'medium': f"https://image.tmdb.org/t/p/w342{p}",
                                'large': f"https://image.tmdb.org/t/p/w500{p}",
                                'xlarge': f"https://image.tmdb.org/t/p/w500{p}",
                                'original': f"https://image.tmdb.org/t/p/w500{p}"
                            }
                            for p in posters[:5]
                        ]

                        item['poster_url_medium'] = item['posters']['medium']
                        item['poster_url_large'] = item['posters']['large']
                        item['poster_source'] = 'tmdb'
                        poster_count += 1

                # Step 5: Get backdrops
                backdrops = self._get_tmdb_images(tmdb_id, media_type, 'backdrops')
                if backdrops:
                    item['backdrops'] = {
                        'small': f"https://image.tmdb.org/t/p/w300{backdrops[0]}",
                        'medium': f"https://image.tmdb.org/t/p/w780{backdrops[0]}",
                        'large': f"https://image.tmdb.org/t/p/w1280{backdrops[0]}",
                        'original': f"https://image.tmdb.org/t/p/original{backdrops[0]}"
                    }

                    item['all_backdrops'] = [
                        {
                            'small': f"https://image.tmdb.org/t/p/w300{b}",
                            'medium': f"https://image.tmdb.org/t/p/w780{b}",
                            'large': f"https://image.tmdb.org/t/p/w1280{b}",
                            'original': f"https://image.tmdb.org/t/p/original{b}"
                        }
                        for b in backdrops[:5]
                    ]

                    item['backdrop_url'] = item['backdrops']['original']

                # Step 6: Get cast and crew
                credits = self._get_tmdb_credits(tmdb_id, media_type)
                if credits:
                    cast = credits.get('cast', [])
                    crew = credits.get('crew', [])

                    item['cast'] = [
                        {
                            'name': c['name'],
                            'character': c.get('character', ''),
                            'profile_path': f"https://image.tmdb.org/t/p/w185{c['profile_path']}" if c.get('profile_path') else None
                        }
                        for c in cast[:10]
                    ]

                    directors = [c['name'] for c in crew if c.get('job') == 'Director']
                    if directors:
                        item['directors'] = directors

                    writers = [c['name'] for c in crew if c.get('job') in ['Writer', 'Screenplay']]
                    if writers:
                        item['writers'] = writers[:5]

                # Step 7: Get videos (trailers)
                videos = self._get_tmdb_videos(tmdb_id, media_type)
                if videos:
                    trailers = [v for v in videos if v.get('type') == 'Trailer' and v.get('site') == 'YouTube']
                    if trailers:
                        official_trailer = next((t for t in trailers if t.get('official')), trailers[0])
                        item['youtube_id'] = official_trailer['key']
                        item['youtube_url'] = f"https://www.youtube.com/watch?v={official_trailer['key']}"
                        item['youtube_title'] = official_trailer.get('name', '')

                enriched_count += 1

                status_parts = []
                if not has_tmdb:
                    status_parts.append("TMDB")
                if not has_imdb and item.get('imdb_id'):
                    status_parts.append("IMDB")
                if not has_poster and item.get('posters'):
                    status_parts.append("poster")
                if metadata_count:
                    status_parts.append("metadata")

                print(f"✓ {' + '.join(status_parts) if status_parts else 'complete'}")

                time.sleep(0.25)  # Rate limiting

            except Exception as e:
                print(f"✗ Error: {str(e)[:40]}")

        # Update the data structure
        self.data['content'] = self.content_list
        self.data['enriched_at'] = datetime.now().isoformat()

        print(f"\n✅ Enriched {enriched_count}/{len(items_to_enrich)} items")
        print(f"   • Added TMDB IDs: {tmdb_count}")
        print(f"   • Added IMDB IDs: {imdb_count}")
        print(f"   • Added posters: {poster_count}")
        print(f"   • Added metadata: {metadata_count}")

    def save(self, filename='ottplay_complete_enriched.json'):
        """Save enriched data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved: {filename}")

        # Final summary
        total_with_tmdb = sum(1 for item in self.content_list if item.get('tmdb_id'))
        total_with_imdb = sum(1 for item in self.content_list if item.get('imdb_id'))
        total_with_posters = sum(1 for item in self.content_list if item.get('posters'))
        total_with_rating = sum(1 for item in self.content_list if item.get('tmdb_rating'))

        print(f"\n📊 Final status:")
        print(f"   • Total items: {len(self.content_list)}")
        print(f"   • Items with TMDB IDs: {total_with_tmdb}/{len(self.content_list)}")
        print(f"   • Items with IMDB IDs: {total_with_imdb}/{len(self.content_list)}")
        print(f"   • Items with posters: {total_with_posters}/{len(self.content_list)}")
        print(f"   • Items with TMDB ratings: {total_with_rating}/{len(self.content_list)}")


def main():
    parser = argparse.ArgumentParser(description='Enrich OTTPlay content using TMDB API')
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
    print("OTTPLAY CONTENT ENRICHER WITH TMDB API")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    enricher = OTTPlayTMDBEnricher(test_mode=args.test, force=args.force)
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
