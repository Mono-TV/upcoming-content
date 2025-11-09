"""
Configuration file for content scraping
Supports multi-city configuration for BookMyShow scraping
"""

# BookMyShow Configuration
BMS_CONFIG = {
    'default_city': 'bengaluru',
    'cities': {
        'bengaluru': {
            'name': 'Bengaluru',
            'display_name': 'Bengaluru',
            'code': 'bengaluru',
            'region': 'South India'
        },
        'mumbai': {
            'name': 'Mumbai',
            'display_name': 'Mumbai',
            'code': 'mumbai',
            'region': 'West India'
        },
        'delhi': {
            'name': 'Delhi-NCR',
            'display_name': 'Delhi-NCR',
            'code': 'ncr',
            'region': 'North India'
        },
        'hyderabad': {
            'name': 'Hyderabad',
            'display_name': 'Hyderabad',
            'code': 'hyderabad',
            'region': 'South India'
        },
        'chennai': {
            'name': 'Chennai',
            'display_name': 'Chennai',
            'code': 'chennai',
            'region': 'South India'
        },
        'pune': {
            'name': 'Pune',
            'display_name': 'Pune',
            'code': 'pune',
            'region': 'West India'
        },
        'kolkata': {
            'name': 'Kolkata',
            'display_name': 'Kolkata',
            'code': 'kolkata',
            'region': 'East India'
        }
    },
    # Scraping settings
    'scroll_iterations': 10,  # Number of times to scroll for lazy loading
    'detail_page_timeout': 30000,  # Timeout in milliseconds
    'request_delay': 2.5,  # Delay between requests in seconds (rate limiting)
    'max_retries': 3,  # Max retries for failed requests
}

# Binged Configuration
BINGED_CONFIG = {
    'base_url': 'https://www.binged.com',
    'platforms': {
        '4': 'Amazon Prime Video',
        '5': 'Apple TV+',
        '6': 'SunNXT',
        '8': 'Zee5',
        '10': 'Jio Hotstar',
        '21': 'ManoramaMAX',
        '30': 'Netflix',
        '53': 'Sony LIV',
        '55': 'Aha Video',
        '71': 'ALT Balaji',
        '72': 'Discovery Plus',
        '73': 'ErosNow',
        '74': 'Hoichoi',
    },
    'request_delay': 1.5,  # Delay between requests
    'detail_page_timeout': 20000,  # Timeout for detail pages
}

# OTT Platform URLs for Binged scraping
OTT_PLATFORM_FILTERS = [
    'ALT Balaji',
    'Aha Video',
    'Amazon',
    'Apple Tv Plus',
    'Book My Show',
    'Chaupal',
    'Crunchyroll',
    'Discovery Plus',
    'ETV Win',
    'Epic On',
    'ErosNow',
    'Hoichoi',
    'Jio Hotstar',
    'KLiKK',
    'Lionsgate Play',
    'Manorama MAX',
    'Mubi',
    'Netflix',
    'Planet Marathi OTT',
    'Shemaroo Me',
    'Sony LIV',
    'Sun NXT',
    'Viki',
    'Zee5'
]

# TMDB Configuration
TMDB_CONFIG = {
    'base_url': 'https://api.themoviedb.org/3',
    'image_base_url': 'https://image.tmdb.org/t/p',
    'request_delay': 0.5,  # Rate limiting
    'max_retries': 3,
}

# YouTube Configuration
YOUTUBE_CONFIG = {
    'search_delay': 1.0,  # Delay between searches
    'max_retries': 3,
}

# Content Type Definitions
CONTENT_TYPES = {
    'ott_released': {
        'name': 'New Releases (OTT)',
        'description': 'Recently released OTT content',
        'output_file': 'ott_releases_enriched.json',
        'display_order': 1
    },
    'ott_upcoming': {
        'name': 'Upcoming OTT Releases',
        'description': 'Upcoming OTT platform releases',
        'output_file': 'movies_enriched.json',  # Keep existing filename
        'display_order': 2
    },
    'theatre_current': {
        'name': 'Movies in Theatre',
        'description': 'Currently playing in theatres',
        'output_file': 'theatre_current_enriched.json',
        'display_order': 3
    },
    'theatre_upcoming': {
        'name': 'Upcoming Theatre Releases',
        'description': 'Upcoming theatrical releases',
        'output_file': 'theatre_upcoming_enriched.json',
        'display_order': 4
    }
}

# Video Format Priorities (for theatre content)
VIDEO_FORMAT_PRIORITY = [
    'IMAX 3D',
    'IMAX 2D',
    'IMAX',
    'DOLBY CINEMA 3D',
    'DOLBY ATMOS',
    'DOLBY CINEMA',
    '4DX 3D',
    '4DX',
    'MX4D 3D',
    'MX4D',
    'ICE 3D',
    'ICE',
    '3D SCREEN X',
    'SCREEN X',
    '3D',
    '2D',
]

# Date range for upcoming theatre releases
UPCOMING_THEATRE_DATE_RANGE = {
    'end_date': '2025-12-31',  # Filter movies releasing before this date
}
