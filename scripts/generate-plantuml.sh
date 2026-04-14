#!/bin/bash
# Generates SVG files from all staged .puml files

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLANTUML_JAR="$SCRIPT_DIR/plantuml.jar"

if [ ! -f "$PLANTUML_JAR" ]; then
  echo "ERROR: plantuml.jar not found at $PLANTUML_JAR"
  exit 1
fi

# Get all staged .puml files
STAGED_PUML=$(git diff --cached --name-only --diff-filter=ACM | grep '\.puml$')

if [ -z "$STAGED_PUML" ]; then
  exit 0
fi

echo "Generating SVG from PlantUML files..."

for puml_file in $STAGED_PUML; do
  echo "  Processing: $puml_file"
  java -jar "$PLANTUML_JAR" -tsvg "$puml_file"

  svg_file="${puml_file%.puml}.svg"
  if [ -f "$svg_file" ]; then
    git add "$svg_file"
    echo "  Generated and staged: $svg_file"
  else
    echo "ERROR: Failed to generate $svg_file"
    exit 1
  fi
done

echo "Done."
