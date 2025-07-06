# Dotfiles

This repository contains my personal dotfiles for a suckless-inspired approach.
Specifically tailored for [Arch Linux](https://archlinux.org/) and the [Qtile](https://qtile.org/).
It contains configurations for various tools and environments, ensuring
a streamlined and personalized experience across my Linux setup.

## Contents

This repository is organized into the following categories:

- **`browser`**: Configurations for web browsers and related tools.
- **`gtkqt`**: Theming and configuration files for GTK and Qt applications.
- **`qtile`**: Custom configurations and scripts for the
  window manager, including efficient [Rofi](https://github.com/davatorium/rofi)
  scripts for enhanced workflow.
- **`shell`**: Configurations for various shells, command-line utilities,
  and text editors.
- **`terminal`**: Settings for terminal emulators.(alacritty, kitty & wezterm)
- **`X11`**: X Window System specific configurations.

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
