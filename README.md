# Web Clipper

CLI helper that turns the text you copy from Chrome or Safari into organized Markdown files. The tool stores every clip by domain, adds metadata such as the browser URL, title, tags, and timestamps, and can be triggered either from the terminal or via a Raycast Script Command.

designed to work with MacOS only.

## Features
- **Smart Format Detection**: Automatically detects clipboard content type
  - HTML from web pages → Converts to clean Markdown with formatting preserved
  - Plain text → Saves as-is
  - Direct image copies → Saves PNG with Markdown link
- **Image Handling**:
  - Downloads images from web page HTML automatically
  - Saves images to `clips/images/` with timestamp-based naming
  - Updates image references to local paths in Markdown
- **Browser Integration**: Captures current URL and tab title via AppleScript (Chrome/Safari)
- **Organized Storage**: Domain-based folder structure with structured Markdown entries
- **Rich Metadata**: Timestamps, tags, page titles, and source URLs for every clip
- **CLI & Raycast**: Simple Typer-powered CLI + optional Raycast integration for global shortcuts

## Requirements
- macOS (AppleScript is used to read browser context from Chrome/Safari).
- [uv](https://docs.astral.sh/uv/) for Python packaging/runtime management.
- Python 3.13 (installed automatically by `uv sync`).
- Raycast (optional, only if you want the script command).

## Setup
```bash
# 1) Install uv (if you don't have it yet)

# 2) Clone the project
git clone https://github.com/harryeslick/web-clipper.git
cd web-clipper

# 3) Install dependencies
uv sync

# 4) Create the default clips directory and confirm config
uv run web-clipper init
```

## Usage
- Clip content: `uv run web-clipper clip --tags "docs,reading"`  
  (leave `--tags` off if you do not want hashtags).
- Show configuration: `uv run web-clipper config`
- Override the storage location: `WEB_CLIPPER_DIR=~/knowledge uv run web-clipper clip`

### Default configuration
Clips are stored inside `~/clips` by default. The snippet below is taken from `src/web_clipper/config.py` to make the defaults explicit, including the requested directory line:

```python
def default(cls) -> "ClipperConfig":
    return cls(
        clips_directory=Path.home() / "clips",
        create_subdirs=True,
        include_title=True,
        include_timestamp=True,
        timestamp_format="%Y-%m-%d %H:%M:%S"
    )
```
To save clips to a custom directory . set ENV variable in: `~/.config/web-clipper/.env`

eg:
```env
 WEB_CLIPPER_DIR=/Users/name/my/path/clips
```

The directory is created automatically and structured by domain (unless `create_subdirs=False`).

### Markdown output
Every clip is appended to a Markdown file such as `~/clips/github.com___issues.md` and looks like:

```markdown
## Issue Title
  **URL**: [Issue Title](https://github.com/org/repo/issues/123)
  **Date**: [[2025-01-15]]
  **time**: 11:45:02
  - **Tags**: #reading #todo

<clipped content with preserved formatting>

**Bold text**, *italic text*, and [links](https://example.com) are preserved.

![screenshot](./images/image_1234567890_0.png)

---
```

### Image Storage
Images are stored in `clips/images/` with the following structure:
```
clips/
├── images/
│   ├── image_1234567890_0.png
│   ├── image_1234567890_1.jpeg
│   └── image_1234567891_0.png
└── example.com___article.md
```

Images are referenced in Markdown with relative paths: `![alt](./images/image_xxx.ext)`

## Raycast Integration
1. Make sure the script is executable: `chmod +x raycast/clip-to-markdown.sh`.
2. If you keep the project somewhere other than `~/Developer/web-clipper`, update the `cd` line inside the script so it points at your clone.
3. Open Raycast → Settings → Extensions → `+` → **Add Script Command** and select `raycast/clip-to-markdown.sh`.
4. Raycast will read the inline metadata (title, mode, optional tags argument, icon) automatically. Assign a hotkey if you like.
5. (Optional) Run `raycast/test-hello.sh` the same way to confirm Raycast can execute scripts in your environment.

The Raycast script simply runs `uv run web-clipper clip --tags "$1"`, so it shares the exact same environment and dependency resolution as the CLI.

## Development
- Run the unit test suite: `uv run pytest`
- Format any Markdown clips however you like—`storage.py` appends to UTF-8 files, so existing notes stay intact.

## How It Works

### Clipboard Detection Flow
1. **Check for HTML** (from web page copies using PyObjC)
   - If found: Convert HTML to Markdown using `markdownify`
   - Download all embedded images via `requests`
   - Update image URLs to local file paths
2. **Check for Plain Text** (if no HTML)
   - Extract text via `pyperclip`
   - Handle UTF-8 encoding errors gracefully
3. **Check for Direct Images** (if copying an image file)
   - Save PNG via AppleScript/`pngpaste`
   - Generate Markdown image link

### Dependencies
- `pyperclip`: Clipboard text access
- `pyobjc-framework-cocoa`: Native macOS clipboard HTML access
- `markdownify`: HTML to Markdown conversion
- `beautifulsoup4`: HTML parsing for image extraction
- `requests`: HTTP image downloading
- `typer` + `rich`: CLI interface

## Troubleshooting
- **No browser context**: If Chrome/Safari is closed, tool falls back to `unknown` URL. Keep browser active for structured folders.
- **Clipboard permissions**: Grant Terminal/Raycast "Accessibility" and "Automation" permissions in System Settings.
- **Image download failures**: Check internet connection. Images that fail to download are skipped (warning logged).
- **UTF-8 errors**: Tool now handles non-UTF-8 clipboard content with automatic fallback and error replacement.
