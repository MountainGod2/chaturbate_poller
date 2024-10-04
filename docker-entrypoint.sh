#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# If the first argument is a flag, assume we want to run cbmetrics
if [ "${1#-}" != "$1" ] || [ -z "$(command -v "$1")" ]; then
  set -- /app/.venv/bin/chaturbate_poller "$@"
fi

# Print the command to the console and execute it with the arguments passed to the entrypoint
echo "Running command:" "$@"
exec "$@"
