# Product Requirements Document (PRD)
## Circuit House - Upcoming Content Showcase

**Version:** 1.0
**Last Updated:** November 16, 2025
**Document Owner:** Product Team
**Status:** Active Development

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Product Overview](#product-overview)
3. [Problem Statement](#problem-statement)
4. [Target Audience](#target-audience)
5. [Product Goals and Objectives](#product-goals-and-objectives)
6. [User Stories](#user-stories)
7. [Features and Requirements](#features-and-requirements)
8. [Technical Architecture](#technical-architecture)
9. [User Experience](#user-experience)
10. [Success Metrics](#success-metrics)
11. [Dependencies and Integrations](#dependencies-and-integrations)
12. [Constraints and Assumptions](#constraints-and-assumptions)
13. [Release Plan](#release-plan)
14. [Future Roadmap](#future-roadmap)

---

## 1. Executive Summary

Circuit House is a web-based content discovery platform that aggregates and displays upcoming movies and TV shows from major streaming platforms (OTT) and theatrical releases. The application provides users with a beautiful, Apple-inspired interface to browse release schedules, watch trailers, and filter content by platform and type.

**Key Highlights:**
- Aggregates content from 25+ streaming platforms and theatrical releases
- Auto-enriched metadata from TMDb, IMDb, and YouTube
- Apple Liquid Design interface with glassmorphism effects
- Progressive Web App (PWA) with offline support
- Fully automated data pipeline for content updates

---

## 2. Product Overview

### 2.1 Product Vision
To become the go-to destination for entertainment enthusiasts to discover what's streaming now and what's coming soon across all platforms and theatres.

### 2.2 Product Description
Circuit House is a static web application that:
- **Scrapes** upcoming content data from Binged.com (OTT) and BookMyShow (theatres)
- **Enriches** data with high-quality posters, trailers, ratings, and metadata
- **Presents** content in a responsive, visually stunning interface
- **Filters** content by platform, type (movies/shows), and release status

### 2.3 Core Value Propositions
1. **Single Source of Truth**: One platform to track all upcoming releases
2. **Rich Metadata**: High-quality posters, trailers, ratings, and descriptions
3. **Platform Agnostic**: Compare releases across Netflix, Prime Video, Hotstar, and more
4. **Beautiful Design**: Apple-inspired aesthetics with fluid animations
5. **Always Updated**: Automated pipeline keeps content fresh

---

## 3. Problem Statement

### 3.1 User Pain Points
**Current State:**
- Users must visit multiple streaming platforms to discover new content
- Theatre release schedules are scattered across different websites
- No unified view of what's coming soon across all platforms
- Poor discovery experience on individual platform apps
- Missing release dates and trailer availability information

**Desired State:**
- One comprehensive view of all upcoming content
- Easy comparison across platforms
- Rich metadata (trailers, ratings, descriptions) in one place
- Beautiful, distraction-free browsing experience
- Mobile-friendly interface for on-the-go discovery

### 3.2 Business Problem
Streaming platforms and theatres lack a centralized discovery mechanism, leading to:
- Poor user engagement with upcoming content
- Missed releases that users would be interested in
- Fragmented user experience across platforms

---

## 4. Target Audience

### 4.1 Primary Users
1. **Entertainment Enthusiasts** (Ages 18-45)
   - Heavy consumers of movies and TV shows
   - Subscribe to multiple streaming platforms
   - Want to stay updated on releases
   - Tech-savvy, use mobile and desktop

2. **Cord Cutters** (Ages 25-55)
   - Migrated from cable to streaming
   - Optimize platform subscriptions based on content
   - Need to track which platform has desired content
   - Budget-conscious

3. **Movie Buffs** (All ages)
   - Follow theatrical releases closely
   - Plan theatre visits in advance
   - Interested in IMAX, 4DX, and premium formats
   - Track specific genres or franchises

### 4.2 Secondary Users
1. **Casual Viewers**: Occasional browsers looking for weekend entertainment
2. **Content Creators**: Reviewers and bloggers tracking release schedules
3. **Industry Professionals**: Media professionals monitoring market releases

### 4.3 User Personas

**Persona 1: Arjun - The Multi-Platform Subscriber**
- Age: 28, Software Engineer
- Subscribes to: Netflix, Prime Video, Hotstar
- Behavior: Watches 3-5 movies/shows per week
- Pain Point: Wastes time browsing each platform separately
- Goal: See all upcoming releases in one place

**Persona 2: Priya - The Weekend Movie Planner**
- Age: 35, Marketing Manager
- Behavior: Plans family theatre visits on weekends
- Pain Point: Misses theatre release announcements
- Goal: Track upcoming theatrical releases with ratings

**Persona 3: Rahul - The Binge Watcher**
- Age: 22, College Student
- Behavior: Shares account with friends, watches daily
- Pain Point: Doesn't know when favorite shows release
- Goal: Get notified about new seasons and releases

---

## 5. Product Goals and Objectives

### 5.1 Business Goals
1. **Content Aggregation**: Aggregate 100+ upcoming titles per week
2. **User Engagement**: Achieve 70% return visitor rate
3. **Data Freshness**: Update content daily with 95%+ accuracy
4. **Platform Coverage**: Cover top 20 streaming platforms in India

### 5.2 User Goals
1. Discover new content across all platforms effortlessly
2. Save time browsing multiple websites
3. Access trailers and metadata in one place
4. Filter content by preferences (platform, type)
5. Get a premium browsing experience

### 5.3 Technical Goals
1. **Performance**: Page load under 2 seconds
2. **Reliability**: 99.9% uptime for web interface
3. **Scalability**: Support 10,000+ content items
4. **Automation**: Fully automated data updates
5. **Accessibility**: WCAG 2.1 AA compliance

---

## 6. User Stories

### 6.1 Epic 1: Content Discovery
- **US-001**: As a user, I want to see upcoming OTT releases so I can plan my watchlist
- **US-002**: As a user, I want to see movies currently in theatres so I can plan weekend outings
- **US-003**: As a user, I want to see upcoming theatrical releases so I can book advance tickets
- **US-004**: As a user, I want to view high-quality movie posters so I can visually identify content

### 6.2 Epic 2: Content Filtering
- **US-005**: As a Netflix subscriber, I want to filter only Netflix content so I see relevant releases
- **US-006**: As a user, I want to filter movies vs shows so I can find my preferred content type
- **US-007**: As a user, I want to clear all filters so I can start a fresh search
- **US-008**: As a user, I want to see filter counts so I know how much content is available

### 6.3 Epic 3: Content Details
- **US-009**: As a user, I want to watch trailers so I can decide if I'm interested
- **US-010**: As a user, I want to see ratings and descriptions so I can make informed decisions
- **US-011**: As a user, I want to see genres so I can find content matching my mood
- **US-012**: As a user, I want direct links to platforms so I can watch immediately

### 6.4 Epic 4: User Experience
- **US-013**: As a mobile user, I want a responsive interface so I can browse on my phone
- **US-014**: As a user, I want a beautiful interface so browsing is enjoyable
- **US-015**: As a user, I want smooth animations so the experience feels premium
- **US-016**: As a user, I want offline access so I can browse without internet

### 6.5 Epic 5: Hero Section
- **US-017**: As a user, I want to see featured content so I discover popular releases
- **US-018**: As a user, I want an interactive hero carousel so I can preview top content
- **US-019**: As a user, I want to navigate the carousel so I can explore featured items

---

## 7. Features and Requirements

### 7.1 Core Features (MVP - Implemented)

#### 7.1.1 Content Aggregation Pipeline
**Priority:** P0 (Critical)

**Description:** Automated scraping and enrichment pipeline

**Functional Requirements:**
- FR-001: Scrape OTT releases from Binged.com with pagination support
- FR-002: Scrape theatre releases from BookMyShow for multiple cities
- FR-003: Enrich content with TMDb metadata (posters, ratings, descriptions, genres)
- FR-004: Fetch YouTube trailers using YouTube Data API or web scraping
- FR-005: Generate fallback placeholder posters for missing images
- FR-006: Support deep links to streaming platforms
- FR-007: Detect and categorize content types (movie/show)

**Technical Requirements:**
- TR-001: Use Playwright for dynamic content scraping
- TR-002: Implement rate limiting to respect API limits
- TR-003: Retry mechanism for failed requests (3 retries max)
- TR-004: Async/await for efficient parallel processing
- TR-005: Generate JSON output files for web consumption

**Acceptance Criteria:**
- ✅ Successfully scrapes 95%+ of available content
- ✅ Enrichment success rate > 90% for metadata
- ✅ Pipeline completes within 15 minutes for 100 items
- ✅ Handles network failures gracefully
- ✅ Output JSON is valid and well-structured

#### 7.1.2 Web Interface
**Priority:** P0 (Critical)

**Description:** Static HTML/CSS/JS web application

**Functional Requirements:**
- FR-008: Display 4 content rows (OTT Released, OTT Upcoming, Theatre Current, Theatre Upcoming)
- FR-009: Horizontal scrollable timeline for each content row
- FR-010: Hero carousel with 5 featured items
- FR-011: Platform filter chips (Netflix, Prime Video, etc.)
- FR-012: Content type filter (Movies/Shows)
- FR-013: Clear all filters button
- FR-014: Expandable detail modal with trailer player
- FR-015: Navigation between content items in detail view
- FR-016: Lazy loading for images
- FR-017: Responsive design (mobile, tablet, desktop)

**UI/UX Requirements:**
- UX-001: Apple Liquid Design with glassmorphism effects
- UX-002: Smooth animations (cubic-bezier timing)
- UX-003: Backdrop blur for modals
- UX-004: Dark theme only
- UX-005: Red Hat Display font
- UX-006: Touch-friendly controls on mobile
- UX-007: Keyboard navigation support

**Acceptance Criteria:**
- ✅ Loads within 2 seconds on 4G connection
- ✅ Renders correctly on screen sizes 320px - 2560px
- ✅ Smooth 60fps animations
- ✅ All interactive elements have hover/focus states
- ✅ No layout shift during loading

#### 7.1.3 Progressive Web App (PWA)
**Priority:** P1 (High)

**Description:** Offline-capable web application

**Functional Requirements:**
- FR-018: Service worker for offline caching
- FR-019: Cache static assets (HTML, CSS, JS)
- FR-020: Cache content JSON files
- FR-021: Cache platform logos and icons
- FR-022: Manifest file for "Add to Home Screen"

**Acceptance Criteria:**
- ✅ Works offline after first visit
- ✅ Updates cache when new content available
- ✅ Installable on mobile devices
- ✅ Custom app icon and splash screen

#### 7.1.4 Platform Support
**Priority:** P0 (Critical)

**Description:** Support for major streaming platforms and theatres

**Supported Platforms:**
- Netflix
- Amazon Prime Video
- Jio Hotstar (Disney+ Hotstar)
- Sony LIV
- Zee5
- Apple TV+
- Sun NXT
- Manorama MAX
- Aha Video
- Hoichoi
- ALT Balaji
- Discovery Plus
- ErosNow
- Lionsgate Play
- BookMyShow (Theatres)
- (25+ platforms total)

**Acceptance Criteria:**
- ✅ All platforms have official logos
- ✅ Filtering works for each platform
- ✅ Deep links open correct platform pages

### 7.2 Data Schema

#### 7.2.1 Enriched Content Schema
```json
{
  "content_type": "ott_upcoming | ott_released | theatre_current | theatre_upcoming",
  "title": "string",
  "url": "string",
  "release_date": "string (DD MMM YYYY)",
  "platforms": ["string[]"],
  "tmdb_id": "number",
  "tmdb_media_type": "movie | tv",
  "overview": "string",
  "description": "string",
  "genres": ["string[]"],
  "runtime": "number (minutes)",
  "tmdb_release_date": "string (YYYY-MM-DD)",
  "status": "Released | Post Production | etc",
  "tmdb_rating": "number (0-10)",
  "tmdb_vote_count": "number",
  "original_title": "string",
  "original_language": "string (ISO 639-1)",
  "imdb_id": "string (ttXXXXXXX)",
  "posters": {
    "thumbnail": "string (URL)",
    "small": "string (URL)",
    "medium": "string (URL)",
    "large": "string (URL)",
    "xlarge": "string (URL)",
    "original": "string (URL)"
  },
  "all_posters": ["object[]"],
  "backdrops": {
    "small": "string (URL)",
    "medium": "string (URL)",
    "large": "string (URL)",
    "original": "string (URL)"
  },
  "all_backdrops": ["object[]"],
  "youtube_id": "string",
  "youtube_url": "string",
  "deeplinks": {
    "PlatformName": "string (URL)"
  },
  "cast": ["string[]"],
  "crew": ["string[]"],
  "production_companies": ["string[]"],
  "languages": ["string[]"],
  "certification": "string",
  "video_formats": ["string[]"] // For theatre content
}
```

### 7.3 Non-Functional Requirements

#### 7.3.1 Performance
- NFR-001: First Contentful Paint (FCP) < 1.5s
- NFR-002: Largest Contentful Paint (LCP) < 2.5s
- NFR-003: Time to Interactive (TTI) < 3s
- NFR-004: Cumulative Layout Shift (CLS) < 0.1
- NFR-005: API response time < 500ms
- NFR-006: Image optimization with lazy loading

#### 7.3.2 Security
- NFR-007: Content Security Policy (CSP) headers
- NFR-008: HTTPS only
- NFR-009: No sensitive data in client-side code
- NFR-010: Rate limiting on scraping scripts
- NFR-011: Respect robots.txt and ToS

#### 7.3.3 Scalability
- NFR-012: Support 10,000+ content items
- NFR-013: Handle 10,000 concurrent users
- NFR-014: CDN caching for static assets
- NFR-015: Efficient JSON parsing and rendering

#### 7.3.4 Reliability
- NFR-016: 99.9% uptime for web interface
- NFR-017: Graceful degradation if enrichment fails
- NFR-018: Fallback images for missing posters
- NFR-019: Error handling for network failures

#### 7.3.5 Accessibility
- NFR-020: WCAG 2.1 AA compliance
- NFR-021: Keyboard navigation support
- NFR-022: Screen reader support
- NFR-023: Proper ARIA labels
- NFR-024: Sufficient color contrast (4.5:1)

#### 7.3.6 Browser Support
- NFR-025: Chrome (latest 2 versions)
- NFR-026: Safari (latest 2 versions)
- NFR-027: Firefox (latest 2 versions)
- NFR-028: Edge (latest 2 versions)
- NFR-029: Mobile browsers (iOS Safari, Chrome Mobile)

---

## 8. Technical Architecture

### 8.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Sources                             │
├─────────────────────────────────────────────────────────────┤
│  Binged.com  │  BookMyShow  │  TMDb API  │  YouTube API    │
└────────┬────────────┬────────────┬────────────┬─────────────┘
         │            │            │            │
         └────────────┴────────────┴────────────┘
                      │
         ┌────────────▼────────────┐
         │   Python Scrapers       │
         │  - scrape_ott_releases  │
         │  - scrape_theatre_*     │
         │  - update_all_content   │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │  Enrichment Pipeline    │
         │  - TMDb metadata        │
         │  - YouTube trailers     │
         │  - Placeholder gen      │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │   JSON Data Files       │
         │  - movies_enriched      │
         │  - ott_releases_enr     │
         │  - theatre_*_enr        │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │   Static Web App        │
         │  - index.html           │
         │  - script.js            │
         │  - styles.css           │
         │  - service-worker.js    │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │   GitHub Pages CDN      │
         │  - Static hosting       │
         │  - HTTPS                │
         │  - Global distribution  │
         └─────────────────────────┘
                      │
         ┌────────────▼────────────┐
         │      End Users          │
         │  - Web browsers         │
         │  - Mobile devices       │
         └─────────────────────────┘
```

### 8.2 Technology Stack

#### 8.2.1 Frontend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Markup | HTML5 | Semantic structure |
| Styling | CSS3 | Apple Liquid Design, glassmorphism |
| Scripting | Vanilla JavaScript (ES6+) | Interactive functionality |
| Fonts | Red Hat Display (Google Fonts) | Typography |
| PWA | Service Worker API | Offline caching |

**Why No Framework?**
- Faster load times (no framework overhead)
- Better performance (direct DOM manipulation)
- Simpler deployment (static files only)
- Easier maintenance (no build process)

#### 8.2.2 Backend / Data Pipeline
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Runtime | Python | 3.7+ | Scraping and enrichment |
| Browser Automation | Playwright | >=1.40.0 | Dynamic content scraping |
| HTML Parsing | BeautifulSoup4 | >=4.12.0 | Static HTML parsing |
| XML Parsing | lxml | >=4.9.0 | XML processing |
| HTTP Client | aiohttp | >=3.9.0 | Async API requests |
| HTTP Client (Fallback) | requests | >=2.31.0 | Sync API requests |
| Image Generation | Pillow | >=10.0.0 | Placeholder creation |

#### 8.2.3 APIs and Data Sources
| Source | Purpose | Rate Limit |
|--------|---------|-----------|
| Binged.com | OTT release schedules | 2.5s delay between requests |
| BookMyShow | Theatre releases | 3.5s delay, 10 scroll iterations |
| TMDb API | Metadata, posters, backdrops | 0.5s delay, 40 req/10s |
| YouTube Data API v3 | Trailer videos | 1.0s delay, 10,000 quota/day |
| YouTube (scraping) | Fallback trailer discovery | 1.0s delay |

#### 8.2.4 Deployment
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Hosting | GitHub Pages | Static site hosting |
| CDN | GitHub CDN | Global content delivery |
| CI/CD | GitHub Actions (optional) | Automated updates |
| Version Control | Git | Code management |

### 8.3 Data Flow

#### 8.3.1 Content Update Flow
```
1. Manual/Scheduled Trigger
   ↓
2. Run update_all_content.py
   ↓
3. Scrape OTT Releases (scrape_ott_releases.py)
   - Fetch from Binged.com
   - Extract title, date, platforms
   - Save to ott_releases.json
   ↓
4. Scrape Theatre Current (scrape_theatre_current.py)
   - Fetch from BookMyShow
   - Extract currently playing
   - Save to theatre_current.json
   ↓
5. Scrape Theatre Upcoming (scrape_theatre_upcoming.py)
   - Fetch from BookMyShow
   - Extract upcoming releases
   - Save to theatre_upcoming.json
   ↓
6. Enrich with TMDb
   - Search by title
   - Fetch metadata, posters, backdrops
   - Add ratings, genres, cast
   ↓
7. Enrich with YouTube
   - Search for official trailers
   - Extract video IDs
   - Add trailer URLs
   ↓
8. Generate Placeholders
   - Create fallback images
   - Save to placeholders/
   ↓
9. Save Enriched JSON
   - *_enriched.json files
   ↓
10. Commit & Push to Git
    ↓
11. GitHub Pages Auto-Deploy
```

#### 8.3.2 User Request Flow
```
1. User visits mono-tv.github.io/upcoming-content
   ↓
2. Load index.html from CDN
   ↓
3. Load CSS/JS from CDN (cached by service worker)
   ↓
4. Fetch JSON data files
   - movies_enriched.json
   - ott_releases_enriched.json
   - theatre_current_enriched.json
   - theatre_upcoming_enriched.json
   ↓
5. Parse and categorize content
   ↓
6. Populate hero carousel with top 5 items
   ↓
7. Render 4 content rows
   ↓
8. Lazy load images as user scrolls
   ↓
9. User interacts (filters, detail view, etc.)
   ↓
10. Service worker caches all assets for offline
```

### 8.4 File Structure
```
upcoming-content/
├── Frontend
│   ├── index.html              # Main page
│   ├── script.js               # UI logic (1,900+ lines)
│   ├── styles.css              # Styling (1,600+ lines)
│   ├── detail-modal.js         # Modal functionality
│   ├── detail-modal.css        # Modal styling
│   └── service-worker.js       # PWA offline support
│
├── Data Pipeline
│   ├── update_all_content.py   # Main orchestrator
│   ├── scrape_ott_releases.py  # Binged.com scraper
│   ├── scrape_theatre_current.py
│   ├── scrape_theatre_upcoming.py
│   ├── regenerate_placeholders.py
│   ├── config.py               # Configuration
│   └── requirements.txt        # Python dependencies
│
├── Data Files
│   ├── movies_enriched.json    # OTT upcoming
│   ├── ott_releases_enriched.json
│   ├── theatre_current_enriched.json
│   └── theatre_upcoming_enriched.json
│
├── Assets
│   ├── Platform Logos
│   │   ├── Netflix.svg
│   │   ├── Amazon_Prime_Video.png
│   │   ├── Jio_Hotstar.svg
│   │   └── ... (25+ logos)
│   │
│   └── placeholders/           # Fallback images
│
├── Documentation
│   ├── README.md
│   ├── PRD.md                  # This document
│   ├── QUICK_SETUP.md
│   ├── TESTING_GUIDE.md
│   ├── OPTIMIZATIONS.md
│   └── MULTI_ROW_IMPLEMENTATION.md
│
└── Configuration
    ├── .gitignore
    ├── manual_corrections.json
    └── serve.py                # Local dev server
```

### 8.5 Key Algorithms

#### 8.5.1 Content Filtering Algorithm
```javascript
function filterContent() {
  // 1. Start with all content
  let filtered = allContent;

  // 2. Filter by platforms
  if (selectedPlatforms.size > 0) {
    filtered = filtered.filter(item =>
      item.platforms.some(p => selectedPlatforms.has(p))
    );
  }

  // 3. Filter by content type (Movies/Shows)
  if (selectedContentType) {
    filtered = filtered.filter(item =>
      item.tmdb_media_type === selectedContentType
    );
  }

  // 4. Update UI with filtered results
  renderContent(filtered);
}
```

#### 8.5.2 Hero Carousel Selection
```javascript
function selectFeaturedContent() {
  // 1. Get all content with trailers and high ratings
  let candidates = allContent.filter(item =>
    item.youtube_id &&
    item.tmdb_rating >= 7.0 &&
    item.posters.large
  );

  // 2. Sort by rating and vote count
  candidates.sort((a, b) => {
    let scoreA = a.tmdb_rating * Math.log10(a.tmdb_vote_count + 1);
    let scoreB = b.tmdb_rating * Math.log10(b.tmdb_vote_count + 1);
    return scoreB - scoreA;
  });

  // 3. Select top 5 diverse items
  return selectDiverseItems(candidates, 5);
}
```

#### 8.5.3 Trailer Matching Algorithm
```python
def find_trailer(title, year):
    """
    Multi-strategy trailer discovery
    """
    # Strategy 1: YouTube Data API (if available)
    if YOUTUBE_API_KEY:
        query = f"{title} {year} official trailer"
        results = youtube_api.search(query, type='video', max_results=3)
        return results[0].id if results else None

    # Strategy 2: Web scraping fallback
    query = f"{title} {year} trailer"
    html = fetch_youtube_search(query)
    video_ids = extract_video_ids(html)

    # Filter for official channels
    for vid_id in video_ids:
        channel = get_video_channel(vid_id)
        if 'official' in channel.lower():
            return vid_id

    # Return first result as fallback
    return video_ids[0] if video_ids else None
```

---

## 9. User Experience

### 9.1 Design Principles

1. **Apple-Inspired Aesthetics**
   - Glassmorphism with backdrop blur
   - Clean, minimalist layout
   - Premium feel with smooth animations
   - Dark theme with high contrast

2. **Content First**
   - Large, high-quality posters
   - Minimal UI chrome
   - Focus on visual discovery
   - Contextual information on demand

3. **Effortless Navigation**
   - Horizontal scrolling timelines
   - One-click filtering
   - Intuitive modal interactions
   - Keyboard shortcuts support

4. **Performance Obsession**
   - Instant interactions
   - Lazy loading for images
   - Smooth 60fps animations
   - Progressive enhancement

### 9.2 User Flows

#### 9.2.1 Discovery Flow
```
1. User lands on homepage
   ↓
2. Hero carousel auto-plays with 5 featured items
   ↓
3. User scrolls to browse 4 content rows
   - New OTT Releases
   - Upcoming OTT Releases
   - Movies in Theatre
   - Upcoming Theatre Releases
   ↓
4. User horizontally scrolls each row
   ↓
5. User clicks on poster → Detail modal opens
   ↓
6. User reads description, watches trailer
   ↓
7. User navigates to next item or closes modal
```

#### 9.2.2 Filtering Flow
```
1. User wants to see only Netflix content
   ↓
2. User scrolls to filters section (below hero)
   ↓
3. User clicks "Netflix" chip
   ↓
4. All rows instantly filter to Netflix-only
   - OTT rows show Netflix content
   - Theatre rows hidden (no platform)
   ↓
5. User adds "Movies" filter
   ↓
6. Content further filtered to Netflix movies only
   ↓
7. User clicks "Clear All" to reset
```

#### 9.2.3 Detail View Flow
```
1. User clicks movie poster
   ↓
2. Detail modal slides up from bottom
   ↓
3. Backdrop image blurs behind modal
   ↓
4. Modal shows:
   - Large poster
   - Title, rating, genres
   - Description
   - Platform logos with deep links
   - Embedded YouTube trailer (autoplay)
   ↓
5. User watches trailer
   ↓
6. User clicks left/right arrows to navigate
   ↓
7. User clicks X or backdrop to close
```

### 9.3 Responsive Breakpoints

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Mobile Small | 320px - 480px | 2 columns, smaller fonts, compact hero |
| Mobile Large | 481px - 768px | 3 columns, larger touch targets |
| Tablet | 769px - 1024px | 4 columns, side-by-side filters |
| Desktop Small | 1025px - 1440px | 5 columns, full feature set |
| Desktop Large | 1441px+ | 6+ columns, maximized content |

### 9.4 Animations and Transitions

| Element | Animation | Duration | Easing |
|---------|-----------|----------|--------|
| Poster hover | Scale up 1.05x | 300ms | cubic-bezier(0.4, 0, 0.2, 1) |
| Detail modal | Slide up from bottom | 400ms | cubic-bezier(0.4, 0, 0.2, 1) |
| Filter chip | Background color fade | 200ms | ease-in-out |
| Hero carousel | Transform translateX | 600ms | cubic-bezier(0.4, 0, 0.2, 1) |
| Timeline scroll | Smooth scroll | 300ms | ease-out |

### 9.5 Accessibility Features

- **Keyboard Navigation**
  - Tab through all interactive elements
  - Enter/Space to activate buttons
  - Escape to close modals
  - Arrow keys for carousel navigation

- **Screen Reader Support**
  - Semantic HTML (header, main, section, article)
  - ARIA labels on all buttons
  - Alt text for all images
  - Focus management in modals

- **Visual Accessibility**
  - High contrast text (WCAG AA)
  - Focus indicators on all elements
  - No information conveyed by color alone
  - Readable font sizes (min 14px)

---

## 10. Success Metrics

### 10.1 Key Performance Indicators (KPIs)

#### 10.1.1 Product Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Weekly Active Users (WAU) | 1,000+ | Google Analytics |
| Return Visitor Rate | 70%+ | Google Analytics |
| Average Session Duration | 3+ minutes | Google Analytics |
| Bounce Rate | < 40% | Google Analytics |
| Pages per Session | 2+ | Google Analytics |

#### 10.1.2 Content Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Total Content Items | 500+ | JSON file analysis |
| Content Freshness | < 24 hours old | Last update timestamp |
| Enrichment Success Rate | > 90% | Pipeline logs |
| Poster Availability | > 95% | Content analysis |
| Trailer Availability | > 80% | Content analysis |

#### 10.1.3 Technical Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Page Load Time (LCP) | < 2.5s | Lighthouse |
| First Contentful Paint | < 1.5s | Lighthouse |
| Time to Interactive | < 3s | Lighthouse |
| Lighthouse Performance Score | > 90 | Lighthouse |
| Uptime | 99.9% | UptimeRobot |

#### 10.1.4 Engagement Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Detail Modal Opens | 60%+ of sessions | Event tracking |
| Trailer Views | 40%+ of detail opens | Event tracking |
| Filter Usage | 30%+ of sessions | Event tracking |
| Hero Carousel Interactions | 20%+ of sessions | Event tracking |

### 10.2 Success Criteria

**Phase 1: Launch (Weeks 1-4)**
- ✅ 100+ weekly active users
- ✅ 300+ content items available
- ✅ < 3s page load time
- ✅ 50%+ return visitor rate

**Phase 2: Growth (Months 2-3)**
- 500+ weekly active users
- 500+ content items available
- 60%+ return visitor rate
- 2+ pages per session

**Phase 3: Maturity (Months 4-6)**
- 1,000+ weekly active users
- 800+ content items available
- 70%+ return visitor rate
- Daily automated updates

### 10.3 Analytics Implementation

**Events to Track:**
1. `page_view` - Page loads
2. `filter_applied` - Platform or content type filter
3. `filter_cleared` - Clear all filters
4. `detail_opened` - Detail modal opened
5. `trailer_played` - YouTube trailer played
6. `platform_link_clicked` - Deep link to platform
7. `carousel_navigated` - Hero carousel interaction
8. `content_scrolled` - Timeline horizontal scroll

**Custom Dimensions:**
1. `content_type` - ott_upcoming, theatre_current, etc.
2. `platform_selected` - Netflix, Prime Video, etc.
3. `media_type` - movie, tv
4. `device_type` - mobile, tablet, desktop

---

## 11. Dependencies and Integrations

### 11.1 External Dependencies

#### 11.1.1 Data Sources
| Dependency | Type | Critical? | Fallback |
|------------|------|-----------|----------|
| Binged.com | Web scraping | Yes | Manual data entry |
| BookMyShow | Web scraping | Yes | Disable theatre features |
| TMDb API | REST API | High | Use Binged images |
| YouTube Data API | REST API | Medium | Web scraping fallback |

#### 11.1.2 Third-Party Services
| Service | Purpose | Free Tier | Limits |
|---------|---------|-----------|--------|
| TMDb | Metadata, posters | Yes | 40 req/10s |
| YouTube Data API | Trailer discovery | Yes | 10,000 quota/day |
| Google Fonts | Typography | Yes | Unlimited |
| GitHub Pages | Hosting | Yes | 100GB bandwidth/month |

#### 11.1.3 Python Libraries
| Library | Purpose | License | Alternatives |
|---------|---------|---------|--------------|
| Playwright | Browser automation | Apache 2.0 | Selenium, Puppeteer |
| BeautifulSoup4 | HTML parsing | MIT | lxml, html.parser |
| aiohttp | Async HTTP | Apache 2.0 | httpx, requests |
| Pillow | Image generation | HPND | Pillow-SIMD |

### 11.2 API Keys Required

**Production:**
- `TMDB_API_KEY` - Required for poster/metadata enrichment
- `YOUTUBE_API_KEY` - Optional but recommended for trailers

**Development:**
- Same as production (use separate keys if available)

**How to Obtain:**
1. **TMDb API Key**
   - Sign up at https://www.themoviedb.org/
   - Navigate to Settings → API
   - Request API key (instant approval)
   - Free tier: 40 requests per 10 seconds

2. **YouTube Data API Key**
   - Create project at https://console.cloud.google.com/
   - Enable YouTube Data API v3
   - Create credentials → API key
   - Free tier: 10,000 quota units per day

### 11.3 Integration Points

#### 11.3.1 Data Integration
```python
# config.py integration points
BINGED_CONFIG = {
    'base_url': 'https://www.binged.com',
    'platforms': {...},
    'request_delay': 2.5
}

TMDB_CONFIG = {
    'base_url': 'https://api.themoviedb.org/3',
    'image_base_url': 'https://image.tmdb.org/t/p'
}
```

#### 11.3.2 Frontend Integration
```javascript
// script.js loads data files
const dataFiles = {
  ottUpcoming: 'movies_enriched.json',
  ottReleased: 'ott_releases_enriched.json',
  theatreCurrent: 'theatre_current_enriched.json',
  theatreUpcoming: 'theatre_upcoming_enriched.json'
};
```

---

## 12. Constraints and Assumptions

### 12.1 Technical Constraints

1. **Static Hosting Only**
   - No server-side processing
   - No database
   - No user authentication
   - No real-time updates

2. **Client-Side Processing**
   - All filtering done in browser
   - Limited to JSON parsing performance
   - Memory constraints for large datasets

3. **Scraping Limitations**
   - Dependent on source website structure
   - Rate limiting required
   - Breaking changes require maintenance
   - Legal/ethical considerations

4. **API Rate Limits**
   - TMDb: 40 requests per 10 seconds
   - YouTube: 10,000 quota units per day
   - Must implement caching and delays

### 12.2 Business Constraints

1. **No Revenue Model**
   - Free to use
   - No ads (currently)
   - No user accounts
   - No premium features

2. **Legal Compliance**
   - Respect robots.txt
   - Fair use of scraped data
   - API terms of service
   - Copyright for images/videos

3. **Resource Constraints**
   - GitHub Pages bandwidth limits
   - API quota limits
   - Development time (volunteer project)

### 12.3 Assumptions

1. **User Assumptions**
   - Users have modern browsers
   - Users have stable internet connection
   - Users understand English
   - Users are in India (content focus)

2. **Data Assumptions**
   - Binged.com maintains current structure
   - BookMyShow API remains accessible
   - TMDb has metadata for most content
   - YouTube has trailers for most content

3. **Technical Assumptions**
   - GitHub Pages remains free
   - APIs remain free for current usage
   - Browser APIs remain stable
   - CDN performance is adequate

### 12.4 Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Source website changes structure | High | High | Automated tests, quick fixes |
| API quota exceeded | Medium | High | Caching, fallback to scraping |
| GitHub Pages bandwidth limit | Low | High | CDN optimization, image compression |
| Content becomes stale | Medium | Medium | Automated daily updates |
| Legal takedown request | Low | Critical | Respect ToS, respond quickly |
| Performance degradation | Medium | Medium | Lazy loading, pagination |

---

## 13. Release Plan

### 13.1 Release History

#### v1.0 - Initial Release (Completed)
**Date:** October 2024
**Status:** ✅ Live

**Features:**
- ✅ Basic OTT content scraping
- ✅ TMDb enrichment
- ✅ YouTube trailer integration
- ✅ Simple web interface
- ✅ Platform filtering

#### v2.0 - Multi-Row Enhancement (Completed)
**Date:** November 2024
**Status:** ✅ Live

**Features:**
- ✅ 4 content rows (OTT released, OTT upcoming, Theatre current, Theatre upcoming)
- ✅ BookMyShow theatre integration
- ✅ Enhanced detail modals
- ✅ Hero carousel
- ✅ Improved mobile UX
- ✅ Liquid glass blur effects

### 13.2 Current Version

**Version:** 2.0
**Release Date:** November 16, 2025
**Status:** Active Development

**Live URL:** https://mono-tv.github.io/upcoming-content/

### 13.3 Deployment Process

#### 13.3.1 Manual Deployment
```bash
# 1. Update content
python3 update_all_content.py

# 2. Test locally
python3 serve.py
# Open http://localhost:8000

# 3. Commit changes
git add .
git commit -m "Update content and features"
git push origin main

# 4. GitHub Pages auto-deploys
# Wait 1-2 minutes for CDN propagation
```

#### 13.3.2 Automated Deployment (Optional)
```yaml
# .github/workflows/update-content.yml
name: Daily Content Update
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: playwright install chromium
      - run: python3 update_all_content.py
      - run: |
          git add *.json
          git commit -m "Auto-update content"
          git push
```

---

## 14. Future Roadmap

### 14.1 Short-Term (Next 3 Months)

#### Feature: Search Functionality
**Priority:** High
**Effort:** Medium

- Search by title, actor, director
- Auto-suggest as user types
- Search across all content types
- Highlight search results

#### Feature: Sorting Options
**Priority:** Medium
**Effort:** Low

- Sort by release date
- Sort by rating
- Sort by popularity
- Sort by platform

#### Feature: Date Filtering
**Priority:** Medium
**Effort:** Medium

- Filter by release month
- Filter by release year
- Date range picker
- "Coming this week" quick filter

#### Feature: Watchlist
**Priority:** High
**Effort:** High

- Save favorites to localStorage
- Sync across devices (optional)
- Export watchlist
- Share watchlist via URL

### 14.2 Medium-Term (3-6 Months)

#### Feature: User Preferences
**Priority:** Medium
**Effort:** Medium

- Remember filter selections
- Preferred platforms
- Dark/light theme toggle
- Content type preference

#### Feature: Notifications
**Priority:** High
**Effort:** High

- Release date reminders
- New content alerts
- Push notifications (PWA)
- Email notifications (optional)

#### Feature: Social Sharing
**Priority:** Low
**Effort:** Low

- Share specific titles
- Social media meta tags
- OG images for sharing
- Twitter/Facebook cards

#### Feature: Advanced Filtering
**Priority:** Medium
**Effort:** Medium

- Genre filtering
- Language filtering
- Rating threshold
- Multiple filter combinations

### 14.3 Long-Term (6-12 Months)

#### Feature: User Accounts
**Priority:** Medium
**Effort:** Very High

**Requirements:**
- Backend service (Firebase/Supabase)
- Authentication system
- User profiles
- Cloud-synced watchlists

**Challenges:**
- Requires moving away from static hosting
- Privacy/GDPR compliance
- Increased infrastructure costs

#### Feature: Recommendations
**Priority:** High
**Effort:** Very High

- ML-based recommendations
- "More like this" suggestions
- Trending content
- Personalized homepage

#### Feature: Reviews and Ratings
**Priority:** Medium
**Effort:** Very High

- User-submitted reviews
- Community ratings
- Moderation system
- Review aggregation

#### Feature: International Expansion
**Priority:** Low
**Effort:** High

- Multi-language support
- Region-specific platforms
- Localized content
- Currency/date formatting

#### Feature: Mobile Apps
**Priority:** Medium
**Effort:** Very High

- Native iOS app
- Native Android app
- React Native cross-platform
- App store publishing

### 14.4 Feature Ideas (Backlog)

**Low Priority / Experimental:**
- [ ] Genre analytics and trends
- [ ] Director/actor filmographies
- [ ] Similar movies suggestion
- [ ] IMDb ratings integration
- [ ] Rotten Tomatoes integration
- [ ] Calendar export (iCal, Google Calendar)
- [ ] Platform subscription optimizer
- [ ] "Where to watch" for older content
- [ ] Behind-the-scenes content
- [ ] Discussion forums
- [ ] Watch party scheduling
- [ ] Integration with TV/streaming devices

### 14.5 Technical Debt and Improvements

**Performance:**
- [ ] Implement pagination for large datasets
- [ ] Virtual scrolling for timelines
- [ ] Image CDN (Cloudflare, Cloudinary)
- [ ] Webpack/Vite build process
- [ ] Code splitting and lazy loading

**Code Quality:**
- [ ] TypeScript migration
- [ ] Unit tests (Jest)
- [ ] E2E tests (Playwright)
- [ ] Linting (ESLint, Prettier)
- [ ] Documentation improvements

**Scraping Pipeline:**
- [ ] Distributed scraping (multiple sources)
- [ ] Error monitoring (Sentry)
- [ ] Scraping queue system
- [ ] Incremental updates (not full refresh)
- [ ] Change detection and alerts

**Infrastructure:**
- [ ] Separate staging environment
- [ ] CI/CD pipeline improvements
- [ ] Automated testing in CI
- [ ] Performance monitoring (Lighthouse CI)
- [ ] Dependency security scanning

---

## 15. Appendices

### 15.1 Glossary

| Term | Definition |
|------|------------|
| OTT | Over-The-Top content delivery (streaming platforms) |
| TMDb | The Movie Database - metadata API |
| PWA | Progressive Web App - web app with offline capabilities |
| Glassmorphism | Design trend using frosted glass aesthetics |
| Liquid Design | Apple's design language with fluid animations |
| Deep Link | Direct URL to content on streaming platform |
| Enrichment | Adding metadata to scraped data |
| Scraping | Automated extraction of data from websites |
| Playwright | Browser automation framework |
| Service Worker | JavaScript that runs in background for PWA |

### 15.2 References

**Design Inspiration:**
- Apple.com design language
- Apple TV+ interface
- Netflix web interface
- Glassmorphism.com

**Technical Documentation:**
- [TMDb API Docs](https://developers.themoviedb.org/3)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [Playwright Docs](https://playwright.dev/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)

**Industry Reports:**
- OTT platform market share in India
- Streaming content consumption trends
- Mobile-first design best practices

### 15.3 Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Nov 16, 2025 | Product Team | Initial PRD creation |

---

## 16. Approvals

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Manager | - | - | - |
| Engineering Lead | - | - | - |
| Design Lead | - | - | - |
| QA Lead | - | - | - |

---

**Document End**

*For questions or feedback on this PRD, please open an issue on GitHub or contact the project maintainers.*
