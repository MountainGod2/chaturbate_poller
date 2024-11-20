#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# If the first argument is a flag (starts with '-') or is empty, assume the default command is `python3 -m chaturbate_poller start`
if [ "${1#-}" != "$1" ] || [ -z "$1" ]; then
  set -- python3 -m chaturbate_poller start "$@"
fi

# Execute the container command with the arguments passed to the script
exec "$@"
