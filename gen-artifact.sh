#!/usr/bin/env bash


CLEAN_DIR="/tmp/machsmt-$$"
DIR=machsmt-artifact

git clone https://github.com/j29scott/MachSMT.git "$CLEAN_DIR"

TO_COPY="
Dockerfile
README-artifact.md
README.md
artifact-data.tar.xz
bin
demo.sh
machsmt
requirements.txt
setup.py
"

rm -rf "$DIR"
mkdir "$DIR"

# Copy files from fresh git clone
for f in $TO_COPY; do
  cp -r "$CLEAN_DIR/$f" "$DIR"
done

tar cJf machsmt-artifact.tar.xz "$DIR"
sha1sum machsmt-artifact.tar.xz

rm -rf "$DIR"
rm -rf "$CLEAN_DIR"
