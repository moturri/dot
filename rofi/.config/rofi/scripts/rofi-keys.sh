#!/bin/bash

cat <<EOF | rofi -dmenu -i -p "󰌌  Keybindings"
   + h : Focus Left
   + l : Focus Right
   + j : Focus Down
   + k : Focus Up
   + Shift + h : Swap Left
   + Shift + l : Swap Right
   + Shift + j : Swap Down
   + Shift + k : Swap Up
   + i : Grow Window
   + m : Shrink Window
   + n : Reset Size
   + Shift + n : Normalize
   + o : Maximize Window
   + Shift + Space : Flip Layout
   + Shift + Enter : Toggle Split
   + Tab : Next Layout
   + Enter : Terminal (Kitty)
   + r : Rofi (Applications)
   + z : Rofi (Windows)
   + t : Rofi (Web Search)
   + v : Rofi (Clipboard)
   + Shift + a : Rofi (Display)
   + Ctrl + x : Kitty Terminal
   + Ctrl + c : calcurse
   + Ctrl + l : LocalSend
   + Ctrl + o : Obsidian
   + Ctrl + h : pavucontrol-qt
   + Ctrl + p : pcmanfm-qt
   + Ctrl + i : iwgtk
   + Print : Screenshot (screengrab)
   + w : Close Window
   + F1 : Power Menu
   + F2 : Lock Screen
   + F4 : Toggle Floating
   + F7 : Mpris Popup
   + F11 : Toggle Fullscreen
   + Ctrl + r : Reload Qtile
   + Ctrl + q : Shutdown Qtile
   + . : Next Screen
   + , : Previous Screen
  XF86MonBrightnessUp : Brightness Up
  XF86MonBrightnessDown : Brightness Down
  XF86AudioRaiseVolume : Volume Up
  XF86AudioLowerVolume : Volume Down
  XF86AudioMute : Mute Audio
  XF86AudioMicMute : Mute Microphone
EOF
