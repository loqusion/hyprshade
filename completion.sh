#!/usr/bin/env bash

# https://click.palletsprojects.com/en/8.1.x/shell-completion/

set -euo pipefail

TARGET_SHELL="$1"

case "$TARGET_SHELL" in
bash | zsh | fish) ;;
*)
	echo "Unknown shell: $TARGET_SHELL" >&2
	exit 1
	;;
esac

export _HYPRSHADE_COMPLETE="${TARGET_SHELL}_source"
export PYTHONPATH=./src
./.venv/bin/python ./src/hyprshade
