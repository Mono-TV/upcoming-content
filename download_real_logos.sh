#!/bin/bash
cd "/Users/mono/Documents/Programs/Circuit House"

echo "Downloading official streaming platform logos..."
echo "=================================================="

# Netflix
curl -L "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg" -o Netflix.svg 2>/dev/null && echo "✓ Netflix logo downloaded"

# Amazon Prime Video
curl -L "https://upload.wikimedia.org/wikipedia/commons/f/f1/Prime_Video.png" -o Amazon_Prime_Video.png 2>/dev/null && echo "✓ Amazon Prime Video logo downloaded"

# Hotstar (Disney+ Hotstar)
curl -L "https://upload.wikimedia.org/wikipedia/commons/1/1e/Disney%2B_Hotstar_logo.svg" -o Jio_Hotstar.svg 2>/dev/null && echo "✓ Hotstar logo downloaded"

echo "=================================================="
echo "Logo download complete!"
