#!/bin/bash
cat <<EOF | rofi -dmenu -i -p "󰌌 "
   + h : Focus Left
   + l : Focus Right
   + j : Focus Down
   + k : Focus Up
   + Shift + h : Swap Left
   + Shift + l : Swap Right
   + Shift + j : Swap Down
   + Shift + k : Swap Up
   + i : Grow
   + m : Shrink
   + n : Reset Size
   + Shift + n : Normalize
   + o : Maximize
   + Shift + Space : Flip Layout
   + Shift + Enter : Toggle Split
   + Enter : Terminal
   + r : Rofi (Applications)
   + z : Rofi (Windows)
   + t : Web Search
   + v : Clipboard Manager
   + F1 : Power Menu
   + Ctrl + x : Terminal (Kitty)
   + Ctrl + a : Arandr
   + Ctrl + l : LocalSend
   + Ctrl + o : Obsidian
   + Ctrl + h : Helvum
   + Ctrl + t : Thunar
   + Ctrl + i : iwgtk
   + Tab : Next Layout
   + w : Close Window
   + F11 : Toggle Fullscreen
   + F4 : Toggle Floating
   + Ctrl + r : Reload Qtile
   + Ctrl + q : Shutdown Qtile
   + F2 : Lock Screen
   + F7 : Mpris Popup
EOF
