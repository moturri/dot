# Arch Qtile Dotfiles

This repository contains my personal dotfiles for a suckless-inspired approach.
Specifically tailored for [Arch Linux](https://archlinux.org/) and [Qtile](https://qtile.org/).
The configs are for various tools and environments, ensuring
a streamlined and personalized experience across my Linux setup.

## Contents

This repository is organized into the following categories:

- **`X11`**: X Window System specific configurations (`.xprofile`, `.Xresources`, `xinitrc`).
- **`browser`**: Configurations for `qutebrowser` and `zen browser` (`user.js`, `userChrome.css`).
- **`gtkqt`**: Theming and configuration files for GTK (`gtk-2.0`, `gtk-3.0`, `gtk-4.0`)
  and Qt applications (`Kvantum`, `qt5ct`, `qt6ct`).
- **`shell`**: Configurations for various shells, command-line utilities, and text editors.
  - Shells: `bash`, `zsh`, `fish`
  - Prompt: `starship`
  - Multiplexer: `tmux`
  - Editors: `neovim`, `vim`
  - File Managers: `ranger`, `yazi`
  - Utilities: `fastfetch`, `tealdeer`
- **`terminal`**: Settings for terminal emulators: `alacritty`, `kitty`, and `wezterm`.
- **`wm`**: Custom configurations and scripts for the window manager and related tools.
  - Window Manager: `qtile`
  - Compositor: `picom`
  - Notification Daemon: `dunst`
  - Clipboard Manager: `greenclip`
  - Launcher: `rofi` (with custom scripts for enhanced workflow)

## Dependencies

The Qtile configurations and some other scripts within this repository rely
on the following tools:

- [brightnessctl](https://github.com/Hummer12007/brightnessctl) — for screen
  brightness control
- [acpi](https://sourceforge.net/projects/acpiclient/) — for battery and
  temperature readings
- [pipewire](https://pipewire.org) — for low-latency audio/video
- [wireplumber](https://gitlab.freedesktop.org/pipewire/wireplumber) — wpctl
- [stow](https://www.gnu.org/software/stow/) — for managing symlinks and
  maintaining clean dotfile deployment
