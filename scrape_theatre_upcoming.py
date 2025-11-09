#!/usr/bin/env python3
"""
BookMyShow Upcoming Theatre Releases Scraper
Scrapes upcoming theatre releases (filtered to end of 2025)

Usage:
    python3 scrape_theatre_upcoming.py [--city bengaluru] [--debug]
"""

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import re
import sys
import asyncio
import argparse
from typing import List, Dict, Optional
from datetime import datetime
from config import BMS_CONFIG, UPCOMING_THEATRE_DATE_RANGE


def parse_release_date(date_str: str) -> Optional[datetime]:
    """
    Parse various date formats to datetime object

    Args:
        date_str: Date string (e.g., "25 Dec 2025", "Dec 25, 2025")

    Returns:
        datetime object or None
    """
    date_patterns = [
        r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})',  # "25 Dec 2025"
        r'([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})',  # "Dec 25, 2025" or "Dec 25 2025"
        r'(\d{4})-(\d{1,2})-(\d{1,2})',  # "2025-12-25"
    ]

    for pattern in date_patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                if pattern == date_patterns[0]:  # "25 Dec 2025"
                    day, month, year = match.groups()
                    date_obj = datetime.strptime(f"{day} {month} {year}", "%d %b %Y")
                elif pattern == date_patterns[1]:  # "Dec 25, 2025"
                    month, day, year = match.groups()
                    date_obj = datetime.strptime(f"{day} {month} {year}", "%d %b %Y")
                elif pattern == date_patterns[2]:  # "2025-12-25"
                    year, month, day = match.groups()
                    date_obj = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")

                return date_obj
            except:
                continue

    return None


def should_include_movie(release_date_str: str, end_date: str) -> bool:
    """
    Check if movie should be included based on release date

    Args:
        release_date_str: Release date string from movie data
        end_date: End date cutoff (format: YYYY-MM-DD)

    Returns:
        True if movie should be included
    """
    if not release_date_str:
        return True  # Include if no date (can't filter)

    movie_date = parse_release_date(release_date_str)
    if not movie_date:
        return True  # Include if can't parse

    try:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        return movie_date <= end_date_obj
    except:
        return True  # Include if end_date parsing fails


async def auto_scroll_page(page, max_scrolls: int = 10, debug: bool = False):
    """
    Auto-scroll page to load all lazy-loaded content

    Args:
        page: Playwright page object
        max_scrolls: Maximum number of scroll iterations
        debug: Enable debug output
    """
    if debug:
        print("  Auto-scrolling to load all content...", file=sys.stderr)

    previous_height = 0
    for i in range(max_scrolls):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

        new_height = await page.evaluate("document.body.scrollHeight")

        if debug:
            print(f"    Scroll {i+1}/{max_scrolls}: Height {new_height}px", file=sys.stderr)

        if new_height == previous_height:
            if debug:
                print("    Reached end of content", file=sys.stderr)
            break

        previous_height = new_height

    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(1)


async def extract_trailer_from_detail_page(page, detail_url: str, debug: bool = False) -> Optional[str]:
    """
    Extract the first official trailer YouTube URL from movie detail page

    Args:
        page: Playwright page object
        detail_url: URL of the movie detail page
        debug: Enable debug output

    Returns:
        YouTube URL or None
    """
    try:
        if debug:
            print(f"      Extracting trailer from detail page...", file=sys.stderr)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Method 1: YouTube iframe embeds
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '')
            if 'youtube.com/embed/' in src or 'youtube-nocookie.com/embed/' in src:
                match = re.search(r'/embed/([a-zA-Z0-9_-]+)', src)
                if match:
                    video_id = match.group(1)
                    youtube_url = f'https://www.youtube.com/watch?v={video_id}'
                    if debug:
                        print(f"      Found trailer (iframe): {youtube_url}", file=sys.stderr)
                    return youtube_url

        # Method 2: YouTube links
        links = soup.find_all('a', href=re.compile(r'youtube\.com/watch'))
        for link in links:
            href = link.get('href', '')
            if 'youtube.com/watch' in href:
                if debug:
                    print(f"      Found trailer (link): {href}", file=sys.stderr)
                return href

        # Method 3: Trailer buttons with onclick/data attributes
        trailer_elements = soup.find_all(['a', 'button', 'div'], class_=re.compile(r'trailer|video', re.I))
        for elem in trailer_elements:
            onclick = elem.get('onclick', '')
            if 'youtube.com' in onclick:
                match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)', onclick)
                if match:
                    video_id = match.group(1)
                    youtube_url = f'https://www.youtube.com/watch?v={video_id}'
                    if debug:
                        print(f"      Found trailer (onclick): {youtube_url}", file=sys.stderr)
                    return youtube_url

            for attr in elem.attrs:
                if 'video' in attr.lower() or 'youtube' in attr.lower():
                    value = elem.get(attr, '')
                    if isinstance(value, str) and len(value) == 11:
                        youtube_url = f'https://www.youtube.com/watch?v={value}'
                        if debug:
                            print(f"      Found trailer (data attr): {youtube_url}", file=sys.stderr)
                        return youtube_url

        if debug:
            print("      No trailer found on detail page", file=sys.stderr)

    except Exception as e:
        if debug:
            print(f"      Error extracting trailer: {e}", file=sys.stderr)

    return None


