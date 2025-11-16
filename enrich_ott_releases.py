#!/usr/bin/env python3
"""
Enrich OTT Releases with TMDB data
Takes ott_releases.json and enriches it with comprehensive TMDB metadata

Usage:
    python3 enrich_ott_releases.py
"""

import json
import os
import re
import sys
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime


class OTTReleasesEnricher:
    """Enrich OTT releases with TMDB data"""

    def __init__(self):
        self.movies = []

        # TMDB API (required)
        self.tmdb_api_key = os.environ.get('TMDB_API_KEY')
        if not self.tmdb_api_key:
            print("\n❌ TMDB_API_KEY environment variable not set")
            print("💡 Set it with: export TMDB_API_KEY='your_key_here'")
            sys.exit(1)

        # Platform mapping for normalization
        self.platform_map = {
            'Platform 2': 'Aha Video',
            'Platform 4': 'Amazon Prime Video',
            'Platform 5': 'Apple TV+',
            'Platform 6': 'Sun NXT',
            'Platform 8': 'Zee5',
            'Platform 10': 'Jio Hotstar',
            'Platform 24': 'Mubi',
            'Platform 25': 'MX Player',
            'Platform 27': 'Manorama MAX',
            'Platform 30': 'Netflix',
            'Platform 49': 'YouTube',
            'Platform 53': 'Sony LIV',
        }

    def load_movies(self, filename='ott_releases.json'):
        """Load OTT releases from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.movies = json.load(f)
            print(f"✓ Loaded {len(self.movies)} OTT releases from {filename}\n")
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
            sys.exit(1)

    def _normalize_platforms(self):
        """Normalize platform names"""
        for movie in self.movies:
            if 'platforms' in movie:
                normalized = []
                for platform in movie['platforms']:
                    normalized_name = self.platform_map.get(platform, platform)
                    if normalized_name not in normalized:
                        normalized.append(normalized_name)
                movie['platforms'] = normalized

    def _clean_title_for_search(self, title):
        """Clean up title for better search results"""
        if not title:
            return title

        cleaned = title
        cleaned = re.sub(r'\([^)]*\)', '', cleaned)  # Remove parentheses
        cleaned = ' '.join(cleaned.split())  # Remove extra whitespace
        cleaned = cleaned.strip(' -:')  # Remove trailing punctuation

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

    def _search_tmdb(self, movie: Dict) -> Optional[Dict]:
        """Search TMDB with multiple strategies"""
        title = movie.get('title', '')
        clean_title = self._clean_title_for_search(title)

        # Try multiple search strategies
        search_queries = [clean_title]

        # Also try original title if different
        if clean_title != title:
            search_queries.append(title)

        for query in search_queries:
            try:
                url = "https://api.themoviedb.org/3/search/multi"
                params = {
                    'api_key': self.tmdb_api_key,
                    'query': query,
                    'language': 'en-US'
                }

                data = self._fetch_with_retry(url, params)

                if data.get('results') and len(data['results']) > 0:
                    return data['results'][0]
            except:
                continue

        return None

    def _get_tmdb_details(self, tmdb_id: int, media_type: str) -> Optional[Dict]:
        """Get full movie/show details from TMDB"""
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
        """Get all images (posters or backdrops) from TMDB"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/images"
            params = {'api_key': self.tmdb_api_key}

            data = self._fetch_with_retry(url, params)

            if image_type == 'posters':
                images = data.get('posters', [])
            else:
                images = data.get('backdrops', [])

            # Sort by vote average (quality)
            images.sort(key=lambda x: x.get('vote_average', 0), reverse=True)

            # Return file paths
            return [img['file_path'] for img in images if img.get('file_path')]

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

    def enrich(self):
        """Enrich OTT releases with TMDB data"""
        print("="*60)
        print("ENRICHING OTT RELEASES WITH TMDB DATA")
        print("="*60 + "\n")

        enriched_count = 0

        for i, movie in enumerate(self.movies, 1):
            title = movie.get('title', 'Unknown')
            print(f"[{i}/{len(self.movies)}] {title[:50]}... ", end='', flush=True)

            try:
                # Search TMDB
                tmdb_result = self._search_tmdb(movie)

                if not tmdb_result:
                    print("✗ Not found")
                    continue

                tmdb_id = tmdb_result['id']
                media_type = tmdb_result.get('media_type', 'movie')

                # Store basic TMDB data
                movie['tmdb_id'] = tmdb_id
                movie['tmdb_media_type'] = media_type

                # Get full details
                details = self._get_tmdb_details(tmdb_id, media_type)
                if details:
                    movie['overview'] = details.get('overview', '')
                    movie['description'] = details.get('overview', '')

                    genres = details.get('genres', [])
                    movie['genres'] = [g['name'] for g in genres]

                    if media_type == 'movie':
                        movie['runtime'] = details.get('runtime')

                    if media_type == 'tv':
                        movie['episode_runtime'] = details.get('episode_run_time', [])
                        movie['number_of_seasons'] = details.get('number_of_seasons')
                        movie['number_of_episodes'] = details.get('number_of_episodes')

                    movie['tmdb_release_date'] = details.get('release_date') or details.get('first_air_date')
                    movie['status'] = details.get('status')
                    movie['tmdb_rating'] = details.get('vote_average')
                    movie['tmdb_vote_count'] = details.get('vote_count')
                    movie['original_title'] = details.get('original_title') or details.get('original_name')
                    movie['original_language'] = details.get('original_language')

                # Get external IDs (IMDb)
                external_ids = self._get_tmdb_external_ids(tmdb_id, media_type)
                if external_ids:
                    imdb_id = external_ids.get('imdb_id')
                    if imdb_id:
                        movie['imdb_id'] = imdb_id

                # Get all posters
                posters = self._get_tmdb_images(tmdb_id, media_type, 'posters')
                if posters:
                    movie['posters'] = {
                        'thumbnail': f"https://image.tmdb.org/t/p/w92{posters[0]}",
                        'small': f"https://image.tmdb.org/t/p/w185{posters[0]}",
                        'medium': f"https://image.tmdb.org/t/p/w342{posters[0]}",
                        'large': f"https://image.tmdb.org/t/p/w500{posters[0]}",
                        'xlarge': f"https://image.tmdb.org/t/p/w780{posters[0]}",
                        'original': f"https://image.tmdb.org/t/p/original{posters[0]}"
                    }

                    movie['all_posters'] = [
                        {
                            'thumbnail': f"https://image.tmdb.org/t/p/w92{p}",
                            'small': f"https://image.tmdb.org/t/p/w185{p}",
                            'medium': f"https://image.tmdb.org/t/p/w342{p}",
                            'large': f"https://image.tmdb.org/t/p/w500{p}",
                            'xlarge': f"https://image.tmdb.org/t/p/w780{p}",
                            'original': f"https://image.tmdb.org/t/p/original{p}"
                        }
                        for p in posters[:5]
                    ]

                    movie['poster_url_medium'] = movie['posters']['medium']
                    movie['poster_url_large'] = movie['posters']['large']

                # Get all backdrops
                backdrops = self._get_tmdb_images(tmdb_id, media_type, 'backdrops')
                if backdrops:
                    movie['backdrops'] = {
                        'small': f"https://image.tmdb.org/t/p/w300{backdrops[0]}",
                        'medium': f"https://image.tmdb.org/t/p/w780{backdrops[0]}",
                        'large': f"https://image.tmdb.org/t/p/w1280{backdrops[0]}",
                        'original': f"https://image.tmdb.org/t/p/original{backdrops[0]}"
                    }

                    movie['all_backdrops'] = [
                        {
                            'small': f"https://image.tmdb.org/t/p/w300{b}",
                            'medium': f"https://image.tmdb.org/t/p/w780{b}",
                            'large': f"https://image.tmdb.org/t/p/w1280{b}",
                            'original': f"https://image.tmdb.org/t/p/original{b}"
                        }
                        for b in backdrops[:5]
                    ]

                    movie['backdrop_url'] = movie['backdrops']['original']

                # Get cast and crew
                credits = self._get_tmdb_credits(tmdb_id, media_type)
                if credits:
                    cast = credits.get('cast', [])
                    crew = credits.get('crew', [])

                    movie['cast'] = [
                        {
                            'name': c['name'],
                            'character': c.get('character', ''),
                            'profile_path': f"https://image.tmdb.org/t/p/w185{c['profile_path']}" if c.get('profile_path') else None
                        }
                        for c in cast[:10]
                    ]

                    directors = [c['name'] for c in crew if c.get('job') == 'Director']
                    movie['directors'] = directors

                    writers = [c['name'] for c in crew if c.get('job') in ['Writer', 'Screenplay']]
                    movie['writers'] = writers[:5]

                # Get videos (trailers)
                videos = self._get_tmdb_videos(tmdb_id, media_type)
                if videos:
                    trailers = [v for v in videos if v.get('type') == 'Trailer' and v.get('site') == 'YouTube']
                    if trailers:
                        official_trailer = next((t for t in trailers if t.get('official')), trailers[0])
                        movie['youtube_id'] = official_trailer['key']
                        movie['youtube_url'] = f"https://www.youtube.com/watch?v={official_trailer['key']}"
                        movie['youtube_title'] = official_trailer.get('name', '')

                enriched_count += 1
                print("✓ Complete")

                time.sleep(0.25)  # Rate limiting

            except Exception as e:
                print(f"✗ Error: {str(e)[:40]}")

        print(f"\n✅ Enriched {enriched_count}/{len(self.movies)} OTT releases with TMDB data\n")

    def save(self, filename='ott_releases_enriched.json'):
        """Save enriched data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.movies, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved: {filename}\n")

    def run(self):
        """Run the enrichment process"""
        print("\n" + "="*60)
        print("OTT RELEASES TMDB ENRICHER")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        self.load_movies()
        self._normalize_platforms()
        self.enrich()
        self.save()

        # Summary
        with_tmdb = sum(1 for m in self.movies if m.get('tmdb_id'))
        with_imdb = sum(1 for m in self.movies if m.get('imdb_id'))
        with_posters = sum(1 for m in self.movies if m.get('posters'))
        with_backdrops = sum(1 for m in self.movies if m.get('backdrops'))
        with_deeplinks = sum(1 for m in self.movies if m.get('deeplinks'))

        print("="*60)
        print("✅ ENRICHMENT COMPLETE")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   • Total OTT releases: {len(self.movies)}")
        print(f"   • With TMDB IDs: {with_tmdb}/{len(self.movies)}")
        print(f"   • With IMDb IDs: {with_imdb}/{len(self.movies)}")
        print(f"   • With posters: {with_posters}/{len(self.movies)}")
        print(f"   • With backdrops: {with_backdrops}/{len(self.movies)}")
        print(f"   • With deeplinks: {with_deeplinks}/{len(self.movies)}")
        print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    enricher = OTTReleasesEnricher()
    enricher.run()
