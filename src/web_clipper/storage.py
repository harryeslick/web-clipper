"""Storage management for organizing and writing clips to markdown files."""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from .config import ClipperConfig


def _sanitize_filename(name: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    # Replace invalid characters with hyphens
    name = re.sub(r'[^\w\s-]', '-', name)
    # Replace whitespace with hyphens
    name = re.sub(r'\s+', '-', name)
    # Remove repeated hyphens
    name = re.sub(r'-+', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    # Convert to lowercase
    return name.lower()


def _get_file_path(url: str, config: ClipperConfig) -> Path:
    """
    Generate the file path for a clip based on URL.

    Organizes clips by domain and endpoint:
    - github.com/anthropics/claude -> github.com/anthropics-claude.md
    - docs.python.org/library/pathlib -> docs.python.org/library-pathlib.md
    """
    parsed = urlparse(url)
    domain = parsed.netloc or "unknown"

    # Remove www. prefix if present
    if domain.startswith("www."):
        domain = domain[4:]

    # Get the path and create a sanitized filename
    path = parsed.path.strip("/")
    if path:
        # Replace slashes with hyphens for the filename
        filename = _sanitize_filename(path.replace("/", "-"))
        if not filename.endswith(".md"):
            filename = f"{filename}.md"
    else:
        filename = "index.md"

    if config.create_subdirs:
        # Organize by domain in subdirectories
        file_path = config.clips_directory / domain / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Flat structure with domain prefix
        filename_with_domain = f"{domain}_{filename}"
        file_path = config.clips_directory / filename_with_domain

    return file_path


def _format_clip(
    content: str,
    url: str,
    title: Optional[str],
    tags: Optional[str],
    config: ClipperConfig
) -> str:
    """
    Format a clip entry as markdown.

    Returns:
        Formatted markdown string for the clip
    """
    lines = ["---"]

    # Title
    clip_title = title or "Untitled"
    lines.append(f"## Clip: {clip_title}")

    # Metadata
    lines.append(f"- **URL**: {url}")

    if config.include_timestamp:
        timestamp = datetime.now().strftime(config.timestamp_format)
        lines.append(f"- **Captured**: {timestamp}")

    if tags:
        # Format tags with hashtags
        tag_list = [f"#{tag.strip()}" for tag in tags.split(",") if tag.strip()]
        if tag_list:
            lines.append(f"- **Tags**: {' '.join(tag_list)}")

    # Empty line before content
    lines.append("")

    # Content
    lines.append(content.strip())

    # Separator
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def save_clip(
    content: str,
    url: str,
    title: Optional[str],
    tags: Optional[str],
    config: ClipperConfig
) -> Path:
    """
    Save a clip to the appropriate markdown file.

    Args:
        content: The clipped text content
        url: The source URL
        title: The page title (optional)
        tags: Comma-separated tags (optional)
        config: Configuration object

    Returns:
        Path to the file where the clip was saved
    """
    # Ensure clips directory exists
    config.ensure_clips_directory()

    # Get the file path
    file_path = _get_file_path(url, config)

    # Format the clip
    clip_text = _format_clip(content, url, title, tags, config)

    # Append to the file (create if doesn't exist)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(clip_text)

    return file_path
