# The recipes every site shares (npm-build, build, serve, clean,
# podman-pull, check-links); a recipe below under the same name replaces
# the theme's.
import 'themes/bienensteff/justfile'

# List all recipes
default:
    @just --list --unsorted

# Creates content/blog/<year>/<slug>/index.md from archetypes/blog/ as a
# draft; photos go into that folder, next to index.md.
# Start a new post, e.g. `just new-post kroatien-im-herbst`
new-post slug:
    {{ hugo }} new content --kind blog "blog/$(date +%Y)/{{ slug }}"

# Creates content/notizen/<date>-<time>/index.md from
# archetypes/notizen/. Photos go into that folder, next to index.md, and
# appear below the text without further ado.
# Start a new note, e.g. `just new-note` or `just new-note Karin`
new-note author="Steff":
    #!/bin/sh
    set -eu
    dir="notizen/$(date +%Y-%m-%d-%H%M)"
    {{ hugo }} new content --kind notizen "$dir"
    sed -i 's/^author: .*/author: {{ author }}/' "content/$dir/index.md"

# Build and upload the site to beehen.de
deploy: build
    rsync -avz --delete public/ deploy@beehen.de:/srv/http/deploy/beehen.de

# Run after adding a raw video and commit the results -- CI does not
# encode videos.
# Encode <name>.raw.<ext> into <name>.mp4 + poster
preprocess-video:
    ./scripts/vidpre.py content
