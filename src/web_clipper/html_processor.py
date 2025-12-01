"""HTML processing - convert clipboard HTML to markdown with image downloading.

This module provides functionality to:
1. Extract HTML content from macOS clipboard using PyObjC
2. Convert HTML to clean markdown format
3. Download embedded images from web URLs
4. Update image references to local file paths

Images are saved to clips/images/ directory with timestamp-based naming.
"""

import re
import time
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from AppKit import NSPasteboard
from bs4 import BeautifulSoup
from markdownify import markdownify as md


def get_html_from_clipboard() -> Optional[str]:
    """
    Get HTML content from macOS clipboard using PyObjC.

    Returns:
        HTML string if available, None otherwise
    """
    try:
        # Get the general pasteboard
        pasteboard = NSPasteboard.generalPasteboard()

        # Try to get HTML data
        html_types = ['public.html', 'Apple HTML pasteboard type']

        for html_type in html_types:
            data = pasteboard.dataForType_(html_type)
            if data:
                try:
                    html_string = bytes(data).decode('utf-8', errors='ignore')
                    # Verify it's actually HTML
                    if '<' in html_string and '>' in html_string:
                        return html_string
                except Exception:
                    continue

        return None
    except Exception:
        return None


def download_image(image_url: str, base_url: str, images_dir: Path) -> Optional[Path]:
    """
    Download an image from a URL.

    Args:
        image_url: URL of the image (can be relative)
        base_url: Base URL to resolve relative URLs
        images_dir: Directory to save images

    Returns:
        Path to saved image, or None if download failed
    """
    try:
        # Resolve relative URLs
        full_url = urljoin(base_url, image_url)

        # Parse URL to get file extension
        parsed = urlparse(full_url)
        path_parts = parsed.path.split('/')
        filename = path_parts[-1] if path_parts else 'image'

        # If no extension, default to .png
        if '.' not in filename:
            ext = '.png'
        else:
            ext = '.' + filename.split('.')[-1]
            # Limit extension length and validate
            if len(ext) > 5 or not ext[1:].isalnum():
                ext = '.png'

        # Generate unique filename
        timestamp_ms = int(time.time() * 1000)
        counter = 0
        image_path = images_dir / f"image_{timestamp_ms}_{counter}{ext}"

        while image_path.exists():
            counter += 1
            image_path = images_dir / f"image_{timestamp_ms}_{counter}{ext}"

        # Download the image
        response = requests.get(full_url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()

        # Save the image
        with open(image_path, 'wb') as f:
            f.write(response.content)

        return image_path

    except Exception as e:
        # Log error but don't fail the whole operation
        print(f"Warning: Failed to download image {image_url}: {e}")
        return None


def process_html_images(html: str, base_url: str, images_dir: Path) -> Tuple[str, int]:
    """
    Process HTML content: download images and update image tags.

    Args:
        html: HTML content
        base_url: Base URL for resolving relative image URLs
        images_dir: Directory to save images

    Returns:
        Tuple of (modified HTML with local image paths, count of downloaded images)
    """
    images_dir.mkdir(parents=True, exist_ok=True)

    soup = BeautifulSoup(html, 'html.parser')
    image_count = 0

    # Find all img tags
    for img in soup.find_all('img'):
        src = img.get('src')
        if not src:
            continue

        # Skip data URIs (base64 images) for now
        if src.startswith('data:'):
            continue

        # Download the image
        local_path = download_image(src, base_url, images_dir)

        if local_path:
            # Update the img tag with local path
            img['src'] = f"./images/{local_path.name}"
            image_count += 1

    return str(soup), image_count


def html_to_markdown(html: str, base_url: str, clips_directory: Path) -> Tuple[str, int]:
    """
    Convert HTML to markdown, downloading images in the process.

    Args:
        html: HTML content from clipboard
        base_url: Base URL for resolving relative image URLs
        clips_directory: Base directory for clips

    Returns:
        Tuple of (markdown content, count of downloaded images)
    """
    images_dir = clips_directory / "images"

    # Process images first (download and update URLs)
    modified_html, image_count = process_html_images(html, base_url, images_dir)

    # Convert HTML to Markdown
    markdown = md(
        modified_html,
        heading_style="ATX",  # Use # for headings
        bullets="-",  # Use - for bullet lists
        strip=['script', 'style'],  # Remove script and style tags
    )

    # Clean up excessive newlines
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)

    return markdown.strip(), image_count
