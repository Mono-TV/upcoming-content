#!/usr/bin/env python3
"""
OTT Releases Scraper for Binged.com
Scrapes already-released OTT content and extracts deeplinks from detail pages

Usage:
    python3 scrape_ott_releases.py [--pages N] [--debug]
"""

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import re
import sys
import asyncio
import argparse
from typing import List, Dict, Optional
from config import BINGED_CONFIG, OTT_PLATFORM_FILTERS


async def extract_deeplinks(page, movie_url: str, debug: bool = False) -> Dict[str, str]:
    """
    Extract deeplinks from a movie's detail page on Binged

    Args:
        page: Playwright page object
        movie_url: URL of the movie detail page
        debug: Enable debug output

    Returns:
        Dictionary of platform: deeplink pairs
    """
    deeplinks = {}

    try:
        if debug:
            print(f"    Fetching deeplinks from {movie_url}...", file=sys.stderr)

        # Navigate to detail page
        await page.goto(movie_url, wait_until='domcontentloaded', timeout=20000)
        await asyncio.sleep(2)  # Wait for dynamic content to load

        # Wait for network to be idle to ensure all content is loaded
        try:
            await page.wait_for_load_state('networkidle', timeout=5000)
        except:
            pass  # Continue if timeout

        # Scroll to trigger any lazy-loaded content
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Platform domains to look for
        platform_domains = {
            'netflix.com': 'Netflix',
            'primevideo.com': 'Amazon Prime Video',
            'amazon.com/gp/video': 'Amazon Prime Video',
            'hotstar.com': 'Jio Hotstar',
            'jiocinema.com': 'Jio Hotstar',
            'sonyliv.com': 'Sony LIV',
            'zee5.com': 'Zee5',
            'sunnxt.com': 'SunNXT',
            'manoramamax.com': 'ManoramaMAX',
            'tv.apple.com': 'Apple TV+',
            'aha.video': 'Aha Video',
            'altbalaji.com': 'ALT Balaji',
            'discoveryplus.in': 'Discovery Plus',
            'erosnow.com': 'ErosNow',
            'hoichoi.tv': 'Hoichoi',
        }

        # Method 1: Look for "Watch Now" or streaming buttons/links with specific classes
        watch_elements = soup.find_all(['a', 'button', 'div'], class_=re.compile(r'watch|stream|play|platform|btn', re.I))

        for elem in watch_elements:
            href = elem.get('href', '')

            # Also check for onclick attributes that might contain links
            onclick = elem.get('onclick', '')

            # Check href
            if href and href.startswith('http'):
                for domain, platform in platform_domains.items():
                    if domain in href and platform not in deeplinks:
                        # Filter out general homepage links
                        if not href.endswith(domain) and not href.endswith(domain + '/'):
                            deeplinks[platform] = href
                            if debug:
                                print(f"      Found {platform} deeplink (href): {href}", file=sys.stderr)

            # Check onclick
            if onclick and 'http' in onclick:
                for domain, platform in platform_domains.items():
                    if domain in onclick and platform not in deeplinks:
                        # Extract URL from onclick
                        url_match = re.search(r'https?://[^\s\'"]+', onclick)
                        if url_match:
                            url = url_match.group(0)
                            if domain in url and not url.endswith(domain) and not url.endswith(domain + '/'):
                                deeplinks[platform] = url
                                if debug:
                                    print(f"      Found {platform} deeplink (onclick): {url}", file=sys.stderr)

        # Method 2: Look for all links in the page
        all_links = soup.find_all('a', href=True)

        for link in all_links:
            href = link.get('href', '')
            if href and href.startswith('http'):
                for domain, platform in platform_domains.items():
                    if domain in href and platform not in deeplinks:
                        # Filter out general homepage links
                        if not href.endswith(domain) and not href.endswith(domain + '/'):
                            deeplinks[platform] = href
                            if debug:
                                print(f"      Found {platform} deeplink (link): {href}", file=sys.stderr)

        # Method 3: Look for data attributes that might contain platform links
        elements_with_data = soup.find_all(attrs={"data-url": True})
        elements_with_data.extend(soup.find_all(attrs={"data-link": True}))
        elements_with_data.extend(soup.find_all(attrs={"data-href": True}))

        for elem in elements_with_data:
            for attr in ['data-url', 'data-link', 'data-href']:
                data_val = elem.get(attr, '')
                if data_val and 'http' in data_val:
                    for domain, platform in platform_domains.items():
                        if domain in data_val and platform not in deeplinks:
                            if not data_val.endswith(domain) and not data_val.endswith(domain + '/'):
                                deeplinks[platform] = data_val
                                if debug:
                                    print(f"      Found {platform} deeplink (data attr): {data_val}", file=sys.stderr)

        # Method 4: Search the entire page content for streaming URLs
        # This catches URLs that might be embedded in JavaScript or other places
        page_content = str(soup)
        for domain, platform in platform_domains.items():
            if platform not in deeplinks and domain in page_content:
                # Find all URLs containing this domain
                pattern = rf'(https?://[^\s\'"<>]*{re.escape(domain)}[^\s\'"<>]*)'
                matches = re.findall(pattern, page_content)
                for match in matches:
                    # Clean up the URL (remove trailing quotes, brackets, etc.)
                    clean_url = re.sub(r'["\'>),;]+$', '', match)
                    # Verify it's a valid streaming link (not just homepage)
                    if not clean_url.endswith(domain) and not clean_url.endswith(domain + '/'):
                        deeplinks[platform] = clean_url
                        if debug:
                            print(f"      Found {platform} deeplink (page scan): {clean_url}", file=sys.stderr)
                        break  # Take the first valid link for this platform

        if debug:
            if deeplinks:
                print(f"    Total deeplinks found: {len(deeplinks)} - {list(deeplinks.keys())}", file=sys.stderr)
            else:
                print(f"    No deeplinks found on detail page", file=sys.stderr)

    except Exception as e:
        if debug:
            print(f"    Error extracting deeplinks: {e}", file=sys.stderr)

    return deeplinks


