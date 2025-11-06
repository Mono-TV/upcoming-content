#!/usr/bin/env python3
"""
Movie Scraper for Binged.com - Optimized Async Version
Uses Playwright async API for better performance
"""

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict
import sys
import asyncio
import argparse


async def scrape_page(page, page_num: int) -> List[Dict[str, any]]:
    """
    Scrape movies from a single page

    Args:
        page: Playwright page object
        page_num: Current page number

    Returns:
        List of movie dictionaries
    """
    movies = []

    print(f"  Parsing page {page_num}...", file=sys.stderr)
    content = await page.content()

    soup = BeautifulSoup(content, 'html.parser')

    # The site uses div-based layout, not actual table tags
    movie_items = soup.find_all('div', class_='bng-movies-table-item')

    # Filter out header and preloader items
    movie_items = [item for item in movie_items if not item.find('div', class_='bng-movies-table-item-th') and not item.find('div', class_='bng-movies-table-item-preloader')]

    print(f"  Found {len(movie_items)} entries on page {page_num}", file=sys.stderr)

    if len(movie_items) == 0:
        return []

    for idx, item in enumerate(movie_items, 1):
        movie_data = {}

        # Extract title
        title_div = item.find('div', class_='bng-movies-table-item-title')
        if title_div:
            link = title_div.find('a')
            if link:
                # Get title text (before any rating spans)
                title_text = link.get_text(separator='|', strip=True)
                # Split by | and take first part (title), ignore ratings
                title_parts = title_text.split('|')
                title_text = title_parts[0].strip()

                # Remove line breaks
                title_text = title_text.replace('\n', ' ').strip()

                if title_text:
                    movie_data['title'] = title_text

                # Extract URL
                href = link.get('href', '')
                if href:
                    movie_data['url'] = href

        # Extract release date
        date_div = item.find('div', class_='bng-movies-table-date')
        if date_div:
            # Find the span with the date
            date_span = date_div.find('span')
            if date_span:
                date_text = date_span.get_text(strip=True)
                if date_text:
                    movie_data['release_date'] = date_text

        # Extract platforms
        platform_div = item.find('div', class_='bng-movies-table-platform')
        if platform_div:
            # Find the platform container
            platform_container = platform_div.find('div', class_='streaming-item-platform')
            if platform_container:
                # Get all images (platforms)
                platform_imgs = platform_container.find_all('img')
                platforms = []
                for img in platform_imgs:
                    # Try to get platform name from image src
                    src = img.get('src', '')
                    if src:
                        # Extract platform ID from path like ".../webp/30.webp" or ".../6.png"
                        match = re.search(r'/(\d+)\.(webp|png)', src)
                        if match:
                            platform_id = match.group(1)
                            # Map IDs to names (you can expand this)
                            platform_map = {
                                '4': 'Amazon Prime Video',
                                '10': 'JioHotstar',
                                '21': 'ManoramaMAX',
                                '30': 'Netflix',
                                '53': 'Sony LIV',
                                '6': 'SunNXT',
                                '8': 'Zee5',
                                '2': 'Aha Video',
                                '11': 'Apple TV Plus'
                            }
                            platform_name = platform_map.get(platform_id, f'Platform {platform_id}')
                            platforms.append(platform_name)

                if platforms:
                    movie_data['platforms'] = platforms

        # Extract image
        img_div = item.find('div', class_='bng-movies-table-item-image')
        if img_div:
            placeholder = img_div.find('div', class_='search-block-placeholder')
            if placeholder and placeholder.get('style'):
                # Extract URL from style="background: url(...)"
                style = placeholder.get('style', '')
                url_match = re.search(r'url\((https?://[^)]+)\)', style)
                if url_match:
                    movie_data['image_url'] = url_match.group(1)

        # Only add if we have at least a title
        if movie_data.get('title'):
            movies.append(movie_data)

    return movies


