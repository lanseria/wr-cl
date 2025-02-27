#!/bin/bash

VERSION_FILE=".version"
PYPROJECT_TOML="pyproject.toml"
INIT_PY="src/__init__.py"

# Check if the argument is valid
if [[ $# -ne 1 ]]; then
  echo "Usage: ./tag-publish.sh [major|minor|patch|<version_number>]"
  exit 1
fi

# Read current version
current_version=$(cat "$VERSION_FILE")

# Parse current version into major, minor, patch
IFS='.' read -ra version_parts <<< "$current_version"
major="${version_parts[0]}"
minor="${version_parts[1]}"
patch="${version_parts[2]}"

# Update version based on argument
if [[ $1 == "major" ]]; then
  major=$((major + 1))
  minor=0
  patch=0
elif [[ $1 == "minor" ]]; then
  minor=$((minor + 1))
  patch=0
elif [[ $1 == "patch" ]]; then
  patch=$((patch + 1))
else
  new_version=$1
  echo "Using custom version: $new_version"
fi

# Construct new version
if [[ -z $new_version ]]; then
  new_version="$major.$minor.$patch"
fi

# Validate version format
if ! [[ $new_version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: Invalid version format, must be X.Y.Z"
  exit 1
fi

# Update version file
echo "$new_version" > "$VERSION_FILE"

# Update pyproject.toml
if [[ -f $PYPROJECT_TOML ]]; then
  sed -i.bak "s/^version = \".*\"$/version = \"$new_version\"/" "$PYPROJECT_TOML" && rm -f "$PYPROJECT_TOML.bak"
  echo "Updated $PYPROJECT_TOML version to $new_version"
else
  echo "Warning: $PYPROJECT_TOML does not exist, skipping"
fi

# Update src/__init__.py
if [[ -f $INIT_PY ]]; then
  sed -i.bak "s/^__version__ = \".*\"$/__version__ = \"$new_version\"/" "$INIT_PY" && rm -f "$INIT_PY.bak"
  echo "Updated $INIT_PY version to $new_version"
else
  echo "Warning: $INIT_PY does not exist, skipping"
fi

# Collect files to commit
files_to_add=("$VERSION_FILE")
[[ -f $PYPROJECT_TOML ]] && files_to_add+=("$PYPROJECT_TOML")
[[ -f $INIT_PY ]] && files_to_add+=("$INIT_PY")

# Commit changes
# git add "${files_to_add[@]}"
# git commit -m "chore(release): bump version to v$new_version"

# Create git tag
# git tag -a "v$new_version" -m "Release v$new_version"

echo "Version update complete! New version: $new_version"
echo "Please use 'git push --tags' to push the tags"