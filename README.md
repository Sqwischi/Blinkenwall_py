Blinkenwall/LED-Matrix flask app for Hackerspace Metalab in vienna

install
xorg
xinit 
firefox
python3-venv

create venv in Blinkenwall_py
python3 -m venv .
source bin/activate

install with pip
flask
waitress

add secure python session key to config.json with:
python -c 'import secrets; print(secrets.token_hex())'

add api key from homeassistant to blinkenwall.sh where token (& replace url I guess)


#put into user folder .xinitrc
exec firefox --kiosk http://127.0.0.1:8080/blinkenwall