async def extract_movie_details(page, movie_url: str, debug: bool = False) -> Dict:
    """
    Extract detailed information from a movie's detail page

    Args:
        page: Playwright page object
        movie_url: URL of the movie detail page
        debug: Enable debug output

    Returns:
        Dictionary with movie details
    """
    details = {}

    try:
        if debug:
            print(f"    Navigating to: {movie_url}", file=sys.stderr)

        await page.goto(movie_url, wait_until='domcontentloaded', timeout=BMS_CONFIG['detail_page_timeout'])
        await asyncio.sleep(2)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Extract title
        title_elem = soup.find('h1') or soup.find(['h1', 'h2'], class_=re.compile(r'title|name', re.I))
        if title_elem:
            details['title'] = title_elem.get_text(strip=True)

        # Extract metadata
        info_elements = soup.find_all(['span', 'div', 'p'], class_=re.compile(r'info|meta|detail', re.I))

        for elem in info_elements:
            text = elem.get_text(strip=True)

            # Duration
            duration_match = re.search(r'(\d+h\s*\d*m?|\d+\s*mins?)', text, re.I)
            if duration_match and 'duration' not in details:
                details['duration'] = duration_match.group(1)

            # CBFC Rating
            cbfc_match = re.search(r'\b(U/A|UA|U|A)\b', text)
            if cbfc_match and 'cbfc_rating' not in details:
                details['cbfc_rating'] = cbfc_match.group(1)

            # Release date
            date_match = re.search(r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})', text, re.I)
            if date_match and 'release_date' not in details:
                details['release_date'] = date_match.group(1)

        # Extract video formats
        format_elements = soup.find_all(['button', 'span', 'div', 'a'], class_=re.compile(r'format|dimension|experience', re.I))

        formats = []
        format_pattern = re.compile(r'\b(2D|3D|IMAX\s*3D|IMAX\s*2D|IMAX|DOLBY\s*CINEMA\s*3D|DOLBY\s*CINEMA|DOLBY\s*ATMOS|4DX\s*3D|4DX|MX4D\s*3D|MX4D|ICE\s*3D|ICE|SCREEN\s*X|3D\s*SCREEN\s*X)\b', re.I)

        for elem in format_elements:
            text = elem.get_text(strip=True)
            matches = format_pattern.findall(text)
            for match in matches:
                normalized_format = match.strip().upper()
                if normalized_format not in formats:
                    formats.append(normalized_format)

        # Also check in page text
        page_text = soup.get_text()
        format_matches = format_pattern.findall(page_text)
        for match in format_matches:
            normalized_format = match.strip().upper()
            if normalized_format not in formats:
                formats.append(normalized_format)

        if formats:
            details['video_formats'] = formats

        # Extract booking link
        book_button = soup.find(['a', 'button'], class_=re.compile(r'book|ticket', re.I))
        if book_button:
            href = book_button.get('href', '')
            if href:
                if href.startswith('/'):
                    href = 'https://in.bookmyshow.com' + href
                details['booking_link'] = href

        # Extract trailer
        trailer_url = await extract_trailer_from_detail_page(page, movie_url, debug=debug)
        if trailer_url:
            details['trailer_bms_url'] = trailer_url

        if debug:
            print(f"    Extracted details: {details.get('title', 'N/A')}", file=sys.stderr)
            if details.get('video_formats'):
                print(f"      Formats: {', '.join(details['video_formats'])}", file=sys.stderr)

    except Exception as e:
        if debug:
            print(f"    Error extracting details: {e}", file=sys.stderr)

    return details


