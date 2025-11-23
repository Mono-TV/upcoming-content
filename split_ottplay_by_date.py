#!/usr/bin/env python3
"""
Split OTTPlay data into Released and Upcoming based on dates

Released: Start of month → Today
Upcoming: Tomorrow → End of month
"""

import json
from datetime import datetime, timedelta
from dateutil import parser
import calendar


def parse_date(date_string):
    """Parse various date formats"""
    if not date_string or date_string == 'TBA':
        return None

    try:
        # Try parsing with dateutil (handles "Nov 01, 2025" format)
        return parser.parse(date_string)
    except:
        return None


def split_by_date():
    """Split ottplay data into released and upcoming"""

    # Load the transformed data
    with open('ottplay_releases.json', 'r', encoding='utf-8') as f:
        all_items = json.load(f)

    print(f"✓ Loaded {len(all_items)} items from ottplay_releases.json")

    # Get current date info
    now = datetime.now()
    today = now.date()

    # Start of current month
    start_of_month = datetime(now.year, now.month, 1).date()

    # End of current month
    last_day = calendar.monthrange(now.year, now.month)[1]
    end_of_month = datetime(now.year, now.month, last_day).date()

    print(f"\n📅 Date ranges:")
    print(f"   • Released: {start_of_month} to {today}")
    print(f"   • Upcoming: {today + timedelta(days=1)} to {end_of_month}")

    # Split items
    released_items = []
    upcoming_items = []
    no_date_items = []

    for item in all_items:
        release_date_str = item.get('release_date', '')
        parsed_date = parse_date(release_date_str)

        if not parsed_date:
            # No valid date - put in upcoming by default
            no_date_items.append(item)
            continue

        release_date = parsed_date.date()

        # Check if date is in current month
        if release_date.month != now.month or release_date.year != now.year:
            # Not in current month - skip or categorize differently
            if release_date < start_of_month:
                # Old content - put in released
                released_items.append(item)
            else:
                # Future content - put in upcoming
                upcoming_items.append(item)
            continue

        # Date is in current month
        if release_date <= today:
            # Released (start of month → today)
            released_items.append(item)
        else:
            # Upcoming (tomorrow → end of month)
            upcoming_items.append(item)

    # Sort by release date (newest first for released, earliest first for upcoming)
    def get_date_for_sort(item):
        parsed = parse_date(item.get('release_date', ''))
        if parsed:
            return parsed
        return datetime.max  # Put items without dates at the end

    released_items.sort(key=get_date_for_sort, reverse=True)  # Newest first
    upcoming_items.sort(key=get_date_for_sort, reverse=False)  # Earliest first

    # Add items without dates to upcoming
    upcoming_items.extend(no_date_items)

    print(f"\n📊 Split results:")
    print(f"   • Released (start of month → today): {len(released_items)} items")
    print(f"   • Upcoming (tomorrow → end of month): {len(upcoming_items)} items")
    print(f"   • No date/TBA: {len(no_date_items)} items (added to upcoming)")

    # Save released items
    with open('ottplay_releases.json', 'w', encoding='utf-8') as f:
        json.dump(released_items, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved: ottplay_releases.json ({len(released_items)} items)")

    # Save upcoming items
    with open('ottplay_upcoming.json', 'w', encoding='utf-8') as f:
        json.dump(upcoming_items, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved: ottplay_upcoming.json ({len(upcoming_items)} items)")

    # Show sample dates
    if released_items:
        print(f"\n📅 Released sample dates:")
        for item in released_items[:5]:
            print(f"   • {item.get('title', 'Unknown')[:40]}: {item.get('release_date', 'TBA')}")

    if upcoming_items:
        print(f"\n📅 Upcoming sample dates:")
        for item in upcoming_items[:5]:
            print(f"   • {item.get('title', 'Unknown')[:40]}: {item.get('release_date', 'TBA')}")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("OTTPLAY DATE SPLITTER")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    split_by_date()

    print("\n" + "="*60)
    print("✅ SPLIT COMPLETE")
    print("="*60 + "\n")
