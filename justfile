npm-build:
    npm run build

build: npm-build
    hugo build

serve: npm-build
    hugo server

build-with-podman: clean npm-build
    podman run \
        --net=none \
        --rm \
        --interactive \
        --tty \
        --volume "$PWD:/mnt/$PWD:z" \
        --workdir "/mnt/$PWD" \
        --userns keep-id \
        --group-add keep-groups \
        --log-driver none \
        ghcr.io/gohugoio/hugo:latest \
        build \
        --ignoreCache

deploy: build
    rsync -avz --delete public/ deploy@beehen.de:/srv/http/deploy/beehen.de

serve-with-podman: clean npm-build
    podman run \
       --net=host \
       --rm \
       --interactive \
       --tty \
       --volume "$PWD:/mnt/$PWD:z" \
       --workdir "/mnt/$PWD" \
       --userns keep-id \
       --group-add keep-groups \
       --log-driver none \
       ghcr.io/gohugoio/hugo:latest \
       server \
       --buildDrafts

clean:
    rm -rf public

podman-pull:
    podman pull ghcr.io/gohugoio/hugo:latest

check-links:
    lychee content/*
