# Dotfiles

A comprehensive set of configurations for a modern Arch Linux desktop, built for efficiency and a streamlined development workflow.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Arch Linux](https://img.shields.io/badge/Arch%20Linux-supported-blue.svg?logo=arch-linux)

## Features

*   **Window Manager:** Highly customized **Qtile** setup with event-driven widgets and a multi-screen configuration.
*   **Terminal:** Pre-configured **Kitty** terminal with the JetBrains Mono font and a powerline-style tab bar.
*   **Shell:** A powerful **Zsh** environment managed by `zim`, featuring numerous aliases, `fzf`-based functions, and a custom `starship` prompt.
*   **Editor:** A fast and modular **Neovim** configuration in Lua, with `lazy.nvim` for plugin management.
*   **File Manager:** A modern `yazi` setup with a Dracula theme and custom keybindings.
*   **Theming:** A consistent dark theme across GTK and Qt applications.

## Installation

These dotfiles are managed using [GNU Stow](https://www.gnu.org/software/stow/).

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/moturri/dot.git ~/.dot
    ```

2.  **Navigate to the directory and deploy:**
    ```bash
    cd ~/.dot && stow .
    ```
    To deploy a specific configuration (e.g., `wm`), you can run `stow wm`.

## Usage

The shell configuration includes several aliases and functions to improve productivity:

*   **`tldrr`**: Interactive `tldr` client using `fzf` (`Ctrl+F`).
*   **`yayfz`**: Interactive `yay` helper with `fzf` (`Ctrl+Y`).
*   **`cht`**: Quick cheat sheet lookup via `cht.sh`.
*   **Aliases**: `ls` is aliased to `eza` and `cat` to `bat`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
