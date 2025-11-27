# Web Clipper

CLI helper that turns the text you copy from Chrome or Safari into organized Markdown files. The tool stores every clip by domain, adds metadata such as the browser URL, title, tags, and timestamps, and can be triggered either from the terminal or via a Raycast Script Command.

designed to work with MacOS only.

## Features
- Captures the current clipboard, browser URL, and tab title via AppleScript on macOS.
- Organizes clips inside domain-based folders and appends structured Markdown entries.
- Adds optional metadata such as timestamps, tags, and page titles to every capture.
- Simple Typer-powered CLI with `clip`, `init`, and `config` commands plus Rich output.
- Optional Raycast integration (`raycast/clip-to-markdown.sh`) for a global launcher shortcut.

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
Every clip is appended to a Markdown file such as `~/clips/github.com/issues.md` and looks like:

```
---
## Clip: Issue Title
- **URL**: https://github.com/org/repo/issues/123
- **Captured**: 2025-01-15 11:45:02
- **Tags**: #reading #todo

<clipped text>

---
```

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

## Troubleshooting
- If Chrome/Safari is closed, the tool falls back to a generic `unknown` URL and file. Make sure one of the browsers is active if you want structured folders.
- Clipboard access errors are usually caused by permission issues—on macOS grant Terminal/Raycast “Accessibility” and “Automation” permissions if prompted.
