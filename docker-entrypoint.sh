#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Ensure the logs directory exists
mkdir -p /app/logs

# Redirect logs to a file and console
exec > >(tee -a /app/logs/app.log) 2>&1

# If the first argument is a flag (starts with '-') or is empty, assume the default command is `python3 -m chaturbate_poller start`
if [ "${1#-}" != "$1" ] || [ -z "$1" ]; then
  set -- python3 -m chaturbate_poller start "$@"
fi

# Execute the container command with the arguments passed to the script
exec "$@"
