"""Browser integration using AppleScript for Chrome and Safari."""

import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class BrowserContext:
    """Browser context information."""

    url: str
    title: Optional[str] = None


class BrowserError(Exception):
    """Raised when unable to get browser context."""


def _run_applescript(script: str, timeout: int = 5) -> str:
    """Run an AppleScript and return the output."""
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        raise BrowserError("AppleScript timed out")
    except subprocess.CalledProcessError as e:
        raise BrowserError(f"AppleScript failed: {e.stderr}")


def _get_chrome_context() -> BrowserContext:
    """Get URL and title from Chrome."""
    script = '''
    tell application "Google Chrome"
        if (count of windows) > 0 then
            tell front window
                set currentTab to active tab
                set currentURL to URL of currentTab
                set currentTitle to title of currentTab
                return currentURL & "\n" & currentTitle
            end tell
        else
            error "No Chrome windows open"
        end if
    end tell
    '''
    output = _run_applescript(script)
    lines = output.split("\n", 1)
    url = lines[0] if lines else ""
    title = lines[1] if len(lines) > 1 else None
    return BrowserContext(url=url, title=title)


def _get_safari_context() -> BrowserContext:
    """Get URL and title from Safari."""
    script = '''
    tell application "Safari"
        if (count of windows) > 0 then
            tell front window
                set currentTab to current tab
                set currentURL to URL of currentTab
                set currentTitle to name of currentTab
                return currentURL & "\n" & currentTitle
            end tell
        else
            error "No Safari windows open"
        end if
    end tell
    '''
    output = _run_applescript(script)
    lines = output.split("\n", 1)
    url = lines[0] if lines else ""
    title = lines[1] if len(lines) > 1 else None
    return BrowserContext(url=url, title=title)


def _get_active_browser() -> Optional[str]:
    """Determine which browser is currently active."""
    script = '''
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
        return frontApp
    end tell
    '''
    try:
        app_name = _run_applescript(script)
        if "Chrome" in app_name:
            return "chrome"
        elif "Safari" in app_name:
            return "safari"
        return None
    except BrowserError:
        return None


def get_browser_context() -> BrowserContext:
    """
    Get current browser URL and title.

    Tries to detect the active browser (Chrome or Safari) and retrieve
    the current tab's URL and title using AppleScript.

    Returns:
        BrowserContext with URL and optional title

    Raises:
        BrowserError: If unable to get browser context
    """
    active_browser = _get_active_browser()

    try:
        if active_browser == "chrome":
            return _get_chrome_context()
        elif active_browser == "safari":
            return _get_safari_context()
        else:
            # Try Chrome first, then Safari
            try:
                return _get_chrome_context()
            except BrowserError:
                return _get_safari_context()
    except BrowserError as e:
        raise BrowserError(
            f"Unable to get browser context. Make sure Chrome or Safari is open "
            f"with an active tab. Error: {e}"
        )
