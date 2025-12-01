"""Core clipping logic - orchestrates clipboard, browser, and storage."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pyperclip

from web_clipper.browser import BrowserContext, BrowserError, get_browser_context
from web_clipper.config import ClipperConfig, get_config
from web_clipper.html_processor import get_html_from_clipboard, html_to_markdown
from web_clipper.images import get_markdown_image_link, save_clipboard_image
from web_clipper.storage import save_clip


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
    Clip content from the browser to markdown with intelligent format detection.

    This function handles multiple clipboard formats:
    - HTML from web pages (converts to markdown, downloads images)
    - Plain text content
    - Direct image copies (saves as PNG with markdown link)

    Process:
    1. Check for HTML content in clipboard (from web page copies)
       - If found: Convert HTML to markdown and download embedded images
    2. If no HTML, get plain text content
       - Check for direct image copy and save if present
    3. Get browser context (URL and title) via AppleScript
    4. Save to organized markdown file with metadata
    5. Return result with file path and statistics

    Images are saved to: clips/images/image_{timestamp}_{counter}.{ext}
    Referenced in markdown as: ![alt](./images/image_xxx.ext)

    Args:
        tags: Optional comma-separated tags (e.g., "python, ai, tutorial")
        config: Optional configuration (uses default from env if not provided)

    Returns:
        ClipResult with details about the saved clip including:
        - file_path: Where the clip was saved
        - url: Source URL
        - title: Page title
        - content_length: Character count

    Raises:
        NoClipboardContentError: If clipboard is empty (no text or image)
        ClipperError: For clipboard read errors or save failures
    """
    if config is None:
        config = get_config()

    # Step 1: Check for HTML content first (from web pages)
    html_content = get_html_from_clipboard()
    image_count = 0
    browser_context = None

    if html_content:
        # We have HTML - need to get browser context first for base URL
        try:
            browser_context = get_browser_context()
            base_url = browser_context.url
        except BrowserError:
            base_url = "https://example.com"  # Fallback URL
            browser_context = BrowserContext(url=base_url, title=None)

        # Convert HTML to Markdown and download images
        try:
            content, image_count = html_to_markdown(
                html_content,
                base_url,
                config.clips_directory
            )
        except Exception as e:
            # If HTML processing fails, fall back to plain text
            html_content = None
            browser_context = None

    # Step 2: If no HTML, get plain text clipboard content
    if not html_content:
        try:
            content = pyperclip.paste()
        except UnicodeDecodeError as e:
            # Handle non-UTF-8 clipboard content by replacing invalid bytes
            import subprocess
            try:
                # Get raw clipboard bytes and decode with error handling
                result = subprocess.run(['pbpaste'], capture_output=True, check=True)
                content = result.stdout.decode('utf-8', errors='replace')
            except Exception as fallback_error:
                raise ClipperError(
                    f"Failed to read clipboard: {e}. "
                    f"Fallback also failed: {fallback_error}"
                )
        except Exception as e:
            raise ClipperError(f"Failed to read clipboard: {e}")

        # Check for clipboard image and save if present (for direct image copies)
        image_path = save_clipboard_image(config.clips_directory)
        if image_path:
            # If we have an image, create markdown link for it
            image_markdown = get_markdown_image_link(
                image_path,
                config.clips_directory,
                alt_text="clipboard_image"
            )

            # If we also have text content, append the image link
            # Otherwise, use just the image link as content
            if content and content.strip():
                content = f"{content.strip()}\n\n{image_markdown}"
            else:
                content = image_markdown
            image_count = 1

    # Validate we have content
    if not content or not content.strip():
        raise NoClipboardContentError(
            "Clipboard is empty. Please copy some text or image before clipping."
        )

    # Step 3: Get browser context (if not already fetched for HTML)
    # TODO Browser context only get chrome, not safari.
    if browser_context is None:
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
