hugo := "./scripts/hugo"

npm-build:
    npm run build

build: npm-build
    {{ hugo }} build

serve: npm-build
    {{ hugo }} server --buildDrafts

deploy: build
    rsync -avz --delete public/ deploy@beehen.de:/srv/http/deploy/beehen.de

clean:
    rm -rf public

podman-pull:
    podman pull ghcr.io/gohugoio/hugo:latest

check-links:
    lychee content/*
