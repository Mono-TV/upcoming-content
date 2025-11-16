// Basic Detail Modal JavaScript

// Get platform logos from script.js (defined globally there)
function getPlatformLogo(platform) {
    // platformLogos is defined in script.js
    return window.platformLogos ? window.platformLogos[platform] : null;
}

// Store carousel state
let currentCarouselIndex = 0;
let carouselContent = [];

// Open detail modal with carousel
window.openDetailModal = function(contentItem, contentArray, clickedIndex) {
    const modal = document.getElementById('detailModal');
    const content = document.getElementById('detailModalContent');

    if (!modal || !content) {
        console.error('Modal elements not found');
        return;
    }

    // Store content array and index
    carouselContent = contentArray || [contentItem];
    currentCarouselIndex = clickedIndex || 0;

    // Build carousel with all content items
    content.innerHTML = buildCarousel(carouselContent);

    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Position carousel at clicked item
    setTimeout(() => {
        navigateToIndex(currentCarouselIndex, false);
        updateNavigationArrows();
    }, 50);
};

// Build carousel with multiple detail pages
function buildCarousel(contentArray) {
    const pages = contentArray.map(item => `
        <div class="detail-page">
            <div class="detail-page-inner">
                ${buildDetailContent(item)}
            </div>
        </div>
    `).join('');

    return `<div class="detail-carousel-track">${pages}</div>`;
}

// Navigate to specific index
function navigateToIndex(index, animate = true) {
    const track = document.querySelector('.detail-carousel-track');
    if (!track) return;

    currentCarouselIndex = Math.max(0, Math.min(index, carouselContent.length - 1));

    // Calculate offset - responsive based on viewport width
    const isMobile = window.innerWidth <= 768;
    const pageWidthPercent = 0.85; // Same for both mobile and desktop
    const gap = isMobile ? 12 : 20;
    const maxPageWidth = isMobile ? 9999 : 1100; // No max on mobile
    const pageWidth = Math.min(window.innerWidth * pageWidthPercent, maxPageWidth);

    // Calculate the centering offset
    const viewportWidth = window.innerWidth;
    const centerOffset = (viewportWidth - pageWidth) / 2;

    // Calculate position: move to the item position minus the centering offset
    const itemPosition = currentCarouselIndex * (pageWidth + gap);
    const offset = itemPosition - centerOffset;

    track.style.transform = `translateX(-${offset}px)`;

    if (!animate) {
        track.style.transition = 'none';
        setTimeout(() => {
            track.style.transition = '';
        }, 50);
    }

    // Update active state for blur effect
    const pages = track.querySelectorAll('.detail-page');
    pages.forEach((page, i) => {
        if (i === currentCarouselIndex) {
            page.classList.add('active');
        } else {
            page.classList.remove('active');
        }
    });

    updateNavigationArrows();
}

// Navigate prev/next
window.navigateDetailPrev = function() {
    if (currentCarouselIndex > 0) {
        navigateToIndex(currentCarouselIndex - 1);
    }
};

window.navigateDetailNext = function() {
    if (currentCarouselIndex < carouselContent.length - 1) {
        navigateToIndex(currentCarouselIndex + 1);
    }
};

// Update navigation arrow visibility
function updateNavigationArrows() {
    const leftArrow = document.getElementById('detailNavLeft');
    const rightArrow = document.getElementById('detailNavRight');

    if (leftArrow) {
        if (currentCarouselIndex > 0) {
            leftArrow.classList.add('visible');
        } else {
            leftArrow.classList.remove('visible');
        }
    }

    if (rightArrow) {
        if (currentCarouselIndex < carouselContent.length - 1) {
            rightArrow.classList.add('visible');
        } else {
            rightArrow.classList.remove('visible');
        }
    }
}

// Close detail modal
window.closeDetailModal = function() {
    const modal = document.getElementById('detailModal');
    modal.classList.remove('active');
    document.body.style.overflow = '';

    // Clear content after animation
    setTimeout(() => {
        document.getElementById('detailModalContent').innerHTML = '';
        carouselContent = [];
        currentCarouselIndex = 0;
    }, 300);
};

