# Arch Qtile Dotfiles

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Stow](https://img.shields.io/badge/managed%20by-Stow-green.svg)](https://www.gnu.org/software/stow/)
[![Arch Linux](https://img.shields.io/badge/Arch%20Linux-passing-blueviolet.svg)](https://archlinux.org/)
This repository contains my personal dotfiles, tailored for an Arch Linux environment running the Qtile window manager. The configurations are designed for a dark, efficient, and visually consistent workflow across various applications, with a "suckless-inspired" philosophy.

## Table of Contents

- [Arch Qtile Dotfiles](#arch-qtile-dotfiles)
  - [Key Configurations](#key-configurations)
    - [Window Manager (Qtile)](#window-manager-qtile)
    - [Terminal Emulators](#terminal-emulators)
    - [Shell Environment](#shell-environment)
    - [Text Editor (Neovim)](#text-editor-neovim)
    - [File Managers](#file-managers)
    - [User Interface](#user-interface)
    - [System Utilities](#system-utilities)
  - [Keybindings](#keybindings)
  - [Usage](#usage)
  - [Prerequisites](#prerequisites)
  - [Dependencies](#dependencies)

## Key Configurations

### Window Manager (Qtile)

- **Configuration:** [`wm/.config/qtile/config.py`](wm/.config/qtile/config.py)
- **Description:** The Qtile setup features a multi-screen configuration with custom bars defined in `wm/.config/qtile/bars.py`. It utilizes various layouts (`MonadTall`, `MonadWide`, `MonadThreeCol`) and refactored, event-driven widgets for improved efficiency and responsiveness. For detailed widget configurations and scripts, refer to the `wm/.config/qtile/widgets/` and `wm/.config/qtile/scripts/` directories respectively.

### Terminal Emulators

- **Kitty:** [`terminal/.config/kitty/kitty.conf`](terminal/.config/kitty/kitty.conf) - The primary terminal emulator, configured with the "JetBrainsMonoNL Nerd Font", a powerline-style tab bar, and custom keybindings.
- **Wezterm:** [`terminal/.wezterm.lua`](terminal/.wezterm.lua) - A highly customizable, Lua-configured terminal emulator.
- **Alacritty:** [`terminal/.config/alacritty/alacritty.toml`](terminal/.config/alacritty/alacritty.toml) - A fast, GPU-accelerated terminal emulator.

### Shell Environment

- **Zsh:** [`shell/.zshrc`](shell/.zshrc) - Powerful shell configured with `zim` for plugin management, aliases, and `fzf`-based interactive functions. Also includes `.zimrc`, `.bashrc`, `.tmux.conf`, and `.vimrc` for specific environments.
- **Fish:** [`shell/config.fish`](shell/config.fish) - User-friendly shell with syntax highlighting, autosuggestions, and tab completions.
- **Starship:** [`shell/.config/starship.toml`](shell/.config/starship.toml) - A minimal, blazing-fast, and infinitely customizable prompt for any shell.
- **Atuin:** [`shell/.config/atuin/config.toml`](shell/.config/atuin/config.toml) - Modern, encrypted, and synchronized shell history.

### Text Editor (Neovim)

- **Configuration:** [`shell/.config/nvim/init.lua`](shell/.config/nvim/init.lua)
- **Description:** The primary text editor, configured in Lua with `lazy.nvim` for modular plugin management. Refer to `shell/.config/nvim/lua/plugins/` for plugin details.

### File Managers

- **Ranger:** [`shell/.config/ranger/`](shell/.config/ranger/) - See configuration for details.
- **Yazi:** [`shell/.config/yazi/`](shell/.config/yazi/) - See configuration for details.

### User Interface

- **GTK/Qt Theming:** [`gtkqt/`](gtkqt/) - Centralized configurations for GTK and Qt applications for a consistent aesthetic.
- **Rofi:** [`wm/.config/rofi/`](wm/.config/rofi/) - Application launcher and script runner. See directory for themes and scripts.
- **Dunst:** [`wm/.config/dunst/dunstrc`](wm/.config/dunst/dunstrc) - Notification daemon configured for a dark theme and custom rules.
- **Picom:** [`wm/.config/picom/picom.conf`](wm/.config/picom/picom.conf) - Lightweight compositor for visual effects.
- **Zen Browser:** [`browser/.zen/m.Default (release)/user.js`](<browser/.zen/m.Default%20(release)/user.js>) - Minimal and privacy-focused browser configuration.

### System Utilities

- **Fastfetch:** [`shell/.config/fastfetch/config.jsonc`](shell/.config/fastfetch/config.jsonc) - Neofetch-like tool for system information.
- **Tealdeer:** [`shell/.config/tealdeer/config.toml`](shell/.config/tealdeer/config.toml) - Fast, modern `tldr` client in Rust.
- **Greenclip:** [`wm/.config/greenclip.toml`](wm/.config/greenclip.toml) - Clipboard manager.
- **X11:** [`X11/`](X11/) - X11-related configurations, including `.xprofile` for session startup and `.Xresources` for application theming.

## Keybindings

For a comprehensive list of keybindings, please refer to the Qtile configuration file: [`wm/.config/qtile/keys.py`](wm/.config/qtile/keys.py)

## Usage

These dotfiles are intended to be managed using [GNU Stow](https://www.gnu.org/software/stow/), a symlink manager. This allows for easy installation and management of the dotfiles by creating symlinks from the files in this repository to their corresponding locations in the user's home directory.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/moturri/dot.git ~/.dot
    ```
2.  **Navigate to the repository:**
    ```bash
    cd ~/.dot
    ```
3.  **Stow the dotfiles:**
    To stow all the dotfiles at once, run:
    ```bash
    stow .
    ```
    To stow a specific part of the configuration, such as the Qtile setup, you can run:
    ```bash
    stow wm
    ```

## Prerequisites

- **Operating System:** Arch Linux.
- **Window Manager:** Qtile.
- **Symlink Manager:** GNU Stow.

## Dependencies

The configurations in this repository rely on several external tools. They are grouped by category below.

### Core

- `stow`
- `pipewire`
- `wireplumber`
- `pyudev`
- `brightnessctl`

### Shell

- `zsh`
- `fish`
- `starship`
- `atuin`
- `neovim`
- `ranger`
- `yazi`
- `fastfetch`
- `tealdeer`

### Graphical User Interface

- `kitty`
- `wezterm`
- `alacritty`
- `rofi`
- `dunst`
- `picom`
- `greenclip`

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
