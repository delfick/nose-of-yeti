#!/bin/bash

cd "$(git rev-parse --show-toplevel)"

HANDLED=0
if [[ "$#" == "1" ]]; then
    if [[ "$1" == "activate" ]]; then
        if [[ "$0" = "$BASH_SOURCE" ]]; then
            echo "You need to run as 'source ./run.sh $1'"
            exit 1
        fi
        VENVSTARTER_ONLY_MAKE_VENV=1 ./tools/venv

        case "$1" in
        activate)
            source ./tools/.python/bin/activate
            HANDLED=1
            ;;
        esac
    fi
fi

if [[ $HANDLED != 1 ]]; then
    exec ./tools/venv "$@"
fi
