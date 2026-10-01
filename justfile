hugo := "./scripts/hugo"

npm-build:
    npm run build

# --gc drops image variants nothing references any more from resources/_gen
build: clean npm-build
    {{ hugo }} build --gc

serve: npm-build
    {{ hugo }} server --buildDrafts

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
