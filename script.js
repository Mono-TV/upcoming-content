// Theme Management - Apple Liquid Design
function initTheme() {
    // Check for saved theme preference or default to 'light'
    const savedTheme = localStorage.getItem('theme') || 'light';
    const html = document.documentElement;

    // Apply theme
    if (savedTheme === 'dark') {
        html.setAttribute('data-theme', 'dark');
        updateMetaThemeColor('#000000');
    } else {
        html.removeAttribute('data-theme');
        updateMetaThemeColor('#fef8f0');
    }
}

function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    if (newTheme === 'dark') {
        html.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        updateMetaThemeColor('#000000');
    } else {
        html.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
        updateMetaThemeColor('#fef8f0');
    }
}

function updateMetaThemeColor(color) {
    // Update meta theme-color for mobile browsers
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
        metaThemeColor.setAttribute('content', color);
    }
}

// Initialize theme on load (before DOM is ready)
initTheme();

// Data and state - Multi-source support
let contentData = {
    ottReleased: [],
    ottUpcoming: [],
    theatreCurrent: [],
    theatreUpcoming: []
};
let filteredContent = {
    ottReleased: [],
    ottUpcoming: [],
    theatreCurrent: [],
    theatreUpcoming: []
};
let selectedPlatforms = new Set();
let selectedContentType = null; // 'Movies', 'Shows', or null for all
let currentExpandedCard = null;

// Cache DOM references for better performance
const domCache = {
    loading: null,
    filtersSection: null,
    contentTypeSection: null,
    filterChips: null,
    backdrop: null,
    // Timeline containers for each content row
    ottReleasedTimeline: null,
    ottUpcomingTimeline: null,
    theatreCurrentTimeline: null,
    theatreUpcomingTimeline: null
};