async def scrape_page(page, page_num: int, platform_map: Dict[str, str], fetch_deeplinks: bool = True, debug: bool = False) -> List[Dict]:
    """
    Scrape movies from a single page

    Args:
        page: Playwright page object
        page_num: Current page number
        platform_map: Mapping of platform IDs to names
        fetch_deeplinks: Whether to fetch deeplinks from detail pages
        debug: Enable debug output

    Returns:
        List of movie dictionaries
    """
    movies = []

    print(f"  Parsing page {page_num}...", file=sys.stderr)
    content = await page.content()

    soup = BeautifulSoup(content, 'html.parser')

    # Find movie items
    movie_items = soup.find_all('div', class_='bng-movies-table-item')
    movie_items = [item for item in movie_items
                   if not item.find('div', class_='bng-movies-table-item-th')
                   and not item.find('div', class_='bng-movies-table-item-preloader')]

    print(f"  Found {len(movie_items)} entries on page {page_num}", file=sys.stderr)

    if len(movie_items) == 0:
        return []

    for idx, item in enumerate(movie_items, 1):
        movie_data = {'content_type': 'ott_released'}

        # Extract title
        title_div = item.find('div', class_='bng-movies-table-item-title')
        if title_div:
            link = title_div.find('a')
            if link:
                title_text = link.get_text(separator='|', strip=True)
                title_parts = title_text.split('|')
                title_text = title_parts[0].strip().replace('\n', ' ').strip()

                if title_text:
                    movie_data['title'] = title_text

                # Extract URL
                href = link.get('href', '')
                if href:
                    # Ensure full URL
                    if href.startswith('/'):
                        href = BINGED_CONFIG['base_url'] + href
                    movie_data['url'] = href

        # Extract release date
        date_div = item.find('div', class_='bng-movies-table-date')
        if date_div:
            date_span = date_div.find('span')
            if date_span:
                date_text = date_span.get_text(strip=True)
                if date_text:
                    movie_data['release_date'] = date_text

        # Extract platforms
        platform_div = item.find('div', class_='bng-movies-table-platform')
        if platform_div:
            platform_container = platform_div.find('div', class_='streaming-item-platform')
            if platform_container:
                platform_imgs = platform_container.find_all('img')
                platforms = []
                for img in platform_imgs:
                    src = img.get('src', '')
                    if src:
                        match = re.search(r'/(\d+)\.(webp|png)', src)
                        if match:
                            platform_id = match.group(1)
                            platform_name = platform_map.get(platform_id, f'Platform {platform_id}')
                            platforms.append(platform_name)

                if platforms:
                    movie_data['platforms'] = platforms

        # Extract image
        img_div = item.find('div', class_='bng-movies-table-item-image')
        if img_div:
            placeholder = img_div.find('div', class_='search-block-placeholder')
            if placeholder and placeholder.get('style'):
                style = placeholder.get('style', '')
                url_match = re.search(r'url\((https?://[^)]+)\)', style)
                if url_match:
                    movie_data['image_url'] = url_match.group(1)

        # Fetch deeplinks if enabled and we have a URL
        if fetch_deeplinks and movie_data.get('url'):
            print(f"  [{idx}/{len(movie_items)}] Fetching deeplinks for: {movie_data['title']}", file=sys.stderr)
            deeplinks = await extract_deeplinks(page, movie_data['url'], debug=debug)
            if deeplinks:
                movie_data['deeplinks'] = deeplinks

            # Add delay to avoid rate limiting
            await asyncio.sleep(BINGED_CONFIG['request_delay'])

        # Only add if we have at least a title
        if movie_data.get('title'):
            movies.append(movie_data)

    return movies


