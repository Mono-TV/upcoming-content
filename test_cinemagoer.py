#!/usr/bin/env python3
"""
Test script to verify Cinemagoer (formerly IMDbPY) API is working
"""

import sys
import time

try:
    from imdb import Cinemagoer
    print("✅ Cinemagoer library imported successfully\n")
except ImportError as e:
    print(f"❌ Failed to import Cinemagoer: {e}")
    print("\n💡 Install with: pip3 install cinemagoer")
    sys.exit(1)

def test_cinemagoer():
    """Run basic tests on Cinemagoer API"""

    print("="*60)
    print("CINEMAGOER API TEST")
    print("="*60)
    print()

    # Initialize Cinemagoer
    try:
        ia = Cinemagoer()
        print("✅ Cinemagoer instance created successfully\n")
    except Exception as e:
        print(f"❌ Failed to create Cinemagoer instance: {e}")
        return False

    # Test 1: Search for a movie by title
    print("Test 1: Search for movies by title")
    print("-" * 40)
    test_title = "The Matrix"
    print(f"Searching for: '{test_title}'")

    try:
        results = ia.search_movie(test_title)
        if results and len(results) > 0:
            print(f"✅ Found {len(results)} results\n")

            # Show first 3 results
            for i, movie in enumerate(results[:3], 1):
                movie_id = movie.movieID
                title = movie.get('title', 'N/A')
                year = movie.get('year', 'N/A')
                print(f"   {i}. {title} ({year}) - IMDb ID: tt{movie_id}")
            print()
        else:
            print("❌ No results found")
            return False
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False

    time.sleep(1)  # Rate limiting

    # Test 2: Get movie details by IMDb ID
    print("\nTest 2: Get movie details by IMDb ID")
    print("-" * 40)
    test_imdb_id = "0133093"  # The Matrix
    print(f"Fetching details for IMDb ID: tt{test_imdb_id}")

    try:
        movie = ia.get_movie(test_imdb_id)

        if movie:
            print("✅ Movie details retrieved successfully\n")
            print(f"   Title: {movie.get('title', 'N/A')}")
            print(f"   Year: {movie.get('year', 'N/A')}")
            print(f"   Rating: {movie.get('rating', 'N/A')}")
            print(f"   Directors: {', '.join([d['name'] for d in movie.get('directors', [])])}")
            print(f"   Genres: {', '.join(movie.get('genres', []))}")
            print()
        else:
            print("❌ No movie data retrieved")
            return False
    except Exception as e:
        print(f"❌ Get movie failed: {e}")
        return False

    time.sleep(1)  # Rate limiting

    # Test 3: Search for a recent Indian movie
    print("\nTest 3: Search for Indian movie")
    print("-" * 40)
    indian_title = "RRR"
    print(f"Searching for: '{indian_title}'")

    try:
        results = ia.search_movie(indian_title)
        if results and len(results) > 0:
            print(f"✅ Found {len(results)} results\n")

            # Show first result
            movie = results[0]
            movie_id = movie.movieID
            title = movie.get('title', 'N/A')
            year = movie.get('year', 'N/A')
            print(f"   Top result: {title} ({year}) - IMDb ID: tt{movie_id}")

            # Get full details
            movie_info = ia.get_movie(movie_id)
            if 'year' in movie_info:
                print(f"   Year from details: {movie_info['year']}")
            print()
        else:
            print("❌ No results found")
            return False
    except Exception as e:
        print(f"❌ Indian movie search failed: {e}")
        return False

    print("="*60)
    print("✅ ALL TESTS PASSED - Cinemagoer API is working!")
    print("="*60)
    return True

if __name__ == '__main__':
    success = test_cinemagoer()
    sys.exit(0 if success else 1)
