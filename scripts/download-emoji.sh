#!/bin/bash
# Download OpenMoji outline emoji SVGs for Asetate
# Source: https://openmoji.org/ (CC BY-SA 4.0)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EMOJI_DIR="$PROJECT_ROOT/asetate/static/emoji"

echo "=== OpenMoji Emoji Download Script ==="
echo "Target directory: $EMOJI_DIR"
echo ""

# Create directory if needed
mkdir -p "$EMOJI_DIR"

# Download SVG pack
echo "Downloading OpenMoji black/outline SVGs (3.5MB)..."
curl -L -o /tmp/openmoji-svg-black.zip \
  https://github.com/hfg-gmuend/openmoji/releases/download/16.0.0/openmoji-svg-black.zip

# Extract SVGs
echo "Extracting SVGs..."
unzip -o /tmp/openmoji-svg-black.zip -d "$EMOJI_DIR/"

# Download metadata
echo "Downloading emoji metadata..."
curl -L -o "$EMOJI_DIR/openmoji.json" \
  https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/data/openmoji.json

# Cleanup
rm /tmp/openmoji-svg-black.zip

# Count files
SVG_COUNT=$(find "$EMOJI_DIR" -name "*.svg" | wc -l | tr -d ' ')

echo ""
echo "=== Done! ==="
echo "Downloaded $SVG_COUNT emoji SVGs"
echo "Metadata: $EMOJI_DIR/openmoji.json"
echo ""
echo "License: CC BY-SA 4.0 - OpenMoji (https://openmoji.org/)"
