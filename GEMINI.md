# Dotfiles Analysis (GEMINI.md)

## Directory Overview

This directory contains a comprehensive set of personal dotfiles, meticulously organized for an Arch Linux environment running the Qtile window manager. The configurations aim for a consistent, dark, and efficient user experience across various command-line and graphical applications, with a strong emphasis on a "suckless-inspired" philosophy.

The dotfiles are structured into logical categories, making it easy to manage configurations for different parts of the system, including the shell, terminal, window manager, browsers, and theming.

## Key Configurations

### Window Manager (Qtile)

- **Configuration:** `wm/.config/qtile/config.py`
- **Description:** The Qtile setup features a multi-screen configuration with custom bars defined in `wm/.config/qtile/bars.py`. It uses a variety of layouts, including `MonadTall`, `MonadWide`, and `MonadThreeCol`. The widgets are now more robust and event-driven.
    - The `BatteryWidget` in `wm/.config/qtile/widgets/battery.py` is now fully event-driven using `pyudev` to monitor battery status, eliminating polling to reduce CPU usage. It features graceful shutdown, debouncing of udev events, and provides visual and notification-based alerts for battery state changes.
    - The `BrightctlWidget` in `wm/.config/qtile/widgets/brightctl.py` has been refactored to be a `TextBox` subclass, making it fully event-driven and removing the need for polling.
    - The `BaseAudioWidget` in `wm/.config/qtile/widgets/wpctl.py` is an event-driven PipeWire audio widget using `wpctl subscribe`. It has been enhanced for safety and clean reloads.

### Terminal (Kitty)

- **Configuration:** `terminal/.config/kitty/kitty.conf`
- **Description:** Kitty is the primary terminal emulator, configured with the "JetBrainsMonoNL Nerd Font". It features a powerline-style tab bar and custom keybindings for a streamlined workflow.

### Shell (Zsh)

- **Configuration:** `shell/.zshrc`, `shell/.zimrc`
- **Description:** Zsh is the default shell, with plugin management handled by `zim`. The configuration includes numerous aliases for common commands (e.g., `ls` -> `eza`, `cat` -> `bat`), custom functions that integrate with `fzf` for interactive workflows (e.g., `tldrr`, `yayfz`), and a customized `starship` prompt.

### Editor (Neovim)

- **Configuration:** `shell/.config/nvim/init.lua`
- **Description:** Neovim is the primary text editor. The configuration is managed in Lua and uses `lazy.nvim` for plugin management, ensuring a fast and modular setup.

### Browser (Zen Browser)

- **Configuration:** `browser/.zen/m.Default (release)/user.js`, `browser/.zen/m.Default (release)/chrome/userChrome.css`
- **Description:** Zen Browser is configured for a minimal and privacy-focused experience, with a dark mode, GTK theme integration, and various performance and privacy enhancements.

### Theming

- **GTK/Qt:** Configurations for GTK and Qt applications are managed in the `gtkqt/` directory, ensuring a consistent look and feel across different toolkits.
- **X11:** The `X11/` directory contains Xresources for theming X applications, including a Dracula-OLED theme for XTerm.

### Other Tools

- **Rofi:** Used as an application launcher and for various scripts. The configuration is in `wm/.config/rofi/`.
- **Dunst:** The notification daemon, configured in `wm/.config/dunst/dunstrc` with a dark theme and custom rules.
- **Picom:** The compositor, configured in `wm/.config/picom/picom.conf` for a lightweight experience without excessive effects.

## Usage

These dotfiles are intended to be managed using a symlink manager like GNU Stow. To deploy the dotfiles, you would typically navigate to the root of this repository and run a command like:

```bash
stow .
```

This would create symlinks from the files in this repository to their corresponding locations in the user's home directory.

## Dependencies

The configurations in this repository rely on several external tools:

- `brightnessctl`
- `pyudev`
- `pipewire`
- `wireplumber`
- `stow`