async def scrape_theatre_upcoming(city: str = 'bengaluru', debug: bool = False) -> List[Dict]:
    """
    Scrape upcoming theatre releases from BookMyShow (filtered to end of 2025)

    Args:
        city: City code (e.g., 'bengaluru', 'mumbai')
        debug: Enable debug mode

    Returns:
        List of movie dictionaries
    """
    all_movies = []

    # Get city configuration
    city_config = BMS_CONFIG['cities'].get(city)
    if not city_config:
        print(f"Error: Unknown city '{city}'", file=sys.stderr)
        print(f"Available cities: {', '.join(BMS_CONFIG['cities'].keys())}", file=sys.stderr)
        return []

    city_code = city_config['code']
    city_name = city_config['display_name']

    url = f"https://in.bookmyshow.com/explore/upcoming-movies-{city_code}?referrerBase=movies&cat=MT"

    print(f"Scraping upcoming movies for {city_name}...", file=sys.stderr)
    print(f"Filtering to releases before {UPCOMING_THEATRE_DATE_RANGE['end_date']}", file=sys.stderr)
    print("Starting browser...", file=sys.stderr)

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = await context.new_page()

            # Avoid detection
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """)

            print("Navigating to page...", file=sys.stderr)
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)

            print("Waiting for content...", file=sys.stderr)
            await asyncio.sleep(3)

            # Auto-scroll to load all movies
            await auto_scroll_page(page, max_scrolls=BMS_CONFIG['scroll_iterations'], debug=debug)

            print("Extracting movie list...", file=sys.stderr)
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Find movie links
            movie_links = []

            # Method 1: Links with 'movies' in URL
            all_links = soup.find_all('a', href=re.compile(r'/movies/[^/]+/ET\d+'))
            for link in all_links:
                href = link.get('href', '')
                if href and '/movies/' in href:
                    if href.startswith('/'):
                        href = 'https://in.bookmyshow.com' + href
                    if href not in movie_links:
                        movie_links.append(href)

            # Method 2: Movie cards
            movie_cards = soup.find_all(['div', 'article'], class_=re.compile(r'movie-card|movie|film', re.I))
            for card in movie_cards:
                link = card.find('a', href=True)
                if link:
                    href = link.get('href', '')
                    if href and '/movies/' in href:
                        if href.startswith('/'):
                            href = 'https://in.bookmyshow.com' + href
                        if href not in movie_links:
                            movie_links.append(href)

            print(f"Found {len(movie_links)} movies", file=sys.stderr)

            if debug and len(movie_links) == 0:
                await page.screenshot(path='debug_theatre_upcoming.png', full_page=True)
                print("Saved screenshot to debug_theatre_upcoming.png", file=sys.stderr)

            # Extract details from each movie
            filtered_count = 0
            for idx, movie_url in enumerate(movie_links, 1):
                print(f"\n[{idx}/{len(movie_links)}] Processing movie...", file=sys.stderr)

                details = await extract_movie_details(page, movie_url, debug=debug)

                if details.get('title'):
                    # Check if movie should be included (date filter)
                    release_date = details.get('release_date', '')
                    if should_include_movie(release_date, UPCOMING_THEATRE_DATE_RANGE['end_date']):
                        movie_data = {
                            'content_type': 'theatre_upcoming',
                            'location': city_name,
                            'detail_url': movie_url,
                            **details
                        }
                        all_movies.append(movie_data)
                    else:
                        filtered_count += 1
                        if debug:
                            print(f"    Filtered out: {details['title']} (releases after 2025)", file=sys.stderr)

                # Rate limiting
                await asyncio.sleep(BMS_CONFIG['request_delay'])

            await browser.close()

            print(f"\n{'='*60}", file=sys.stderr)
            print(f"Scraped {len(all_movies)} upcoming theatre movies for {city_name}", file=sys.stderr)
            print(f"Filtered out {filtered_count} movies releasing after 2025", file=sys.stderr)
            print(f"{'='*60}\n", file=sys.stderr)

        except Exception as e:
            print(f"Error during scraping: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)

    return all_movies


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Scrape upcoming theatre releases from BookMyShow')
    parser.add_argument('--city', type=str, default='bengaluru',
                       choices=list(BMS_CONFIG['cities'].keys()),
                       help='City to scrape (default: bengaluru)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (screenshots, verbose output)')
    args = parser.parse_args()

    print("="*60, file=sys.stderr)
    print("BookMyShow Upcoming Theatre Releases Scraper", file=sys.stderr)
    print("="*60, file=sys.stderr)

    movies = asyncio.run(scrape_theatre_upcoming(city=args.city, debug=args.debug))

    print("="*60, file=sys.stderr)
    print(f"Successfully scraped {len(movies)} upcoming theatre movies", file=sys.stderr)
    print("="*60, file=sys.stderr)

    if movies:
        # Output JSON to stdout
        print(json.dumps(movies, indent=2, ensure_ascii=False))

        # Save to file
        output_file = f'theatre_upcoming_{args.city}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(movies, f, indent=2, ensure_ascii=False)

        print(f"\nData saved to {output_file}", file=sys.stderr)
        print(f"Total movies: {len(movies)}", file=sys.stderr)

        # Stats
        with_trailers = sum(1 for m in movies if m.get('trailer_bms_url'))
        with_formats = sum(1 for m in movies if m.get('video_formats'))
        print(f"Movies with trailers: {with_trailers}/{len(movies)}", file=sys.stderr)
        print(f"Movies with video formats: {with_formats}/{len(movies)}", file=sys.stderr)
    else:
        print("\nNo movies found. Run with --debug to save screenshot", file=sys.stderr)
        print("[]")


if __name__ == "__main__":
    main()
