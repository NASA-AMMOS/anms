#!/usr/bin/env bash

# Copy example.env to .env if file doesn't already exist.
[[ -f .env ]] || cp example.env .env

# Add or update GIT_VERSION and GIT_DATE in .env file
GIT_VERSION="$(git describe --tags --always --dirty)"
GIT_DATE="$(git log -1 --format=%cI)"

if grep -q '^GIT_VERSION=' .env; then
    sed -i.bak "s|^GIT_VERSION=.*|GIT_VERSION=${GIT_VERSION}|" .env
else
    echo "GIT_VERSION=${GIT_VERSION}" >> .env
fi

if grep -q '^GIT_DATE=' .env; then
    sed -i.bak "s|^GIT_DATE=.*|GIT_DATE=${GIT_DATE}|" .env
else
    echo "GIT_DATE=${GIT_DATE}" >> .env
fi

# Add OPENSEARCH_INITIAL_ADMIN_PASSWORD if missing.
if ! grep -q '^OPENSEARCH_INITIAL_ADMIN_PASSWORD=' .env; then
    password="$(openssl rand -base64 24 | tr -d '=+/' | cut -c1-20)"
    echo "OPENSEARCH_INITIAL_ADMIN_PASSWORD=${password}" >> .env
fi
