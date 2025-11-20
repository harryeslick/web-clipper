"""Core clipping logic - orchestrates clipboard, browser, and storage."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pyperclip

from .browser import BrowserContext, BrowserError, get_browser_context
from .config import ClipperConfig, get_config
from .storage import save_clip


class ClipperError(Exception):
    """Base exception for clipper errors."""


class NoClipboardContentError(ClipperError):
    """Raised when clipboard is empty."""


@dataclass
class ClipResult:
    """Result of a clipping operation."""

    file_path: Path
    url: str
    title: Optional[str]
    content_length: int


def clip(tags: Optional[str] = None, config: Optional[ClipperConfig] = None) -> ClipResult:
    """
    Clip content from the browser to markdown.

    Steps:
    1. Read content from clipboard
    2. Get browser context (URL and title) via AppleScript
    3. Save to organized markdown file
    4. Return result

    Args:
        tags: Optional comma-separated tags
        config: Optional configuration (uses default if not provided)

    Returns:
        ClipResult with details about the saved clip

    Raises:
        NoClipboardContentError: If clipboard is empty
        BrowserError: If unable to get browser context
        ClipperError: For other clipping errors
    """
    if config is None:
        config = get_config()

    # Step 1: Get clipboard content
    try:
        content = pyperclip.paste()
    except Exception as e:
        raise ClipperError(f"Failed to read clipboard: {e}")

    if not content or not content.strip():
        raise NoClipboardContentError(
            "Clipboard is empty. Please copy some text before clipping."
        )

    # Step 2: Get browser context
    try:
        browser_context = get_browser_context()
    except BrowserError:
        # Fallback: save without browser context
        browser_context = BrowserContext(url="unknown", title=None)

    # Step 3: Save the clip
    try:
        file_path = save_clip(
            content=content,
            url=browser_context.url,
            title=browser_context.title,
            tags=tags,
            config=config
        )
    except Exception as e:
        raise ClipperError(f"Failed to save clip: {e}")

    # Step 4: Return result
    return ClipResult(
        file_path=file_path,
        url=browser_context.url,
        title=browser_context.title,
        content_length=len(content)
    )
