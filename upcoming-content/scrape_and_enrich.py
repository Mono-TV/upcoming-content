#!/usr/bin/env python3
"""
Combined Script: Scrape Movies and Enrich with IMDb IDs
Runs both scraping and enrichment in one go
"""

import sys
import subprocess


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}\n")

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=False
        )
        print(f"\n✅ {description} completed successfully!\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with error code {e.returncode}\n")
        return False


def main():
    """Main function to run scraper and all enrichment steps"""
    print("\n" + "="*60)
    print("AUTOMATED MOVIE SCRAPING AND ENRICHMENT")
    print("="*60 + "\n")

    # Step 1: Run the scraper
    scraper_success = run_command(
        "python3 scrape_movies.py",
        "STEP 1: Scraping movies from Binged.com"
    )

    if not scraper_success:
        print("❌ Scraping failed. Aborting enrichment.")
        sys.exit(1)

    # Step 2: Run IMDb enrichment
    imdb_success = run_command(
        "python3 enrich_with_imdb.py",
        "STEP 2: Enriching movies with IMDb data"
    )

    if not imdb_success:
        print("❌ IMDb enrichment failed. Aborting YouTube enrichment.")
        sys.exit(1)

    # Step 3: Run YouTube enrichment
    youtube_success = run_command(
        "python3 enrich_with_youtube.py",
        "STEP 3: Finding YouTube trailers for movies"
    )

    if not youtube_success:
        print("❌ YouTube enrichment failed.")
        sys.exit(1)

    # Step 4: Run poster enrichment (optional, requires TMDb API key)
    import os
    if os.environ.get('TMDB_API_KEY'):
        poster_success = run_command(
            "python3 enrich_with_posters.py",
            "STEP 4: Adding high-quality posters from TMDb"
        )

        if poster_success:
            final_file = "movies_enriched.json"
        else:
            print("⚠️  Poster enrichment failed, using movies_with_trailers.json")
            final_file = "movies_with_trailers.json"
    else:
        print("\n" + "="*60)
        print("⏭️  STEP 4: Skipping poster enrichment (optional)")
        print("="*60)
        print("\n💡 To add high-quality posters:")
        print("   1. Get free API key: https://www.themoviedb.org/settings/api")
        print("   2. Set: export TMDB_API_KEY='your_key'")
        print("   3. Re-run this script")
        print("")
        final_file = "movies_with_trailers.json"

    # Success message
    print("\n" + "="*60)
    print("✅ ALL DONE!")
    print("="*60)
    print("\n📁 Files created:")
    print("   - movies.json (scraped data)")
    print("   - movies_with_imdb.json (enriched with IMDb IDs)")
    print("   - movies_with_trailers.json (enriched with YouTube trailers)")
    if os.environ.get('TMDB_API_KEY'):
        print("   - movies_enriched.json (enriched with high-quality posters)")
    print(f"\n💡 Tip: Use {final_file} for your application!")
    print("   It has everything: movie data + IMDb IDs + YouTube trailers" +
          (" + HD posters" if final_file == "movies_enriched.json" else ""))
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
