"""Tests for configuration module."""

from pathlib import Path

from web_clipper.config import ClipperConfig


def test_default_config():
    """Test default configuration values."""
    config = ClipperConfig.default()

    assert config.clips_directory == Path.home() / "clips"
    assert config.create_subdirs is True
    assert config.include_title is True
    assert config.include_timestamp is True
    assert config.timestamp_format == "%Y-%m-%d %H:%M:%S"


def test_custom_config():
    """Test custom configuration values."""
    custom_dir = Path("/tmp/my-clips")
    config = ClipperConfig(
        clips_directory=custom_dir,
        create_subdirs=False,
        include_title=False
    )

    assert config.clips_directory == custom_dir
    assert config.create_subdirs is False
    assert config.include_title is False
