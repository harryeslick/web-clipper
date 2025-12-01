#!/usr/bin/env bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Clip to Markdown
# @raycast.mode compact
# @raycast.packageName Web Clipper

# Optional parameters:
# @raycast.icon icon-system-clipboard
# @raycast.argument1 { "type": "text", "placeholder": "Tags (optional)", "optional": true }
# @raycast.author Harry Eslick
# @raycast.description Clip web content from browser to organized markdown files

set -euo pipefail

cd "$HOME/Developer/web-clipper" || exit 1
uv run web-clipper clip --tags "$1"

