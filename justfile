hugo := "./scripts/hugo"

npm-build:
    npm run build

build: npm-build
    {{ hugo }} build --cleanDestinationDir

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

preprocess-video:
    ./scripts/vidpre.py --webm content
