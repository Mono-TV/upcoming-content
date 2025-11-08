#!/usr/bin/env python3
"""Quick test to inspect Binged HTML structure for poster extraction"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def test_poster_extraction():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to Binged page 1
        url = f"https://www.binged.com/streaming-premiere-dates/page/1/"
        print(f"Fetching: {url}\n")
        await page.goto(url, wait_until='networkidle')

        # Get HTML content
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')

        # Find first movie item
        items = soup.find_all('div', class_='bng-movies-table-item')

        if items:
            print(f"Found {len(items)} movie items\n")
            print("="*80)
            print("INSPECTING FIRST MOVIE ITEM:")
            print("="*80)

            first_item = items[0]

            # Get title
            title_link = first_item.find('a', class_='bng-movies-table-link')
            title = title_link.text.strip() if title_link else "Unknown"
            print(f"\nTitle: {title}\n")

            # Find image div
            image_div = first_item.find('div', class_='bng-movies-table-image')

            if image_div:
                print("Found image_div: YES")
                print(f"\nImage div HTML:\n{image_div.prettify()}\n")

                # Check for img tag
                img = image_div.find('img')
                if img:
                    print("Found img tag: YES")
                    print(f"\nImg attributes:")
                    for attr, value in img.attrs.items():
                        print(f"  {attr}: {value}")

                    # Check different possible attributes
                    src = img.get('src', '')
                    data_src = img.get('data-src', '')
                    data_lazy = img.get('data-lazy-src', '')

                    print(f"\n--- URL Analysis ---")
                    print(f"src: {src}")
                    print(f"data-src: {data_src}")
                    print(f"data-lazy-src: {data_lazy}")

                    # Best URL
                    best_url = data_src or src or data_lazy
                    print(f"\nBest URL: {best_url}")
                    print(f"Starts with http: {best_url.startswith('http') if best_url else False}")

                else:
                    print("Found img tag: NO")

                    # Check for other image elements
                    print("\nLooking for other image elements...")
                    all_imgs = image_div.find_all('img')
                    print(f"Total img tags in div: {len(all_imgs)}")

            else:
                print("Found image_div: NO")
                print("\nSearching for ANY image in item...")
                all_imgs = first_item.find_all('img')
                print(f"Total img tags found: {len(all_imgs)}")
                if all_imgs:
                    print(f"\nFirst img tag: {all_imgs[0]}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_poster_extraction())