// Platform logo mapping (matching exact names from JSON)
const platformLogos = {
    // Full platform names
    'Netflix': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/30.png',
    'Amazon Prime Video': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/4.png',
    'Apple TV+': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/5.png',
    'Jio Hotstar': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/10.png',
    'Sun NXT': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/41.png',
    'SunNXT': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/41.png',
    'Manorama MAX': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/27.png',
    'Sony LIV': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/39.png',
    'Zee5': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/52.png',
    'Aha Video': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/2.png',
    'Hoichoi': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/19.png',
    'ALT Balaji': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/1.png',
    'Addatimes': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/0.png',
    'Airtel Xstream': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/3.png',
    'Book My Show': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/6.png',
    'Crunchyroll': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/7.png',
    'Curiosity Stream': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/8.png',
    'Discovery Plus': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/9.png',
    'Epic On': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/11.png',
    'ErosNow': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/12.png',
    'Film Rise': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/13.png',
    'Firstshows': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/14.png',
    'Gemplex': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/15.png',
    'Google Play': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/16.png',
    'GudSho': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/17.png',
    'GuideDoc': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/18.png',
    'Hungama': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/20.png',
    'Jio Cinema': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/21.png',
    'KLiKK': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/22.png',
    'Koode': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/23.png',
    'Mubi': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/24.png',
    'MX Player': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/25.png',
    'Lionsgate Play': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/26.png',
    'Movie Saints': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/28.png',
    'Nee Stream': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/29.png',
    'Oho Gujarati': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/31.png',
    'Planet Marathi OTT': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/32.png',
    'Rooster Teeth': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/33.png',
    'Roots Video': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/34.png',
    'Saina Play': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/35.png',
    'Shemaroo Me': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/36.png',
    'Shreyas ET': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/37.png',
    'Simply South': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/38.png',
    'Spark OTT': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/40.png',
    'TVFPlay': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/42.png',
    'Tata Sky': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/43.png',
    'Tubi': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/44.png',
    'ULLU': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/45.png',
    'Viki': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/46.png',
    'Viu': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/47.png',
    'Voot': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/48.png',
    'Youtube': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/49.png',
    'Yupp Tv': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/50.png',
    'Zee Plex': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/51.png',
    'iTunes': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/53.png',
    'ETV Win': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/55.png',
    'Chaupal': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/56.png',
    'Ultra Jhakaas': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/57.png',
    'Tentkotta': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/58.png',
    'Ultra Play': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/59.png',
    // Platform number references (for backwards compatibility)
    'Platform 0': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/0.png',
    'Platform 1': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/1.png',
    'Platform 2': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/2.png',
    'Platform 3': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/3.png',
    'Platform 4': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/4.png',
    'Platform 5': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/5.png',
    'Platform 6': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/6.png',
    'Platform 7': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/7.png',
    'Platform 8': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/8.png',
    'Platform 9': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/9.png',
    'Platform 10': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/10.png',
    'Platform 11': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/11.png',
    'Platform 12': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/12.png',
    'Platform 13': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/13.png',
    'Platform 14': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/14.png',
    'Platform 15': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/15.png',
    'Platform 16': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/16.png',
    'Platform 17': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/17.png',
    'Platform 18': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/18.png',
    'Platform 19': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/19.png',
    'Platform 20': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/20.png',
    'Platform 21': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/21.png',
    'Platform 22': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/22.png',
    'Platform 23': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/23.png',
    'Platform 24': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/24.png',
    'Platform 25': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/25.png',
    'Platform 26': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/26.png',
    'Platform 27': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/27.png',
    'Platform 28': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/28.png',
    'Platform 29': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/29.png',
    'Platform 30': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/30.png',
    'Platform 31': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/31.png',
    'Platform 32': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/32.png',
    'Platform 33': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/33.png',
    'Platform 34': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/34.png',
    'Platform 35': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/35.png',
    'Platform 36': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/36.png',
    'Platform 37': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/37.png',
    'Platform 38': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/38.png',
    'Platform 39': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/39.png',
    'Platform 40': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/40.png',
    'Platform 41': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/41.png',
    'Platform 42': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/42.png',
    'Platform 43': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/43.png',
    'Platform 44': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/44.png',
    'Platform 45': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/45.png',
    'Platform 46': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/46.png',
    'Platform 47': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/47.png',
    'Platform 48': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/48.png',
    'Platform 49': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/49.png',
    'Platform 50': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/50.png',
    'Platform 51': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/51.png',
    'Platform 52': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/52.png',
    'Platform 53': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/53.png',
    'Platform 54': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/54.png',
    'Platform 55': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/55.png',
    'Platform 56': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/56.png',
    'Platform 57': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/57.png',
    'Platform 58': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/58.png',
    'Platform 59': 'https://www.binged.com/wp-content/themes/binged/assets_new/images/platform-tabs-logos/59.png'
};

// Initialize DOM cache
function initDOMCache() {
    domCache.loading = document.getElementById('loading');
    domCache.filtersSection = document.getElementById('filtersSection');
    domCache.contentTypeSection = document.getElementById('contentTypeSection');
    domCache.filterChips = document.getElementById('filterChips');
    domCache.backdrop = document.getElementById('backdrop');
    // Timeline containers
    domCache.ottReleasedTimeline = document.getElementById('ottReleasedTimeline');
    domCache.ottUpcomingTimeline = document.getElementById('ottUpcomingTimeline');
    domCache.theatreCurrentTimeline = document.getElementById('theatreCurrentTimeline');
    domCache.theatreUpcomingTimeline = document.getElementById('theatreUpcomingTimeline');
}

