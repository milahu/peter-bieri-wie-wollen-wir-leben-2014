#!/bin/sh

# TODO set config values
cover_src=0663-level/097.tiff

magick "$cover_src" -scale 50% -quality 50% cover.avif
