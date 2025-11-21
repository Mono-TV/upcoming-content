# Data Sources Analysis for Upcoming Movie/TV Content (India)

## Current Issues with Binged.com

### Problems Identified:
1. **Limited Data**: Only 6 movies found with platform filters applied
2. **No Pagination**: Website shows "no more pages available" immediately
3. **Unreliable Structure**: Content may not always be complete or up-to-date
4. **Aggregator Issues**: Third-party aggregators may have delays or missing data

---

## Alternative Data Sources

### 1. TMDB (The Movie Database) API ⭐ **RECOMMENDED**

#### Advantages:
- ✅ **Official API** with comprehensive data
- ✅ **Free tier** with 50+ requests per second
- ✅ **Region filtering** (IN for India)
- ✅ **Release type filtering** (Theatrical, TV, Streaming)
- ✅ **Already integrated** in current codebase
- ✅ **Rich metadata**: posters, cast, crew, trailers, genres
- ✅ **No scraping needed** - direct JSON API
- ✅ **Reliable and maintained**

#### Available Endpoints:

**1. Upcoming Movies (Theatrical)**
```
GET /movie/upcoming?region=IN&language=en-US
```
- Returns: Movies upcoming in theaters in India
- Date range: Next 3-4 weeks
- Result: ~20-50 movies per page

**2. Discover Movies (Custom Filters)**
```
GET /discover/movie?region=IN&release_date.gte=YYYY-MM-DD&release_date.lte=YYYY-MM-DD&sort_by=release_date.asc
```
- Returns: Movies with custom date ranges
- Can filter by: release type, genres, language, etc.
- Result: Tested with 106 upcoming movies found

**3. Discover TV Shows**
```
GET /discover/tv?air_date.gte=YYYY-MM-DD&air_date.lte=YYYY-MM-DD&sort_by=first_air_date.asc
```
- Returns: TV shows airing in date range
- Can filter by: networks, genres, language, etc.

**4. Movie/TV Details with Watch Providers**
```
GET /movie/{id}/watch/providers
GET /tv/{id}/watch/providers
```
- Returns: Streaming platforms by region (Netflix, Prime, Hotstar, etc.)
- Shows: rent, buy, flatrate (subscription) options
- Region-specific: Can filter for India (IN)

#### Current Test Results:
- ✅ Discovered 106 upcoming movies for India (Nov-Dec 2025)
- ✅ Contains Indian movies (e.g., "Dhurandhar" - धुरंधर)
- ✅ Includes international releases in India
- ✅ Has accurate release dates

---

### 2. Official Streaming Platform Pages

#### Disney+ Hotstar
- **URL**: `https://www.hotstar.com/in/browse/editorial/coming-soon/8445`
- **Structure**: Dynamic JavaScript (Next.js)
- **API**: Uses `bifrost-api.hotstar.com`
- **Feasibility**: ⚠️ **Difficult** - Requires API authentication/tokens
- **Data Quality**: ⭐⭐⭐⭐⭐ (Direct from source)

#### Netflix
- **URL**: No public "coming soon" page
- **API**: Private API, requires authentication
- **Feasibility**: ❌ **Not Feasible** - No public access

#### Amazon Prime Video
- **URL**: No dedicated upcoming page
- **API**: Private API
- **Feasibility**: ❌ **Not Feasible** - No public access

#### Zee5, Sony LIV, Sun NXT
- **Structure**: Similar issues - dynamic content, no public APIs
- **Feasibility**: ⚠️ **Difficult** - Would require reverse engineering

---

### 3. JustWatch (Aggregator) ⭐

#### Overview:
- **URL**: `https://www.justwatch.com/in/upcoming`
- **Purpose**: Aggregates upcoming content across all streaming platforms
- **Coverage**: Netflix, Prime, Hotstar, Zee5, Sony LIV, Sun NXT, etc.

#### Advantages:
- ✅ Multi-platform aggregation
- ✅ India-specific content
- ✅ Release dates and platform information
- ✅ "Notify me" feature for users

#### Challenges:
- ⚠️ Client-side rendering (JavaScript frameworks)
- ⚠️ May require API reverse engineering
- ⚠️ No official public API
- ⚠️ Potential for breaking changes

#### Feasibility:
- **With Browser Automation**: ✅ Possible (Playwright/Selenium)
- **Without Automation**: ❌ Difficult

---

### 4. OTT News/Entertainment Websites

