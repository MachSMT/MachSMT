#!/usr/bin/env bash

tar cJf cavae20-artifact.tar.xz \
  Dockerfile \
  README-artifact.md \
  artifact-data.tar.xz \
  bin \
  demo.sh \
  machsmt \
  requirements.txt \
  setup.py

sha1sum cavae20-artifact.tar.xz
