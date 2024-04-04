#!/bin/bash

host='0.0.0.0'
port=9001

sudo apt-get update -y
sudo apt-get install git curl build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python3-openssl jq -y

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

base_directory="/var/www/$USER"
sudo mkdir -p "$base_directory/pyprinter"
sudo cp -r ./* "$base_directory/pyprinter"

echo "Dando permissões ao usuário $USER"
sudo chown "$USER:$USER" -R "$base_directory"
sudo chmod -R 755 "$base_directory/pyprinter"
cd "$base_directory/pyprinter" || exit
pyenv local 3.8

pip install -U pip
pip install -r requirement.txt

python_path=$(pyenv prefix)

if [ -z "$host" ] || [ -z "$port" ]; then
  echo "As configurações de host e/ou porta não foram encontradas no arquivo de configuração."
  exit 1
fi

service_content="[Unit]
Description=Gunicorn instance to serve $USER
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$base_directory/pyprinter
Environment=\"PATH=${python_path}/bin\"
ExecStart=${python_path}/bin/gunicorn --workers 1 --bind $host:$port server:app

[Install]
WantedBy=multi-user.target"

service_file="/etc/systemd/system/pyprinter.service"
echo "$service_content" | sudo tee "$service_file" > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable pyprinter

if systemctl is-active --quiet pyprinter; then
  echo "O serviço pyprinter está ativo."
else
  echo "O serviço pyprinter está inativo. Ativando o serviço..."
  sudo systemctl start pyprinter

  if systemctl is-active --quiet pyprinter; then
    echo "O serviço pyprinter foi ativado com sucesso."
    echo "Instalação concluída com sucesso !!!"
  else
    echo "Não foi possível ativar o serviço pyprinter."
  fi
fi

# pyenv uninstall 3.8.12
