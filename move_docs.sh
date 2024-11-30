#!/bin/bash

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create parent docs directory if it doesn't exist
mkdir -p ../../

# Move files to their new locations
mv .github ../../
mv README.md ../../
mv LICENSE ../../

# Move existing wiki files
mv docs/wiki ../../

echo "✨ Documentation structure moved!"
echo "📝 Wiki files moved to: ../../wiki"
