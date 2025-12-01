"""Image handling for direct clipboard image copies.

This module provides functionality to:
1. Detect when clipboard contains image data (not HTML with images)
2. Save clipboard images directly to disk as PNG files
3. Generate markdown image links with proper relative paths

Note: This handles direct image copies (right-click > Copy Image).
For images embedded in web page HTML, see html_processor.py
"""

import subprocess
import time
from pathlib import Path
from typing import Optional


def has_clipboard_image() -> bool:
    """
    Check if clipboard contains image data.

    Uses macOS pbpaste to check for image formats.
    """
    try:
        result = subprocess.run(
            ['osascript', '-e', 'clipboard info'],
            capture_output=True,
            text=True,
            check=True
        )
        # Check if output contains image format indicators
        output = result.stdout.lower()
        return any(fmt in output for fmt in ['picture', 'png', 'jpeg', 'tiff', 'image'])
    except Exception:
        return False


def save_clipboard_image(clips_directory: Path) -> Optional[Path]:
    """
    Save clipboard image to the images directory.

    Args:
        clips_directory: Base clips directory

    Returns:
        Path to saved image file, or None if no image in clipboard
    """
    if not has_clipboard_image():
        return None

    # Create images directory
    images_dir = clips_directory / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp-based filename
    timestamp_ms = int(time.time() * 1000)
    counter = 0
    image_path = images_dir / f"image_{timestamp_ms}_{counter}.png"

    # Ensure unique filename
    while image_path.exists():
        counter += 1
        image_path = images_dir / f"image_{timestamp_ms}_{counter}.png"

    # Save image using AppleScript/osascript
    try:
        script = f'''
        set imageData to the clipboard as «class PNGf»
        set fileHandle to open for access POSIX file "{image_path}" with write permission
        write imageData to fileHandle
        close access fileHandle
        '''
        subprocess.run(
            ['osascript', '-e', script],
            check=True,
            capture_output=True
        )
        return image_path
    except subprocess.CalledProcessError:
        # Try alternative method using pngpaste if available
        try:
            subprocess.run(
                ['pngpaste', str(image_path)],
                check=True,
                capture_output=True
            )
            return image_path
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None


def get_markdown_image_link(image_path: Path, clips_directory: Path, alt_text: str = "") -> str:
    """
    Generate markdown image link with relative path.

    Args:
        image_path: Absolute path to the image
        clips_directory: Base clips directory
        alt_text: Alternative text for the image

    Returns:
        Markdown image syntax with relative path
    """
    # Get relative path from clips directory to the image
    # Since markdown files are stored in clips_directory, we use relative path from there
    try:
        rel_path = image_path.relative_to(clips_directory)
    except ValueError:
        # If not relative, use absolute
        rel_path = image_path

    # Convert to forward slashes for markdown and ensure it starts with ./
    rel_path_str = str(rel_path).replace('\\', '/')
    if not rel_path_str.startswith('./'):
        rel_path_str = f"./{rel_path_str}"

    return f"![{alt_text}]({rel_path_str})"