async def scrape_movies(url: str, debug: bool = False) -> List[Dict[str, any]]:
    """
    Scrape movie data from the Binged website (all pages)

    Args:
        url: The URL to scrape
        debug: Enable debug mode (screenshots, etc.)

    Returns:
        List of dictionaries containing movie information
    """
    all_movies = []

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

            # Add extra properties to avoid detection
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """)

            print("Navigating to page...", file=sys.stderr)

            # Navigate with domcontentloaded (faster than waiting for all resources)
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)

            print("Waiting for content...", file=sys.stderr)

            # Wait for the table with better error handling
            try:
                await page.wait_for_selector('#bng-movies-table', timeout=10000)
                print("Table found!", file=sys.stderr)
            except:
                print("Table not found immediately, continuing anyway...", file=sys.stderr)

            # Wait for JavaScript - use network idle for more reliability
            try:
                await page.wait_for_load_state('networkidle', timeout=15000)
            except:
                # Fallback to simple wait
                await asyncio.sleep(5)

            # Scroll to trigger lazy loading
            print("Scrolling page...", file=sys.stderr)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)

            # Optional debug screenshot
            if debug:
                await page.screenshot(path='debug_screenshot.png', full_page=True)
                print("Saved screenshot to debug_screenshot.png", file=sys.stderr)

            # Scrape first page
            current_page = 1
            print(f"\nScraping page {current_page}...", file=sys.stderr)
            page_movies = await scrape_page(page, current_page)
            all_movies.extend(page_movies)

            # Check for pagination
            while True:
                # Look for Next button or next page number
                try:
                    # Find pagination container
                    pagination_html = await page.inner_html('.bng-movies-table-pagination')
                    soup = BeautifulSoup(pagination_html, 'html.parser')

                    # Find all page spans
                    page_spans = soup.find_all('span', {'data-page': True})

                    if not page_spans:
                        print("  No more pages found", file=sys.stderr)
                        break

                    # Find the next page (current + 1)
                    next_page_num = current_page + 1
                    next_button = None

                    # Look for "Next" button or specific page number
                    for span in page_spans:
                        text = span.get_text(strip=True)
                        if text.lower() == 'next' or text == str(next_page_num):
                            next_button = span
                            break

                    if not next_button:
                        print("  No next button found", file=sys.stderr)
                        break

                    print(f"\n  Clicking to page {next_page_num}...", file=sys.stderr)

                    # Click the next page button
                    await page.click(f'.bng-movies-table-pagination span:has-text("{next_button.get_text(strip=True)}")')

                    # Wait for new content to load - use networkidle for reliability
                    try:
                        await page.wait_for_load_state('networkidle', timeout=10000)
                    except:
                        await asyncio.sleep(3)

                    # Scrape this page
                    current_page = next_page_num
                    print(f"Scraping page {current_page}...", file=sys.stderr)
                    page_movies = await scrape_page(page, current_page)

                    if not page_movies:
                        print("  No movies found on this page, stopping", file=sys.stderr)
                        break

                    all_movies.extend(page_movies)

                except Exception as e:
                    print(f"  Error during pagination: {e}", file=sys.stderr)
                    break

            await browser.close()

            print(f"\n{'='*60}", file=sys.stderr)
            print(f"Scraped {len(all_movies)} total movies from {current_page} pages", file=sys.stderr)
            print(f"{'='*60}\n", file=sys.stderr)

        except Exception as e:
            print(f"Error during scraping: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)

    return all_movies


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Scrape movies from Binged.com')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (screenshots)')
    args = parser.parse_args()

    url = "https://www.binged.com/streaming-premiere-dates/?mode=streaming-month&platform[]=Aha%20Video&platform[]=Amazon&platform[]=Apple%20Tv%20Plus&platform[]=Jio%20Hotstar&platform[]=Manorama%20MAX&platform[]=Netflix&platform[]=Sony%20LIV&platform[]=Sun%20NXT&platform[]=Zee5"

    print("="*60, file=sys.stderr)
    print("Binged.com Movie Scraper (Optimized)", file=sys.stderr)
    print("="*60, file=sys.stderr)

    movies = asyncio.run(scrape_movies(url, debug=args.debug))

    print("="*60, file=sys.stderr)
    print(f"Successfully scraped {len(movies)} movies", file=sys.stderr)
    print("="*60, file=sys.stderr)

    if movies:
        # Output JSON to stdout
        print(json.dumps(movies, indent=2, ensure_ascii=False))

        # Save to file
        output_file = 'movies.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(movies, f, indent=2, ensure_ascii=False)

        print(f"\nData saved to {output_file}", file=sys.stderr)
        print(f"Total movies: {len(movies)}", file=sys.stderr)
    else:
        print("\nNo movies found. Run with --debug to save screenshot", file=sys.stderr)
        print("[]")


if __name__ == "__main__":
    main()
