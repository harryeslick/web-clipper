"""Tests for storage module."""

from pathlib import Path

import pytest

from web_clipper.config import ClipperConfig
from web_clipper.storage import _get_file_path, _sanitize_filename, save_clip


def test_sanitize_filename():
    """Test filename sanitization."""
    assert _sanitize_filename("Hello World") == "hello-world"
    assert _sanitize_filename("test/path/file") == "test-path-file"
    assert _sanitize_filename("special@#$chars") == "special-chars"
    assert _sanitize_filename("Multiple   Spaces") == "multiple-spaces"
    assert _sanitize_filename("---leading-trailing---") == "leading-trailing"


def test_get_file_path_with_subdirs():
    """Test file path generation with subdirectories."""
    config = ClipperConfig(
        clips_directory=Path("/tmp/clips"),
        create_subdirs=True
    )

    # Test with domain and path
    url = "https://github.com/anthropics/claude"
    path = _get_file_path(url, config)
    assert path == Path("/tmp/clips/github.com/anthropics-claude.md")

    # Test with domain only
    url = "https://example.com"
    path = _get_file_path(url, config)
    assert path == Path("/tmp/clips/example.com/index.md")

    # Test with www prefix
    url = "https://www.example.com/docs/guide"
    path = _get_file_path(url, config)
    assert path == Path("/tmp/clips/example.com/docs-guide.md")


def test_get_file_path_flat_structure():
    """Test file path generation without subdirectories."""
    config = ClipperConfig(
        clips_directory=Path("/tmp/clips"),
        create_subdirs=False
    )

    url = "https://github.com/anthropics/claude"
    path = _get_file_path(url, config)
    assert path == Path("/tmp/clips/github.com_anthropics-claude.md")


def test_save_clip(tmp_path):
    """Test saving a clip to file."""
    config = ClipperConfig(
        clips_directory=tmp_path,
        create_subdirs=True,
        include_title=True,
        include_timestamp=True
    )

    content = "This is my clipped content."
    url = "https://example.com/page"
    title = "Example Page"
    tags = "test,example"

    file_path = save_clip(content, url, title, tags, config)

    # Check file was created
    assert file_path.exists()
    assert file_path.parent == tmp_path / "example.com"

    # Check content
    saved_content = file_path.read_text()
    assert "## Clip: Example Page" in saved_content
    assert "https://example.com/page" in saved_content
    assert "This is my clipped content." in saved_content
    assert "#test" in saved_content
    assert "#example" in saved_content
    assert "---" in saved_content


def test_save_clip_without_title(tmp_path):
    """Test saving a clip without title."""
    config = ClipperConfig(
        clips_directory=tmp_path,
        create_subdirs=True
    )

    content = "Content without title."
    url = "https://example.com"

    file_path = save_clip(content, url, None, None, config)

    saved_content = file_path.read_text()
    assert "## Clip: Untitled" in saved_content


def test_save_multiple_clips(tmp_path):
    """Test saving multiple clips to same file."""
    config = ClipperConfig(
        clips_directory=tmp_path,
        create_subdirs=True
    )

    url = "https://example.com/page"

    # Save first clip
    save_clip("First clip", url, "Title 1", None, config)

    # Save second clip
    file_path = save_clip("Second clip", url, "Title 2", None, config)

    # Both clips should be in the same file
    saved_content = file_path.read_text()
    assert "First clip" in saved_content
    assert "Second clip" in saved_content
    assert saved_content.count("---") >= 4  # At least 2 separators per clip
