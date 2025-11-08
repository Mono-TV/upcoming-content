// Data and state
let moviesData = [];
let filteredMovies = [];
let selectedPlatforms = new Set();
let selectedContentType = null; // 'Movies', 'Shows', or null for all
let currentExpandedCard = null;

// Cache DOM references for better performance
const domCache = {
    loading: null,
    filtersSection: null,
    contentTypeSection: null,
    filterChips: null,
    moviesGrid: null,
    backdrop: null
};

// Platform logo mapping
const platformLogos = {
    'Netflix': 'Netflix.png',
    'Amazon Prime Video': 'Amazon_Prime_Video.png',
    'JioHotstar': 'jiohotstar.svg',
    'SunNXT': 'sunnxt.png',
    'ManoramaMAX': 'manoramamax.png'
};

// Initialize DOM cache
function initDOMCache() {
    domCache.loading = document.getElementById('loading');
    domCache.filtersSection = document.getElementById('filtersSection');
    domCache.contentTypeSection = document.getElementById('contentTypeSection');
    domCache.filterChips = document.getElementById('filterChips');
    domCache.moviesGrid = document.getElementById('moviesGrid');
    domCache.backdrop = document.getElementById('backdrop');
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
    moviesData.forEach(movie => {
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
    moviesChip.textContent = 'Movies';
    moviesChip.onclick = () => toggleContentType('Movies', moviesChip);
    domCache.contentTypeSection.appendChild(moviesChip);

    const showsChip = document.createElement('div');
    showsChip.className = 'filter-chip content-type-chip';
    showsChip.textContent = 'Shows';
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
    // Check cache first
    const cacheKey = getCacheKey();
    if (filterCache.has(cacheKey)) {
        filteredMovies = filterCache.get(cacheKey);
        displayMovies(filteredMovies);
        return;
    }

    let filtered = moviesData;

    // Apply content type filter
    if (selectedContentType) {
        filtered = filtered.filter(movie => {
            // Check if it's a TV show based on title or media type
            const isShow = movie.tmdb_media_type === 'tv' ||
                           movie.title?.toLowerCase().includes('season') ||
                           movie.title?.toLowerCase().match(/\bs\d+/i); // Matches S1, S2, etc.

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

    // Cache the result
    filterCache.set(cacheKey, filtered);
    filteredMovies = filtered;
    displayMovies(filteredMovies);
}

// Load and display movies
async function loadMovies() {
    try {
        // Try loading enriched version first, fallback to trailers version
        let response;
        try {
            response = await fetch('movies_enriched.json');
            if (!response.ok) throw new Error('Not found');
        } catch {
            response = await fetch('movies_with_trailers.json');
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        moviesData = await response.json();
        filteredMovies = moviesData; // Initialize filtered movies

        domCache.loading.style.display = 'none';
        createFilterChips(); // Create platform filters
        displayMovies(filteredMovies);
    } catch (error) {
        console.error('Error loading movies:', error);
        domCache.loading.innerHTML = `
            <div style="color: #d32f2f;">
                Unable to load movies. Please check your connection.
                <br><br>
                <button onclick="loadMovies()" style="padding: 10px 20px; cursor: pointer; border-radius: 8px; border: none; background: #f5af19; color: white; font-weight: 600;">
                    Retry
                </button>
            </div>
        `;
    }
}

function displayMovies(movies) {
    domCache.moviesGrid.innerHTML = '';

    // Use document fragment for better performance
    const fragment = document.createDocumentFragment();

    movies.forEach(movie => {
        const card = createMovieCard(movie);
        fragment.appendChild(card);
    });

    domCache.moviesGrid.appendChild(fragment);

    // Trigger animation
    requestAnimationFrame(() => {
        domCache.moviesGrid.style.opacity = '1';
    });
}

function createMovieCard(movie) {
    const card = document.createElement('div');
    card.className = 'movie-card';

    // Only make clickable if trailer exists
    if (movie.youtube_id) {
        card.onclick = (e) => {
            if (!e.target.closest('.close-button')) {
                expandCard(card, movie);
            }
        };
    } else {
        card.style.cursor = 'default';
    }

    const platforms = movie.platforms || [];
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

    card.innerHTML = `
        <div class="movie-poster">
            <img src="${safePosterUrl}"
                 alt="${safeTitle}"
                 loading="lazy"
                 data-title="${safeTitle}"
                 class="movie-poster-img">

            <!-- Hover Tooltip -->
            <div class="movie-tooltip">
                <div class="tooltip-content">
                    <div class="tooltip-title">${safeTitle}</div>
                    <div class="tooltip-meta">
                        ${safeYear ? `<p>${safeYear}</p>` : ''}
                        ${safeReleaseDate ? `<p>Streaming ${safeReleaseDate}</p>` : ''}
                        ${platformsHTML ? `<p>${platformsHTML}</p>` : ''}
                    </div>
                </div>
            </div>

            <!-- Trailer Window (hidden by default, iframe created on demand) -->
            <div class="trailer-window" data-youtube-id="${movie.youtube_id || ''}"></div>

            <!-- Close Button -->
            <button class="close-button" onclick="collapseCard(event)"></button>
        </div>
    `;

    // Add error handler for missing images - create liquid glass placeholder
    const posterImg = card.querySelector('.movie-poster-img');
    if (posterImg) {
        posterImg.addEventListener('error', function() {
            // Don't recreate if already has placeholder
            if (this.parentElement.querySelector('.poster-placeholder')) return;

            // Create liquid glass placeholder
            const placeholder = document.createElement('div');
            placeholder.className = 'poster-placeholder';

            const titleText = document.createElement('div');
            titleText.className = 'poster-placeholder-text';
            titleText.textContent = this.getAttribute('data-title') || 'Untitled';

            placeholder.appendChild(titleText);

            // Hide the broken image and add placeholder
            this.style.display = 'none';
            this.parentElement.appendChild(placeholder);
        });
    }

    return card;
}

function expandCard(card, movie) {
    if (currentExpandedCard) return; // Prevent multiple expansions

    // Don't expand if no trailer available
    if (!movie.youtube_id) {
        console.log('No trailer available for:', movie.title);
        return;
    }

    console.log('Expanding card for:', movie.title, 'YouTube ID:', movie.youtube_id);
    currentExpandedCard = card;

    // Get current position before changing anything
    const rect = card.getBoundingClientRect();

    // Set initial fixed position at current location
    card.style.position = 'fixed';
    card.style.top = rect.top + 'px';
    card.style.left = rect.left + 'px';
    card.style.width = rect.width + 'px';
    card.style.height = rect.height + 'px';
    card.style.zIndex = '5000';
    card.style.margin = '0';

    // Add expanded class immediately
    card.classList.add('expanded');
    console.log('Card expanded class added');

    // LAZY IFRAME CREATION: Create iframe only when needed
    const trailerWindow = card.querySelector('.trailer-window');
    console.log('Trailer window found:', trailerWindow);

    if (!trailerWindow.querySelector('iframe') && movie.youtube_id) {
        const iframe = document.createElement('iframe');
        // Add autoplay parameter and sanitize the youtube_id
        const safeYoutubeId = sanitizeAttribute(movie.youtube_id);
        const embedUrl = `https://www.youtube.com/embed/${safeYoutubeId}?autoplay=1&rel=0`;
        console.log('Creating iframe with URL:', embedUrl);

        iframe.src = embedUrl;
        iframe.setAttribute('frameborder', '0');
        iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
        iframe.setAttribute('allowfullscreen', '');
        iframe.style.width = '100%';
        iframe.style.height = '100%';

        trailerWindow.appendChild(iframe);
        console.log('Iframe appended to trailer window');
    } else {
        console.log('Iframe already exists or no youtube_id');
    }

    // Force a reflow
    card.offsetHeight;
}

function collapseCard(event) {
    if (event) {
        event.stopPropagation();
    }

    if (!currentExpandedCard) return;

    const card = currentExpandedCard;

    // Remove iframe to stop playback and save resources
    const trailerWindow = card.querySelector('.trailer-window');
    const iframe = trailerWindow.querySelector('iframe');
    if (iframe) {
        iframe.remove();
    }

    // Collapse card
    card.classList.remove('expanded');

    // Reset inline styles after transition
    setTimeout(() => {
        if (card && !card.classList.contains('expanded')) {
            card.style.position = '';
            card.style.top = '';
            card.style.left = '';
            card.style.width = '';
            card.style.height = '';
            card.style.zIndex = '';
            card.style.margin = '';
        }
    }, 600); // Match the transition duration

    currentExpandedCard = null;
}

// Close on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') collapseCard();
});

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initDOMCache();
    loadMovies();
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
