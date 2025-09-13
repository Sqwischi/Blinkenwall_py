# Blinkenwall/LED-Matrix flask app for Hackerspace Metalab in vienna

# install on anything that works with autorun i ended up using ubuntu desktop because nothing else wanted to work

# install
# - firefox
# - curl
# - python3 python3-pip python3-venv


# install with pip in venv
# -flask
# -waitress

flask --app flaskr init-db

# add secure python session key to config.json with:
python3 -c 'import secrets; print(secrets.token_hex())'

# add api key from homeassistant to blinkenwall.sh where token (& replace url I guess)

# set up autologin
# set up auto start of script blinkenwall.sh
# set up nginx reverse proxy


# set up nginx reverse proxy
