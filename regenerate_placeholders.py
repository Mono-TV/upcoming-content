#!/usr/bin/env python3
"""
Regenerate Placeholder Posters Only
This script regenerates placeholder images for movies without posters
without re-scraping or re-enriching the data.

Usage:
    pip install Pillow>=10.0.0
    python3 regenerate_placeholders.py
"""

import json
import os
import sys
from typing import Dict, Optional, List

# Check for PIL/Pillow
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("❌ Pillow is not installed!")
    print("\n💡 Install with:")
    print("   pip install Pillow>=10.0.0")
    sys.exit(1)


class PlaceholderGenerator:
    """Generate placeholder posters for movies without images"""

    def __init__(self):
        # Platform color schemes with Apple Glass Design aesthetics
        # Format: (top_color, middle_color, bottom_color) for multi-stop gradient
        self.platform_colors = {
            'Netflix': ('#FF1744', '#C2185B', '#880E4F'),  # Vibrant red to deep pink glass
            'Amazon Prime Video': ('#00B8D4', '#0277BD', '#01579B'),  # Cyan to deep blue glass
            'Apple TV+': ('#424242', '#212121', '#000000'),  # Sleek dark glass
            'Jio Hotstar': ('#2196F3', '#1565C0', '#0D47A1'),  # Bright to deep blue glass
            'Zee5': ('#AB47BC', '#7B1FA2', '#4A148C'),  # Purple glass
            'Sony LIV': ('#FF6F00', '#E65100', '#BF360C'),  # Orange glass
            'Sun NXT': ('#FFC107', '#FF8F00', '#FF6F00'),  # Gold glass
            'Manorama MAX': ('#E53935', '#C62828', '#B71C1C'),  # Red glass
            'default': ('#455A64', '#263238', '#000000')  # Blue-grey glass
        }

        # Create placeholders directory
        os.makedirs('placeholders', exist_ok=True)

    def _create_glass_gradient(self, width, height, colors):
        """
        Create Apple Glass Design styled gradient with blur and depth
        Uses multi-stop gradient with frosted glass effect
        """
        # Create base image
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)

        # Parse colors (now we have 3 colors: top, middle, bottom)
        r1, g1, b1 = int(colors[0][1:3], 16), int(colors[0][3:5], 16), int(colors[0][5:7], 16)
        r2, g2, b2 = int(colors[1][1:3], 16), int(colors[1][3:5], 16), int(colors[1][5:7], 16)
        r3, g3, b3 = int(colors[2][1:3], 16), int(colors[2][3:5], 16), int(colors[2][5:7], 16)

        # Draw multi-stop gradient (top to middle, then middle to bottom)
        for y in range(height):
            if y < height // 2:
                # Top half: color1 to color2
                ratio = (y / (height // 2))
                r = int(r1 + (r2 - r1) * ratio)
                g = int(g1 + (g2 - g1) * ratio)
                b = int(b1 + (b2 - b1) * ratio)
            else:
                # Bottom half: color2 to color3
                ratio = ((y - height // 2) / (height // 2))
                r = int(r2 + (r3 - r2) * ratio)
                g = int(g2 + (g3 - g2) * ratio)
                b = int(b2 + (b3 - b2) * ratio)

            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Apply subtle blur for frosted glass effect
        img = img.filter(ImageFilter.GaussianBlur(radius=2))

        # Add radial light overlay for glass shine effect
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        # Create circular light gradient in the center-top area
        center_x, center_y = width // 2, height // 4
        max_radius = width // 2

        for i in range(max_radius, 0, -10):
            # Calculate alpha for soft glow (more transparent towards edge)
            alpha = int((1 - i / max_radius) * 30)  # Max 30 for subtle effect
            overlay_draw.ellipse(
                [center_x - i, center_y - i, center_x + i, center_y + i],
                fill=(255, 255, 255, alpha)
            )

        # Composite the overlay onto the gradient
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        img = img.convert('RGB')

        return img

    def _wrap_text(self, text, max_width, font):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else [text]

    def generate_placeholder_poster(self, movie: Dict) -> Optional[str]:
        """
        Generate a beautiful placeholder poster using PIL/Pillow
        Shows only the title with large font
        Returns the file path to the generated placeholder
        """
        try:
            title = movie.get('title', 'Untitled')
            platforms = movie.get('platforms', [])

            # Choose primary platform for color scheme
            primary_platform = platforms[0] if platforms else 'default'
            colors = self.platform_colors.get(primary_platform, self.platform_colors['default'])

            # Image dimensions (standard poster size)
            width, height = 500, 750

            # Create Apple Glass Design gradient background
            img = self._create_glass_gradient(width, height, colors)
            draw = ImageDraw.Draw(img)

            # Calculate font size proportionally based on poster dimensions
            # Use 40% of width for much better visibility (for 500px width = 200pt)
            font_size = int(width * 0.40)

            # Try to load TrueType font with multiple fallbacks
            # MUST use TrueType fonts - default font has fixed size!
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "C:\\Windows\\Fonts\\arialbd.ttf",  # Windows
            ]

            title_font = None
            for font_path in font_paths:
                try:
                    title_font = ImageFont.truetype(font_path, font_size)
                    break
                except (OSError, IOError):
                    continue

            # Final fallback - but warn if this happens
            if title_font is None:
                print(f"⚠️  Warning: Could not load TrueType font, using fixed-size default for '{title[:30]}'")
                title_font = ImageFont.load_default()

            # Wrap title text
            max_title_width = width - 60  # 30px padding on each side
            title_lines = self._wrap_text(title, max_title_width, title_font)

            # Limit to 4 lines max
            if len(title_lines) > 4:
                title_lines = title_lines[:3] + [title_lines[3][:20] + '...']

            # Calculate total text height (line height proportional to font size)
            line_height = int(font_size * 1.3)  # 130% of font size for good spacing
            title_height = len(title_lines) * line_height

            # Draw title (centered vertically)
            y_offset = (height - title_height) // 2

            for line in title_lines:
                bbox = title_font.getbbox(line)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2

                # Draw text shadow
                draw.text((x + 2, y_offset + 2), line, fill=(0, 0, 0, 180), font=title_font)
                # Draw text
                draw.text((x, y_offset), line, fill=(255, 255, 255), font=title_font)
                y_offset += line_height

            # Generate filename (sanitize title)
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-')).rstrip()
            safe_title = safe_title.replace(' ', '-').lower()[:50]

            # Save medium and large versions
            filename_medium = f"placeholders/{safe_title}-medium.jpg"
            filename_large = f"placeholders/{safe_title}-large.jpg"

            # Save medium (500x750)
            img.save(filename_medium, 'JPEG', quality=85, optimize=True)

            # Create larger version (1000x1500)
            img_large = img.resize((1000, 1500), Image.Resampling.LANCZOS)
            img_large.save(filename_large, 'JPEG', quality=90, optimize=True)

            return filename_medium

        except Exception as e:
            print(f"⚠️  Placeholder generation error for '{title}': {str(e)}")
            return None

    def regenerate_all_placeholders(self, input_file='movies_enriched.json', output_file='movies_enriched.json'):
        """Regenerate placeholders for movies without posters"""

        print("🎬 Placeholder Regeneration Tool")
        print("=" * 60)

        # Load existing data
        if not os.path.exists(input_file):
            print(f"❌ Error: {input_file} not found!")
            print("   Run the full enrichment process first.")
            sys.exit(1)

        with open(input_file, 'r', encoding='utf-8') as f:
            movies = json.load(f)

        print(f"📁 Loaded {len(movies)} movies from {input_file}")

        # Find movies without posters
        movies_needing_placeholders = []
        for movie in movies:
            has_poster = (
                movie.get('poster_url_medium') and
                not movie.get('poster_url_medium', '').startswith('placeholders/')
            )
            if not has_poster:
                movies_needing_placeholders.append(movie)

        if not movies_needing_placeholders:
            print("\n✅ All movies already have posters! No placeholders needed.")
            return

        print(f"\n🖼️  Generating placeholders for {len(movies_needing_placeholders)} movies...")
        print("-" * 60)

        # Generate placeholders
        generated_count = 0
        for i, movie in enumerate(movies_needing_placeholders, 1):
            title = movie.get('title', 'Untitled')
            print(f"[{i}/{len(movies_needing_placeholders)}] Generating: {title[:50]}", end='')

            placeholder_path = self.generate_placeholder_poster(movie)

            if placeholder_path:
                movie['poster_url_medium'] = placeholder_path
                movie['poster_url_large'] = placeholder_path.replace('-medium.jpg', '-large.jpg')
                generated_count += 1
                print(" ✓")
            else:
                print(" ✗")

        # Save updated data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(movies, f, indent=2, ensure_ascii=False)

        print("-" * 60)
        print(f"\n✅ Generated {generated_count} placeholder images")
        print(f"💾 Updated data saved to {output_file}")
        print(f"📂 Placeholder images saved in: placeholders/")
        print("\nDone! 🎉")


if __name__ == '__main__':
    generator = PlaceholderGenerator()
    generator.regenerate_all_placeholders()
