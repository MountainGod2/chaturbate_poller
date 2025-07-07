#!/bin/sh

set -e

# If the first argument is a flag (starts with '-') or is empty,
# assume the default command is the chaturbate_poller module
if [ "${1#-}" != "$1" ] || [ -z "$1" ]; then
  set -- python3 -m chaturbate_poller start "$@"
fi

exec "$@"
