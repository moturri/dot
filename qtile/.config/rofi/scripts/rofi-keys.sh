#!/bin/bash

cat <<EOF | rofi -dmenu -i -p "󰌌  Keybindings"
$(python3 /home/m/.config/rofi/scripts/main/generate_keys.py)
EOF
