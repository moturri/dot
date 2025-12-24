# Arch Linux Dotfiles

This repository contains a curated collection of personal dotfiles for an Arch Linux system running the Qtile window manager. The configurations are designed to create an efficient, powerful, and visually consistent development environment.

The guiding philosophy is a preference for tools that are simple, lightweight, and adhere to the "do one thing well" principle. This "suckless-inspired" approach is balanced with a pragmatic selection of more complex tools when they offer significant workflow enhancements.

## Core Components

This setup is built around a few key components that define the user experience:

-   **Window Manager (Qtile):** As a tiling window manager configured in Python, Qtile provides a high degree of flexibility and control. The configuration is modular and includes a multi-screen setup, custom status bars, and a variety of layouts. To maximize efficiency, the widgets are event-driven. The main configuration can be found in [`wm/.config/qtile/config.py`](wm/.config/qtile/config.py).
-   **Terminal Emulators:** A selection of high-performance terminal emulators are configured:
    -   **Kitty:** The primary terminal, offering a balance of speed, features, and extensive configurability.
    -   **Wezterm:** A powerful, cross-platform terminal emulator and multiplexer written in Rust and configured in Lua.
    -   **Alacritty:** A simple, fast, and GPU-accelerated terminal emulator.
-   **Shell Environment:**
    -   **Zsh:** A powerful and flexible shell, with plugin management handled by `zim`. It is configured with a rich set of aliases, custom functions, and a sleek `starship` prompt.
    -   **Fish:** A user-friendly shell with excellent out-of-the-box features like syntax highlighting and autosuggestions.
-   **Text Editor (Neovim):** The configuration for this highly extensible, Vim-based text editor is written in Lua and uses `lazy.nvim` for fast and modular plugin management.
-   **File Manager (Yazi):** A modern, terminal-based file manager written in Rust, designed for speed and usability.

## Theming and Aesthetics

A consistent visual theme is maintained across the entire environment:

-   **GTK/Qt Theming:** Centralized configurations in the [`gtkqt/`](gtkqt/) directory ensure a uniform appearance for both GTK and Qt applications.
-   **Icons and Cursors:** Custom icon and cursor themes are used to provide a polished and cohesive visual experience.
-   **Fonts:** Nerd Fonts are used to provide a rich set of icons and symbols in the terminal and status bars, with JetBrainsMono Nerd Font being the preferred typeface.

## Installation

These dotfiles are managed using **GNU Stow**, a symlink farm manager that simplifies the process of deploying and managing configurations.

### Prerequisites

-   **Operating System:** Arch Linux (adaptable to other Linux distributions).
-   **Window Manager:** Qtile.
-   **Symlink Manager:** GNU Stow.

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/moturri/dot.git ~/.dot
    ```
2.  **Navigate to the repository:**
    ```bash
    cd ~/.dot
    ```
3.  **Deploy the dotfiles:**
    To deploy all dotfiles at once, run:
    ```bash
    stow .
    ```
    Alternatively, to deploy a specific set of configurations (e.g., for Qtile), you can run:
    ```bash
    stow wm
    ```

## Dependencies

The following table lists the primary dependencies for this setup, grouped by category.

| Category | Dependency | Description |
| :--- | :--- | :--- |
| **Core** | `stow` | A symlink farm manager for deploying the dotfiles. |
| | `pipewire` | A modern server for handling audio and video streams. |
| | `wireplumber` | A session and policy manager for PipeWire. |
| | `pyudev` | A Python binding for libudev, used by some Qtile widgets. |
| | `brightnessctl`| A utility for controlling screen brightness. |
| **Shell** | `zsh` | A powerful and extensible command-line shell. |
| | `fish` | A smart and user-friendly command-line shell. |
| | `starship` | A minimal, fast, and infinitely customizable prompt for any shell. |
| | `atuin` | A modern, encrypted, and synchronized shell history manager. |
| | `neovim` | A highly extensible, Vim-based text editor. |
| | `yazi` | A modern, terminal-based file manager written in Rust. |
| | `fastfetch` | A fast and lightweight system information tool. |
| | `tealdeer` | A fast and modern `tldr` client implemented in Rust. |
| **Graphical UI** | `kitty` | The primary terminal emulator, offering speed and features. |
| | `wezterm` | A powerful, cross-platform terminal emulator and multiplexer. |
| | `alacritty` | A simple, fast, and GPU-accelerated terminal emulator. |
| | `rofi` | A versatile application launcher and window switcher. |
| | `dunst` | A lightweight and customizable notification daemon. |
| | `picom` | A lightweight compositor for X11, providing visual effects. |
| | `greenclip` | A simple and efficient clipboard manager. |

## Contributing

Contributions and suggestions for improvement are always welcome. Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
