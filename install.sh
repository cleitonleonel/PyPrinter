#!/bin/bash

sudo apt-get update -y
sudo apt-get install git curl build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python3-openssl -y

# git clone https://github.com/pyenv/pyenv.git ~/.pyenv
curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash

lines_to_append="
export PYENV_ROOT=\"\$HOME/.pyenv\"
export PATH=\"\$PYENV_ROOT/bin:\$PATH\"
eval \"\$(pyenv init --path)\"
eval \"\$(pyenv virtualenv-init -)\"
"

echo "$lines_to_append" >> "$HOME/.bashrc"

source "$HOME/.bashrc"

pyenv install 3.8
pyenv local 3.8

# pyenv uninstall 3.8.12
