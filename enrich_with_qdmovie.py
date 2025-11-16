#!/usr/bin/env python3
"""
Alternative Enrichment Script using qdMovieAPI
Enriches movies with IMDB data via qdMovieAPI (https://github.com/tveronesi/qdMovieAPI)

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
    python3 enrich_with_qdmovie.py [--api-url URL] [--test]
"""

import asyncio
import json
import re
import time
import argparse
from typing import Dict, List, Optional
import requests


class QDMovieEnricher:
    """Enrich movies using qdMovieAPI (IMDB-based)"""

    def __init__(self, api_url="http://127.0.0.1:5000", test_mode=False, force=False, input_file="movies_enriched.json"):
        self.api_url = api_url.rstrip('/')
        self.test_mode = test_mode
        self.force = force
        self.input_file = input_file
        self.movies = []

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
        """Search for movie using qdMovieAPI"""
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
        """Get full movie details from qdMovieAPI"""
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
        """Extract poster URL from movie details"""
        # Try common fields where poster might be stored
        poster_fields = ['cover_url', 'poster', 'poster_url', 'image', 'cover', 'coverUrl', 'Poster']

        for field in poster_fields:
            if field in details and details[field]:
                poster = details[field]
                if isinstance(poster, str) and poster.startswith('http'):
                    return poster

        return None

    def load_movies(self, filename='movies_enriched.json'):
        """Load movies from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.movies = json.load(f)
            print(f"✓ Loaded {len(self.movies)} movies from {filename}\n")
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
            exit(1)

    async def enrich_movies(self):
        """Enrich movies with qdMovieAPI (IMDB) data"""
        print("="*60)
        print("ENRICHING WITH QDMOVIEAPI (IMDB DATA)")
        if self.force:
            print(" (FORCE MODE - Re-enriching all movies)")
        print("="*60 + "\n")

        # Find movies that need enrichment
        if self.force:
            movies_to_enrich = self.movies
        else:
            movies_to_enrich = [
                m for m in self.movies
                if not m.get('posters') or not m.get('imdb_id')
            ]

        print(f"Total movies: {len(self.movies)}")
        print(f"Movies {'to re-enrich' if self.force else 'needing enrichment'}: {len(movies_to_enrich)}\n")

        if not movies_to_enrich:
            print("✅ All movies already enriched!")
            return

        enriched_count = 0
        poster_count = 0
        imdb_count = 0

        for i, movie in enumerate(movies_to_enrich, 1):
            title = movie.get('title', 'Unknown')
            print(f"[{i}/{len(movies_to_enrich)}] {title[:50]}... ", end='', flush=True)

            try:
                # Track what we already have (unless force mode)
                has_imdb = bool(movie.get('imdb_id')) and not self.force
                has_poster = bool(movie.get('posters')) and not self.force

                # Step 1: Search for the movie
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
                    movie['imdb_id'] = imdb_id
                    imdb_count += 1

                # Try to get poster from search result first (faster)
                if not has_poster:
                    poster_url = self._extract_poster_from_details(search_result)
                    if poster_url:
                        movie['posters'] = {
                            'thumbnail': poster_url,
                            'small': poster_url,
                            'medium': poster_url,
                            'large': poster_url,
                            'xlarge': poster_url,
                            'original': poster_url
                        }
                        movie['poster_url_medium'] = poster_url
                        movie['poster_url_large'] = poster_url
                        movie['poster_source'] = 'imdb'
                        poster_count += 1
                        has_poster = True

                # Step 2: Get full movie details
                details = self._get_movie_details(imdb_id)

                if details:
                    # Extract various metadata

                    # Description/Plot
                    for field in ['plot', 'overview', 'description', 'Plot']:
                        if field in details and details[field]:
                            movie['description'] = details[field]
                            movie['overview'] = details[field]
                            break

                    # Genres
                    for field in ['genres', 'genre', 'Genre']:
                        if field in details and details[field]:
                            genres = details[field]
                            if isinstance(genres, str):
                                movie['genres'] = [g.strip() for g in genres.split(',')]
                            elif isinstance(genres, list):
                                movie['genres'] = genres
                            break

                    # Rating
                    for field in ['rating', 'imdbRating', 'imdb_rating', 'Rating']:
                        if field in details and details[field]:
                            try:
                                movie['imdb_rating'] = float(details[field])
                            except:
                                pass
                            break

                    # Runtime
                    for field in ['runtime', 'Runtime', 'duration']:
                        if field in details and details[field]:
                            movie['runtime'] = details[field]
                            break

                    # Year
                    for field in ['year', 'Year', 'releaseDate', 'release_date']:
                        if field in details and details[field]:
                            movie['year'] = details[field]
                            break

                    # Director
                    for field in ['director', 'Director', 'directors']:
                        if field in details and details[field]:
                            directors = details[field]
                            if isinstance(directors, str):
                                movie['directors'] = [d.strip() for d in directors.split(',')]
                            elif isinstance(directors, list):
                                movie['directors'] = directors
                            break

                    # Cast/Actors
                    for field in ['actors', 'Actors', 'cast']:
                        if field in details and details[field]:
                            actors = details[field]
                            if isinstance(actors, str):
                                movie['actors'] = [a.strip() for a in actors.split(',')]
                            elif isinstance(actors, list):
                                movie['actors'] = actors
                            break

                    # Poster - only if we don't have one
                    if not has_poster:
                        poster_url = self._extract_poster_from_details(details)

                        if poster_url:
                            movie['posters'] = {
                                'thumbnail': poster_url,
                                'small': poster_url,
                                'medium': poster_url,
                                'large': poster_url,
                                'xlarge': poster_url,
                                'original': poster_url
                            }
                            movie['poster_url_medium'] = poster_url
                            movie['poster_url_large'] = poster_url
                            movie['poster_source'] = 'imdb'
                            poster_count += 1

                    enriched_count += 1

                    status_parts = []
                    if not has_imdb:
                        status_parts.append("IMDB ID")
                    if not has_poster and poster_url:
                        status_parts.append("poster")
                    if details.get('plot') or details.get('overview'):
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

        # Save enriched data
        with open(self.input_file, 'w', encoding='utf-8') as f:
            json.dump(self.movies, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Enriched {enriched_count}/{len(movies_to_enrich)} movies")
        print(f"   • Added IMDB IDs: {imdb_count}")
        print(f"   • Added posters: {poster_count}")
        print(f"💾 Saved: {self.input_file}")

        # Final summary
        total_with_imdb = sum(1 for m in self.movies if m.get('imdb_id'))
        total_with_posters = sum(1 for m in self.movies if m.get('posters'))

        print(f"\n📊 Final status:")
        print(f"   • Movies with IMDB IDs: {total_with_imdb}/{len(self.movies)}")
        print(f"   • Movies with posters: {total_with_posters}/{len(self.movies)}")


async def main():
    parser = argparse.ArgumentParser(description='Enrich movies using qdMovieAPI')
    parser.add_argument('--api-url', default='http://127.0.0.1:5000',
                        help='qdMovieAPI URL (default: http://127.0.0.1:5000)')
    parser.add_argument('--input', default='movies_enriched.json',
                        help='Input JSON file (default: movies_enriched.json)')
    parser.add_argument('--test', action='store_true',
                        help='Test mode: process only first 3 movies')
    parser.add_argument('--force', action='store_true',
                        help='Force re-enrichment of all movies, even if already enriched')

    args = parser.parse_args()

    enricher = QDMovieEnricher(api_url=args.api_url, test_mode=args.test, force=args.force, input_file=args.input)
    enricher.load_movies(args.input)

    if args.test and len(enricher.movies) > 3:
        print(f"🧪 TEST MODE: Processing only first 3 movies (out of {len(enricher.movies)})\n")
        enricher.movies = enricher.movies[:3]

    await enricher.enrich_movies()


if __name__ == '__main__':
    asyncio.run(main())
