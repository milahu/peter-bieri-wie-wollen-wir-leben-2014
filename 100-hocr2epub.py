#!/usr/bin/env python3

import glob
import os
import re
import shutil
import subprocess
import sys
import zipfile
import shlex
from datetime import datetime
from pathlib import Path

from _shared import (
    load_config,
    get_page_num,
)


src = Path("090-ocr")

# write EPUB file
# dst = Path(Path(__file__).stem + ".epub")

# write unpacked EPUB files to workdir
dst = Path(".")


config = load_config()


if dst != Path(".") and dst.exists():
    print(f"error: output exists: {dst}")
    sys.exit(1)


# downscale to 300 dpi
# 600 dpi -> 300 dpi: 90 MB -> 60 MB
scale = 300 / config.scan_resolution


hocr_to_epub_fxl = "hocr-to-epub-fxl"

# TODO dont commit
if 1:
    hocr_to_epub_fxl = "/home/user/src/archive-hocr-tools/bin/hocr-to-epub-fxl"

args = [
    hocr_to_epub_fxl,
    "--output", str(dst),
]

if dst == Path("."):
    args.append("--output-unpacked")


def git_modified():
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        text=True,
    ).strip()


def stat_modified(path):
    ts = Path(path).stat().st_mtime
    dt = datetime.fromtimestamp(ts).astimezone()
    return dt.isoformat(timespec="seconds")


doc_modified = max(
    git_modified(),
    stat_modified(src),
)


args += [
    "--scale", str(scale),
    "--image-format", "avif",
    "--text-format", "html",
    # TODO? move these config items to 000-config.py
    "--doc-modified", doc_modified,
    "--doc-title", "Wie wollen wir leben?",
    # "--doc-subtitle", "",
    # "--doc-subject", "",
    "--doc-date", "2014",
    "--doc-edition", "3",
    "--doc-extent", "96 pages",
    "--color-image-pages", "97,98",
    "--doc-author", "Peter Bieri",
    # "--doc-introducer", "",
    # "--doc-contributor", "",
    # "--doc-translator", "",
    "--doc-publisher", "Deutscher Taschenbuch Verlag",
    "--doc-language", "de", # german
    # "--doc-language", "en", # english
    "--doc-isbn", "9783423348010",
    "--doc-cover-image", "0663-level/097.tiff",
    "--canonical-url-base", "https://milahu.github.io/peter-bieri-wie-wollen-wir-leben-2014/",
    "--doc-description", """
**Erkenne dich selbst!**

Spätestens seit der Aufklärung sind Selbstbestimmung, Vernunft und freier Wille
wesentlich für ein würdiges, zufriedenes, glückliches Leben.

Doch was genau bedeutet das?
Wie hängen Selbsterkenntnis und Selbstbestimmung zusammen?

Unser Denken, Fühlen und Handeln sind ja auch von äußeren Umständen geprägt.
Wie können wir trotzdem Einfluss auf unser Leben nehmen,
sodass es uns nicht einfach nur zustößt?

Welche Rolle spielen die anderen,
und wie kann es gelingen, das was wir wollen in Einklang mit unserer Umgebung zu bringen?

Anschaulich und abwechslungsreich erkundet Peter Bieri diese Kernthemen der menschlichen Existenz
und regt dazu an, zum Verfasser der eigenen Lebensgeschichte zu werden.
""",
]


print(">", shlex.join(args + sys.argv[1:]) + f" {src}/*.hocr")


hocr_files = list(src.glob("*.hocr"))

hocr_files.sort()

subprocess.run(
    args + sys.argv[1:] + hocr_files,
    check=True,
)


if dst == Path("."):
    print("done ./index.xhtml")
    sys.exit(0)


print(f"done {dst}")


# extract the EPUB content files

# rm -rf $dst.unzip
unzip_dir = Path(str(dst) + ".unzip")
shutil.rmtree(unzip_dir, ignore_errors=True)
unzip_dir.mkdir()


# unzip -q ../$dst
with zipfile.ZipFile(dst) as z:
    z.extractall(unzip_dir)


print(f"done {unzip_dir}/index.html")