async def scrape_ott_releases(max_pages: int = 5, fetch_deeplinks: bool = True, debug: bool = False) -> List[Dict]:
    """
    Scrape already-released OTT content from Binged

    Args:
        max_pages: Maximum number of pages to scrape
        fetch_deeplinks: Whether to fetch deeplinks from detail pages
        debug: Enable debug mode

    Returns:
        List of movie dictionaries
    """
    all_movies = []

    # Construct URL with all OTT platforms
    platform_params = '&'.join([f'platform[]={p}' for p in OTT_PLATFORM_FILTERS])
    url = f"{BINGED_CONFIG['base_url']}/streaming-premiere-dates/?mode=streaming-month&{platform_params}"

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
            try:
                await page.wait_for_selector('#bng-movies-table', timeout=10000)
                print("Table found!", file=sys.stderr)
            except:
                print("Table not found immediately, continuing anyway...", file=sys.stderr)

            # Wait for JavaScript
            try:
                await page.wait_for_load_state('networkidle', timeout=15000)
            except:
                await asyncio.sleep(5)

            # Scroll to trigger lazy loading
            print("Scrolling page...", file=sys.stderr)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)

            # Optional debug screenshot
            if debug:
                await page.screenshot(path='debug_ott_releases.png', full_page=True)
                print("Saved screenshot to debug_ott_releases.png", file=sys.stderr)

            # Scrape first page
            current_page = 1
            print(f"\nScraping page {current_page}...", file=sys.stderr)
            page_movies = await scrape_page(page, current_page, BINGED_CONFIG['platforms'],
                                          fetch_deeplinks=fetch_deeplinks, debug=debug)
            all_movies.extend(page_movies)

            # Pagination
            while current_page < max_pages:
                try:
                    pagination_html = await page.inner_html('.bng-movies-table-pagination')
                    soup = BeautifulSoup(pagination_html, 'html.parser')

                    page_spans = soup.find_all('span', {'data-page': True})

                    if not page_spans:
                        print("  No more pages found", file=sys.stderr)
                        break

                    next_page_num = current_page + 1
                    next_button = None

                    for span in page_spans:
                        text = span.get_text(strip=True)
                        if text.lower() == 'next' or text == str(next_page_num):
                            next_button = span
                            break

                    if not next_button:
                        print("  No next button found", file=sys.stderr)
                        break

                    print(f"\n  Clicking to page {next_page_num}...", file=sys.stderr)
                    await page.click(f'.bng-movies-table-pagination span:has-text("{next_button.get_text(strip=True)}")')

                    try:
                        await page.wait_for_load_state('networkidle', timeout=10000)
                    except:
                        await asyncio.sleep(3)

                    current_page = next_page_num
                    print(f"Scraping page {current_page}...", file=sys.stderr)
                    page_movies = await scrape_page(page, current_page, BINGED_CONFIG['platforms'],
                                                   fetch_deeplinks=fetch_deeplinks, debug=debug)

                    if not page_movies:
                        print("  No movies found on this page, stopping", file=sys.stderr)
                        break

                    all_movies.extend(page_movies)

                except Exception as e:
                    print(f"  Error during pagination: {e}", file=sys.stderr)
                    break

            await browser.close()

            print(f"\n{'='*60}", file=sys.stderr)
            print(f"Scraped {len(all_movies)} total OTT releases from {current_page} pages", file=sys.stderr)
            print(f"{'='*60}\n", file=sys.stderr)

        except Exception as e:
            print(f"Error during scraping: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)

    return all_movies


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Scrape already-released OTT content from Binged.com')
    parser.add_argument('--pages', type=int, default=5, help='Maximum number of pages to scrape (default: 5)')
    parser.add_argument('--no-deeplinks', action='store_true', help='Skip deeplink extraction (faster)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (screenshots, verbose output)')
    args = parser.parse_args()

    print("="*60, file=sys.stderr)
    print("Binged.com OTT Releases Scraper", file=sys.stderr)
    print("="*60, file=sys.stderr)

    movies = asyncio.run(scrape_ott_releases(
        max_pages=args.pages,
        fetch_deeplinks=not args.no_deeplinks,
        debug=args.debug
    ))

    print("="*60, file=sys.stderr)
    print(f"Successfully scraped {len(movies)} OTT releases", file=sys.stderr)
    print("="*60, file=sys.stderr)

    if movies:
        # Output JSON to stdout
        print(json.dumps(movies, indent=2, ensure_ascii=False))

        # Save to file
        output_file = 'ott_releases.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(movies, f, indent=2, ensure_ascii=False)

        print(f"\nData saved to {output_file}", file=sys.stderr)
        print(f"Total OTT releases: {len(movies)}", file=sys.stderr)

        # Stats
        with_deeplinks = sum(1 for m in movies if m.get('deeplinks'))
        print(f"Movies with deeplinks: {with_deeplinks}/{len(movies)}", file=sys.stderr)
    else:
        print("\nNo movies found. Run with --debug to save screenshot", file=sys.stderr)
        print("[]")


if __name__ == "__main__":
    main()