// Build detail content HTML
function buildDetailContent(item) {
    const backdropUrl = item.backdrops?.large || item.backdrop_url ||
                       item.backdrops?.original ||
                       item.poster_url_large || item.posters?.large;

    const title = item.title || item.original_title || 'Untitled';
    const year = extractYear(item.release_date || item.tmdb_release_date || item.imdb_year);
    const rating = item.tmdb_rating || item.imdb_rating || 0;
    const runtime = item.runtime || (item.episode_runtime && item.episode_runtime[0]);
    const overview = item.overview || item.description || 'No description available.';

    // Build meta info
    let metaHTML = '';
    if (year) {
        metaHTML += `<span class="detail-meta-item">${year}</span>`;
    }
    if (rating > 0) {
        metaHTML += `
            ${year ? '<div class="meta-separator"></div>' : ''}
            <div class="detail-rating">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
                <span class="detail-meta-item">${rating.toFixed(1)}</span>
            </div>
        `;
    }
    if (runtime) {
        metaHTML += `
            ${(year || rating > 0) ? '<div class="meta-separator"></div>' : ''}
            <span class="detail-meta-item">${formatRuntime(runtime)}</span>
        `;
    }

    // Build genre badges
    let genresHTML = '';
    if (item.genres && item.genres.length > 0) {
        genresHTML = `
            <div class="detail-genres">
                ${item.genres.slice(0, 4).map(genre =>
                    `<div class="detail-genre-badge">${genre.toUpperCase()}</div>`
                ).join('')}
            </div>
        `;
    }

    // Build platforms section
    let platformsHTML = '';
    if (item.platforms && item.platforms.length > 0) {
        const platformChips = item.platforms.map(platform => {
            const logoUrl = getPlatformLogo(platform);
            const logoHTML = logoUrl ? `<img src="${logoUrl}" alt="${platform}" loading="lazy">` : '';
            return `
                <div class="detail-platform-chip">
                    ${logoHTML}
                    <span>${platform}</span>
                </div>
            `;
        }).join('');

        platformsHTML = `
            <div class="detail-platforms-section">
                <div class="detail-platforms-title">Available On</div>
                <div class="detail-platforms">
                    ${platformChips}
                </div>
            </div>
        `;
    }

    // Build additional info section
    let infoItems = [];

    // Directors
    if (item.directors && item.directors.length > 0) {
        infoItems.push({
            label: 'Directors',
            value: item.directors.join(', ')
        });
    }

    // Writers
    if (item.writers && item.writers.length > 0) {
        infoItems.push({
            label: 'Writers',
            value: item.writers.join(', ')
        });
    }

    // Release Date
    const releaseDate = item.tmdb_release_date || item.release_date;
    if (releaseDate) {
        infoItems.push({
            label: 'Release Date',
            value: formatDate(releaseDate)
        });
    }

    // Language
    if (item.original_language) {
        infoItems.push({
            label: 'Language',
            value: getLanguageName(item.original_language)
        });
    }

    // Seasons (for TV shows)
    if (item.tmdb_media_type === 'tv' && item.number_of_seasons) {
        infoItems.push({
            label: 'Seasons',
            value: `${item.number_of_seasons} Season${item.number_of_seasons > 1 ? 's' : ''}`
        });
    }

    // Status
    if (item.status) {
        infoItems.push({
            label: 'Status',
            value: item.status
        });
    }

    const infoHTML = infoItems.length > 0 ? `
        <div class="detail-additional">
            <div class="detail-info-grid">
                ${infoItems.map(info => `
                    <div class="detail-info-item">
                        <div class="detail-info-label">${info.label}</div>
                        <div class="detail-info-value">${info.value}</div>
                    </div>
                `).join('')}
            </div>
        </div>
    ` : '';

    // Build cast section
    let castHTML = '';
    if (item.cast && item.cast.length > 0) {
        const castItems = item.cast.slice(0, 8).map(person => {
            const photoHTML = person.profile_path
                ? `<img src="${person.profile_path}" alt="${person.name}" loading="lazy">`
                : '';

            return `
                <div class="detail-cast-item">
                    <div class="detail-cast-photo">${photoHTML}</div>
                    <div class="detail-cast-name">${person.name}</div>
                    <div class="detail-cast-character">${person.character || 'Unknown'}</div>
                </div>
            `;
        }).join('');

        castHTML = `
            <div class="detail-cast-section">
                <h3 class="detail-section-title">Cast</h3>
                <div class="detail-cast-grid">
                    ${castItems}
                </div>
            </div>
        `;
    }

    // Construct full HTML
    return `
        <div class="detail-backdrop">
            ${backdropUrl ? `<img src="${backdropUrl}" alt="${title}">` : ''}
        </div>
        <div class="detail-inner">
            <div class="detail-info">
                <h1 class="detail-title">${title}</h1>
                ${metaHTML ? `<div class="detail-meta">${metaHTML}</div>` : ''}
                ${genresHTML}
                <div class="detail-overview">${overview}</div>
                ${platformsHTML}
                ${buildActionButtons(item)}
            </div>
            ${infoHTML}
            ${castHTML}
        </div>
    `;
}

