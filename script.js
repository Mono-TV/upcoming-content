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

// Platform logo mapping (matching exact names from JSON)
const platformLogos = {
    'Netflix': 'Netflix.svg',
    'Amazon Prime Video': 'Amazon_Prime_Video.png',
    'Jio Hotstar': 'Jio_Hotstar.svg',
    'Sun NXT': 'sunnxt.png',
    'Manorama MAX': 'manoramamax.png',
    'Sony LIV': 'sonyliv.png'
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

    // Update timeline width to match content
    requestAnimationFrame(() => {
        updateTimelineWidth();
    });

    // Trigger animation
    requestAnimationFrame(() => {
        domCache.moviesGrid.style.opacity = '1';
    });
}

// Update timeline width based on actual content width
function updateTimelineWidth() {
    const grid = domCache.moviesGrid;
    if (!grid) return;

    // Get the actual scrollable width
    const scrollWidth = grid.scrollWidth;

    // Set CSS variable for timeline width (extends slightly past content)
    grid.style.setProperty('--timeline-width', `${scrollWidth + 50}px`);
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

    // Build platform badges for hover overlay
    const platformBadgesHTML = platforms
        .map(p => `<div class="platform-badge">${sanitizeText(p)}</div>`)
        .join('');

    card.innerHTML = `
        <!-- Release Date on Timeline -->
        <div class="release-date-label">${sanitizeText(formattedDate)}</div>

        <div class="movie-poster">
            <img src="${safePosterUrl}"
                 alt="${safeTitle}"
                 loading="lazy"
                 onerror="this.src='${fallbackSvg}'">

            <!-- Play Button Overlay on Hover -->
            ${movie.youtube_id ? `
                <div class="play-button-overlay">
                    <div class="play-button">
                        <div class="play-tooltip">Play Trailer</div>
                    </div>
                </div>
            ` : ''}

            <!-- Platform Overlay - Only Bottom Part on Hover -->
            <div class="platform-overlay">
                ${platformBadgesHTML ? `
                    <div class="platform-overlay-label">Available on</div>
                    <div class="platform-overlay-content">
                        ${platformBadgesHTML}
                    </div>
                ` : ''}
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
