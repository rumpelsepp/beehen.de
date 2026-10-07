hugo := "./scripts/hugo"

npm-build:
    npm run build

# --gc drops image variants nothing references any more from resources/_gen
build: clean npm-build
    {{ hugo }} build --gc

serve: npm-build
    {{ hugo }} server --buildDrafts

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

deploy: build
    rsync -avz --delete public/ deploy@beehen.de:/srv/http/deploy/beehen.de

clean:
    rm -rf public

podman-pull:
    podman pull ghcr.io/gohugoio/hugo:latest

check-links: build
    lychee --offline --include-fragments public

# Encode <name>.raw.<ext> into <name>.mp4 + poster. Run after adding a raw
# video and commit the results -- CI does not encode videos.
preprocess-video:
    ./scripts/vidpre.py content
