#!/bin/bash

cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
pipenv run python bot.py
