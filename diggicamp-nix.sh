#! /usr/bin/env nix-shell
#! nix-shell -i bash -p python3 python37Packages.requests python37Packages.lxml python37Packages.beautifulsoup4 python37Packages.clint

DGC_PATH=$(dirname $(realpath $0))
$DGC_PATH/diggicamp.py "$@"