// Build action buttons (Play, Play Trailer, etc.)
function buildActionButtons(item) {
    const buttons = [];

    // Play buttons for deeplinks (prioritize first available platform)
    if (item.deeplinks && Object.keys(item.deeplinks).length > 0) {
        const platforms = Object.keys(item.deeplinks);
        const primaryPlatform = platforms[0];
        const primaryLink = item.deeplinks[primaryPlatform];

        // Primary play button for first platform
        buttons.push(`
            <a href="${primaryLink}" target="_blank" rel="noopener noreferrer" class="detail-btn detail-btn-primary">
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z"/>
                </svg>
                <span>Play on ${primaryPlatform}</span>
            </a>
        `);

        // Additional platform links (if more than one)
        if (platforms.length > 1) {
            platforms.slice(1).forEach(platform => {
                buttons.push(`
                    <a href="${item.deeplinks[platform]}" target="_blank" rel="noopener noreferrer" class="detail-btn detail-btn-secondary">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M8 5v14l11-7z"/>
                        </svg>
                        <span>${platform}</span>
                    </a>
                `);
            });
        }
    }

    // Play Trailer button
    if (item.youtube_id) {
        buttons.push(`
            <button class="detail-btn detail-btn-trailer" onclick="openTrailerModal('${item.youtube_id}')">
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z"/>
                </svg>
                <span>Play Trailer</span>
            </button>
        `);
    }

    if (buttons.length === 0) return '';

    return `
        <div class="detail-actions">
            ${buttons.join('')}
        </div>
    `;
}

// Utility functions
function extractYear(dateString) {
    if (!dateString) return null;
    const yearMatch = dateString.match(/\d{4}/);
    return yearMatch ? yearMatch[0] : null;
}

function formatRuntime(minutes) {
    if (!minutes || minutes === 0) return 'N/A';

    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;

    if (hours === 0) {
        return `${mins}m`;
    } else if (mins === 0) {
        return `${hours}h`;
    } else {
        return `${hours}h ${mins}m`;
    }
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';

    try {
        let date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString;

        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch (e) {
        return dateString;
    }
}

function getLanguageName(code) {
    const languages = {
        'en': 'English',
        'hi': 'Hindi',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ml': 'Malayalam',
        'kn': 'Kannada',
        'bn': 'Bengali',
        'mr': 'Marathi',
        'gu': 'Gujarati',
        'pa': 'Punjabi',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese'
    };

    return languages[code] || code.toUpperCase();
}

// Open trailer modal
window.openTrailerModal = function(youtubeId) {
    const modal = document.getElementById('trailerModal');
    const player = document.getElementById('trailerPlayer');

    if (!modal || !player) {
        console.error('Trailer modal elements not found');
        return;
    }

    // Create iframe
    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube.com/embed/${youtubeId}?autoplay=1&rel=0`;
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    iframe.allowFullscreen = true;

    player.innerHTML = '';
    player.appendChild(iframe);

    modal.classList.add('active');
};

// Close trailer modal
window.closeTrailerModal = function() {
    const modal = document.getElementById('trailerModal');
    const player = document.getElementById('trailerPlayer');

    if (player) {
        player.innerHTML = '';
    }
    if (modal) {
        modal.classList.remove('active');
    }
};

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    const modal = document.getElementById('detailModal');
    const isModalActive = modal && modal.classList.contains('active');

    if (e.key === 'Escape') {
        closeDetailModal();
        closeTrailerModal();
    } else if (isModalActive) {
        if (e.key === 'ArrowLeft') {
            navigateDetailPrev();
        } else if (e.key === 'ArrowRight') {
            navigateDetailNext();
        }
    }
});

// Click outside to close
document.addEventListener('click', (e) => {
    const detailModal = document.getElementById('detailModal');
    if (e.target === detailModal) {
        closeDetailModal();
    }

    const trailerModal = document.getElementById('trailerModal');
    if (e.target === trailerModal) {
        closeTrailerModal();
    }
});

// Touch/swipe support for carousel
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', (e) => {
    const modal = document.getElementById('detailModal');
    if (modal && modal.classList.contains('active')) {
        touchStartX = e.changedTouches[0].screenX;
    }
}, { passive: true });

document.addEventListener('touchend', (e) => {
    const modal = document.getElementById('detailModal');
    if (modal && modal.classList.contains('active')) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }
}, { passive: true });

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swiped left - go to next
            navigateDetailNext();
        } else {
            // Swiped right - go to prev
            navigateDetailPrev();
        }
    }
}

// Handle window resize to recalculate carousel position
window.addEventListener('resize', () => {
    const modal = document.getElementById('detailModal');
    if (modal && modal.classList.contains('active')) {
        navigateToIndex(currentCarouselIndex, false);
    }
});