#### FilmiBeat, IndiaTV, TheHansIndia, etc.
- **URLs**: Various entertainment news sites
- **Content**: Weekly OTT release articles
- **Structure**: Traditional HTML, easier to scrape

#### Advantages:
- ✅ Human-curated content
- ✅ Often includes reviews/ratings
- ✅ Easier HTML structure

#### Disadvantages:
- ❌ Not real-time (weekly updates)
- ❌ Manual curation may miss content
- ❌ Inconsistent formats across sites
- ❌ May contain inaccuracies

---

## Recommended Strategy

### **Primary Source: TMDB API** ⭐⭐⭐⭐⭐

Use TMDB as the primary data source with these approaches:

#### 1. **Upcoming Theatrical Releases**
```python
# Get movies upcoming in theaters in India
GET /movie/upcoming?region=IN&page=1
```

#### 2. **Upcoming Streaming Releases**
```python
# Use discover with date range and watch providers
GET /discover/movie?region=IN&release_date.gte={today}&release_date.lte={+60days}&sort_by=release_date.asc

# Then for each movie, check watch providers:
GET /movie/{id}/watch/providers
# Filter for India (IN) region
```

#### 3. **TV Shows**
```python
# Discover upcoming TV shows
GET /discover/tv?air_date.gte={today}&air_date.lte={+60days}&sort_by=first_air_date.asc

# Check watch providers:
GET /tv/{id}/watch/providers
```

#### 4. **Platform-Specific Filtering**
After fetching from TMDB, filter by streaming platforms:
- Netflix (Provider ID: 8)
- Amazon Prime Video (Provider ID: 9)
- Disney+ Hotstar (Provider ID: 122)
- Zee5 (Provider ID: 232)
- Sony LIV (Provider ID: 237)
- Sun NXT (Provider ID: 309)
- Apple TV+ (Provider ID: 350)
- Aha (Provider ID: 532)

### **Secondary Source: JustWatch (Optional)**

Use JustWatch with browser automation for additional validation:
- Cross-reference TMDB data
- Find platform-exclusive content
- Verify release dates
- Get user ratings/interest

---

## Implementation Plan

### Phase 1: TMDB-Based Scraping (Immediate)
1. ✅ Update scraper to use TMDB discover endpoints
2. ✅ Fetch movies and TV shows with date ranges
3. ✅ Get watch providers for each item
4. ✅ Filter for Indian streaming platforms
5. ✅ Store platform information with each item

### Phase 2: Enhanced Data (Optional)
1. Add JustWatch scraping with Playwright
2. Cross-reference with TMDB data
3. Add user interest/popularity metrics

### Phase 3: Platform-Specific (Future)
1. Research official platform APIs
2. Consider partnerships for data access
3. Implement direct integrations where possible

---

## TMDB Watch Provider IDs for India

### Major Platforms:
```json
{
  "Netflix": 8,
  "Amazon Prime Video": 9,
  "Disney+ Hotstar": 122,
  "Zee5": 232,
  "Sony LIV": 237,
  "Sun NXT": 309,
  "Apple TV+": 350,
  "Aha": 532,
  "Manorama MAX": Need to verify,
  "ALT Balaji": Need to verify
}
```

---

## Sample TMDB API Calls

### Get Upcoming Movies (Next 60 Days):
```bash
curl "https://api.themoviedb.org/3/discover/movie?api_key=YOUR_KEY&region=IN&release_date.gte=2025-11-21&release_date.lte=2026-01-20&sort_by=release_date.asc"
```

### Get Watch Providers for a Movie:
```bash
curl "https://api.themoviedb.org/3/movie/MOVIE_ID/watch/providers?api_key=YOUR_KEY"
```

### Get Upcoming TV Shows:
```bash
curl "https://api.themoviedb.org/3/discover/tv?api_key=YOUR_KEY&air_date.gte=2025-11-21&air_date.lte=2026-01-20&sort_by=first_air_date.asc"
```

---

## Conclusion

**TMDB API is the clear winner** for reliable, comprehensive, and easy-to-access data about upcoming movies and TV shows in India. It provides:

- ✅ Better data quality than Binged.com
- ✅ No scraping complexity (direct API)
- ✅ Official streaming platform information
- ✅ Rich metadata already integrated
- ✅ Free and reliable service
- ✅ Region-specific filtering

**Action Item**: Migrate from Binged.com scraping to TMDB API-based discovery with watch provider filtering.
