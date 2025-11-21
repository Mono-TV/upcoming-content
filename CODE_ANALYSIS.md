# Code Analysis: update_content.py

## Critical Issues

### 1. **Bare Exception Handlers**
**Location:** Lines 144, 274, 319, 366, 587, 597, 618, 628, 640

**Problem:** Catching all exceptions silently makes debugging impossible and hides real errors.

**Example:**
```python
except:
    continue  # Line 319 - silently fails
```

**Fix:** Catch specific exceptions and log them:
```python
except requests.exceptions.RequestException as e:
    logger.warning(f"Request failed for query '{query}': {e}")
    continue
```

### 2. **Index Out of Range Risk**
**Location:** Lines 468, 512

**Problem:** Accessing `posters[0]` and `backdrops[0]` without checking if lists are empty.

**Current Code:**
```python
movie['posters'] = {
    'thumbnail': f"https://image.tmdb.org/t/p/w92{posters[0]}",  # Crashes if posters is empty
    ...
}
```

**Fix:**
```python
if posters and len(posters) > 0:
    movie['posters'] = {
        'thumbnail': f"https://image.tmdb.org/t/p/w92{posters[0]}",
        ...
    }
```

### 3. **KeyError Risk**
**Location:** Line 543

**Problem:** Accessing dictionary key without checking existence.

**Current Code:**
```python
'profile_path': f"https://image.tmdb.org/t/p/w185{c['profile_path']}" if c.get('profile_path') else None
```

**Note:** This one is actually safe due to `.get()`, but the pattern is inconsistent elsewhere.

### 4. **Inefficient Browser Management**
**Location:** Lines 324-369 (`_fetch_binged_poster`)

**Problem:** Creates a new Playwright browser instance for each poster fetch, which is extremely expensive.

**Fix:** Pass browser context as parameter or reuse existing browser instance.

### 5. **Blocking Sleep in Async Function**
**Location:** Line 570

**Problem:** `time.sleep(0.25)` blocks the entire event loop in an async function.

**Fix:** Use `await asyncio.sleep(0.25)` instead.

### 6. **Missing Rate Limit Handling**
**Location:** `_fetch_with_retry` method (lines 260-275)

**Problem:** Doesn't handle HTTP 429 (Too Many Requests) responses from TMDB API.

**Fix:** Add handling for 429 status code with exponential backoff:
```python
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        retry_after = int(e.response.headers.get('Retry-After', 60))
        if attempt < max_retries - 1:
            time.sleep(retry_after)
            continue
    raise
```

## Major Issues

### 7. **Code Duplication**
**Location:** Lines 400-411 and 493-506

**Problem:** Poster fallback logic is duplicated.

**Fix:** Extract to a helper method:
```python
def _set_poster_fallback(self, movie: Dict, poster_url: str):
    """Set poster URLs from fallback source"""
    movie['poster_url_medium'] = poster_url
    movie['poster_url_large'] = poster_url
    movie['posters'] = {
        'thumbnail': poster_url,
        'small': poster_url,
        'medium': poster_url,
        'large': poster_url,
        'xlarge': poster_url,
        'original': poster_url
    }
```

### 8. **No Parallelization**
**Location:** `enrich_with_tmdb_comprehensive` (line 389)

**Problem:** Processes movies sequentially, which is slow.

**Fix:** Use `asyncio.gather()` with semaphore for rate limiting:
```python
semaphore = asyncio.Semaphore(5)  # Limit concurrent requests

async def enrich_movie(movie):
    async with semaphore:
        # enrichment logic
        await asyncio.sleep(0.25)

tasks = [enrich_movie(movie) for movie in self.movies]
await asyncio.gather(*tasks)
```

### 9. **Long Method**
**Location:** `enrich_with_tmdb_comprehensive` (lines 371-576)

**Problem:** 200+ line method violates single responsibility principle.

**Fix:** Break into smaller methods:
- `_enrich_single_movie()`
- `_add_tmdb_details()`
- `_add_tmdb_images()`
- `_add_tmdb_credits()`
- `_add_tmdb_videos()`

### 10. **Hardcoded Configuration**
**Location:** Throughout the file

**Problem:** Magic numbers and hardcoded values:
- Timeouts: 60000, 15000
- Retry counts: 3
- Sleep durations: 0.25, 2, 3, 4
- Platform mapping dictionary

**Fix:** Move to configuration constants or config file.

## Minor Issues

### 11. **Missing Type Hints**
**Location:** Several methods

**Problem:** Inconsistent type hints make code harder to understand.

**Fix:** Add complete type hints:
```python
def _parse_movie_item(self, item: BeautifulSoup) -> Optional[Dict[str, Any]]:
```

### 12. **Inconsistent Error Messages**
**Location:** Various print statements

**Problem:** Mix of emoji and text, inconsistent formatting.

**Fix:** Use logging module with consistent format.

### 13. **No Input Validation**
**Location:** `__init__` method

**Problem:** No validation of API key format or environment variables.

**Fix:** Add basic validation:
```python
if not self.tmdb_api_key or len(self.tmdb_api_key) < 10:
    raise ValueError("Invalid TMDB API key format")
```

### 14. **Unused Parameter**
**Location:** Line 706 (`--no-trailers`)

**Problem:** `enable_trailers` parameter is stored but never used in the code.

**Fix:** Either implement the feature or remove the parameter.

### 15. **Potential Memory Issues**
**Location:** Line 477 (`all_posters`)

**Problem:** Storing multiple poster sizes for multiple posters could use significant memory.

**Fix:** Consider storing only file paths and constructing URLs on demand.

## Recommendations

1. **Add Logging:** Replace print statements with proper logging
2. **Add Unit Tests:** Critical methods lack test coverage
3. **Add Configuration File:** Move hardcoded values to config
4. **Add Progress Bar:** Use `tqdm` for better UX during long operations
5. **Add Retry Logic:** Implement exponential backoff for all API calls
6. **Add Validation:** Validate API responses before processing
7. **Refactor:** Break down large methods into smaller, testable units
8. **Add Documentation:** Add docstrings for all public methods

## Priority Fix Order

1. **Critical:** Fix index out of range issues (Issue #2)
2. **Critical:** Replace bare except clauses (Issue #1)
3. **High:** Fix blocking sleep (Issue #5)
4. **High:** Add rate limit handling (Issue #6)
5. **High:** Fix browser management (Issue #4)
6. **Medium:** Remove code duplication (Issue #7)
7. **Medium:** Add parallelization (Issue #8)
8. **Low:** Refactor long methods (Issue #9)
9. **Low:** Move to configuration (Issue #10)

