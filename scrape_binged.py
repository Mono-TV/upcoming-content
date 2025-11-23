#!/usr/bin/env python3
"""
Binged.com Content Scraper
Scrapes upcoming streaming content from Binged.com and saves to JSON.

Usage:
    python3 scrape_binged.py [--pages N] [--output FILE] [--test]
"""

import asyncio
import json
import re
import sys
import argparse
from typing import List, Dict, Optional
from datetime import datetime

# Check required packages
try:
    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("\n💡 Install required packages:")
    print("   pip3 install playwright beautifulsoup4")
    print("   playwright install chromium")
    sys.exit(1)


class BingedScraper:
    """Scraper for Binged.com streaming premiere dates"""

    # Base URL for scraping
    BASE_URL = "https://www.binged.com/streaming-premiere-dates/"
    
    # Default URL with platform filters
    DEFAULT_URL = (
        "https://www.binged.com/streaming-premiere-dates/"
        "?mode=streaming-soon-month"
        "&platform[]=Aha%20Video"
        "&platform[]=Amazon"
        "&platform[]=Apple%20Tv%20Plus"
        "&platform[]=Jio%20Hotstar"
        "&platform[]=Manorama%20MAX"
        "&platform[]=Netflix"
        "&platform[]=Sony%20LIV"
        "&platform[]=Sun%20NXT"
        "&platform[]=Zee5"
    )

    # Platform ID to name mapping
    PLATFORM_MAP = {
        '4': 'Amazon Prime Video',
        '5': 'Apple TV+',
        '6': 'Sun NXT',
        '8': 'Zee5',
        '10': 'Jio Hotstar',
        '21': 'Manorama MAX',
        '30': 'Netflix',
        '53': 'Sony LIV',
        '55': 'Aha Video',
        '71': 'ALT Balaji',
        '72': 'Discovery Plus',
        '73': 'ErosNow',
        '74': 'Hoichoi'
    }

    # Configuration constants
    PAGE_LOAD_TIMEOUT = 60000  # 60 seconds
    SELECTOR_WAIT_TIMEOUT = 15000  # 15 seconds
    INITIAL_LOAD_DELAY = 3  # seconds
    PAGE_NAVIGATION_DELAY = 2  # seconds
    PAGE_NAVIGATION_DELAY_FALLBACK = 4  # seconds

    def __init__(self, max_pages: int = 5, output_file: str = 'scraped_content.json', test_mode: bool = False):
        """
        Initialize the scraper
        
        Args:
            max_pages: Maximum number of pages to scrape
            output_file: Output JSON filename
            test_mode: If True, limit to first page only
        """
        self.max_pages = max_pages
        self.output_file = output_file
        self.test_mode = test_mode
        self.movies: List[Dict] = []

    async def scrape(self, url: Optional[str] = None) -> List[Dict]:
        """
        Main scraping method
        
        Args:
            url: Custom URL to scrape (uses DEFAULT_URL if None)
            
        Returns:
            List of scraped movie/show dictionaries
        """
        if url is None:
            url = self.DEFAULT_URL

        print("\n" + "="*60)
        print("BINGED.COM CONTENT SCRAPER")
        print("="*60)
        print(f"URL: {url}")
        print(f"Max pages: {self.max_pages}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = await context.new_page()

            # Hide webdriver property
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """)

            try:
                # Load initial page
                print(f"📄 Loading initial page...")
                await page.goto(url, wait_until='domcontentloaded', timeout=self.PAGE_LOAD_TIMEOUT)
                await page.wait_for_selector('.bng-movies-table-item', timeout=self.SELECTOR_WAIT_TIMEOUT)
                await asyncio.sleep(self.INITIAL_LOAD_DELAY)

                # Scrape first page
                current_page = 1
                await self._scrape_page(page, current_page)

                # Test mode: only scrape first page
                if self.test_mode:
                    print("\n🧪 TEST MODE: Only scraping first page")
                else:
                    # Paginate through remaining pages
                    for page_num in range(2, self.max_pages + 1):
                        success = await self._navigate_to_page(page, page_num)
                        if not success:
                            break
                        await self._scrape_page(page, page_num)

            except Exception as e:
                print(f"\n❌ Error during scraping: {e}")
                import traceback
                traceback.print_exc()

            finally:
                await browser.close()

        print(f"\n✅ Scraping complete: {len(self.movies)} items found")
        return self.movies

    async def _navigate_to_page(self, page, page_num: int) -> bool:
        """
        Navigate to a specific page number
        
        Args:
            page: Playwright page object
            page_num: Page number to navigate to
            
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            next_button = await page.query_selector('.bng-movies-table-pagination span:has-text("Next")')
            if not next_button:
                print(f"  ℹ️  No more pages available (stopped at page {page_num - 1})")
                return False

            print(f"\n📄 Navigating to page {page_num}...")
            await next_button.click()

            try:
                await page.wait_for_load_state('domcontentloaded', timeout=self.SELECTOR_WAIT_TIMEOUT)
                await asyncio.sleep(self.PAGE_NAVIGATION_DELAY)
            except asyncio.TimeoutError:
                # Fallback delay if page load detection fails
                print(f"  ⚠️  Page load timeout, using fallback delay...")
                await asyncio.sleep(self.PAGE_NAVIGATION_DELAY_FALLBACK)

            return True

        except Exception as e:
            print(f"  ⚠️  Error navigating to page {page_num}: {e}")
            return False

    async def _scrape_page(self, page, page_num: int) -> None:
        """
        Scrape content from current page
        
        Args:
            page: Playwright page object
            page_num: Current page number
        """
        try:
            print(f"📋 Scraping page {page_num}...")
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Find all movie items, excluding headers and loaders
            movie_items = soup.find_all('div', class_='bng-movies-table-item')
            movie_items = [
                item for item in movie_items
                if not item.find('div', class_='bng-movies-table-item-th')
                and not item.find('div', class_='bng-movies-table-item-preloader')
            ]

            print(f"  Found {len(movie_items)} entries")

            if not movie_items:
                print("  ⚠️  No movies found on this page")
                return

            # Parse each item
            page_count = 0
            for item in movie_items:
                movie_data = self._parse_movie_item(item)
                if movie_data and movie_data.get('title'):
                    self.movies.append(movie_data)
                    page_count += 1

            print(f"  ✅ Parsed {page_count} valid entries")

        except Exception as e:
            print(f"  ❌ Error scraping page {page_num}: {e}")
            import traceback
            traceback.print_exc()

    def _parse_movie_item(self, item) -> Optional[Dict]:
        """
        Parse a single movie/show item from HTML
        
        Args:
            item: BeautifulSoup element containing movie data
            
        Returns:
            Dictionary with movie data or None if invalid
        """
        movie_data: Dict = {}

        # Extract title and URL
        title_div = item.find('div', class_='bng-movies-table-item-title')
        if title_div:
            link = title_div.find('a')
            if link:
                # Get title (handle cases with separators like "Title | Subtitle")
                title_text = link.get_text(separator='|', strip=True).split('|')[0].strip()
                title_text = title_text.replace('\n', ' ').strip()
                if title_text:
                    movie_data['title'] = title_text

                # Get URL
                href = link.get('href', '')
                if href:
                    # Make URL absolute if relative
                    if href.startswith('/'):
                        movie_data['url'] = f"https://www.binged.com{href}"
                    else:
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
                    # Extract platform ID from image URL (e.g., /4.webp or /30.png)
                    match = re.search(r'/(\d+)\.(webp|png)', src)
                    if match:
                        platform_id = match.group(1)
                        platform_name = self.PLATFORM_MAP.get(platform_id, f'Platform {platform_id}')
                        if platform_name not in platforms:
                            platforms.append(platform_name)
                
                if platforms:
                    movie_data['platforms'] = platforms

        # Only return if we have at least a title
        return movie_data if movie_data.get('title') else None

    def save_to_json(self, data: List[Dict], filename: Optional[str] = None) -> None:
        """
        Save scraped data to JSON file
        
        Args:
            data: List of movie dictionaries
            filename: Output filename (uses self.output_file if None)
        """
        if filename is None:
            filename = self.output_file

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved {len(data)} items to: {filename}")
        except Exception as e:
            print(f"\n❌ Error saving to {filename}: {e}")
            raise

    def print_summary(self) -> None:
        """Print summary statistics"""
        if not self.movies:
            print("\n⚠️  No data to summarize")
            return

        print("\n" + "="*60)
        print("SCRAPING SUMMARY")
        print("="*60)
        print(f"Total items scraped: {len(self.movies)}")
        
        # Count by platform
        platform_counts: Dict[str, int] = {}
        for movie in self.movies:
            platforms = movie.get('platforms', [])
            for platform in platforms:
                platform_counts[platform] = platform_counts.get(platform, 0) + 1

        if platform_counts:
            print(f"\nPlatform distribution:")
            for platform, count in sorted(platform_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {platform}: {count}")

        # Count with release dates
        with_dates = sum(1 for m in self.movies if m.get('release_date'))
        print(f"\nItems with release dates: {with_dates}/{len(self.movies)}")
        
        # Count with URLs
        with_urls = sum(1 for m in self.movies if m.get('url'))
        print(f"Items with URLs: {with_urls}/{len(self.movies)}")
        
        print("="*60 + "\n")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Scrape upcoming streaming content from Binged.com',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scrape_binged.py                    # Scrape 5 pages (default)
  python3 scrape_binged.py --pages 10         # Scrape 10 pages
  python3 scrape_binged.py --output data.json # Save to custom file
  python3 scrape_binged.py --test             # Test mode (1 page only)
        """
    )
    
    parser.add_argument(
        '--pages',
        type=int,
        default=5,
        help='Number of pages to scrape (default: 5)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='scraped_content.json',
        help='Output JSON filename (default: scraped_content.json)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: scrape only first page'
    )

    args = parser.parse_args()

    scraper = BingedScraper(
        max_pages=args.pages,
        output_file=args.output,
        test_mode=args.test
    )

    try:
        # Scrape data
        movies = await scraper.scrape()
        
        # Save to JSON
        if movies:
            scraper.save_to_json(movies)
            scraper.print_summary()
        else:
            print("\n⚠️  No data was scraped. Check the URL and try again.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        if scraper.movies:
            print(f"💾 Saving {len(scraper.movies)} items collected so far...")
            scraper.save_to_json(scraper.movies)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())