// Sanitize text to prevent XSS
function sanitizeText(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Sanitize HTML attributes
function sanitizeAttribute(attr) {
    return attr.replace(/[<>"']/g, (char) => {
        const entities = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return entities[char];
    });
}

// Memoization for filter results
const filterCache = new Map();

function getCacheKey() {
    const platforms = Array.from(selectedPlatforms).sort().join(',');
    return `${selectedContentType || 'all'}:${platforms}`;
}

// Filter functions
function createFilterChips() {
    const platforms = new Set();
    // Only collect platforms from OTT content (not theatre)
    [...contentData.ottReleased, ...contentData.ottUpcoming].forEach(movie => {
        if (movie.platforms) {
            movie.platforms.forEach(platform => {
                // Exclude Platform 52
                if (platform !== 'Platform 52') {
                    platforms.add(platform);
                }
            });
        }
    });

    // Create content type filters (Movies/Shows)
    domCache.contentTypeSection.innerHTML = '';

    const moviesChip = document.createElement('div');
    moviesChip.className = 'filter-chip content-type-chip';
    moviesChip.innerHTML = `
        <img src="icon_movies.svg" alt="Movies" style="width: 18px; height: 18px;">
        <span>Movies</span>
    `;
    moviesChip.onclick = () => toggleContentType('Movies', moviesChip);
    domCache.contentTypeSection.appendChild(moviesChip);

    const showsChip = document.createElement('div');
    showsChip.className = 'filter-chip content-type-chip';
    showsChip.innerHTML = `
        <img src="icon_shows.svg" alt="Shows" style="width: 18px; height: 18px;">
        <span>Shows</span>
    `;
    showsChip.onclick = () => toggleContentType('Shows', showsChip);
    domCache.contentTypeSection.appendChild(showsChip);

    // Create platform filters
    domCache.filterChips.innerHTML = '';

    Array.from(platforms).sort().forEach(platform => {
        const chip = document.createElement('div');
        chip.className = 'filter-chip platform-chip';

        // Add logo if available (logo only, no text)
        if (platformLogos[platform]) {
            const logo = document.createElement('img');
            logo.src = platformLogos[platform];
            logo.alt = sanitizeAttribute(platform);
            logo.title = sanitizeAttribute(platform); // Show platform name on hover
            logo.loading = 'lazy'; // Lazy load platform logos
            chip.appendChild(logo);
        } else {
            // Add platform name text only if no logo
            const text = document.createElement('span');
            text.textContent = platform;
            chip.appendChild(text);
        }

        chip.onclick = () => toggleFilter(platform, chip);
        domCache.filterChips.appendChild(chip);
    });

    domCache.filtersSection.style.display = 'block';
}

function toggleContentType(type, chipElement) {
    // Remove active from all content type chips
    const contentTypeChips = domCache.contentTypeSection.querySelectorAll('.content-type-chip');
    contentTypeChips.forEach(chip => {
        chip.classList.remove('active');
    });

    // Toggle selection
    if (selectedContentType === type) {
        selectedContentType = null;
    } else {
        selectedContentType = type;
        chipElement.classList.add('active');
    }

    applyFilters();
}

function toggleFilter(platform, chipElement) {
    if (selectedPlatforms.has(platform)) {
        selectedPlatforms.delete(platform);
        chipElement.classList.remove('active');
    } else {
        selectedPlatforms.add(platform);
        chipElement.classList.add('active');
    }
    applyFilters();
}

function clearFilters() {
    selectedPlatforms.clear();
    selectedContentType = null;
    const allChips = domCache.filtersSection.querySelectorAll('.filter-chip');
    allChips.forEach(chip => {
        chip.classList.remove('active');
    });
    applyFilters();
}

function applyFilters() {
    // Apply filters to OTT content only
    ['ottReleased', 'ottUpcoming'].forEach(contentType => {
        const data = contentData[contentType];
        let filtered = data;

        // Apply content type filter
        if (selectedContentType) {
            filtered = filtered.filter(movie => {
                // Check if it's a TV show based on title or media type
                const isShow = movie.tmdb_media_type === 'tv' ||
                               movie.title?.toLowerCase().includes('season') ||
                               movie.title?.toLowerCase().match(/\bs\d+/i);

                if (selectedContentType === 'Shows') {
                    return isShow;
                } else if (selectedContentType === 'Movies') {
                    return !isShow;
                }
                return true;
            });
        }

        // Apply platform filter
        if (selectedPlatforms.size > 0) {
            filtered = filtered.filter(movie => {
                if (!movie.platforms) return false;
                return movie.platforms.some(platform => selectedPlatforms.has(platform));
            });
        }

        filteredContent[contentType] = filtered;
    });

    // Theatre content is not filtered, always show all
    filteredContent.theatreCurrent = contentData.theatreCurrent;
    filteredContent.theatreUpcoming = contentData.theatreUpcoming;

    // Re-render all content
    displayAllContent();
}

// Load and display all content
async function loadMovies() {
    try {
        // Load all 4 data sources in parallel
        const dataFiles = {
            ottReleased: 'ott_releases_enriched.json',
            ottUpcoming: 'movies_enriched.json',
            theatreCurrent: 'theatre_current_enriched.json',
            theatreUpcoming: 'theatre_upcoming_enriched.json'
        };

        const loadPromises = Object.entries(dataFiles).map(async ([key, filename]) => {
            try {
                const response = await fetch(filename);
                if (response.ok) {
                    contentData[key] = await response.json();
                    filteredContent[key] = contentData[key]; // Initialize filtered data
                    console.log(`✓ Loaded ${contentData[key].length} items from ${filename}`);
                } else {
                    console.warn(`⚠ Could not load ${filename}, using empty array`);
                    contentData[key] = [];
                    filteredContent[key] = [];
                }
            } catch (error) {
                console.warn(`⚠ Error loading ${filename}:`, error.message);
                contentData[key] = [];
                filteredContent[key] = [];
            }
        });

        // Wait for all data to load
        await Promise.all(loadPromises);

        domCache.loading.style.display = 'none';
        createFilterChips(); // Create platform filters (OTT only)
        displayAllContent(); // Render all content rows
    } catch (error) {
        console.error('Error loading content:', error);
        domCache.loading.innerHTML = `
            <div style="color: #d32f2f;">
                Unable to load content. Please check your connection.
                <br><br>
                <button onclick="loadMovies()" style="padding: 10px 20px; cursor: pointer; border-radius: 8px; border: none; background: #f5af19; color: white; font-weight: 600;">
                    Retry
                </button>
            </div>
        `;
    }
}

// Display all content rows
function displayAllContent() {
    displayContentRow('ottReleased', filteredContent.ottReleased, domCache.ottReleasedTimeline);
    displayContentRow('ottUpcoming', filteredContent.ottUpcoming, domCache.ottUpcomingTimeline);
    displayContentRow('theatreCurrent', filteredContent.theatreCurrent, domCache.theatreCurrentTimeline);
    displayContentRow('theatreUpcoming', filteredContent.theatreUpcoming, domCache.theatreUpcomingTimeline);

    // Hide empty rows
    hideEmptyRows();
}

// Display a single content row
function displayContentRow(rowType, items, container) {
    if (!container) return;

    container.innerHTML = '';

    if (!items || items.length === 0) {
        container.innerHTML = '<div class="empty-row-message">No content available</div>';
        return;
    }

    // Use document fragment for better performance
    const fragment = document.createDocumentFragment();

    items.forEach(item => {
        const card = createMovieCard(item, rowType);
        fragment.appendChild(card);
    });

    container.appendChild(fragment);

    // Update timeline width
    requestAnimationFrame(() => {
        updateTimelineWidth(container);
    });

    // Trigger animation
    requestAnimationFrame(() => {
        container.style.opacity = '1';
    });
}

// Hide rows with no content
function hideEmptyRows() {
    const rowMappings = {
        ottReleased: 'ottReleasedRow',
        ottUpcoming: 'ottUpcomingRow',
        theatreCurrent: 'theatreCurrentRow',
        theatreUpcoming: 'theatreUpcomingRow'
    };

    Object.entries(rowMappings).forEach(([dataKey, rowId]) => {
        const row = document.getElementById(rowId);
        if (row) {
            if (filteredContent[dataKey] && filteredContent[dataKey].length > 0) {
                row.style.display = 'block';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

function displayMovies(movies) {
    // Legacy function - keeping for compatibility
    // This is now handled by displayAllContent()
    console.warn('displayMovies() is deprecated, use displayAllContent() instead');
}

// Update timeline width based on actual content width
function updateTimelineWidth(container) {
    if (!container) return;

    // Get all cards
    const cards = container.querySelectorAll('.movie-card');
    if (cards.length === 0) return;

    // Get the position of the last card
    const lastCard = cards[cards.length - 1];
    const lastCardRect = lastCard.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();

    // Calculate the exact position to the center of the last card
    const lastCardCenter = lastCardRect.left - containerRect.left + (lastCardRect.width / 2) + container.scrollLeft;

    // Set CSS variable for timeline width (exactly to last card center)
    container.style.setProperty('--timeline-width', `${lastCardCenter}px`);
}

function createMovieCard(movie, rowType = 'ott_upcoming') {
    const card = document.createElement('div');
    card.className = 'movie-card';

    const isTheatre = rowType.startsWith('theatre');

    // Make clickable if trailer or deeplinks exist
    const hasDeeplinks = movie.deeplinks && Object.keys(movie.deeplinks).length > 0;

    if (movie.youtube_id) {
        // Has trailer - expand to show trailer
        card.onclick = (e) => {
            if (!e.target.closest('.close-button')) {
                expandCard(card, movie);
            }
        };
    } else if (hasDeeplinks) {
        // Has deeplinks - show deeplink modal
        card.onclick = (e) => {
            if (!e.target.closest('.close-button')) {
                showDeeplinkModal(movie);
            }
        };
        card.style.cursor = 'pointer';
    } else {
        card.style.cursor = 'default';
    }

    const platforms = movie.platforms || [];
    const videoFormats = movie.video_formats || [];
    const year = movie.imdb_year || movie.release_date?.match(/\d{4}/) || '';
    const releaseDate = movie.release_date || 'TBA';

    // Use high-quality poster if available, fallback to original
    const posterUrl = movie.poster_url_large || movie.poster_url_medium || movie.image_url;

    // Sanitize all text content
    const safeTitle = sanitizeText(movie.title || 'Untitled');
    const safePosterUrl = sanitizeAttribute(posterUrl || '');
    const safeYear = sanitizeText(year);
    const safeReleaseDate = sanitizeText(releaseDate);

    // Build platforms HTML safely
    const platformsHTML = platforms
        .map(p => sanitizeText(p))
        .join(' • ');

    // Create fallback SVG URL for broken images
    const fallbackSvg = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 450'%3E%3Crect fill='%23667eea' width='300' height='450'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='white'%3E${encodeURIComponent(movie.title || 'Untitled')}%3C/text%3E%3C/svg%3E`;

    // Format release date for timeline (e.g., "Nov 15" or "2024")
    let formattedDate = 'TBA';
    if (releaseDate && releaseDate !== 'TBA') {
        try {
            const date = new Date(releaseDate);
            if (!isNaN(date.getTime())) {
                formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            } else {
                formattedDate = releaseDate;
            }
        } catch (e) {
            formattedDate = releaseDate;
        }
    }

    // Build platform badges for hover overlay (OTT content)
    const platformBadgesHTML = platforms
        .map(p => `<div class="platform-badge">${sanitizeText(p)}</div>`)
        .join('');

    // Build video format badges for theatre content
    const videoFormatBadgesHTML = videoFormats
        .map(f => `<div class="format-badge">${sanitizeText(f)}</div>`)
        .join('');

    card.innerHTML = `
        <!-- Release Date on Timeline -->
        <div class="release-date-label">${sanitizeText(formattedDate)}</div>

        <div class="movie-poster">
            <img src="${safePosterUrl}"
                 alt="${safeTitle}"
                 class="poster-image loading"
                 loading="lazy"
                 onload="this.classList.remove('loading'); this.classList.add('loaded');"
                 onerror="this.src='${fallbackSvg}'; this.classList.remove('loading'); this.classList.add('loaded');">

            <!-- Play Button Overlay on Hover -->
            ${movie.youtube_id ? `
                <div class="play-button-overlay">
                    <div class="play-button">
                        <div class="play-tooltip">Play Trailer</div>
                    </div>
                </div>
            ` : ''}

            <!-- Platform/Format Overlay - Only Bottom Part on Hover -->
            <div class="platform-overlay">
                ${isTheatre ? `
                    ${videoFormatBadgesHTML ? `
                        <div class="platform-overlay-label">Formats</div>
                        <div class="platform-overlay-content">
                            ${videoFormatBadgesHTML}
                        </div>
                    ` : ''}
                ` : `
                    ${platformBadgesHTML ? `
                        <div class="platform-overlay-label">Available on</div>
                        <div class="platform-overlay-content">
                            ${platformBadgesHTML}
                        </div>
                    ` : ''}
                `}
            </div>

            <!-- Hover Tooltip (Hidden) -->
            <div class="movie-tooltip"></div>

            <!-- Trailer Window (hidden by default, iframe created on demand) -->
            <div class="trailer-window" data-youtube-id="${movie.youtube_id || ''}"></div>

            <!-- Close Button -->
            <button class="close-button" onclick="collapseCard(event)"></button>
        </div>

        <!-- Card Title - Below Poster -->
        <div class="card-title">
            <div class="card-title-text ${safeTitle.length > 25 ? 'marquee' : ''}" data-text="${safeTitle}">
                ${safeTitle}
            </div>
        </div>
    `;

    return card;
}

function showDeeplinkModal(movie) {
    const backdrop = document.getElementById('backdrop');

    // Create modal
    const modal = document.createElement('div');
    modal.className = 'deeplink-modal';
    modal.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #fef8f0 0%, #fef5e7 100%);
        border-radius: 24px;
        padding: 32px;
        max-width: 500px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        z-index: 10001;
        font-family: 'Red Hat Display', sans-serif;
    `;

    const title = sanitizeText(movie.title || 'Untitled');
    const deeplinks = movie.deeplinks || {};
    const platforms = Object.keys(deeplinks);

    modal.innerHTML = `
        <div style="margin-bottom: 24px;">
            <h2 style="margin: 0 0 8px 0; font-size: 24px; font-weight: 700; color: #2c3e50;">${title}</h2>
            <p style="margin: 0; color: #7f8c8d; font-size: 14px;">Watch on your favorite platform</p>
        </div>
        <div style="display: flex; flex-direction: column; gap: 12px;">
            ${platforms.map(platform => {
                const link = sanitizeAttribute(deeplinks[platform]);
                const safePlatform = sanitizeText(platform);
                return `
                    <a href="${link}" target="_blank" rel="noopener noreferrer"
                       style="display: flex; align-items: center; justify-content: space-between;
                              padding: 16px 20px; background: white; border-radius: 12px;
                              text-decoration: none; color: #2c3e50; font-weight: 600;
                              transition: all 0.2s ease; border: 2px solid transparent;
                              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);"
                       onmouseover="this.style.borderColor='#f5af19'; this.style.transform='translateX(4px)';"
                       onmouseout="this.style.borderColor='transparent'; this.style.transform='translateX(0)';">
                        <span style="font-size: 16px;">${safePlatform}</span>
                        <span style="font-size: 20px;">→</span>
                    </a>
                `;
            }).join('')}
        </div>
        <button onclick="closeDeeplinkModal()"
                style="margin-top: 24px; width: 100%; padding: 14px;
                       background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
                       color: white; border: none; border-radius: 12px;
                       font-weight: 700; font-size: 16px; cursor: pointer;
                       transition: opacity 0.2s ease;"
                onmouseover="this.style.opacity='0.9';"
                onmouseout="this.style.opacity='1';">
            Close
        </button>
    `;

    document.body.appendChild(modal);
    backdrop.style.display = 'block';

    // Animate in
    setTimeout(() => {
        backdrop.style.opacity = '1';
        modal.style.opacity = '1';
    }, 10);

    // Close on backdrop click
    backdrop.onclick = closeDeeplinkModal;

    // Close on Escape key
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            closeDeeplinkModal();
        }
    };
    document.addEventListener('keydown', escapeHandler);

    // Store reference for cleanup
    modal.escapeHandler = escapeHandler;
}

function closeDeeplinkModal() {
    const modal = document.querySelector('.deeplink-modal');
    const backdrop = document.getElementById('backdrop');

    if (modal) {
        // Remove escape handler
        if (modal.escapeHandler) {
            document.removeEventListener('keydown', modal.escapeHandler);
        }

        // Animate out
        modal.style.opacity = '0';
        backdrop.style.opacity = '0';

        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
            backdrop.style.display = 'none';
            backdrop.onclick = null;
        }, 300);
    }
}

function expandCard(card, movie) {
    if (currentExpandedCard) return; // Prevent multiple expansions

    // Don't expand if no trailer available
    if (!movie.youtube_id) {
        console.log('No trailer available for:', movie.title);
        return;
    }

    currentExpandedCard = card;

    // Create backdrop overlay
    const backdrop = document.createElement('div');
    backdrop.className = 'trailer-backdrop';
    backdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.85);
        z-index: 4999;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    document.body.appendChild(backdrop);

    // Fade in backdrop
    requestAnimationFrame(() => {
        backdrop.style.opacity = '1';
    });

    // Detect mobile for responsive sizing
    const isMobile = window.innerWidth <= 768;

    // Create centered modal container for trailer
    const modal = document.createElement('div');
    modal.className = 'trailer-modal';
    modal.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) scale(0.9);
        width: ${isMobile ? '95vw' : '85vw'};
        max-width: ${isMobile ? '95vw' : '1100px'};
        aspect-ratio: 16/9;
        z-index: 5000;
        border-radius: ${isMobile ? '16px' : '24px'};
        overflow: hidden;
        background: #000;
        box-shadow: 0 50px 100px rgba(0, 0, 0, 0.6),
                    0 20px 40px rgba(0, 0, 0, 0.4),
                    0 0 0 1px rgba(255, 255, 255, 0.1);
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    `;

    // Create iframe
    const iframe = document.createElement('iframe');
    const safeYoutubeId = sanitizeAttribute(movie.youtube_id);
    const origin = encodeURIComponent(window.location.origin);
    iframe.src = `https://www.youtube-nocookie.com/embed/${safeYoutubeId}?autoplay=1&rel=0&modestbranding=1&origin=${origin}`;
    iframe.setAttribute('frameborder', '0');
    iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share');
    iframe.setAttribute('allowfullscreen', '');
    iframe.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
    iframe.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border: none;
        border-radius: ${isMobile ? '16px' : '24px'};
    `;

    modal.appendChild(iframe);

    // Create close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'modal-close-button';
    closeBtn.onclick = (e) => collapseCard(e);
    closeBtn.style.cssText = `
        position: absolute;
        top: ${isMobile ? '-50px' : '-60px'};
        right: 0;
        width: ${isMobile ? '40px' : '48px'};
        height: ${isMobile ? '40px' : '48px'};
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.8);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        z-index: 5001;
    `;

    // Add X icon to close button
    closeBtn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 18 18" style="pointer-events: none;">
            <line x1="0" y1="0" x2="18" y2="18" stroke="#1d1d1f" stroke-width="2"/>
            <line x1="18" y1="0" x2="0" y2="18" stroke="#1d1d1f" stroke-width="2"/>
        </svg>
    `;

    modal.appendChild(closeBtn);
    document.body.appendChild(modal);

    // Store references for cleanup
    card._modal = modal;
    card._backdrop = backdrop;

    // Animate modal in
    requestAnimationFrame(() => {
        modal.style.opacity = '1';
        modal.style.transform = 'translate(-50%, -50%) scale(1)';
    });

    // Close on backdrop click
    backdrop.onclick = () => collapseCard();

    // Close on Escape key
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            collapseCard();
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);
    card._escapeHandler = escapeHandler;
}

function collapseCard(event) {
    if (event) {
        event.stopPropagation();
    }

    if (!currentExpandedCard) return;

    const card = currentExpandedCard;

    // Fade out modal and backdrop
    if (card._modal) {
        card._modal.style.opacity = '0';
        card._modal.style.transform = 'translate(-50%, -50%) scale(0.9)';
    }

    if (card._backdrop) {
        card._backdrop.style.opacity = '0';
    }

    // Remove modal and backdrop after animation
    setTimeout(() => {
        if (card._modal && card._modal.parentNode) {
            card._modal.remove();
            card._modal = null;
        }
        if (card._backdrop && card._backdrop.parentNode) {
            card._backdrop.remove();
            card._backdrop = null;
        }
    }, 300); // Match the transition duration

    // Remove escape key handler
    if (card._escapeHandler) {
        document.removeEventListener('keydown', card._escapeHandler);
        card._escapeHandler = null;
    }

    currentExpandedCard = null;
}

// Close on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') collapseCard();
});

// Update timeline width on window resize
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        updateTimelineWidth();
    }, 150); // Debounce resize events
});

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initDOMCache();
    loadMovies();

    // Setup theme toggle button
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
});

// Register service worker for offline support
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registered:', registration.scope);
            })
            .catch(err => {
                console.log('ServiceWorker registration failed:', err);
            });
    });
}
