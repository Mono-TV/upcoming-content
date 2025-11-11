#!/usr/bin/env python3
"""
Detailed Cinemagoer diagnostic test
"""

from imdb import Cinemagoer
import sys

print("="*60)
print("DETAILED CINEMAGOER DIAGNOSTIC")
print("="*60)
print()

ia = Cinemagoer()

# Test 1: Direct movie fetch by known ID
print("Test 1: Direct fetch by ID (tt0133093 - The Matrix)")
print("-" * 40)
try:
    movie = ia.get_movie('0133093')
    print(f"✅ SUCCESS!")
    print(f"   Title: {movie.get('title', 'N/A')}")
    print(f"   Year: {movie.get('year', 'N/A')}")
    print(f"   Kind: {movie.get('kind', 'N/A')}")
    print(f"   Rating: {movie.get('rating', 'N/A')}")
    print()
except Exception as e:
    print(f"❌ FAILED: {type(e).__name__}: {e}")
    print()

# Test 2: Search functionality
print("Test 2: Search functionality")
print("-" * 40)
try:
    print("Searching for 'The Matrix'...")
    results = ia.search_movie('The Matrix')
    print(f"   Results type: {type(results)}")
    print(f"   Results length: {len(results)}")

    if results:
        print(f"✅ Found {len(results)} results")
        for i, movie in enumerate(results[:3], 1):
            print(f"   {i}. {movie.get('title', 'N/A')} ({movie.get('year', 'N/A')})")
    else:
        print("❌ Search returned empty list")
    print()
except Exception as e:
    print(f"❌ FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    print()

# Test 3: Check Cinemagoer version and configuration
print("Test 3: Cinemagoer configuration")
print("-" * 40)
try:
    print(f"   Version: {Cinemagoer.__version__ if hasattr(Cinemagoer, '__version__') else 'Unknown'}")
    print(f"   Instance type: {type(ia)}")
    print(f"   Available methods: {[m for m in dir(ia) if not m.startswith('_')][:10]}...")
    print()
except Exception as e:
    print(f"❌ Error: {e}")
    print()

print("="*60)
print("Diagnostic complete!")
print("="*60)
