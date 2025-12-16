# Arch Qtile Dotfiles

This repository contains my personal dotfiles, tailored for an Arch Linux environment running the Qtile window manager. The configurations are designed for a dark, efficient, and visually consistent workflow across various applications, with a "suckless-inspired" philosophy.

## Key Configurations

### Window Manager (Qtile)

- **Configuration:** [`wm/.config/qtile/config.py`](wm/.config/qtile/config.py)
- **Description:** The Qtile setup features a multi-screen configuration with custom bars defined in `wm/.config/qtile/bars.py`. It uses a variety of layouts, including `MonadTall`, `MonadWide`, and `MonadThreeCol`. The widgets have been refactored to be more robust and event-driven.
    - **Battery Widget:** The `BatteryWidget` in `wm/.config/qtile/widgets/battery.py` is a purely event-driven component, using `pyudev` and `select` for listening to power events.
    - **Audio Widget:** The `BaseAudioWidget` in `wm/.config/qtile/widgets/wpctl.py` is an event-driven PipeWire audio widget using `wpctl subscribe`.
    - **Brightness Widget:** The `BrightctlWidget` in `wm/.config/qtile/widgets/brightctl.py` uses `brightnessctl` to control screen brightness.
    - **Scripts:** The `wm/.config/qtile/scripts/` directory contains various utility scripts for autostart, keybinding generation, and monitor setup.

### Terminal (Kitty)

- **Configuration:** [`terminal/.config/kitty/kitty.conf`](terminal/.config/kitty/kitty.conf)
- **Description:** Kitty is the primary terminal emulator, configured with the "JetBrainsMonoNL Nerd Font". It features a powerline-style tab bar and custom keybindings for a streamlined workflow.

### Shell (Zsh)

- **Configuration:** [`shell/.zshrc`](shell/.zshrc)
- **Description:** Zsh is configured using `zim` for plugin management. The configuration includes numerous aliases (e.g., `ls` -> `eza`, `cat` -> `bat`), custom functions that integrate with `fzf` for interactive workflows (e.g., `tldrr`, `yayfz`), and a customized `starship` prompt.

### Editor (Neovim)

- **Configuration:** [`shell/.config/nvim/init.lua`](shell/.config/nvim/init.lua)
- **Description:** Neovim is the primary text editor. The configuration is managed in Lua and uses `lazy.nvim` for plugin management, ensuring a fast and modular setup.

### Browser (Zen Browser)

- **Configuration:** [`browser/.zen/m.Default (release)/user.js`](browser/.zen/m.Default%20(release)/user.js)
- **Description:** Zen Browser is configured for a minimal and privacy-focused experience, with a dark mode, GTK theme integration, and various performance and privacy enhancements.

### Theming

- **GTK/Qt:** Configurations for GTK and Qt applications are managed in the `gtkqt/` directory, ensuring a consistent look and feel.
- **X11:** The `X11/` directory contains X11-related configurations such as `.xprofile` for session startup and `.Xresources` for X application theming.

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

The configurations in this repository rely on several external tools, including:

- `brightnessctl`
- `pyudev`
- `pipewire`
- `wireplumber`
- `stow`
- `zsh`
- `neovim`
- `kitty`
- `rofi`
- `dunst`
- `picom`