# BookMyShow Scraping - Anti-Block Solutions

## 🚫 Current Issue
BookMyShow is blocking automated scraping with:
- Bot detection
- Headless browser detection
- Rate limiting
- CAPTCHA challenges

## ✅ Solutions (Ranked by Effectiveness)

### Solution 1: Enhanced Anti-Detection (Recommended)

Update the theatre scrapers with these improvements:

```python
# In scrape_theatre_current.py and scrape_theatre_upcoming.py

async def scrape_theatre_current(city: str = 'bengaluru', debug: bool = False):
    # ... existing code ...

    async with async_playwright() as p:
        # ENHANCED: Use real Chrome instead of Chromium
        browser = await p.chromium.launch(
            headless=False,  # Run with visible browser (harder to detect)
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--window-size=1920,1080',
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # ENHANCED: Add more browser context
            locale='en-IN',
            timezone_id='Asia/Kolkata',
            geolocation={'latitude': 12.9716, 'longitude': 77.5946},  # Bangalore
            permissions=['geolocation'],
        )

        page = await context.new_page()

        # ENHANCED: Better stealth
        await page.add_init_script("""
            // Remove webdriver flag
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Mock Chrome properties
            window.chrome = {
                runtime: {}
            };

            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)

        # ENHANCED: Slower, more human-like navigation
        print("Navigating to BookMyShow...")
        await page.goto(url, wait_until='networkidle', timeout=60000)

        # ENHANCED: Random delays to mimic human behavior
        import random
        await asyncio.sleep(random.uniform(2, 4))

        # ... rest of scraping logic ...
```

### Solution 2: Use Residential Proxies

BookMyShow may block datacenter IPs. Use residential proxies:

```python
# Install: pip install playwright-stealth

from playwright_stealth import stealth_async

context = await browser.new_context(
    proxy={
        "server": "http://proxy-server:port",
        "username": "username",
        "password": "password"
    }
)

page = await context.new_page()
await stealth_async(page)  # Apply stealth patches
```

**Proxy Services:**
- Bright Data (https://brightdata.com)
- Oxylabs (https://oxylabs.io)
- ScraperAPI (https://scraperapi.com)

### Solution 3: Session Persistence & Cookies

Save browser state between runs:

```python
# Save session
await context.storage_state(path="bms_session.json")

# Reuse session
context = await browser.new_context(
    storage_state="bms_session.json"
)
```

### Solution 4: Increase Delays & Reduce Frequency

Update `config.py`:

```python
BMS_CONFIG = {
    'request_delay': 5.0,  # Increase from 2.5 to 5 seconds
    'scroll_iterations': 5,  # Reduce from 10 to 5
    'detail_page_timeout': 60000,  # Increase timeout
    'max_retries': 5,  # More retries
}
```

### Solution 5: Use BookMyShow API (Best Long-term)

Instead of scraping, use their unofficial API:

```python
import requests

# Example API endpoint (may change)
url = "https://in.bookmyshow.com/api/explore/v2/browse/movies"
headers = {
    "User-Agent": "Mozilla/5.0...",
    "Accept": "application/json",
    "x-region-slug": "bengaluru"
}

response = requests.get(url, headers=headers)
data = response.json()
```

**Note:** API endpoints may require reverse engineering from network tab.

### Solution 6: Manual CAPTCHA Solving

For development/testing, run with `headless=False` and solve CAPTCHAs manually:

```python
browser = await p.chromium.launch(headless=False)  # Show browser
# Browser window opens, you can solve CAPTCHA manually
await asyncio.sleep(30)  # Wait for manual intervention
```

### Solution 7: Use Alternative Data Sources

Instead of BookMyShow, consider:

**For Theatre Data:**
- **JustWatch** - Has theatre listings
- **Google Movies** - Rich snippets
- **PVR Cinemas API** - Direct cinema chain data
- **INOX API** - Another cinema chain
- **Paytm Movies** - Alternative ticketing platform

**Example with JustWatch:**
```python
import requests

url = "https://apis.justwatch.com/content/titles/en_IN/popular"
params = {
    "body": {
        "content_types": ["movie"],
        "monetization_types": ["cinema"]
    }
}
response = requests.post(url, json=params)
```

## 🔧 Quick Fix - Modified Scraper

Create `scrape_theatre_current_stealth.py`:

```python
#!/usr/bin/env python3
"""
BookMyShow Theatre Scraper - Stealth Version
Uses enhanced anti-detection techniques
"""

from playwright.async_api import async_playwright
import asyncio
import random
import json

async def scrape_with_stealth():
    async with async_playwright() as p:
        # Launch with stealth
        browser = await p.chromium.launch(
            headless=False,  # Visible browser
            slow_mo=100,  # Slow down operations
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            locale='en-IN',
            timezone_id='Asia/Kolkata',
            geolocation={'latitude': 12.9716, 'longitude': 77.5946},
            permissions=['geolocation'],
        )

        page = await context.new_page()

        # Stealth script
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
        """)

        url = "https://in.bookmyshow.com/explore/movies-bengaluru?cat=MT"

        print("🌐 Navigating to BookMyShow...")
        await page.goto(url, wait_until='networkidle', timeout=60000)

        print("⏳ Waiting for human-like delay...")
        await asyncio.sleep(random.uniform(3, 5))

        print("📜 Scrolling page...")
        for i in range(3):  # Reduced scrolls
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
            await asyncio.sleep(random.uniform(2, 4))

        print("✅ Page loaded successfully!")
        print("🛑 Paused for 30 seconds - solve CAPTCHA if needed")
        await asyncio.sleep(30)

        # Extract movie links
        content = await page.content()
        # ... rest of scraping ...

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_with_stealth())
```

## 📊 Testing Strategy

### Phase 1: Test OTT Only (Works)
```bash
# This should work fine
python3 scrape_ott_releases.py --pages 1 --no-deeplinks
```

### Phase 2: Test Theatre with Stealth
```bash
# Run with visible browser
python3 scrape_theatre_current_stealth.py
```

### Phase 3: Manual Data Collection
If automation fails, manually collect a small dataset:
1. Visit BookMyShow
2. Copy movie data to JSON
3. Use as seed data

### Phase 4: Alternative Sources
```bash
# Use JustWatch or other APIs
python3 scrape_justwatch_theatre.py
```

## 🎯 Recommended Approach

**For Now:**
1. ✅ Use OTT scrapers (works perfectly)
2. ✅ Create dummy theatre data for frontend testing
3. ⏸️ Pause BookMyShow scraping
4. 🔄 Investigate alternative theatre data sources

**For Production:**
1. Use BookMyShow API (reverse engineered)
2. Or use paid proxy service
3. Or use alternative data sources (JustWatch, Google)
4. Or manually curate theatre listings weekly

## 💡 Alternative: Hybrid Approach

**Automated (Daily):**
- OTT releases (Binged) ✅
- OTT upcoming (Binged) ✅

**Manual/API (Weekly):**
- Theatre current (Manual or API)
- Theatre upcoming (Manual or API)

This reduces scraping frequency and avoids blocks.

## 📝 Next Steps

1. **Test OTT scrapers** (should work perfectly)
2. **Create dummy theatre data** for frontend testing
3. **Investigate BookMyShow API** (network tab analysis)
4. **Consider alternative sources** (JustWatch, etc.)
5. **Deploy with OTT only** initially
6. **Add theatre data** once solution found

---

**Bottom Line:** Focus on OTT content first (works great), solve theatre data separately.
