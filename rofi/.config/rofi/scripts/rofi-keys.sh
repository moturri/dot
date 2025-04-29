#!/bin/bash
cat <<EOF | rofi -dmenu -i -p "Keybindings "
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
   + r : Rofi (Drun)
   + z : Rofi (Windows)
   + t : Web Search
   + v : Clipboard Manager
   + F1 : Power Menu

   + Ctrl + x : Terminal (Kitty)
   + Ctrl + a : Arandr
   + Ctrl + l : LocalSend
   + Ctrl + n : Obsidian
   + Ctrl + o : Octopi
   + Ctrl + m : Spotify
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

  XF86 keys (Volume Up, Down, Mute, Mic Mute)
  Brightness Up/Down
EOF
