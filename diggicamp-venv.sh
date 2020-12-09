#!/usr/bin/env bash

DGC_PATH=$(dirname $(realpath $0))

if [ ! -d $DGC_PATH/venv ] || [ $1 == 'install' ] ; then
    python3 -m venv $DGC_PATH/venv
    $DGC_PATH/venv/bin/pip install -r $DGC_PATH/requirements.txt
    echo -e "\n\n######"
    echo "  virtual environment installation complete!"
    echo -e "  you can now use diggicamp!\n######\n\n"
fi

$DGC_PATH/venv/bin/python3 $DGC_PATH/diggicamp.py "$@"

