# Arch Qtile Dotfiles

This repository contains my personal dotfiles for a suckless-inspired approach.
Specifically tailored for [Arch Linux](https://archlinux.org/) and [Qtile](https://qtile.org/).
The configs are for various tools and environments, ensuring
a streamlined and personalized experience across my Linux setup.

## Key Configurations

- **Window Manager ([Qtile](https://qtile.org/)):** The [Qtile setup](wm/.config/qtile/config.py) features a multi-screen configuration with custom bars, layouts (`MonadTall`, `MonadWide`, `MonadThreeCol`), and a startup script for essential applications.
- **Terminal ([Kitty](https://sw.kovidgoyal.net/kitty/)):** [Kitty](terminal/.config/kitty/kitty.conf) is the primary terminal emulator, configured with "JetBrainsMonoNL Nerd Font," a powerline-style tab bar, and custom keybindings for a streamlined workflow.
- **Shell ([Zsh](https://www.zsh.org/)):** The [Zsh configuration](shell/.zshrc) is managed by `zim` and includes numerous aliases, `fzf`-integrated functions, and a customized `starship` prompt.
- **Editor ([Neovim](https://neovim.io/)):** The [Neovim configuration](shell/.config/nvim/init.lua) is managed in Lua and uses `lazy.nvim` for plugin management.
- **Browser ([Zen Browser](https://github.com/zen-browser/zen)):** [Zen Browser](browser/.zen/m.Default%20(release)/user.js) is configured for a minimal and privacy-focused experience, with a dark mode, GTK theme integration, and various performance and privacy enhancements.

### Theming

- **[GTK/Qt](gtkqt/):** Consistent look and feel across GTK and Qt applications.
- **[X11](X11/):** Xresources for theming X applications, including a Dracula-OLED theme for XTerm.

### Other Tools

- **[Rofi](https://github.com/davatorium/rofi):** Application launcher with [custom scripts](wm/.config/rofi/scripts/).
- **[Dunst](https://dunst-project.org/):** Notification daemon with a [dark theme and custom rules](wm/.config/dunst/dunstrc).
- **[Picom](https://github.com/yshui/picom):** Lightweight compositor with a [minimal configuration](wm/.config/picom/picom.conf).

## Usage

These dotfiles are intended to be managed using a symlink manager like GNU Stow. To deploy the dotfiles, you would typically navigate to the root of this repository and run a command like:

```bash
stow .
```

This would create symlinks from the files in this repository to their corresponding locations in the user's home directory.

## Dependencies

The Qtile configurations and some other scripts within this repository rely
on the following tools:

- [brightnessctl](https://github.com/Hummer12007/brightnessctl) — for screen
  brightness control (`BrightctlWidget`)

- [pyudev](https://github.com/pyudev/pyudev) — for monitoring ACPI battery events (`BatteryWidget`)
- [pipewire](https://pipewire.org) — for low-latency audio/video
- [wireplumber](https://gitlab.freedesktop.org/pipewire/wireplumber) — for managing audio devices via `wpctl`
- [stow](https://www.gnu.org/software/stow/) — for managing symlinks and
  maintaining clean dotfile deployment
