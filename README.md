# Blinkenwall/LED-Matrix flask app for Hackerspace Metalab in vienna

# on alpine image
setup-alpine
setup-desktop

# install

# -firefox
# -python3
# -git

 git clone this repository

# create venv in Blinkenwall_py
python3 -m venv .
source bin/activate

# install with pip
# -flask
# -waitress

flask --app flask init-db

# add secure python session key to config.json with:
python -c 'import secrets; print(secrets.token_hex())'

# add api key from homeassistant to blinkenwall.sh where token (& replace url I guess)

# set up autologin
# set up auto start of script blinkenwall.sh