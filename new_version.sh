#!/usr/bin/env bash

if (( $(git status -s | wc -l) > 1 ))
then
    echo "First commit the changes in the repository except for the scron/version.py file."
    exit 1
fi

if [ $(git status -s scron/version.py | wc -l) == 1 ]
then
    cd docs/
    make html
    cd ..
    version=$(awk '{ if ($0 ~ /__version__/) {out=gensub(/[\047\057]/,"", "g", $3); print out}}' ./scron/version.py)
    git add scron/version.py
    git add docs/
    git commit -m "New version ${version}"
    git tag -a "v${version}" -m "New version ${version}"
    git push origin "v${version}"
    git push
    python3 setup.py sdist upload
else
    echo 'Change the version in the scron/version.py file.';
    exit 1
fi
