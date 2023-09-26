#!/usr/bin/env bash

set -euo pipefail

if [ -z "${1:-}" ]; then
	echo "Please specify a version compatible with \`hatch version\`." >&2
	exit 1
elif ! git diff --quiet; then
	echo "Please commit or stash all changes before running this script." >&2
	exit 1
fi

hatch version "$1"
version=$(hatch version)

git add --verbose --all
git commit --verbose --message="chore: bump version to $version"
git tag --annotate --message="$version" "$version"
git push --verbose --follow-tags
gh release create --generate-notes "$version"
