#!/usr/bin/env bash

# Replace cache: false to cache: false, and ignore all comments on that line
sed -E '/^[[:space:]]*cache:[[:space:]]*false/ s/cache:[[:space:]]*false.*/cache: true/' .github/workflows/ci.yaml
