#!/usr/bin/env python3
"""
Re-enrich movies that are missing posters
"""

import asyncio
import json
import os
import time
import requests
from typing import Dict, List, Optional

try:
    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("\n💡 Install required packages:")
    print("   pip3 install playwright beautifulsoup4 requests")
    print("   playwright install chromium")
    exit(1)


class PosterReEnricher:
    """Re-enrich movies with missing posters"""

    def __init__(self):
        self.tmdb_api_key = os.environ.get('TMDB_API_KEY')
        if not self.tmdb_api_key:
            print("❌ TMDB_API_KEY environment variable not set")
            print("   export TMDB_API_KEY='your_key_here'")
            exit(1)

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

    async def _fetch_binged_poster(self, movie: Dict) -> Optional[str]:
        """Fallback: Fetch poster from Binged.com content page"""
        url = movie.get('url')
        if not url:
            return None

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                await asyncio.sleep(1)

                content = await page.content()
                await browser.close()

                soup = BeautifulSoup(content, 'html.parser')

                # Try multiple selectors for poster
                poster_selectors = [
                    'img.movie-poster', 'img.show-poster',
                    '.movie-image img', '.show-image img',
                    'img[alt*="poster"]', 'img[alt*="Poster"]'
                ]

                for selector in poster_selectors:
                    img = soup.select_one(selector)
                    if img:
                        poster_url = img.get('src') or img.get('data-src')
                        if poster_url and poster_url.startswith('http') and 'Binged.png' not in poster_url:
                            return poster_url

                # Try og:image
                og_image = soup.find('meta', property='og:image')
                if og_image:
                    poster_url = og_image.get('content')
                    if poster_url and poster_url.startswith('http') and 'Binged.png' not in poster_url:
                        return poster_url

        except Exception as e:
            print(f"    Error fetching from Binged: {str(e)[:50]}")

        return None

    async def re_enrich_missing_posters(self):
        """Re-enrich movies missing posters"""

        # Load current data
        with open('movies_enriched.json', 'r', encoding='utf-8') as f:
            movies = json.load(f)

        # Find movies without posters
        movies_without_posters = [m for m in movies if not m.get('posters')]

        print(f"Total movies: {len(movies)}")
        print(f"Movies missing posters: {len(movies_without_posters)}")

        if not movies_without_posters:
            print("✅ All movies have posters!")
            return

        print("\n" + "="*60)
        print("RE-ENRICHING POSTERS")
        print("="*60 + "\n")

        enriched_count = 0

        for i, movie in enumerate(movies_without_posters, 1):
            title = movie.get('title', 'Unknown')
            print(f"[{i}/{len(movies_without_posters)}] {title[:50]}... ", end='', flush=True)

            try:
                # If we have TMDB ID, try to get posters from TMDB
                if movie.get('tmdb_id') and movie.get('tmdb_media_type'):
                    tmdb_id = movie['tmdb_id']
                    media_type = movie['tmdb_media_type']

                    # Get posters
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

                        enriched_count += 1
                        print("✓ TMDB poster found")
                        time.sleep(0.25)
                        continue

                # Fallback: Try Binged.com
                binged_poster = await self._fetch_binged_poster(movie)
                if binged_poster:
                    movie['poster_url_medium'] = binged_poster
                    movie['poster_url_large'] = binged_poster
                    movie['posters'] = {
                        'thumbnail': binged_poster,
                        'small': binged_poster,
                        'medium': binged_poster,
                        'large': binged_poster,
                        'xlarge': binged_poster,
                        'original': binged_poster
                    }
                    movie['poster_source'] = 'binged'
                    enriched_count += 1
                    print("✓ Binged poster found")
                else:
                    print("✗ No poster found")

                time.sleep(0.5)

            except Exception as e:
                print(f"✗ Error: {str(e)[:40]}")

        # Save updated data
        with open('movies_enriched.json', 'w', encoding='utf-8') as f:
            json.dump(movies, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Re-enriched {enriched_count}/{len(movies_without_posters)} movies with posters")
        print(f"💾 Saved: movies_enriched.json")

        # Show summary
        movies_with_posters = sum(1 for m in movies if m.get('posters'))
        print(f"\n📊 Final status: {movies_with_posters}/{len(movies)} movies have posters")


async def main():
    enricher = PosterReEnricher()
    await enricher.re_enrich_missing_posters()


if __name__ == '__main__':
    asyncio.run(main())
