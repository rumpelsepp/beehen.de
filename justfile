deploy:
    hugo && rsync -avz --delete public/ deploy@beehen.de:/srv/http/deploy/beehen.de

clean:
    rm -rf public
