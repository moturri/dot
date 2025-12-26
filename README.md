# Arch Linux Dotfiles

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Project Overview

This repository contains a curated collection of personal dotfiles for an Arch Linux system running the Qtile window manager. The configurations are designed to create an efficient, powerful, and visually consistent development environment, guided by a "suckless-inspired" philosophy that favors simplicity and modularity.

### Core Components

- **Window Manager (Qtile):** A flexible, Python-based tiling window manager with a modular, multi-screen setup, custom status bars, and event-driven widgets for maximum efficiency. The main configuration can be found in [`wm/.config/qtile/config.py`](wm/.config/qtile/config.py).
- **Terminal Emulators:** A selection of high-performance terminal emulators are configured:
  - **Kitty:** The primary terminal, offering a balance of speed, features, and extensive configurability.
  - **Wezterm:** A powerful, cross-platform terminal emulator and multiplexer written in Rust.
  - **Alacritty:** A simple, fast, and GPU-accelerated terminal emulator.
- **Shell Environment:**
  - **Zsh:** A powerful and flexible shell with plugin management handled by `zim`.
  - **Fish:** A user-friendly shell with excellent out-of-the-box features.
- **Text Editor (Neovim):** A highly extensible, Vim-based text editor configured in Lua with `lazy.nvim` for fast, modular plugin management.
- **File Manager (Yazi):** A modern, terminal-based file manager written in Rust, designed for speed and usability.

### Theming and Aesthetics

A consistent visual theme is maintained across the entire environment:

- **GTK/Qt Theming:** Centralized configurations in the [`gtkqt/`](gtkqt/) directory ensure a uniform appearance for both GTK and Qt applications.
- **Icons and Cursors:** Custom icon and cursor themes provide a polished and cohesive visual experience.
- **Fonts:** JetBrainsMono Nerd Font is used to provide a rich set of icons and symbols in the terminal and status bars.

## Installation Guide

These dotfiles are managed using **GNU Stow**, a symlink farm manager that simplifies the process of deploying and managing configurations.

### Prerequisites

- **Operating System:** Arch Linux (adaptable to other Linux distributions).
- **Window Manager:** Qtile.
- **Symlink Manager:** GNU Stow.
- **Dependencies:** Ensure the tools listed in the table below are installed.

| Category         | Dependency      | Description                                                      |
| :--------------- | :-------------- | :--------------------------------------------------------------- |
| **Core**         | `stow`          | Symlink farm manager for deploying the dotfiles.                 |
|                  | `pipewire`      | Modern server for handling audio and video streams.              |
|                  | `wireplumber`   | Session and policy manager for PipeWire.                         |
|                  | `pyudev`        | Python binding for `libudev`, used by some Qtile widgets.        |
|                  | `brightnessctl` | Utility for controlling screen brightness.                       |
| **Shell**        | `zsh`           | Powerful and extensible command-line shell.                      |
|                  | `fish`          | Smart and user-friendly command-line shell.                      |
|                  | `starship`      | Minimal, fast, and infinitely customizable prompt for any shell. |
|                  | `atuin`         | Modern, encrypted, and synchronized shell history manager.       |
|                  | `neovim`        | Highly extensible, Vim-based text editor.                        |
|                  | `yazi`          | Modern, terminal-based file manager written in Rust.             |
|                  | `fastfetch`     | Fast and lightweight system information tool.                    |
|                  | `tealdeer`      | Fast and modern `tldr` client implemented in Rust.               |
| **Graphical UI** | `kitty`         | Primary terminal emulator, offering speed and features.          |
|                  | `wezterm`       | Powerful, cross-platform terminal emulator and multiplexer.      |
|                  | `alacritty`     | Simple, fast, and GPU-accelerated terminal emulator.             |
|                  | `rofi`          | Versatile application launcher and window switcher.              |
|                  | `dunst`         | Lightweight and customizable notification daemon.                |
|                  | `picom`         | Lightweight compositor for X11, providing visual effects.        |
|                  | `greenclip`     | Simple and efficient clipboard manager.                          |

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/moturri/dot.git ~/.dot
    ```
2.  **Navigate to the repository:**
    ```bash
    cd ~/.dot
    ```
3.  **Deploy the dotfiles:**
    To deploy all configurations, run:
    ```bash
    stow .
    ```
    To deploy a specific set of configurations (e.g., for Qtile), you can stow the corresponding directory:
    ```bash
    stow wm
    ```

## Usage Examples

The Zsh configuration includes several custom functions and aliases to streamline common tasks:

- **`tldrr`**: An interactive `tldr` client that uses `fzf` to search for and display cheat sheets.
  ```bash
  # Bound to Ctrl+F
  tldrr
  ```
- **`yayfz`**: An interactive `yay` helper that uses `fzf` to search for and view information about packages in the Arch User Repository (AUR).
  ```bash
  h
  # Bound to Ctrl+Y
  yayfz
  ```
- **`cht`**: A simple script to quickly fetch cheat sheets from `cht.sh`.
  ```bash
  # Get a cheat sheet for tar
  cht tar
  ```
- **Enhanced Commands**:
  - `ls` is aliased to `eza --icons=always` for modern, icon-rich directory listings.
  - `cat` is aliased to `bat --paging=never --style=full` for syntax-highlighted file viewing.

## Contribution Guidelines

Contributions, issues, and feature requests are welcome. If you have any suggestions for improvement, please feel free to open an issue or submit a pull request.

1.  Fork the repository.
2.  Create a new branch: `git checkout -b feature/...`.
3.  Make your changes and commit them: `git commit -m '...'`.
4.  Push to the branch: `git push origin feature/...`.
5.  Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
