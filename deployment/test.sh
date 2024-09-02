#!/usr/bin/env nix-shell
#!nix-shell shell.testing.nix -i bash
echo ------ Running pytest for the entire project ------
parent_dir=$(dirname "$(realpath "$0")")/..
cd "$parent_dir"
pytest
if [ $? -ne 0 ]; then
    echo ------ ERROR - tests failed, aborting ------
    exit 1
else
    echo ------ Finished running tests successfully ------
fi
