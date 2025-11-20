"""Configuration management for web clipper."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ClipperConfig:
    """Configuration for the web clipper."""

    clips_directory: Path
    create_subdirs: bool = True
    include_title: bool = True
    include_timestamp: bool = True
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def default(cls) -> "ClipperConfig":
        """Create default configuration."""
        return cls(
            clips_directory=Path.home() / "clips",
            create_subdirs=True,
            include_title=True,
            include_timestamp=True,
            timestamp_format="%Y-%m-%d %H:%M:%S"
        )

    @classmethod
    def from_env(cls) -> "ClipperConfig":
        """Load configuration from environment variables."""
        config = cls.default()

        # Override with environment variables if present
        if clips_dir := os.getenv("WEB_CLIPPER_DIR"):
            config.clips_directory = Path(clips_dir).expanduser()

        return config

    def ensure_clips_directory(self) -> None:
        """Ensure the clips directory exists."""
        self.clips_directory.mkdir(parents=True, exist_ok=True)


def get_config() -> ClipperConfig:
    """Get the current configuration."""
    return ClipperConfig.from_env()
