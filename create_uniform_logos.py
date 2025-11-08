#!/usr/bin/env python3
"""
Create uniform SVG logos for streaming platforms
Using simple text-based SVG for uniformity
"""
import os

os.chdir('/Users/mono/Documents/Programs/Circuit House')

# Create simple,uniform SVG logos with consistent styling
logos = {
    'Netflix.svg': '''<svg viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="netflixGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#E50914;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#B20710;stop-opacity:1" />
    </linearGradient>
  </defs>
  <text x="100" y="40" font-family="Arial, sans-serif" font-weight="bold" font-size="36" fill="url(#netflixGrad)" text-anchor="middle">NETFLIX</text>
</svg>''',

    'Amazon_Prime_Video.svg': '''<svg viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="primeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#00A8E1;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0080B8;stop-opacity:1" />
    </linearGradient>
  </defs>
  <text x="100" y="35" font-family="Arial, sans-serif" font-weight="bold" font-size="20" fill="url(#primeGrad)" text-anchor="middle">Prime Video</text>
</svg>''',

    'Sony_LIV.svg': '''<svg viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sonyGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#5F259F;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#8B3DAF;stop-opacity:1" />
    </linearGradient>
  </defs>
  <text x="100" y="40" font-family="Arial, sans-serif" font-weight="bold" font-size="32" fill="url(#sonyGrad)" text-anchor="middle">SonyLIV</text>
</svg>''',

    'Jio_Hotstar.svg': '''<svg viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="hotstarGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0F1014;stop-opacity:1" />
      <stop offset="40%" style="stop-color:#1A2540;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0F1014;stop-opacity:1" />
    </linearGradient>
  </defs>
  <text x="100" y="38" font-family="Arial, sans-serif" font-weight="bold" font-size="26" fill="url(#hotstarGrad)" text-anchor="middle">Jio Hotstar</text>
</svg>''',

    'Sun_NXT.svg': '''<svg viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sunGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#FF6B00;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#FF8C00;stop-opacity:1" />
    </linearGradient>
  </defs>
  <text x="100" y="40" font-family="Arial, sans-serif" font-weight="bold" font-size="32" fill="url(#sunGrad)" text-anchor="middle">Sun NXT</text>
</svg>''',

    'Manorama_MAX.svg': '''<svg viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="manoramaGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#C41E3A;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#8B0000;stop-opacity:1" />
    </linearGradient>
  </defs>
  <text x="100" y="35" font-family="Arial, sans-serif" font-weight="bold" font-size="22" fill="url(#manoramaGrad)" text-anchor="middle">Manorama MAX</text>
</svg>'''
}

print("Creating uniform SVG logos...")
print("=" * 50)

for filename, svg_content in logos.items():
    with open(filename, 'w') as f:
        f.write(svg_content)
    print(f"✓ Created {filename}")

print("=" * 50)
print("All logos created successfully!")
print("\nLogos are now uniform in:")
print("- Format: SVG (scalable)")
print("- Style: Modern gradients")
print("- Size: Consistent viewBox")
