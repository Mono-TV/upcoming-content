#!/usr/bin/env python3
"""
Filter movies to keep only upcoming releases
Removes movies that have already been released based on current date

Usage:
    python3 filter_upcoming.py [--input FILE] [--output FILE]
"""

import json
import argparse
from datetime import datetime


def parse_release_date(date_str):
    """Parse release date string to datetime object"""
    if not date_str:
        return None

    try:
        # Handle format like "12 Nov 2025"
        return datetime.strptime(date_str, '%d %b %Y')
    except:
        try:
            # Handle format like "Nov 12, 2025"
            return datetime.strptime(date_str, '%b %d, %Y')
        except:
            return None


def filter_upcoming_movies(movies):
    """Filter to keep only upcoming movies (future releases)"""
    today = datetime.now()

    filtered_movies = []
    removed_movies = []

    for movie in movies:
        release_date_str = movie.get('release_date')
        title = movie.get('title', 'Unknown')

        if not release_date_str:
            # Keep movies without release date
            filtered_movies.append(movie)
            continue

        release_date = parse_release_date(release_date_str)
        if release_date:
            # Only keep if release date is today or in the future
            if release_date.date() >= today.date():
                filtered_movies.append(movie)
            else:
                removed_movies.append((title, release_date_str))
        else:
            # Keep if we can't parse the date
            filtered_movies.append(movie)

    return filtered_movies, removed_movies


def filter_recent_releases(movies, days=14):
    """Filter to keep only recent releases (last N days)"""
    from datetime import timedelta
    today = datetime.now()
    cutoff_date = today - timedelta(days=days)

    filtered_movies = []
    removed_movies = []

    for movie in movies:
        release_date_str = movie.get('release_date')
        title = movie.get('title', 'Unknown')

        if not release_date_str:
            # Keep movies without release date
            filtered_movies.append(movie)
            continue

        release_date = parse_release_date(release_date_str)
        if release_date:
            # Keep if released within the last N days
            if cutoff_date.date() <= release_date.date() <= today.date():
                filtered_movies.append(movie)
            else:
                removed_movies.append((title, release_date_str))
        else:
            # Keep if we can't parse the date
            filtered_movies.append(movie)

    return filtered_movies, removed_movies


def main():
    parser = argparse.ArgumentParser(description='Filter movies by release date')
    parser.add_argument('--input', default='movies_enriched.json',
                        help='Input JSON file (default: movies_enriched.json)')
    parser.add_argument('--output', default='movies_enriched.json',
                        help='Output JSON file (default: movies_enriched.json)')
    parser.add_argument('--mode', choices=['upcoming', 'recent'], default='upcoming',
                        help='Filter mode: upcoming (future) or recent (last N days)')
    parser.add_argument('--days', type=int, default=14,
                        help='For recent mode: number of days to keep (default: 14)')

    args = parser.parse_args()

    mode_label = "UPCOMING" if args.mode == 'upcoming' else f"RECENT RELEASES (LAST {args.days} DAYS)"

    print("\n" + "="*60)
    print(f"FILTERING {mode_label}")
    print("="*60)
    print(f"📅 Current date: {datetime.now().strftime('%d %b %Y')}")
    print("="*60 + "\n")

    # Load movies
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            movies = json.load(f)
        print(f"✓ Loaded {len(movies)} movies from {args.input}\n")
    except FileNotFoundError:
        print(f"❌ File not found: {args.input}")
        return

    # Filter movies based on mode
    before_count = len(movies)
    if args.mode == 'upcoming':
        filtered_movies, removed_movies = filter_upcoming_movies(movies)
        result_label = "upcoming movies"
    else:
        filtered_movies, removed_movies = filter_recent_releases(movies, args.days)
        result_label = f"recent releases (last {args.days} days)"

    after_count = len(filtered_movies)
    removed_count = before_count - after_count

    # Display results
    if removed_count > 0:
        action = "outside date range" if args.mode == 'recent' else "already-released"
        print(f"🗑️  Removed {removed_count} {action} movie(s):\n")
        for title, date in removed_movies[:10]:  # Show first 10
            print(f"   ✗ {title[:50]}... (released {date})")
        if removed_count > 10:
            print(f"   ... and {removed_count - 10} more")
        print()

    print(f"✅ Keeping {after_count} {result_label}\n")

    # Save filtered movies
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(filtered_movies, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved {after_count} movies to {args.output}\n")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
