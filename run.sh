#!/bin/bash

bash
pyenv virtualenv 3.11 pvenv
pyenv activate pvenv
python3 src/main.py
pyenv deactivate
