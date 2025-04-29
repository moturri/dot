#!/bin/bash
cat <<EOF | rofi -dmenu -i -p "Keybindings "
    [Window Movement]
   + h : Focus Left
   + l : Focus Right
   + j : Focus Down
   + k : Focus Up

    [Window Movement (Swap)]
   + Shift + h : Swap Left
   + Shift + l : Swap Right
   + Shift + j : Swap Down
   + Shift + k : Swap Up

    [Resize]
   + i : Grow
   + m : Shrink
   + n : Reset Size
   + Shift + n : Normalize

    [Layouts]
   + o : Maximize
   + Shift + Space : Flip Layout
   + Shift + Enter : Toggle Split

    [Launch]
   + Enter : Terminal
   + r : Rofi (Drun)
   + z : Rofi (Windows)
   + t : Web Search
   + v : Clipboard Manager
   + F1 : Power Menu

    [Scratchpads]
   + Ctrl + x : Terminal (Kitty)
   + Ctrl + a : Arandr
   + Ctrl + l : LocalSend
   + Ctrl + n : Obsidian
   + Ctrl + o : Octopi
   + Ctrl + m : Spotify
   + Ctrl + h : Helvum
   + Ctrl + t : Thunar
   + Ctrl + i : iwgtk

    [System]
   + Tab : Next Layout
   + w : Close Window
   + F11 : Toggle Fullscreen
   + F4 : Toggle Floating
   + Ctrl + r : Reload Qtile
   + Ctrl + q : Shutdown Qtile
   + F2 : Lock Screen

    [Volume & Brightness]
  XF86 keys (Volume Up, Down, Mute, Mic Mute)
  Brightness Up/Down
EOF
