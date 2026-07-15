#!/bin/sh

repo_root=$(git rev-parse --show-toplevel)
exec "$repo_root/update_env.sh"
