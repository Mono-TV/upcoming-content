#!/usr/bin/env python3
"""Debug HTML structure to understand Binged's poster layout"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def debug_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        url = "https://www.binged.com/streaming-premiere-dates/page/1/"
        print(f"Loading: {url}\n")

        # Use domcontentloaded instead of networkidle
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)

        # Wait a bit for any dynamic content
        await page.wait_for_timeout(3000)

        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')

        # Find first movie item
        items = soup.find_all('div', class_='bng-movies-table-item')

        if items and len(items) > 1:
            print(f"Found {len(items)} movie items\n")

            # Find first non-header, non-preloader item
            movie_item = None
            for idx, item in enumerate(items):
                classes = item.get('class', [])
                if 'bng-movies-table-item-th' not in classes and 'bng-movies-table-item-preloader' not in classes:
                    movie_item = item
                    print(f"Found first actual movie at index {idx}")
                    break

            if movie_item:
                print("="*80)
                print("ACTUAL MOVIE ITEM HTML:")
                print("="*80)
                print(movie_item.prettify()[:3000])  # First 3000 chars
                print("\n...(truncated)...\n")

                # Look for ANY img tags
                all_imgs = movie_item.find_all('img')
                print(f"\nTotal <img> tags in item: {len(all_imgs)}")
                for i, img in enumerate(all_imgs):
                    print(f"\nImage {i+1}:")
                    print(f"  Tag: {img}")
                    print(f"  Attributes: {img.attrs}")

                # Check for background images in style attributes
                print("\n" + "="*80)
                print("Checking for background-image in style attributes...")
                print("="*80)
                for elem in movie_item.find_all(style=True):
                    if 'background' in elem.get('style', ''):
                        print(f"\nElement with background: {elem.name}")
                        print(f"Style: {elem['style']}")
            else:
                print("No actual movie items found (all are headers or preloaders)")

        else:
            print("No movie items found!")
            print("\nHTML Preview:")
            print(soup.prettify()[:500])

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_html())
