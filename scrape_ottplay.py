#!/usr/bin/env python3
"""
OTT Play scraper - extracts streaming release information.

Extracts for each content:
- title: Movie/show title
- title_type: "movie" or "show"
- genre: Genre(s)
- streaming_date: Release date (replaces "today" with actual date)
- content_provider: Streaming platform
- link: URL to the content page
- cbfc_rating: Content rating (U, U/A, U/A 13+, A, etc.) - from deep scrape
- description: Content description - from deep scrape

URL: https://www.ottplay.com/ott-releases-streaming-now-this-week-watch-online
"""

import json
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OTTPlayScraper:
    def __init__(self, headless=True):
        """Initialize the scraper."""
        self.url = "https://www.ottplay.com/ott-releases-streaming-now-this-week-watch-online"
        self.content_list = []
        self.setup_driver(headless)

    def setup_driver(self, headless=True):
        """Setup Chrome WebDriver with bot detection bypass."""
        import os
        chrome_options = Options()

        if headless:
            chrome_options.add_argument('--headless=new')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')

        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        try:
            if USE_WEBDRIVER_MANAGER:
                driver_path = ChromeDriverManager().install()
                if os.path.isfile(driver_path) and not driver_path.endswith('chromedriver'):
                    driver_dir = os.path.dirname(driver_path)
                    chromedriver_path = os.path.join(driver_dir, 'chromedriver')
                    if os.path.exists(chromedriver_path) and os.access(chromedriver_path, os.X_OK):
                        driver_path = chromedriver_path
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome WebDriver initialized")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("Chrome WebDriver initialized")
            except Exception as e2:
                logger.error(f"Failed to initialize WebDriver: {e2}")
                raise

    def load_page_fully(self):
        """Load the OTT Play page and scroll to load all content."""
        # Execute CDP commands to hide webdriver
        try:
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            })
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except:
            pass

        logger.info(f"Loading page: {self.url}")
        self.driver.get(self.url)
        time.sleep(10)

        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.info("Page loaded successfully")
        except:
            logger.warning("Page load timeout, continuing...")

        # Scroll to load all content
        logger.info("Scrolling to load all content...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        no_change_count = 0

        for i in range(50):  # Increased scroll iterations to capture all data
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Increased wait time for lazy loading

            # Try clicking "Load More" button if it exists
            try:
                load_more_buttons = self.driver.find_elements(By.XPATH,
                    "//*[contains(text(), 'Load More') or contains(text(), 'Show More') or contains(text(), 'View More')]")
                for btn in load_more_buttons:
                    if btn.is_displayed():
                        btn.click()
                        time.sleep(2)
                        logger.info(f"Clicked 'Load More' button")
            except:
                pass

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                no_change_count += 1
                logger.info(f"No new content at scroll {i+1} (count: {no_change_count})")
                # Wait for 3 consecutive no-changes to be sure
                if no_change_count >= 3:
                    logger.info(f"Confirmed all content loaded after {no_change_count} checks")
                    break
            else:
                no_change_count = 0
                last_height = new_height
                logger.info(f"Scroll {i+1} - Height: {new_height}")

        # Scroll back to top
        logger.info("Scrolling back to top...")
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(3)

    def find_all_cards(self):
        """Find all content cards from top to bottom."""
        logger.info("Finding all content cards...")

        # Try different selectors for content cards
        card_selectors = [
            "div[class*='card']",
            "a[href*='/movie/']",
            "a[href*='/show/']",
            "article",
            "[data-testid*='card']",
        ]

        all_cards = []
        seen_links = set()

        for selector in card_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    try:
                        # Get link if it's an anchor or find anchor inside
                        if elem.tag_name == 'a':
                            link = elem.get_attribute('href')
                        else:
                            try:
                                anchor = elem.find_element(By.TAG_NAME, 'a')
                                link = anchor.get_attribute('href')
                            except:
                                link = None

                        # Only add cards with valid links that we haven't seen
                        if link and link not in seen_links and ('/movie/' in link or '/show/' in link):
                            all_cards.append(elem)
                            seen_links.add(link)
                    except:
                        continue
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue

        logger.info(f"Found {len(all_cards)} unique content cards")
        return all_cards

    def scrape_content_details(self, link):
        """Scrape detailed metadata from individual content page."""
        details = {
            'cbfc_rating': '',
            'description': ''
        }

        try:
            logger.debug(f"Fetching details from: {link}")
            self.driver.get(link)
            time.sleep(2)  # Wait for page to load

            # Extract CBFC rating
            rating_selectors = [
                "[class*='rating']",
                "[class*='certificate']",
                "[class*='cbfc']",
                "div[class*='meta'] span",
                "div[class*='info'] span",
            ]

            for selector in rating_selectors:
                try:
                    rating_elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in rating_elems:
                        text = elem.text.strip()
                        # Look for CBFC ratings like U, U/A, U/A 13+, U/A 16+, A, etc.
                        if re.search(r'\b(U/A\s*\d+\+?|U\s*\d+\+?|A\s*\d+\+?|U/A|U|A)\b', text, re.IGNORECASE):
                            match = re.search(r'\b(U/A\s*\d+\+?|U\s*\d+\+?|A\s*\d+\+?|U/A|U|A)\b', text, re.IGNORECASE)
                            if match:
                                details['cbfc_rating'] = match.group(1).strip()
                                break
                    if details['cbfc_rating']:
                        break
                except:
                    continue

            # Extract description
            description_selectors = [
                "[class*='description']",
                "[class*='synopsis']",
                "[class*='overview']",
                "[class*='plot']",
                "meta[name='description']",
                "meta[property='og:description']",
            ]

            for selector in description_selectors:
                try:
                    if 'meta' in selector:
                        desc_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        desc = desc_elem.get_attribute('content')
                    else:
                        desc_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        desc = desc_elem.text.strip()

                    if desc and len(desc) > 20:  # Valid description should be longer
                        details['description'] = desc
                        break
                except:
                    continue

            logger.debug(f"Extracted details - Rating: {details['cbfc_rating']}, Desc length: {len(details['description'])}")

        except Exception as e:
            logger.debug(f"Error scraping content details from {link}: {e}")

        return details

    def extract_card_data(self, card):
        """Extract all required data from a single card."""
        data = {
            'title': '',
            'title_type': '',
            'genre': '',
            'streaming_date': '',
            'content_provider': '',
            'link': '',
            'cbfc_rating': '',
            'description': ''
        }

        try:
            # Get the full card text for parsing
            card_text = card.text.strip()

            # Extract link
            try:
                if card.tag_name == 'a':
                    link = card.get_attribute('href')
                else:
                    anchor = card.find_element(By.TAG_NAME, 'a')
                    link = anchor.get_attribute('href')

                if link:
                    data['link'] = link

                    # Determine title type from URL
                    if '/movie/' in link:
                        data['title_type'] = 'movie'
                    elif '/show/' in link:
                        data['title_type'] = 'show'
            except:
                pass

            # Extract title - try various selectors
            title_selectors = [
                "h1", "h2", "h3", "h4",
                "[class*='title']",
                "[class*='name']",
            ]

            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text.strip()
                    if title and len(title) > 1 and len(title) < 150:
                        # Filter out dates that might be captured as titles
                        if not re.match(r'^[A-Za-z]{3}\s+\d{1,2},?\s+\d{4}$', title):
                            data['title'] = title
                            break
                except:
                    continue

            # If no title found, try first line of card text
            if not data['title'] and card_text:
                lines = card_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 1 and len(line) < 150:
                        if not re.match(r'^[A-Za-z]{3}\s+\d{1,2},?\s+\d{4}$', line):
                            data['title'] = line
                            break

            # Extract genre using XPath pattern
            # The pattern is: .//div/div[2]/div[1]/ul/li[3]/text()
            # This gets the third li item which contains the genre
            try:
                # Try XPath approach first - looking for genre in list items
                genre_elements = card.find_elements(By.XPATH, ".//div/div[2]/div[1]/ul/li[3]")
                if genre_elements:
                    genre = genre_elements[0].text.strip()
                    if genre:
                        data['genre'] = genre
            except:
                pass

            # Fallback to CSS selectors if XPath didn't work
            if not data['genre']:
                genre_selectors = [
                    "[class*='genre']",
                    "[class*='category']",
                ]

                for selector in genre_selectors:
                    try:
                        genre_elem = card.find_element(By.CSS_SELECTOR, selector)
                        genre = genre_elem.text.strip()
                        if genre:
                            data['genre'] = genre
                            break
                    except:
                        continue

            # Extract streaming date
            date_selectors = [
                "[class*='date']",
                "[class*='release']",
                "[class*='stream']",
            ]

            for selector in date_selectors:
                try:
                    date_elem = card.find_element(By.CSS_SELECTOR, selector)
                    date_text = date_elem.text.strip()
                    if date_text:
                        # Check if it says "today" or similar
                        if re.search(r'\btoday\b', date_text, re.IGNORECASE):
                            data['streaming_date'] = 'today'
                        else:
                            data['streaming_date'] = date_text
                        break
                except:
                    continue

            # If no date found, look in card text for date patterns
            if not data['streaming_date'] and card_text:
                # Look for "today"
                if re.search(r'\btoday\b', card_text, re.IGNORECASE):
                    data['streaming_date'] = 'today'
                else:
                    # Look for date patterns like "Nov 01, 2025"
                    date_match = re.search(r'([A-Za-z]{3}\s+\d{1,2},?\s+\d{4})', card_text)
                    if date_match:
                        data['streaming_date'] = date_match.group(1)

            # Extract content provider (platform)
            provider_keywords = [
                'Netflix', 'Amazon Prime Video', 'Prime Video', 'Disney+ Hotstar', 'Hotstar',
                'Zee5', 'ZEE5', 'SonyLiv', 'Sony Liv', 'Voot', 'MX Player', 'Hoichoi',
                'Aha', 'Apple TV+', 'Apple TV', 'JioCinema', 'Jio Cinema', 'Sun NXT',
                'LionsGate Play', 'Lionsgate', 'Discovery+', 'HBO Max', 'Hulu',
                'Peacock', 'Paramount+', 'Showtime', 'Starz'
            ]

            provider_selectors = [
                "[class*='provider']",
                "[class*='platform']",
                "[class*='ott']",
                "img[alt]",
            ]

            for selector in provider_selectors:
                try:
                    provider_elem = card.find_element(By.CSS_SELECTOR, selector)
                    if selector == "img[alt]":
                        provider_text = provider_elem.get_attribute('alt')
                    else:
                        provider_text = provider_elem.text.strip()

                    if provider_text:
                        for keyword in provider_keywords:
                            if keyword.lower() in provider_text.lower():
                                data['content_provider'] = keyword
                                break
                    if data['content_provider']:
                        break
                except:
                    continue

            # If no provider found, search in card text
            if not data['content_provider'] and card_text:
                for keyword in provider_keywords:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', card_text, re.IGNORECASE):
                        data['content_provider'] = keyword
                        break

            # Only return if we have at least a title and link
            if data['title'] and data['link']:
                return data

            return None

        except Exception as e:
            logger.debug(f"Error extracting card data: {e}")
            return None

    def scrape(self, deep_scrape=True):
        """Main scraping method.

        Args:
            deep_scrape: If True, visits each content page to extract CBFC rating and description
        """
        try:
            # Load page fully and scroll to top
            self.load_page_fully()

            # Find all cards
            cards = self.find_all_cards()

            if not cards:
                logger.warning("No cards found")
                return

            logger.info(f"Processing {len(cards)} cards...")

            # First pass: Extract basic data from all cards
            for idx, card in enumerate(cards):
                try:
                    data = self.extract_card_data(card)
                    if data:
                        # Replace "today" with actual date
                        if data['streaming_date'].lower() == 'today':
                            today = datetime.now()
                            data['streaming_date'] = today.strftime("%b %d, %Y")

                        self.content_list.append(data)
                        logger.info(f"[{idx+1}/{len(cards)}] Extracted basic info: {data['title']} ({data['title_type']})")
                except Exception as e:
                    logger.debug(f"Error processing card {idx+1}: {e}")
                    continue

            logger.info(f"Successfully extracted {len(self.content_list)} items from listing")

            # Second pass: Deep scrape each content page
            if deep_scrape:
                logger.info(f"Starting deep scrape for {len(self.content_list)} items...")
                for idx, item in enumerate(self.content_list):
                    try:
                        if item['link']:
                            logger.info(f"[{idx+1}/{len(self.content_list)}] Deep scraping: {item['title']}")
                            details = self.scrape_content_details(item['link'])
                            item['cbfc_rating'] = details['cbfc_rating']
                            item['description'] = details['description']
                            logger.info(f"[{idx+1}/{len(self.content_list)}] Rating: {item['cbfc_rating']}, Desc: {len(item['description'])} chars")
                    except Exception as e:
                        logger.warning(f"Error deep scraping {item['title']}: {e}")
                        continue

                logger.info(f"Deep scraping completed")

        except Exception as e:
            logger.error(f"Error during scraping: {e}", exc_info=True)

    def save_to_json(self, filename='ottplay_results.json'):
        """Save extracted content to JSON file."""
        output = {
            'scraped_at': datetime.now().isoformat(),
            'source_url': self.url,
            'total_items': len(self.content_list),
            'content': self.content_list
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

        logger.info(f"✓ Saved {len(self.content_list)} items to {filename}")

    def cleanup(self):
        """Close the browser."""
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("Browser closed")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Scrape OTT Play for streaming releases')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run browser in headless mode (default: True)')
    parser.add_argument('--no-headless', dest='headless', action='store_false',
                       help='Run browser in visible mode')
    parser.add_argument('--output', default='ottplay_results.json',
                       help='Output JSON filename (default: ottplay_results.json)')
    parser.add_argument('--deep-scrape', action='store_true', default=True,
                       help='Visit each content page to extract CBFC rating and description (default: True)')
    parser.add_argument('--no-deep-scrape', dest='deep_scrape', action='store_false',
                       help='Skip deep scraping, only extract basic info from listing')

    args = parser.parse_args()

    scraper = OTTPlayScraper(headless=args.headless)

    try:
        scraper.scrape(deep_scrape=args.deep_scrape)

        if scraper.content_list:
            scraper.save_to_json(args.output)
            logger.info(f"✓ Successfully scraped {len(scraper.content_list)} items")
        else:
            logger.warning("No content was extracted")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        scraper.cleanup()


if __name__ == '__main__':
    main()
